# SupportFlow AI

### Agentic Customer Support System powered by Gemini

SupportFlow AI is an end-to-end AI customer support platform that combines **LLM reasoning, function calling, RAG, conversation memory, and backend actions**.

Instead of simply generating chatbot responses, the agent can investigate customer accounts, retrieve transactions, search company policies, evaluate refund eligibility, create refund requests, and open support tickets.

---

## 🚀 Overview

Traditional customer-support chatbots mainly answer questions.

SupportFlow AI is designed to **reason and take action**.

A typical interaction looks like:

```text
Customer
   │
   ▼
SupportFlow AI Agent
   │
   ├── Understand request
   │
   ├── Search knowledge base
   │
   ├── Retrieve customer information
   │
   ├── Inspect transactions
   │
   ├── Determine required action
   │
   └── Execute backend tool
          │
          ├── Refund request
          ├── Support ticket
          └── Account lookup
```

The agent uses deterministic backend tools for operations while Gemini handles natural-language reasoning and interpretation.

---

## ✨ Key Features

### 🤖 Agentic AI

The system uses Gemini function calling to decide when backend tools are required.

The agent can:

- Check customer accounts
- Retrieve transactions
- Investigate duplicate charges
- Check refund eligibility
- Submit refund requests
- Create support tickets
- Retrieve previous conversation context

### 📚 Retrieval-Augmented Generation

SupportFlow AI includes a local knowledge base powered by:

- Gemini Embeddings
- Qdrant
- Semantic search

Current knowledge includes:

- Refund policies
- Subscription policies
- Account policies

The agent can retrieve relevant policy information before responding.

### 🧠 Conversation Memory

Conversations are persisted using SQLite.

The system stores:

- User messages
- Assistant responses
- Conversation IDs
- Customer IDs
- Timestamps

This allows the agent to maintain context across messages.

### 💳 Transaction Investigation

The agent can inspect customer transactions and identify situations such as:

```text
Customer:
Why was I charged twice?

Agent:
→ Check customer
→ Retrieve transactions
→ Identify duplicate transaction
→ Explain the finding
→ Offer refund/support workflow
```

### 💰 Refund Workflow

Refund requests are handled through a backend tool rather than simply being described by the LLM.

Workflow:

```text
Customer request
       ↓
Check transaction
       ↓
Check refund eligibility
       ↓
Create refund request
       ↓
Persist request in SQLite
       ↓
Return refund ID
```

Example:

```text
REFUND-0001
Status: pending
```

The refund system is intentionally a mock support/payment workflow for demonstration purposes. It does not process real payments.

### 🎫 Support Tickets

The agent can create support tickets when an issue requires escalation.

Example:

```text
TICKET-0001
Status: open
```

Tickets are persisted in SQLite.

---

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │      Customer       │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Next.js Frontend  │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Gemini AI Agent   │
                         │                     │
                         │  Reasoning + Tools  │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    │               │                │
                    ▼               ▼                ▼
              ┌──────────┐   ┌────────────┐   ┌──────────────┐
              │ Customer │   │ Knowledge  │   │ Conversation │
              │  Tools   │   │   Base     │   │    Memory    │
              └────┬─────┘   └─────┬──────┘   └──────┬───────┘
                   │               │                 │
                   ▼               ▼                 ▼
              ┌──────────┐   ┌────────────┐   ┌──────────────┐
              │Customer/ │   │  Qdrant    │   │    SQLite    │
              │Transaction│   │  Vectors   │   │   Database   │
              │   Data   │   └────────────┘   └──────────────┘
              └──────────┘
```

---

## 🧠 Agent Workflow

For every support request, the agent can determine whether it needs additional information or an action.

Example:

```text
User:
"Can I get a refund for my $49.99 charge?"

             ↓

Understand request

             ↓

Retrieve customer account

             ↓

Retrieve transaction

             ↓

Check refund eligibility

             ↓

Submit refund request

             ↓

