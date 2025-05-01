# 🧠 Smart Email Agent: GPT-Powered Inbox Summarizer

An intelligent email assistant that helps users quickly understand their inbox by summarizing and prioritizing incoming emails using GPT-4 and the Gmail API.

## 📌 What It Does

This agent-powered tool:

- 🔎 Fetches unread emails from Gmail
- 🤖 Summarizes each email using OpenAI GPT-4
- 🏷️ Classifies it as:
  - Important / Not Important
  - Job / Event / Newsletter / System / Social / Other
- 📁 Saves all summaries to a local JSON file
- 🖥️ Displays summaries in a sleek web interface (Flask)
- 🔄 Provides a one-click Refresh button to pull new emails and reprocess

## 📸 Demo Video

📺 [🎥 Click here to watch the 5-minute demo](https://youtu.be/eDj8XokDK7A)

## 🧠 Why This Agent

Managing emails is cognitively expensive.
This agent acts as a knowledge filter for your inbox, helping you:

- Instantly catch up on what matters
- Avoid wasting time on spam or low-priority content
- Stay organized with categorized, summarized views

We built it with:

- Autonomous decision-making (via GPT-4 prompts)
- Agentic structure: Observes → Thinks → Acts (label, summarize, store)
- Modular, extensible Python pipeline for rapid experimentation

## ⚙️ Tech Stack

| Category | Tech |
|----------|------|
| Language | Python |
| Agent Model | OpenAI GPT-4 |
| Email API | Gmail API (OAuth 2.0) |
| Backend | Flask |
| Frontend | HTML + JS (no full framework) |
| Persistence | JSON (summaries.json) |
| Agent Action Loop | summarize_email() → classify → store |

## 🗺️ Architecture Overview

```
[Gmail Inbox] ──► [email_helper.py]
                  ├─► Fetch raw emails
                  ├─► GPT-4: summarization + classification
                  └─► Save as summaries.json

[Flask Web App] ──► Render templates/index.html
                  ├─► Show important / unimportant groups
                  └─► One-click refresh (calls /api/refresh)
```

## 📁 Project Structure

```
email-agent/
├── app.py                  # Flask web application
├── email_helper.py         # Email processing and GPT integration (runs in background)
├── templates/              # Web templates
│   └── index.html          # Main UI
├── summaries.json          # Local summary storage (one JSON per line)
├── token.pickle            # Gmail API credentials cache (generated after OAuth)
└── README.md               # Project documentation
```

## 💡 How Agentic Framework Helped

Instead of writing manual rules for parsing emails, we used GPT-4 to take on the agent's cognitive work:

- Reads the full email body
- Understands intent + context
- Makes decisions (important/not, category)
- Summarizes for the user

This mimics how a human assistant would help someone triage their inbox — it thinks autonomously, not via hardcoded logic.

## 🧪 How to Run

### 🛠️ Setup

```bash
git clone https://github.com/your-username/email-agent.git
cd email-agent
pip install -r requirements.txt
```

### 🔐 Add your credentials

1. Add your Gmail API `credentials.json`
2. Set up your OpenAI API key using one of these methods:

   - Environment variable (recommended):
     ```bash
     export OPENAI_API_KEY=sk-xxxx
     ```
   
   - Create a `.env` file (included in `.gitignore` for security):
     ```
     OPENAI_API_KEY=sk-xxxx
     ```
     The app will automatically load this file using python-dotenv.

### ▶️ Start the app

```bash
python app.py
```

### 🔒 Security Notes

- Never hardcode API keys in your source code
- The `.gitignore` file is set up to prevent committing sensitive files like `.env`, `credentials.json`, and `token.pickle`
- For production deployments, use a secure secrets management solution

## 🚀 What's Next

This MVP showcases a powerful email triage agent. In the future, we plan to:

- Add memory & personalization (learn user's preferences)
- Use vector search to group related emails
- Deploy as a browser extension or Gmail plugin
- Turn it into a proactive agent ("Remind me if important mail hasn't been replied to in 2 days")

## 👥 Team

- Ziqi Wei

## 📄 License

MIT License 