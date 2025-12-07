"""
Streamlit Frontend for AI Task Assignment System
Enhanced with GitHub integration, database storage, and multi-provider AI support.
"""

import json
import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ai.graph import run_graph
from backend.data_source_manager import DataSourceManager
from backend.database import get_database
from backend.crud import AssignmentService, IssueService, DeveloperService, AuthService
from frontend.auth import render_login, render_signup


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="AI Task Assignment System",
        page_icon="🤖",
        layout="wide"
    )
    
    # Initialize Database
    db = get_database()
    
    # Session State Initialization
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "auth_mode" not in st.session_state:
        st.session_state.auth_mode = "login"
        
    # Auth Flow
    if not st.session_state.logged_in:
        # Check for OAuth callback token
        query_params = st.query_params
        if 'auth_token' in query_params:
            import requests
            oauth_url = os.getenv('OAUTH_SERVER_URL', 'http://localhost:8502')
            
            try:
                response = requests.get(
                    f"{oauth_url}/auth/verify",
                    params={'token': query_params['auth_token']},
                    timeout=5
                )
                
                if response.status_code == 200 and response.json().get('valid'):
                    data = response.json()
                    st.session_state.user_id = data['user_id']
                    st.session_state.username = data['username']
                    st.session_state.logged_in = True
                    
                    # Clear the token from URL
                    st.query_params.clear()
                    st.rerun()
            except Exception as e:
                st.error(f"OAuth verification failed: {str(e)}")
        
        if st.session_state.auth_mode == "login":
            render_login()
        else:
            render_signup()
        return

    # Load User Keys
    if "keys_loaded" not in st.session_state:
        session = db.get_session()
        auth_service = AuthService(session)
        keys = auth_service.get_user_keys(st.session_state.user_id)
        session.close()
        
        if keys.get("openai"):
            os.environ["OPENAI_API_KEY"] = keys["openai"]
        if keys.get("gemini"):
            os.environ["GOOGLE_API_KEY"] = keys["gemini"]
        st.session_state.keys_loaded = True

    render_main_app()


