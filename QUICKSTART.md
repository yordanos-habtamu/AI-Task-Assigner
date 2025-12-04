# Quick Start Guide

## Step 1: Add Your API Key

Open the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

## Step 3: Run the Application

### Option A: Web Interface (Recommended)

```bash
streamlit run frontend/app.py
```

Then open http://localhost:8501 in your browser.

### Option B: Command Line

```bash
cd backend
python main.py
```

Results will be saved in `assignments.json`.

## Troubleshooting

**Issue**: API key not found
- **Solution**: Make sure you edited `.env` and added your API key after `OPENAI_API_KEY=`

**Issue**: Module not found
- **Solution**: Activate the virtual environment: `source venv/bin/activate`

**Issue**: python-dotenv error
- **Solution**: Reinstall: `pip install python-dotenv`
