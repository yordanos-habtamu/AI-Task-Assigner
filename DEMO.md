# Demo Script - AI Task Assignment System

## 🎬 30-Second Quick Demo

### Setup (5 seconds)
1. Navigate to project: `cd TaskAssignAi`
2. Activate venv: `source venv/bin/activate`
3. Start app: `streamlit run frontend/app.py`

### Demo Flow (25 seconds)

**Opening (5s)**
> "This is an AI-powered task assignment system that automatically matches GitHub issues to the right developers based on their skills, workload, and preferences."

**Upload Data (5s)**
1. Enter OpenAI API key in sidebar
2. Upload `backend/data/issues.json` (10 issues)
3. Upload `backend/data/developers.json` (5 developers)
4. Show preview: "We have 10 issues ranging from authentication to UI work"

**Run Assignment (10s)**
1. Click "Run AI Assignment" button
2. *While processing*: "The system runs 3 AI agents - one analyzes issues, one analyzes developers, and one makes intelligent assignments"
3. Results appear!

**Show Results (5s)**
1. Point to assignment table: "Each issue is matched to the best developer"
2. Click on a row: "Notice the confidence score and reasoning"
3. Click "Download JSON": "Results can be exported for your workflow"

---

## 🎥 Full Feature Demo (2-3 minutes)

### Part 1: Introduction (30s)

**Script:**
> "Welcome to the AI Task Assignment System. This tool solves a common problem in software teams: how do you efficiently assign tasks to developers in a way that considers skills, workload, and preferences? Let's see how AI can help."

### Part 2: Show the Data (30s)

**Actions:**
- Show `issues.json` in editor
- Highlight diverse issue types (authentication, UI, database, testing)
- Show `developers.json`
- Point out different skill sets and workload states

**Script:**
> "We have real-world data here - 10 GitHub issues covering everything from security to frontend work, and 5 developers with different specializations. Notice how Alice is experienced in backend, Bob focuses on UI, and Diana specializes in testing."

### Part 3: Architecture Explanation (30s)

**Actions:**
- Show README architecture section or diagram

**Script:**
> "The system uses three intelligent agents powered by GPT-4:
> 1. Issue Analyzer - extracts required skills and difficulty from each issue
> 2. Developer Analyzer - evaluates strengths, weaknesses, and current workload
> 3. Assignment Agent - makes optimal matches considering all factors
> 
> These agents are orchestrated using LangGraph, ensuring a structured workflow."

### Part 4: Live Demo (45s)

**Actions:**
1. Start Streamlit app
2. Enter API key
3. Upload both files
4. Expand issue preview: "See how the data looks"
5. Click Run AI Assignment
6. Wait for processing
7. Show results table

**Script:**
> "Let's run it live. I'll upload our data files... and click Run Assignment. 
> 
> *[While processing]*: Behind the scenes, the AI is analyzing each issue to understand what skills are needed, evaluating each developer's capacity and expertise, and then finding the optimal matches.
> 
> *[Results appear]*: And here we go! Each issue has been assigned. Look at this one - the authentication issue went to Alice because of her strong backend and security experience, and she has availability. The confidence score is 9 out of 10."

### Part 5: Features & Export (30s)

**Actions:**
1. Scroll through assignments
2. Point out reasoning for 2-3 assignments
3. Show statistics at bottom
4. Download JSON
5. Download CSV

**Script:**
> "Every assignment comes with detailed reasoning - not just 'who', but 'why'. 
> 
> Down here we see statistics: we've assigned all 10 issues across our team with an average confidence of 8.5. 
> 
> And you can export everything as JSON for your CI/CD pipeline, or CSV for your spreadsheets."

### Part 6: CLI Demo (Optional, 15s)

**Actions:**
```bash
cd backend
python main.py
```

**Script:**
> "There's also a command-line interface for automation. Just run the backend script, and it processes everything and outputs assignments.json."

### Part 7: Closing (15s)

**Script:**
> "So there you have it - an AI-powered system that takes the guesswork out of task assignment. It considers skills, workload, preferences, and more to make fair, efficient assignments for your team. The code is modular, so you can customize the logic for your specific needs."

---

## 🎯 Key Demo Tips

### What to Emphasize
- ✅ **Speed**: AI does in seconds what takes humans hours
- ✅ **Intelligence**: Multi-factor decision making (not just random assignment)
- ✅ **Transparency**: Every assignment has detailed reasoning
- ✅ **Flexibility**: Works via UI or CLI, exports multiple formats
- ✅ **Modularity**: Easy to customize for specific team needs

### Common Questions & Answers

**Q: What if the AI makes a bad assignment?**
> A: The confidence score helps you identify uncertain assignments. You can review the reasoning and override if needed. Over time, you can also fine-tune the prompts.

**Q: Does it work with real GitHub?**
> A: The current version takes JSON files, but you can easily integrate with GitHub's API to pull live issues.

**Q: What about privacy/cost?**
> A: Data is sent to OpenAI's API for processing. Use gpt-4o-mini for cost efficiency (~$0.01 per 10 assignments).

**Q: Can I customize the assignment logic?**
> A: Absolutely! Edit the prompts in `assign_agent.py` to change how assignments are made.

---

## 📝 Sample Demo Narration Notes

### For Technical Audience
- Emphasize architecture (LangGraph, LangChain, structured outputs)
- Show code structure
- Discuss extensibility and customization options
- Mention Pydantic models for type safety

### For Business Audience
- Focus on time savings
- Highlight fairness and transparency
- Emphasize team efficiency gains
- Show export and integration options

### For Product Demo
- Lead with the problem (inefficient task assignment)
- Show the solution (AI automation)
- Prove it works (live demo)
- Close with benefits (faster, fairer, scalable)
