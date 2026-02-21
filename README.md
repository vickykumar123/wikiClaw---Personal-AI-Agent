# wikiClaw - Personal AI Agent

A sophisticated personal AI assistant built with hierarchical multi-agent architecture. Designed for learning agentic AI development patterns used in modern AI systems like AutoGPT, Open Interpreter, and Claude.

## Overview

wikiClaw is not just another chatbot - it's a fully autonomous agent capable of:
- Understanding natural language requests
- Breaking down complex tasks into sub-tasks
- Routing tasks to specialized agents
- Executing actions via tools (APIs, databases, web)
- Learning and remembering user information

---

## Features

| Feature | Description |
|---------|-------------|
| **Semantic Memory** | Save and recall information using vector embeddings |
| **Notes Management** | Full CRUD operations with semantic search |
| **Calendar Integration** | Google Calendar sync for scheduling |
| **Email Sending** | Gmail integration for communication |
| **Web Search** | Real-time web and news search |
| **File Analysis** | Process PDFs, documents, spreadsheets, code |

---

## System Architecture

### High-Level Overview

```
+------------------------------------------------------------------+
|                           wikiClaw                                |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------------+    +-------------------+                   |
|  |    Telegram Bot   |    |   Webhook Server  |                   |
|  |  (User Interface) |<-->|  (FastAPI/ngrok)  |                   |
|  +-------------------+    +-------------------+                   |
|            |                                                      |
|            v                                                      |
|  +-----------------------------------------------------------+   |
|  |                      AGENT CORE                            |   |
|  |  - Message processing                                      |   |
|  |  - Conversation history management                         |   |
|  |  - Sub-agent orchestration                                 |   |
|  +-----------------------------------------------------------+   |
|            |                                                      |
|            v                                                      |
|  +-----------------------------------------------------------+   |
|  |                     ORCHESTRATOR                           |   |
|  |                                                            |   |
|  |   "I analyze user intent and route to the right agent"    |   |
|  |                                                            |   |
|  |   Available Agents:                                        |   |
|  |   [Memory] [Notes] [Calendar] [Web] [Email]               |   |
|  +-----------------------------------------------------------+   |
|            |                                                      |
|            +------------------+------------------+                 |
|            |                  |                  |                 |
|            v                  v                  v                 |
|  +----------------+  +----------------+  +----------------+        |
|  |  SUB-AGENT 1   |  |  SUB-AGENT 2   |  |  SUB-AGENT N   |        |
|  |  (Specialized) |  |  (Specialized) |  |  (Specialized) |        |
|  +----------------+  +----------------+  +----------------+        |
|            |                  |                  |                 |
|            v                  v                  v                 |
|  +----------------+  +----------------+  +----------------+        |
|  |    TOOLS       |  |    TOOLS       |  |    TOOLS       |        |
|  | (Actions/APIs) |  | (Actions/APIs) |  | (Actions/APIs) |        |
|  +----------------+  +----------------+  +----------------+        |
|                                                                   |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|                      EXTERNAL SERVICES                            |
|  +----------+  +----------+  +----------+  +----------+          |
|  | MongoDB  |  |  Google  |  |  Ollama  |  |  OpenAI  |          |
|  |  Atlas   |  | Calendar |  |   LLM    |  |Embeddings|          |
|  +----------+  +----------+  +----------+  +----------+          |
+------------------------------------------------------------------+
```

---

### Hierarchical Agent Pattern

wikiClaw implements a **hierarchical multi-agent system** - a design pattern used in production AI systems:

```
                         +---------------------------+
                         |       ORCHESTRATOR        |
                         |                           |
                         |  - Receives user message  |
                         |  - Analyzes intent        |
                         |  - Routes to sub-agents   |
                         |  - Combines results       |
                         +-------------+-------------+
                                       |
     +-----------+-----------+---------+---------+-----------+
     |           |           |                   |           |
     v           v           v                   v           v
+----------+ +----------+ +----------+     +----------+ +----------+
|  MEMORY  | |  NOTES   | | CALENDAR |     |   WEB    | |  EMAIL   |
|  AGENT   | |  AGENT   | |  AGENT   |     |  AGENT   | |  AGENT   |
+----------+ +----------+ +----------+     +----------+ +----------+
|          | |          | |          |     |          | |          |
| save     | | create   | | create   |     | web      | | send     |
| memory   | | note     | | event    |     | search   | | email    |
|          | |          | |          |     |          | |          |
| search   | | search   | | list     |     | news     | +----------+
| memory   | | notes    | | events   |     | search   |
|          | |          | |          |     |          |
+----------+ | list     | | search   |     +----------+
             | notes    | | events   |
             |          | |          |
             | delete   | | delete   |
             | note     | | event    |
             +----------+ +----------+
```