Return refund reference

             ↓

"Your refund request REFUND-0001
has been submitted and is pending review."
```

The LLM does not directly modify the database.

Instead:

```text
LLM
 ↓
Tool selection
 ↓
Backend function
 ↓
Database/API
 ↓
Tool result
 ↓
LLM
 ↓
Final response
```

This separation makes the system easier to control and audit.

---

## 🛠️ Tech Stack

### Backend

- Python
- FastAPI
- Pydantic
- SQLite
- Google Gemini API
- Gemini Function Calling
- Gemini Embeddings

### AI / RAG

- Gemini
- Qdrant
- Retrieval-Augmented Generation
- Semantic Search

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

---

## 📁 Project Structure

```text
supportflow-ai/
│
├── backend/
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── llm_service.py
│   │   │
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   └── support_tools.py
│   │   │
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   └── knowledge_base.py
│   │   │
│   │   └── memory/
│   │       ├── __init__.py
│   │       └── conversation_memory.py
│   │
│   ├── data/
│   │   └── knowledge/
│   │       ├── refund_policy.txt
│   │       ├── subscription_policy.txt
│   │       └── account_policy.txt
│   │
│   ├── index_knowledge.py
│   ├── test_rag.py
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── app/
│   │   └── page.tsx
│   ├── package.json
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd supportflow-ai
```

### Backend Setup

Enter the backend directory:

```bash
cd backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### Environment Variables

Create:

```text
backend/.env
```

Add:

```text
GEMINI_API_KEY=your_gemini_api_key_here
```

Never commit the `.env` file to GitHub.

### Initialize the Database

Run:

```bash
python -c "from app.database import init_database; init_database(); print('Database initialized successfully')"
```

### Index the Knowledge Base

Run:

```bash
python index_knowledge.py
```

Test retrieval:

```bash
python test_rag.py
```

### Start the Backend

From:

```text
supportflow-ai/backend
```

run:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

### Frontend Setup

Open another terminal.

From the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

---

## 🔌 API Endpoints

| Method | Endpoint                     | Purpose                        |
|--------|-------------------------------|---------------------------------|
| GET    | `/`                           | API health check                |
| POST   | `/chat`                       | Send support message            |
| GET    | `/conversations/{id}`         | Retrieve conversation           |
| DELETE | `/conversations/{id}`         | Clear conversation              |
| GET    | `/customers/{id}`             | Retrieve customer information   |
| GET    | `/customers/{id}/refunds`     | Retrieve refund requests        |
| GET    | `/customers/{id}/tickets`     | Retrieve support tickets        |

---

## 💬 Example Interactions

### Duplicate Charge

```text
User:
Why was I charged twice?

Agent:
→ Checks customer
→ Retrieves transactions
→ Detects duplicate charge
→ Explains transaction
```

### Refund

```text
User:
Can I get a refund for TXN1001?

Agent:
→ Checks transaction
→ Checks refund eligibility
→ Creates refund request
→ Returns refund ID
```

### Account Question

```text
User:
What subscription am I currently on?

Agent:
→ Retrieves customer account
→ Identifies subscription
→ Responds with account information
```

### Policy Question

```text
User:
What is your refund policy?

Agent:
→ Searches knowledge base
→ Retrieves relevant policy
→ Generates grounded response
```

### Escalation

```text
User:
I need help with an issue that cannot be resolved.

Agent:
→ Determines escalation is required
→ Creates support ticket
→ Returns ticket ID
```

---

## 🔐 Safety & Reliability

SupportFlow AI separates reasoning from execution.

The LLM is responsible for understanding requests and selecting tools, while backend functions control actual operations.

The system also includes protections such as:

- Customer ID validation
- Prevention of unauthorized customer lookups
- Duplicate refund-request checks
- Transaction validation
- Tool-based database actions
- Knowledge-base grounding
- Persistent conversation history

The AI is instructed not to invent transaction or refund information.
