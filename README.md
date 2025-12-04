# 🤖 AI Task Assignment System

An intelligent AI-powered task assignment system that uses **LangChain** and **LangGraph** to automatically analyze issues and developers, then make optimal task assignments based on skills, workload, and preferences.

## 🎯 Features

- **Intelligent Issue Analysis**: AI analyzes GitHub issues to extract required skills, difficulty, and complexity
- **Developer Profile Analysis**: Evaluates developer strengths, weaknesses, workload, and preferences
- **Smart Assignment Engine**: Matches issues to developers using multi-factor optimization
- **Interactive Web UI**: User-friendly Streamlit interface for easy interaction
- **Export Results**: Download assignments as JSON or CSV

## 🏗️ Architecture

The system uses a multi-agent workflow orchestrated by LangGraph:

```
1. Issue Analyzer → Analyzes all issues
2. Developer Analyzer → Analyzes all developers  
3. Assignment Agent → Creates optimal assignments
```

Each agent is powered by OpenAI's GPT models with structured JSON output using LangChain.

## 📋 Requirements

- Python 3.9+
- OpenAI API key

## 🚀 Installation

1. **Clone or download this project**

2. **Create and activate a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your OpenAI API key**:
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
   Or on Windows:
   ```cmd
   set OPENAI_API_KEY=your-api-key-here
   ```

## 💻 Usage

### Option 1: Web Interface (Recommended)

1. **Run the Streamlit app**:
   ```bash
   streamlit run frontend/app.py
   ```

2. **Open your browser** to `http://localhost:8501`

3. **Enter your OpenAI API key** in the sidebar

4. **Upload your data files**:
   - Issues JSON file
   - Developers JSON file

5. **Click "Run AI Assignment"** and view the results!

### Option 2: Command Line

1. **Prepare your data files** in `backend/data/`:
   - `issues.json`
   - `developers.json`

2. **Run the backend**:
   ```bash
   cd backend
   python main.py
   ```

3. **View results** in `assignments.json`

## 📁 Project Structure

```
project/
├── backend/
│   ├── main.py              # CLI entry point
│   ├── ai/
│   │   ├── issue_agent.py   # Issue analysis agent
│   │   ├── dev_agent.py     # Developer analysis agent
│   │   ├── assign_agent.py  # Assignment agent
│   │   └── graph.py         # LangGraph workflow
│   └── data/
│       ├── issues.json      # Sample issues
│       └── developers.json  # Sample developers
├── frontend/
│   └── app.py              # Streamlit UI
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 📊 Data Format

### Issues JSON

```json
[
  {
    "id": "ISSUE-001",
    "title": "Issue title",
    "description": "Detailed description",
    "labels": ["backend", "security"],
    "estimated_hours": 16
  }
]
```

### Developers JSON

```json
[
  {
    "id": "DEV-001",
    "name": "Alice Johnson",
    "skills": ["Python", "Django", "PostgreSQL"],
    "experience_years": 5,
    "current_workload_hours": 20,
    "max_capacity_hours": 40,
    "recent_performance": "excellent",
    "preferences": ["backend", "databases"]
  }
]
```

## 🎨 Example Output

```json
{
  "issue_id": "ISSUE-001",
  "assigned_to": "DEV-001",
  "developer_name": "Alice Johnson",
  "confidence_score": 9,
  "reason": "Alice has strong Python and security experience, and her current workload allows for this high-priority task."
}
```

## 🔧 Configuration

- **Model**: Default is `gpt-4o-mini` (configured in agent files)
- **Temperature**: Set to 0 for deterministic outputs
- **Output Format**: Structured JSON using Pydantic models

## 🛠️ Development

### Running Tests

Sample data is provided in `backend/data/` for testing:
- 10 sample issues covering various technologies
- 5 sample developers with different skills and workloads

### Modifying Agents

Each agent is in its own file:
- `issue_agent.py` - Modify issue analysis logic
- `dev_agent.py` - Modify developer analysis logic
- `assign_agent.py` - Modify assignment strategy

### Customizing the Workflow

Edit `backend/ai/graph.py` to modify the workflow sequence or add new nodes.

## 📝 License

This project is open source and available for use.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## ❓ Troubleshooting

**Issue**: `OPENAI_API_KEY not set`
- **Solution**: Set the environment variable with your OpenAI API key

**Issue**: `Module not found` errors
- **Solution**: Make sure you've activated the virtual environment and installed requirements

**Issue**: API rate limits
- **Solution**: The system processes items sequentially. For large datasets, consider upgrading your OpenAI plan.

## 📧 Support

For questions or issues, please open a GitHub issue.

---

Built with ❤️ using LangChain, LangGraph, and Streamlit