#### Why Hierarchical?

| Flat Architecture | Hierarchical Architecture |
|-------------------|---------------------------|
| Single agent with all tools | Orchestrator + specialized agents |
| LLM sees 15+ tools at once | Each agent sees only 2-4 tools |
| Harder to scale | Easy to add new agents |
| Generic prompts | Domain-specific prompts |
| Higher error rate | Better accuracy |

---

### Agent Communication Flow

```
User: "Schedule a meeting tomorrow at 3pm and email John about it"
                              |
                              v
+------------------------------------------------------------------+
|                        ORCHESTRATOR                               |
|                                                                   |
|  1. Parse: "schedule meeting" + "email John"                     |
|  2. Decide: Need calendar_agent AND email_agent                  |
|  3. Execute: Call both agents                                    |
+------------------------------------------------------------------+
                              |
              +---------------+---------------+
              |                               |
              v                               v
+------------------------+      +------------------------+
|    CALENDAR AGENT      |      |     EMAIL AGENT        |
|                        |      |                        |
| Task: "Schedule        |      | Task: "Email John      |
|  meeting tomorrow 3pm" |      |  about the meeting"    |
|                        |      |                        |
| Tool: create_event     |      | Tool: send_email       |
|                        |      |                        |
| Result: "Meeting       |      | Result: "Email sent    |
|  created for 3pm"      |      |  to john@example.com"  |
+------------------------+      +------------------------+
              |                               |
              +---------------+---------------+
                              |
                              v
+------------------------------------------------------------------+
|                        ORCHESTRATOR                               |
|                                                                   |
|  Combine results:                                                 |
|  "Done! I've scheduled a meeting for tomorrow at 3pm and sent    |
|   an email to John about it."                                    |
+------------------------------------------------------------------+
                              |
                              v
                         User Response
```

---

### Tool Execution Loop

Each agent follows this execution pattern:

```
                    +------------------+
                    |  Receive Task    |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Build Messages   |
                    | (System + Task)  |
                    +--------+---------+
                             |
                             v
              +------>+------------------+
              |       |    Call LLM      |
              |       | (with tool list) |
              |       +--------+---------+
              |                |
              |                v
              |       +------------------+
              |       | LLM Response     |
              |       +--------+---------+
              |                |
              |       +--------+---------+
              |       |                  |
              |       v                  v
              |  [Tool Call]      [Final Response]
              |       |                  |
              |       v                  v
              |  +----------+      +----------+
              |  | Execute  |      |  Return  |
              |  |   Tool   |      |  Result  |
              +--+----------+      +----------+
```

---

### Memory Architecture (Vector Search)

wikiClaw uses semantic memory powered by embeddings:

```
User: "Remember that my favorite color is blue"
                    |
                    v
        +------------------------+
        |    MEMORY AGENT        |
        +------------------------+
                    |
                    v
        +------------------------+
        |   save_memory tool     |
        +------------------------+
                    |
    +---------------+---------------+
    |                               |
    v                               v
+----------+                +----------------+
| OpenAI   |                |   MongoDB      |
| Embed    |                |   Atlas        |
| API      |                |                |
+----------+                +----------------+
    |                               ^
    v                               |
+----------+                        |
| Vector   |  ----> Store ------->  |
| [0.12,   |        with            |
|  -0.34,  |        metadata        |
|  0.56,   |                        |
|  ...]    |                        |
+----------+                        |
                                    |
                                    |
User: "What color do I like?"       |
                    |               |
                    v               |
        +------------------------+  |
        |   search_memory tool   |  |
        +------------------------+  |
                    |               |
                    v               |
        +------------------------+  |
        |  Generate query        |  |
        |  embedding             |  |
        +------------------------+  |
                    |               |
                    v               |
        +------------------------+  |
        |  Vector similarity     |<-+
        |  search in MongoDB     |
        +------------------------+
                    |
                    v
        +------------------------+
        | Result: "User's        |
        | favorite color is blue"|
        +------------------------+
```

**Why Vector Search?**

| Traditional Search | Vector Search |
|--------------------|---------------|
| "favorite color" matches only "favorite color" | "favorite color" matches "color I like", "preferred color", etc. |
| Keyword-based | Meaning-based |
| Exact match required | Semantic similarity |

---

### File Processing Pipeline

