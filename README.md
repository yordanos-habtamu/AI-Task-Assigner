# 🤖 AI Task Assignment System

An intelligent task assignment system powered by AI that analyzes GitHub issues and developer profiles to make optimal task assignments. Features multi-provider AI support, Google SSO authentication, and automatic notification generation.

## ✨ Features

### 🔐 **Authentication & Security**
- **User Authentication**: Secure login/signup with password hashing
- **Google SSO**: One-click sign-in with Google OAuth
- **API Key Management**: Store and auto-load your AI provider keys

### 🤖 **Multi-Provider AI Support**
- **OpenAI** (GPT-4, GPT-3.5)
- **Google Gemini** (Gemini 1.5 Pro, Gemini 2.0 Flash)
- **Local AI** (Ollama - run models locally)

### 📊 **Smart Task Assignment**
- **GitHub Integration**: Fetch issues and contributors directly from repositories
- **AI Analysis**: Intelligent matching of tasks to developers based on skills, workload, and preferences
- **Manual Upload**: JSON file upload for offline use

### 📝 **Notification System**
- Auto-generate **Jira tickets** with professional descriptions
- Create **Slack messages** for developer notifications
- Draft **Messenger updates** for quick status sharing

### 💾 **Database & History**
- SQLite database for persistent storage
- Assignment history tracking
- User profile management

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Git
- Google Cloud Console account (for Google SSO)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yordanos-habtamu/AI-Task-Assigner.git
cd AI-Task-Assigner
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
# AI Provider (choose one)
OPENAI_API_KEY=your_openai_key
# OR
GOOGLE_API_KEY=your_gemini_key

# Google OAuth (optional, for SSO)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# GitHub (optional, for higher rate limits)
GITHUB_TOKEN=your_github_token
```

### Running the Application

#### **Option 1: With Google SSO (Recommended)**

Terminal 1 - Start OAuth Server:
```bash
./run_oauth.sh
```

Terminal 2 - Start Streamlit App:
```bash
./run.sh
```

Access at:
- **Streamlit App**: http://localhost:8501
- **OAuth Server**: http://localhost:8502

#### **Option 2: Without Google SSO**

```bash
./run.sh
```

Then create an account using username/password.

## 🔧 Configuration

### Google SSO Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Go to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure OAuth consent screen
6. Add redirect URI: `http://localhost:8502/auth/google/callback`
7. Copy **Client ID** and **Client Secret** to `.env`

See [GOOGLE_SSO_SETUP.md](.gemini/antigravity/brain/71cb1cad-a4cd-4272-93f7-12f00d405284/GOOGLE_SSO_SETUP.md) for detailed instructions.

### AI Provider Setup

#### OpenAI
1. Get API key from [OpenAI Platform](https://platform.openai.com/)
2. Add to `.env`: `OPENAI_API_KEY=sk-...`

#### Google Gemini  
1. Get API key from [Google AI Studio](https://makersuite.google.com/)
2. Add to `.env`: `GOOGLE_API_KEY=...`

#### Ollama (Local AI)
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama3.1`
3. Start Ollama: `ollama serve`

## 📖 Usage

### 1. Sign In
- **Google**: Click "Continue with Google"
- **Username/Password**: Create an account or login

### 2. Configure AI Provider
- Select provider (OpenAI, Gemini, or Ollama)
- Enter API key if needed
- Choose model
- Click **"💾 Save API Keys to Profile"** (optional)

### 3. Load Data
**Option A: GitHub Repository**
- Enter repository URL (e.g., `owner/repo`)
- Add GitHub token for private repos
- Click "Fetch Data"

**Option B: Manual JSON Upload**
- Upload `issues.json` and `developers.json`
- See `backend/data/` for example formats

### 4. Run Assignment
- Click **"🚀 Run AI Assignment"**
- View results in the table
- Check **"📝 Review & Send"** tab for notifications

### 5. Review Notifications
- Edit Jira ticket descriptions
- Customize Slack messages
- Click **"🚀 Send All (Simulate)"** or individual send buttons

## 📁 Project Structure

```
TaskAssignAi/
├── backend/
│   ├── ai/                      # AI agents
│   │   ├── llm_provider.py     # Multi-provider abstraction
│   │   ├── issue_agent.py      # Issue analysis
│   │   ├── dev_agent.py        # Developer analysis
│   │   ├── assign_agent.py     # Task assignment
│   │   └── notification_agent.py # Notification generation
│   ├── oauth_server.py         # Flask OAuth server
│   ├── database.py             # SQLAlchemy models
│   ├── crud.py                 # Database operations
│   ├── auth_utils.py           # Password hashing
│   └── data/                   # Sample JSON files
├── frontend/
│   ├── app.py                  # Main Streamlit UI
│   └── auth.py                 # Login/Signup pages
├── run.sh                      # Start Streamlit
├── run_oauth.sh               # Start OAuth server
└── requirements.txt           # Python dependencies
```

## 🛠️ Development

### Running Tests
```bash
pytest
```

### Backend Only
```bash
python backend/main.py
```

### Database Management
```bash
# View database
sqlite3 task_assignments.db

# Reset database
rm task_assignments.db
```

## 🔒 Security Notes

- API keys are stored in plain text in the database (encrypt in production)
- Use HTTPS in production
- Rotate OAuth secrets regularly
- Don't commit `.env` file to version control

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- AI powered by OpenAI, Google Gemini, and Ollama
- OAuth integration with [Authlib](https://authlib.org/)

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/yordanos-habtamu/AI-Task-Assigner/issues
- Documentation: See `QUICKSTART.md` and `DEMO.md`

---

**Made with ❤️ by the TaskAssignAI Team**
