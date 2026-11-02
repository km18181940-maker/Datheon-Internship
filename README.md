# Datheon Python + Generative AI & LangChain Internship

**Student:** Muzammil Khan  
**Application ID:** DT-2026-FB98G  
**Program:** Python + Generative AI & LangChain Internship  

This repository contains implementations for all four internship tasks.

| # | Task | Folder | Main deliverable |
|---|---|---|---|
| 1 | Structured AI extraction | `task1_structured_extraction/` | Invoice/resume text converted to Pydantic-validated JSON |
| 2 | RAG document chatbot | `task2_rag/` | PDF/TXT/MD question answering with source/page citations |
| 3 | Tool-using AI agent | `task3_agent/` | Agent with web search, safe calculator, and sandboxed file reader |
| 4 | Streamlit AI application | `task4_streamlit/` | Browser chat UI with streaming output and session history |

## 1. Requirements

- Python 3.10 or newer
- Git and a GitHub account
- An API key from Google AI Studio (Gemini) or OpenAI for live model calls
- Internet access for package installation and web search

## 2. Windows setup (VS Code)

Open this repository folder in VS Code. Open **Terminal → New Terminal**, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Open `.env` and add your own key. For Gemini, set:

```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=PASTE_YOUR_GEMINI_API_KEY_HERE
```

Or use OpenAI:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=PASTE_YOUR_OPENAI_API_KEY_HERE
```

**Never upload `.env` or share your API key.** The `.gitignore` excludes `.env` and local environment/database files. Keep the placeholder values in `.env.example` only.

## 3. Run each task

Run commands from the repository root after activating `.venv`.

### Task 1 — Structured extraction

Gemini example:

```powershell
python task1_structured_extraction/main.py task1_structured_extraction/samples/invoice.txt --type invoice --provider gemini
```

Resume example:

```powershell
python task1_structured_extraction/main.py task1_structured_extraction/samples/resume.txt --type resume --provider gemini --out resume_result.json
```

The pipeline uses prompt templates, Pydantic schemas, validation rules, and retries when the model returns invalid JSON.

### Task 2 — RAG document chatbot

Index the included sample document:

```powershell
python -m task2_rag.cli ingest task2_rag/docs
```

Ask a question:

```powershell
python -m task2_rag.cli ask "How many remote days are allowed per week?"
```

Start interactive terminal chat:

```powershell
python -m task2_rag.cli chat
```

You can also ingest your own PDF, TXT, or Markdown files by providing their folder/path. PDF answers include source page citations. The local ChromaDB index is generated on your machine and is not committed to GitHub.

### Task 3 — Tool-using AI agent

```powershell
python -m task3_agent.agent "Read sales.txt, total the revenue, then tell me the average per month"
```

The agent can call DuckDuckGo web search, a restricted arithmetic calculator, and a local file reader limited to `task3_agent/workspace/`.

### Task 4 — Streamlit web application

```powershell
streamlit run task4_streamlit/app.py
```

Open the local URL shown in the terminal (normally `http://localhost:8501`). Upload PDF/TXT/MD documents in the sidebar, click **Build knowledge base**, and ask questions. The interface streams answers and keeps chat history in the current session.

## 4. Run tests

These tests run offline and do not need an API key:

```powershell
python -m pytest -q
python -m pytest -q task1_structured_extraction/tests
```

## 5. GitHub submission checklist

1. Sign in to GitHub and create a **new public repository**. Suggested repository name: `Datheon_Python_Generative_AI_LangChain_Internship`.
2. Keep this README and all four task folders in the repository.
3. In VS Code, open **Source Control** (branch icon), choose **Initialize Repository**, stage the project files, and commit with a message such as `Complete Datheon Generative AI internship tasks`.
4. Choose **Publish to GitHub** / **Publish Branch** and select **Public**. Alternatively, use the Git commands below.
5. Open the repository on GitHub and confirm that the README and all four task folders are visible. Confirm that `.env`, `.venv`, and `chroma_db` are not uploaded.
6. Copy the public repository URL, for example `https://github.com/YOUR-USERNAME/Datheon_Python_Generative_AI_LangChain_Internship`.
7. Return to the Datheon Student Workspace. Paste the URL into **GitHub Repository URL**. Add your LinkedIn post URL if you publish a project demo; the demo/video URL is optional.
8. Tick only the task completion boxes for work actually included in your repository. With this package, all four task folders are included; run the tasks with your API key before representing them as live-tested.
9. Review everything, then click **Submit Project for Credential Verification**. Save a screenshot or confirmation of your submission.

### Git commands (alternative)

Create the public repository on GitHub first, then run these commands from the project root (replace the URL with your repository URL):

```powershell
git init
git add .
git commit -m "Complete Datheon Generative AI internship tasks"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

## 6. Datheon submission details to remember

- Program deadline shown in your workspace: **Sunday, November 29, 2026**.
- The workspace says the repository link can be edited/resubmitted within **24 hours** after submission; after that it is locked for evaluation.
- The workspace asks for at least **2 or 3 of the 4 tasks**. This repository includes all four task implementations.
- Do not claim a certificate has been issued until Datheon completes its review and approval.

## Project structure

```text
Datheon_Python_Generative_AI_LangChain_Internship/
├── common/                         # Shared model and safety helpers
├── task1_structured_extraction/    # Gemini/OpenAI structured extraction
├── task2_rag/                      # Document ingestion, vector store, QA
├── task3_agent/                    # Web, calculator, and file tools
├── task4_streamlit/                # Streamlit chat application
├── tests/                          # Shared offline tests
├── .env.example                    # Safe environment-variable template
├── .gitignore
├── requirements.txt
└── README.md
```