```
User sends PDF via Telegram
            |
            v
+---------------------------+
|     TELEGRAM BOT          |
|                           |
| 1. Check file extension   |
| 2. Check file size (<5MB) |
+-------------+-------------+
              |
              v
+---------------------------+
|    FILE PROCESSOR         |
|                           |
| - PDF: pdfplumber         |
| - Word: python-docx       |
| - Excel: openpyxl         |
| - CSV: built-in csv       |
| - Code/Text: direct read  |
+-------------+-------------+
              |
              v
+---------------------------+
|    APPLY LIMITS           |
|                           |
| - Max 20 PDF pages        |
| - Max 500 rows            |
| - Max 15,000 characters   |
+-------------+-------------+
              |
              v
+---------------------------+
|    BUILD MESSAGE          |
|                           |
| "[File: report.pdf]       |
|  {extracted text}         |
|                           |
|  User request: Summarize" |
+-------------+-------------+
              |
              v
+---------------------------+
|    ORCHESTRATOR           |
|    (Process as normal)    |
+---------------------------+
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **LLM** | Ollama Cloud (gpt-oss:120b-cloud) | Natural language understanding and generation |
| **Embeddings** | OpenAI text-embedding-3-small | Convert text to vectors for semantic search |
| **Database** | MongoDB Atlas | Store conversations, memories, notes |
| **Vector Search** | MongoDB Atlas Vector Search | Semantic similarity search |
| **Calendar** | Google Calendar API | Schedule and manage events |
| **Email** | Gmail API | Send emails |
| **Web Search** | DuckDuckGo (ddgs) | Search the internet |
| **Bot Platform** | Telegram (python-telegram-bot) | User interface |
| **Webhook** | FastAPI + ngrok | Receive Telegram updates |
| **Language** | Python 3.11+ | Application code |

---

## Project Structure

```
wikiClaw/
├── src/
│   ├── agent/                    # Core agent logic
│   │   ├── core.py               # Main agent class
│   │   ├── llm.py                # Ollama LLM client
│   │   └── prompts.py            # System prompts
│   │
│   ├── agents/                   # Hierarchical agents
│   │   ├── base.py               # BaseSubAgent class
│   │   ├── orchestrator.py       # Main orchestrator
│   │   └── sub_agents/           # Specialized agents
│   │       ├── memory.py         # Memory operations
│   │       ├── notes.py          # Notes management
│   │       ├── calendar.py       # Calendar operations
│   │       ├── web.py            # Web search
│   │       └── email.py          # Email sending
│   │
│   ├── tools/                    # Action executors
│   │   ├── base.py               # BaseTool class
│   │   ├── memory.py             # save_memory, search_memory
│   │   ├── notes.py              # CRUD for notes
│   │   ├── calendar.py           # Calendar tools
│   │   ├── websearch.py          # Web/news search
│   │   └── email.py              # send_email
│   │
│   ├── integrations/             # External services
│   │   ├── telegram/             # Telegram bot + webhook
│   │   └── google/               # Calendar + Gmail clients
│   │
│   ├── database/                 # Data layer
│   │   └── mongodb.py            # MongoDB operations
│   │
│   ├── memory/                   # Memory layer
│   │   └── embeddings.py         # OpenAI embeddings client
│   │
│   ├── schemas/                  # Data models
│   │   ├── context.py            # Long-term memory
│   │   ├── message.py            # Chat messages
│   │   ├── note.py               # Notes
│   │   └── reminder.py           # Reminders
│   │
│   ├── utils/                    # Utilities
│   │   └── file_processor.py     # File text extraction
│   │
│   ├── config.py                 # Configuration loader
│   ├── constants.py              # All constants
│   └── main.py                   # Entry point
│
├── scripts/                      # Testing & setup
│   ├── setup_vector_index.py     # MongoDB index setup
│   ├── test_hierarchical.py      # Test all agents
│   ├── test_file_processing.py   # Test file extraction
│   └── test_file_with_agent.py   # Test files + LLM
│
├── requirements.txt              # Dependencies
├── .env                          # Environment variables
├── credentials.json              # Google OAuth credentials
├── token.json                    # Google OAuth token
└── README.md                     # This file
```

---

## Setup Guide

### Prerequisites

- Python 3.11+
- MongoDB Atlas account (free tier works)
- Telegram account
- OpenAI API key (for embeddings)
- Ollama or LLM API access
- Google Cloud account (optional, for Calendar/Gmail)

### Step 1: Clone and Setup Environment

```bash
git clone <repository>
cd wikiClaw
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create `.env` file:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/wikiclaw

# OpenAI (for embeddings only)
OPENAI_API_KEY=sk-your-openai-api-key