def render_main_app():
    """Render the main application content."""
    st.title("🤖 AI Task Assignment System")
    st.markdown("""
    Upload your issues and developers data OR connect to a GitHub repository for intelligent task assignments powered by AI.
    The system analyzes skills, workload, and preferences to make optimal assignments.
    """)
    
    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")
    
    # User Profile Section
    with st.sidebar.expander("👤 User Profile", expanded=False):
        st.write(f"Logged in as: **{st.session_state.username}**")
        if st.button("Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.keys_loaded = False
            st.rerun()
    
    # AI Provider Selection
    
    # AI Provider Selection
    st.sidebar.subheader("🤖 AI Provider")
    
    provider = st.sidebar.selectbox(
        "Select AI Provider",
        ["openai", "gemini", "ollama"],
        index=0,
        help="Choose which AI provider to use for analysis"
    )
    
    # Set provider in environment
    os.environ["AI_PROVIDER"] = provider
    
    # Provider-specific configuration
    if provider == "openai":
        default_openai_key = os.getenv("OPENAI_API_KEY", "")
        openai_key = st.sidebar.text_input(
            "OpenAI API Key",
            value=default_openai_key,
            type="password",
            help="Your OpenAI API key"
        )
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        if default_openai_key:
            st.sidebar.success("✓ OpenAI API key loaded")
        
        model = st.sidebar.selectbox(
            "Model",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
            help="Select OpenAI model"
        )
        os.environ["OPENAI_MODEL"] = model
        st.sidebar.info(f"Using: {model}")
        
    elif provider == "gemini":
        default_gemini_key = os.getenv("GOOGLE_API_KEY", "")
        gemini_key = st.sidebar.text_input(
            "Google API Key",
            value=default_gemini_key,
            type="password",
            help="Your Google API key for Gemini"
        )
        if gemini_key:
            os.environ["GOOGLE_API_KEY"] = gemini_key
        if default_gemini_key:
            st.sidebar.success("✓ Google API key loaded")
        
        model = st.sidebar.selectbox(
            "Model",
            ["gemini-1.5-pro", "gemini-pro","gemini-2.0-flash"],
            help="Select Gemini model"
        )
        os.environ["GEMINI_MODEL"] = model
        st.sidebar.info(f"Using: {model}")
        
    else:  # ollama
        st.sidebar.info("🏠 Using local AI (no API key needed)")
        
        base_url = st.sidebar.text_input(
            "Ollama URL",
            value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            help="Ollama server URL"
        )
        os.environ["OLLAMA_BASE_URL"] = base_url
        
        model = st.sidebar.text_input(
            "Model",
            value=os.getenv("OLLAMA_MODEL", "llama3.1"),
            help="Ollama model name (e.g., llama3.1, mistral)"
        )
        os.environ["OLLAMA_MODEL"] = model
        st.sidebar.info(f"Using: {model}")
        
        with st.sidebar.expander("ℹ️ Ollama Setup"):
            st.markdown("""
            **Quick Start:**
            1. Install Ollama: `curl -fsSL https://ollama.com/install.sh | sh`
            2. Pull a model: `ollama pull llama3.1`
            3. Verify: `ollama list`
            
            Popular models: llama3.1, mistral, codellama
            """)
    
    st.sidebar.markdown("---")
    
    # Save Keys Button
    if st.sidebar.button("💾 Save API Keys to Profile"):
        db = get_database()
        session = db.get_session()
        auth_service = AuthService(session)
        
        openai_key = os.getenv("OPENAI_API_KEY")
        google_key = os.getenv("GOOGLE_API_KEY")
        
        auth_service.update_api_keys(
            st.session_state.user_id, 
            openai_key=openai_key, 
            google_key=google_key
        )
        session.close()
        st.sidebar.success("Keys saved to profile!")
    
    st.sidebar.markdown("---")
    
    # GitHub Token Input
    st.sidebar.subheader("🐙 GitHub")
    default_github_token = os.getenv("GITHUB_TOKEN", "")
    
    github_token = st.sidebar.text_input(
        "GitHub Token (Optional)",
        value=os.getenv("GITHUB_TOKEN", ""),
        type="password",
        help="Required for private repositories or higher rate limits"
    )
    
    if default_github_token:
        st.sidebar.info("✓ GitHub token loaded")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📂 Data Source", "📜 Assignment History", "📝 Review & Send"])
    
    with tab1:
        render_data_source_tab(github_token)
    
    with tab2:
        render_history_tab()
        
    with tab3:
        render_review_tab()


def render_data_source_tab(github_token):
    """Render the data source selection tab."""
    st.subheader("📂 Data Source")
    
    data_source = st.radio(
        "Choose data source:",
        ("🐙 GitHub Repository", "📁 Manual JSON Upload"),
        horizontal=True
    )
    
    issues_data = None
    developers_data = None
    repo_id = None
    
    if data_source == "🐙 GitHub Repository":
        # GitHub Repository Input
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        
        with col1:
            repo_url = st.text_input(
                "Repository URL",
                placeholder="e.g., owner/repo or https://github.com/owner/repo",
                help="Enter the GitHub repository URL"
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            fetch_btn = st.button("🔄 Fetch Data", type="primary", use_container_width=True)
        
        if fetch_btn and repo_url:
           with st.spinner("Fetching data from GitHub..."):
                try:
                    manager = DataSourceManager(github_token if github_token else None)
                    
                    # Check repo state
                    has_issues, issue_count = manager.detect_repo_state(repo_url)
                    
                    if not has_issues:
                        st.warning(f"⚠️ This repository has no open issues ({issue_count} total). Please use Manual JSON Upload instead.")
                    else:
                        st.info(f"📊 Found {issue_count} open issues in repository")
                        
                        # Fetch data from GitHub
                        issues_data, developers_data, repo_id = manager.get_data_from_github(repo_url)
                        
                        # Store in session state
                        st.session_state.issues_data = issues_data
                        st.session_state.developers_data = developers_data
                        st.session_state.repo_id = repo_id
                        st.session_state.data_source = "github"
                        
                        st.success(f"✅ Loaded {len(issues_data)} issues and {len(developers_data)} contributors!")
                        
                except Exception as e:
                    st.error(f"❌ Error fetching from GitHub: {str(e)}")
        
        # Show loaded data
        if "issues_data" in st.session_state and st.session_state.get("data_source") == "github":
            issues_data = st.session_state.issues_data
            developers_data = st.session_state.developers_data
            repo_id = st.session_state.repo_id
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Issues Loaded", len(issues_data))
            with col2:
                st.metric("Developers Loaded", len(developers_data))
    
    else:
        # Manual JSON Upload
        st.markdown("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Issues")
            uploaded_issues = st.file_uploader(
                "Upload issues JSON file",
                type=["json"],
                key="issues"
            )
            
            if uploaded_issues:
                try:
                    issues_json = json.load(uploaded_issues)
                    st.success(f"✓ Loaded {len(issues_json)} issues")
                    
                    with st.expander("Preview Issues"):
                        st.json(issues_json[:3] if len(issues_json) > 3 else issues_json)
                    
                    st.session_state.issues_json = issues_json
                except json.JSONDecodeError:
                    st.error("Invalid JSON file for issues")
        
        with col2:
            st.subheader("👥 Developers")
            uploaded_developers = st.file_uploader(
                "Upload developers JSON file",
                type=["json"],
                key="developers"
            )
            
            if uploaded_developers:
                try:
                    developers_json = json.load(uploaded_developers)
                    st.success(f"✓ Loaded {len(developers_json)} developers")
                    
                    with st.expander("Preview Developers"):
                        st.json(developers_json[:3] if len(developers_json) > 3 else developers_json)
                    
                    st.session_state.developers_json = developers_json
                except json.JSONDecodeError:
                    st.error("Invalid JSON file for developers")
        
        # Process JSON data
        if "issues_json" in st.session_state and "developers_json" in st.session_state:
            if st.button("💾 Load Data", type="primary"):
                with st.spinner("Loading data into database..."):
                    try:
                        manager = DataSourceManager(github_token if github_token else None)
                        issues_data, developers_data, repo_id = manager.get_data_from_json(
                            st.session_state.issues_json,
                            st.session_state.developers_json
                        )
                        
                        st.session_state.issues_data = issues_data
                        st.session_state.developers_data = developers_data
                        st.session_state.repo_id = repo_id
                        st.session_state.data_source = "json"
                        
                        st.success("✅ Data loaded successfully!")
                    except Exception as e:
                        st.error(f"❌ Error loading data: {str(e)}")
            
            if "issues_data" in st.session_state and st.session_state.get("data_source") == "json":
                issues_data = st.session_state.issues_data
                developers_data = st.session_state.developers_data
                repo_id = st.session_state.repo_id
    
    # Run Assignment Button
    st.markdown("---")
    
    if "issues_data" in st.session_state:
        issues_data = st.session_state.get("issues_data")
        developers_data = st.session_state.get("developers_data")
        repo_id = st.session_state.get("repo_id")
    
    if st.button("🚀 Run AI Assignment", type="primary", use_container_width=True, disabled=(issues_data is None)):
        # Validate provider-specific requirements
        provider = os.getenv("AI_PROVIDER", "openai")
        can_proceed = True
        
        if provider == "openai" and not os.getenv("OPENAI_API_KEY"):
            st.error("❌ Please provide an OpenAI API key in the sidebar")
            can_proceed = False
        elif provider == "gemini" and not os.getenv("GOOGLE_API_KEY"):
            st.error("❌ Please provide a Google API key in the sidebar")
            can_proceed = False
        elif not issues_data or not developers_data:
            st.error("❌ Please load data first (GitHub or JSON)")
            can_proceed = False
        
        if can_proceed:
            with st.spinner(f"Running AI assignment workflow with {provider.upper()}..."):
                try:
                    # Get current API key and model based on provider
                    current_api_key = None
                    current_model = None
                    
                    if provider == "openai":
                        current_api_key = os.getenv("OPENAI_API_KEY")
                        current_model = os.getenv("OPENAI_MODEL")
                    elif provider == "gemini":
                        current_api_key = os.getenv("GOOGLE_API_KEY")
                        current_model = os.getenv("GEMINI_MODEL")
                    elif provider == "ollama":
                        current_model = os.getenv("OLLAMA_MODEL")
                    
                    # Run the workflow with explicit settings
                    assignments = run_graph(
                        issues=issues_data, 
                        developers=developers_data,
                        api_key=current_api_key,
                        model_name=current_model,
                        provider_type=provider
                    )
                    
                    # Store assignments in database properly
                    if repo_id:
                        db = get_database()
                        session = db.get_session()
                        try:
                            # Get issues and developers from database
                            db_issues = IssueService.get_by_repo(session, repo_id)
                            db_developers = DeveloperService.get_by_repo(session, repo_id)
                            
                            # Create mapping from IDs to database records
                            issue_map = {issue.github_id or f"ISSUE-{issue.id}": issue for issue in db_issues}
                            dev_map = {dev.github_username or f"DEV-{dev.id}": dev for dev in db_developers}
                            
                            # Store each assignment
                            for assignment in assignments:
                                issue_db = issue_map.get(assignment['issue_id'])
                                dev_db = dev_map.get(assignment['assigned_to'])
                                
                                if issue_db and dev_db:
                                    AssignmentService.create(
                                        session,
                                        issue_id=issue_db.id,
                                        developer_id=dev_db.id,
                                        confidence_score=assignment['confidence_score'],
                                        reason=assignment['reason']
                                    )
                        finally:
                            session.close()
                    
                    # Store in session state
                    st.session_state.assignments = assignments
                    st.session_state.last_run_provider = provider
                    st.session_state.last_run_time = datetime.now()
                    
                    st.success(f"✅ Successfully created {len(assignments)} assignments using {provider.upper()}!")
                    
                except Exception as e:
                    st.error(f"❌ Error running assignment: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
    
    # Display current run results
    if "assignments" in st.session_state and st.session_state.assignments:
        st.markdown("---")
        st.header("📊 Assignment Results")
        
        # Show run info
        if "last_run_provider" in st.session_state:
            col1, col2 = st.columns([1, 3])
            with col1:
                st.info(f"🤖 Provider: **{st.session_state.last_run_provider.upper()}**")
            with col2:
                if "last_run_time" in st.session_state:
                    st.info(f"🕒 Generated: {st.session_state.last_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        assignments = st.session_state.assignments
        
        # Create DataFrame for display
        df = pd.DataFrame(assignments)
        
        # Reorder columns for better display
        column_order = ['issue_id', 'developer_name', 'assigned_to', 'confidence_score', 'reason']
        df = df[column_order]
        
        # Rename columns for display
        df.columns = ['Issue ID', 'Developer Name', 'Developer ID', 'Confidence', 'Reason']
        
        # Display as table
        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )
        
        # Download and Statistics
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            json_str = json.dumps(assignments, indent=2)
            st.download_button(
                label="📥 Download JSON",
                data=json_str,
                file_name="assignments.json",
                mime="application/json"
            )
        
        with col2:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV",
                data=csv,
                file_name="assignments.csv",
                mime="text/csv"
            )
        
        # Statistics
        st.markdown("---")
        st.subheader("📈 Statistics")
        
        stat_col1, stat_col2, stat_col3 = st.columns(3)
        
        with stat_col1:
            st.metric("Total Assignments", len(assignments))
        
        with stat_col2:
            avg_confidence = sum(a['confidence_score'] for a in assignments) / len(assignments)
            st.metric("Average Confidence", f"{avg_confidence:.1f}/10")
        
        with stat_col3:
            unique_devs = len(set(a['assigned_to'] for a in assignments))
            st.metric("Developers Assigned", unique_devs)


def render_history_tab():
    """Render the assignment history tab."""
    st.subheader("📜 Assignment History")
    
    db = get_database()
    session = db.get_session()
    
    try:
        # Get assignment history
        history = AssignmentService.get_history(session, limit=100)
        
        if not history:
            st.info("No assignment history yet. Run an assignment to see history here.")
            return
        
        st.success(f"Found {len(history)} historical assignments")
        
        # Create DataFrame
        history_data = []
        for assignment in history:
            history_data.append({
                "Date": assignment.created_at.strftime("%Y-%m-%d %H:%M"),
                "Issue": assignment.issue.title if assignment.issue else "N/A",
                "Developer": assignment.developer.name if assignment.developer else "N/A",
                "Confidence": assignment.confidence_score,
                "Status": assignment.status,
                "Reason": assignment.reason[:100] + "..." if len(assignment.reason) > 100 else assignment.reason
            })
        
        df = pd.DataFrame(history_data)
        
        # Display table
        st.dataframe(
            df,
            use_container_width=True,
            height=500
        )
        
        # Export history
        col1, col2 = st.columns(2)
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export History (CSV)",
                data=csv,
                file_name=f"assignment_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        
        # Statistics
        st.markdown("---")
        st.subheader("📊 Historical Statistics")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Assignments", len(history))
        with col2:
            avg_conf = sum(a.confidence_score for a in history if a.confidence_score) / len(history)
            st.metric("Avg Confidence", f"{avg_conf:.1f}/10")
        with col3:
            status_counts = {}
            for a in history:
                status_counts[a.status] = status_counts.get(a.status, 0) + 1
            st.metric("Pending", status_counts.get("pending", 0))
        
    finally:
        session.close()


def render_review_tab():
    """Render the review and send tab."""
    st.subheader("📝 Review & Send Notifications")
    
    if "assignments" not in st.session_state or not st.session_state.assignments:
        st.info("No assignments generated yet. Go to 'Data Source' and run the AI assignment first.")
        return
    
    assignments = st.session_state.assignments
    
    # Check if we have notification data (backward compatibility)
    if not assignments or "jira_title" not in assignments[0]:
        st.warning("Old assignment data detected. Please re-run the assignment to generate notifications.")
        return
    
    st.success(f"Ready to send {len(assignments)} notifications")
    
    # Global Actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Send All (Simulate)", type="primary", use_container_width=True):
            st.toast("Sending all notifications...", icon="🚀")
            import time
            time.sleep(1)
            st.balloons()
            st.success("All notifications sent successfully! (Simulated)")
            
    with col2:
        # Export Notifications
        json_str = json.dumps(assignments, indent=2)
        st.download_button(
            label="📥 Export All Drafts (JSON)",
            data=json_str,
            file_name="notifications.json",
            mime="application/json",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Individual Cards
    for i, item in enumerate(assignments):
        with st.expander(f"📌 {item.get('issue_id')} → {item.get('developer_name')}", expanded=(i==0)):
            
            # Jira Section
            st.markdown("### <img src='https://cdn.iconscout.com/icon/free/png-256/free-jira-3628861-3030021.png' width='20'/> Jira Ticket", unsafe_allow_html=True)
            jira_col1, jira_col2 = st.columns([3, 1])
            with jira_col1:
                st.text_input("Title", value=item.get("jira_title", ""), key=f"jira_title_{i}")
                st.text_area("Description", value=item.get("jira_description", ""), height=100, key=f"jira_desc_{i}")
                st.caption(f"Priority: {item.get('jira_priority', 'Medium')}")
            with jira_col2:
                if st.button("Create Ticket", key=f"btn_jira_{i}"):
                    st.toast(f"Created Jira ticket for {item.get('issue_id')}", icon="✅")
            
            st.markdown("---")
            
            # Slack Section
            st.markdown("### <img src='https://cdn.iconscout.com/icon/free/png-256/free-slack-logo-icon-download-in-svg-png-gif-file-formats--social-media-company-brand-pack-logos-icons-2563539.png' width='20'/> Slack Message", unsafe_allow_html=True)
            slack_col1, slack_col2 = st.columns([3, 1])
            with slack_col1:
                st.text_area("Message", value=item.get("slack_message", ""), height=80, key=f"slack_msg_{i}")
            with slack_col2:
                if st.button("Send Slack", key=f"btn_slack_{i}"):
                    st.toast(f"Sent Slack to {item.get('developer_name')}", icon="💬")
            
            st.markdown("---")
            
            # Messenger Section
            st.markdown("### <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/Facebook_Messenger_logo_2020.svg/2048px-Facebook_Messenger_logo_2020.svg.png' width='20'/> Messenger", unsafe_allow_html=True)
            msg_col1, msg_col2 = st.columns([3, 1])
            with msg_col1:
                st.text_area("Update", value=item.get("messenger_message", ""), height=60, key=f"msg_msg_{i}")
            with msg_col2:
                if st.button("Send Msg", key=f"btn_msg_{i}"):
                    st.toast("Sent Messenger update", icon="📱")


if __name__ == "__main__":
    main()
