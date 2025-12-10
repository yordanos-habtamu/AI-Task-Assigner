"""
LLM Provider abstraction layer.
Supports multiple AI providers: OpenAI, Google Gemini, and local AI via Ollama.
"""

import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def get_json_completion(self, prompt: str, system_prompt: str, schema: type[BaseModel]) -> Dict[str, Any]:
        """
        Get structured JSON completion from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt
            schema: Pydantic model for output schema
            
        Returns:
            Dict with parsed JSON output
        """
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the name of the provider."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-4o-mini)
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        
        self.api_key = api_key
        self.model = model
        self.llm = ChatOpenAI(
            model=model,
            temperature=0,
            api_key=api_key
        )
        self.parser_class = JsonOutputParser
        self.prompt_template = ChatPromptTemplate
    
    def get_json_completion(self, prompt: str, system_prompt: str, schema: type[BaseModel]) -> Dict[str, Any]:
        """Get JSON completion from OpenAI."""
        parser = self.parser_class(pydantic_object=schema)
        
        prompt_obj = self.prompt_template.from_messages([
            ("system", system_prompt + "\n\n{format_instructions}"),
            ("user", prompt)
        ])
        
        chain = prompt_obj | self.llm | parser
        
        result = chain.invoke({
            "format_instructions": parser.get_format_instructions()
        })
        
        return result
    
    def get_provider_name(self) -> str:
        return f"OpenAI ({self.model})"


class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key
            model: Model name (default: gemini-1.5-pro)
                   Available models: gemini-pro, gemini-1.5-pro
        """
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        
        self.api_key = api_key
        self.model = model
        self.llm = ChatGoogleGenerativeAI(
            model=model,
            temperature=0,
            google_api_key=api_key,
            convert_system_message_to_human=True  # Important for Gemini
        )
        self.parser_class = JsonOutputParser
        self.prompt_template = ChatPromptTemplate
    
    def get_json_completion(self, prompt: str, system_prompt: str, schema: type[BaseModel]) -> Dict[str, Any]:
        """Get JSON completion from Gemini."""
        parser = self.parser_class(pydantic_object=schema)
        
        prompt_obj = self.prompt_template.from_messages([
            ("system", system_prompt + "\n\n{format_instructions}"),
            ("user", prompt)
        ])
        
        chain = prompt_obj | self.llm | parser
        
        try:
            result = chain.invoke({
                "format_instructions": parser.get_format_instructions()
            })
            return result
        except Exception as e:
            error_str = str(e)
            if "404" in error_str and "not found" in error_str:
                raise ValueError(
                    f"Gemini Model '{self.model}' not found or API not enabled.\n"
                    "1. Check if 'Google Generative AI API' is enabled in your Google Cloud Console.\n"
                    "2. Verify your API key is correct.\n"
                    "3. Try a different model (e.g., gemini-1.5-flash)."
                ) from e
            raise e
    
    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"


class OllamaProvider(LLMProvider):
    """Local AI provider using OpenAI-compatible API endpoints (Ollama, LM Studio, etc.)."""
    
    def __init__(self, base_url: str = "http://localhost:1234", model: str = "llama-3.2-1b-instruct"):
        """
        Initialize Local AI provider with OpenAI-compatible endpoints.
        
        Args:
            base_url: Base URL for local AI server (default: http://localhost:1234)
            model: Model name (default: llama-3.2-1b-instruct)
        
        Note: This uses the OpenAI-compatible API format (/v1/chat/completions)
        Works with: Ollama, LM Studio, LocalAI, etc.
        """
        from langchain_openai import ChatOpenAI
        from langchain_core.output_parsers import JsonOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        
        self.base_url = base_url
        self.model = model
        
        # Use ChatOpenAI with custom base_url for OpenAI-compatible endpoints
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,  # Match your curl example
            base_url=f"{base_url}/v1",  # Adds /v1 automatically
            api_key="not-needed",  # Local server doesn't need API key
            max_tokens=-1,  # Match your curl example (-1 = no limit)
            streaming=False  # Disable streaming to match your example
        )
        self.parser_class = JsonOutputParser
        self.prompt_template = ChatPromptTemplate
    
    def get_json_completion(self, prompt: str, system_prompt: str, schema: type[BaseModel]) -> Dict[str, Any]:
        """Get JSON completion from local AI."""
        parser = self.parser_class(pydantic_object=schema)
        
        prompt_obj = self.prompt_template.from_messages([
            ("system", system_prompt + "\n\n{format_instructions}"),
            ("user", prompt)
        ])
        
        chain = prompt_obj | self.llm | parser
        
        try:
            result = chain.invoke({
                "format_instructions": parser.get_format_instructions()
            })
            
            if result is None:
                raise ValueError(
                    f"Local AI server at {self.base_url} returned None. "
                    f"Check if the server is running and model '{self.model}' is available."
                )
            
            return result
        except Exception as e:
            error_msg = str(e)
            if "Connection" in error_msg or "refused" in error_msg:
                raise ValueError(
                    f"Cannot connect to local AI server at {self.base_url}/v1/chat/completions\n"
                    f"1. Check if your AI server is running\n"
                    f"2. Verify the base URL in .env: OLLAMA_BASE_URL={self.base_url}\n"
                    f"3. Test with: curl {self.base_url}/v1/models"
                ) from e
            raise e
    
    def get_provider_name(self) -> str:
        return f"Local AI ({self.model})"


def create_provider(
    provider_type: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> LLMProvider:
    """
    Factory function to create LLM providers.
    
    Args:
        provider_type: Type of provider ('openai', 'gemini', or 'ollama')
        api_key: API key for cloud providers
        model: Model name (optional, uses defaults if not provided)
        base_url: Base URL for Ollama (optional)
        
    Returns:
        LLMProvider instance
        
    Raises:
        ValueError: If provider_type is unknown or required parameters are missing
    """
    provider_type = provider_type.lower()
    
    if provider_type == "openai":
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key.")
        
        model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAIProvider(api_key, model)
    
    elif provider_type == "gemini":
        if not api_key:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable or pass api_key.")
        
        model = model or os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
        return GeminiProvider(api_key, model)
    
    elif provider_type == "ollama":
        base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:1234")
        model = model or os.getenv("OLLAMA_MODEL", "llama-3.2-1b-instruct")
        return OllamaProvider(base_url, model)
    
    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Supported: 'openai', 'gemini', 'ollama'")