# Ollama LLM
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=gpt-oss:120b-cloud

# ngrok (for webhook)
NGROK_AUTH_TOKEN=your_ngrok_token

# Google APIs (optional)
GOOGLE_CREDENTIALS_PATH=credentials.json
GOOGLE_TOKEN_PATH=token.json

# Webhook
WEBHOOK_PORT=8443
```

### Step 3: Setup External Services

#### Telegram Bot
1. Open Telegram, search for `@BotFather`
2. Send `/newbot` and follow prompts
3. Copy token to `.env`

#### MongoDB Atlas
1. Create free cluster at [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Create database user
3. Get connection string
4. Run: `python scripts/setup_vector_index.py`

#### Google APIs (Optional)
1. Create project at [console.cloud.google.com](https://console.cloud.google.com)
2. Enable Calendar API and Gmail API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download `credentials.json`
5. First run will prompt for authorization

#### ngrok
1. Sign up at [ngrok.com](https://ngrok.com)
2. Copy auth token to `.env`

### Step 4: Run

```bash
python src/main.py
```

---

## Usage Examples

### Memory

```
You: Remember that I'm allergic to peanuts
Bot: Saved! I'll remember that you're allergic to peanuts.

You: What am I allergic to?
Bot: You're allergic to peanuts.
```

### Notes

```
You: Make a note: Project ideas - AI assistant, chatbot, automation
Bot: Created note "Project ideas" with your content.

You: Show my notes
Bot: Your notes:
     - Project ideas (created today)
```

### Calendar

```
You: Schedule a dentist appointment tomorrow at 2pm
Bot: Done! Created "Dentist appointment" for tomorrow at 2:00 PM.

You: What's on my calendar this week?
Bot: Your upcoming events:
     - Dentist appointment: Tomorrow at 2:00 PM
```

### Web Search

```
You: Search for best practices in Python async programming
Bot: Here's what I found:
     - Use asyncio for I/O-bound tasks
     - Avoid blocking calls in async functions
     - Use aiohttp for async HTTP requests
     ...
```

### File Analysis

```
You: [Upload sales_report.pdf]
     Summarize this report

Bot: This sales report shows:
     - Total revenue: $1.2M (up 15% from last quarter)
     - Top product: Widget Pro (35% of sales)
     - Key markets: US (45%), Europe (30%), Asia (25%)
```

---

## Configuration

Key settings in `src/constants.py`:

```python
# Conversation
MAX_RECENT_MESSAGES = 15          # Messages to keep in context

# File Processing
MAX_FILE_SIZE_MB = 5              # Maximum upload size
MAX_EXTRACTED_TEXT_CHARS = 15000  # Max text to send to LLM
MAX_PDF_PAGES = 20                # Pages to extract from PDFs
MAX_EXCEL_ROWS = 500              # Rows to read from spreadsheets

# Embeddings
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536

# Agent Iterations
MAX_ORCHESTRATOR_ITERATIONS = 5   # Orchestrator loop limit
MAX_SUB_AGENT_ITERATIONS = 3      # Sub-agent loop limit
```

---

## Testing

```bash
# Test all hierarchical agents
python scripts/test_hierarchical.py

# Test file text extraction
python scripts/test_file_processing.py

# Test file processing with LLM
python scripts/test_file_with_agent.py
```

---

## Design Decisions

### Why Hierarchical Agents?

1. **Separation of Concerns** - Each agent is an expert in its domain
2. **Scalability** - Add new agents without modifying existing ones
3. **Better Prompts** - Focused prompts perform better than generic ones
4. **Reduced Errors** - Agents see fewer, relevant tools

### Why MongoDB Atlas?

1. **Vector Search** - Native support for embedding-based search
2. **Free Tier** - 512MB storage free forever
3. **Managed Service** - No infrastructure to maintain
4. **Flexible Schema** - JSON documents fit AI applications

### Why Telegram?

1. **Mobile First** - Access your agent anywhere
2. **Rich Features** - Files, voice, images supported
3. **Free** - No API costs
4. **Webhooks** - Real-time message delivery

---

## Future Roadmap

- [ ] Voice message support (speech-to-text)
- [ ] Image understanding (vision models)
- [ ] Scheduled reminders
- [ ] Multi-user support
- [ ] Parallel sub-agent execution
- [ ] Cloud deployment (AWS/GCP/Railway)
- [ ] Web UI alternative

---

## License

MIT License - Feel free to use for learning and building.

---

## Acknowledgments

Built for learning agentic AI patterns. Inspired by:
- OpenAI Assistants API
- LangChain Agents
- AutoGPT
- Open Interpreter
