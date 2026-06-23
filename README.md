# 📰 AI Multi-Agent Fake News Detection Web App

- This web application uses a team of AI agents to read news articles and figure out if they're trustworthy or just fake news, clickbait, and extreme bias.

- Instead of relying on a single AI prompt, it splits the job between two specialized agents (a Researcher and a Linguist), and then passes their notes to a Judge agent who gives a final score and a breakdown of red flags.

- The backend runs on FastAPI and orchestrates the agents using LangGraph, while utilizing Groq to run Llama-3.3 instantly. The frontend is built with simple, fast,  HTML, CSS, and JavaScript.

## Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML, CSS, JavaScript
- **AI Agents:** LangGraph (async state graph)
- **Agent Role:** Researcher, Linguist, Judge
- **LLM Engine:** Groq Cloud API (llama-3.3-70b-versatile)
- **Environment & Package Management:** Python venv + uv (fast package installer)

## 🏗️ Project Architecture
The application uses an asynchronous state graph to process requests. Instead of a linear pipeline, the system analyzes the text from two entirely different analytical perspectives at the exact same time before passing it to a final arbitrator.

Here is how data flows through the application:

Plaintext

       [ User inputs article text in UI ]
                       │
                       ▼
         [ FastAPI Endpoint (/api/verify) ]
                       │
                       ▼
         [ LangGraph State Initialization ]
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
     [ Researcher Agent ]   [ Stylist Agent ]
     (Analyzes claims       (Analyzes tone,
      & primary sources)     bias, & clickbait)
             └─────────┬─────────┘
                       │
                       ▼
               [ Judge Agent ]
         (Synthesizes both reports into
          a structured Pydantic schema)
                       │
                       ▼
          [ JSON Verdict Returned to UI ]




## How the Agents Work Together:

The Researcher Node (research_agent): Acts like an investigative journalist. It looks at the actual claims in the text and flags anything that sounds completely detached from reality or lacks basic primary sources.

The Stylist Node (style_agent): Acts like a linguistic expert. It completely ignores whether the facts are true and focuses purely on how it's written—scanning for emotional manipulation, clickbait titles, and heavy bias.

The Judge Node (judge_agent): Takes the independent reports from both the Researcher and Stylist, combines them, and forces the LLM to output a clean, predictable JSON response matching your VerdictSchema.


## 📁 Project Layout

├── fake_news.py         # The FastAPI backend & LangGraph agent setup
├── .env                 # Where you keep your private Groq API key
|
└── static/              # Everything for the browser interface
    ├── index.html       # The main webpage layout
    ├── style.css        # Simple, clean layout styling
    └── script.js        # Handles sending the text to the backend and showing the results
    |___logo.png         # Logo for App
