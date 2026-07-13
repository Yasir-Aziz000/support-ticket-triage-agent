# Support Ticket Triage Agent

An LLM agent that reads an incoming support ticket, decides which tools it needs (customer lookup, order status, help-article search), calls them, and produces a category, urgency level, draft reply, and an escalate-to-human decision — instead of just answering from training data.

## Problem it solves

A generic chatbot can answer FAQ-style questions but can't tell you *this specific customer's* plan tier, *this specific order's* status, or *when to stop and hand off to a human*. This agent demonstrates real agentic tool use: the LLM decides, per ticket, which internal systems to query before responding, and knows its own limits (escalating angry, legal, or security-related tickets rather than guessing).

## How it works

![Agent demo](screenshots/agent-demo.png)

1. A ticket comes in: customer email, subject, message.
2. The agent (`agent.py`) sends the ticket to an LLM (Groq, Llama 3.3 70B) along with 4 tool definitions:
   - `lookup_customer` — account plan, signup date, prior ticket count
   - `check_order_status` — order/shipment status by order ID
   - `search_knowledge_base` — keyword search over internal help articles
   - `escalate_to_human` — flags the ticket instead of auto-replying
3. The LLM decides which tools to call (zero, one, or several — it's not hardcoded which ones run), tools execute against local mock data, and results are fed back to the LLM.
4. The LLM produces a final structured JSON verdict: category, urgency, whether to escalate (and why), and a draft reply.
5. The Streamlit UI (`app.py`) displays the verdict plus a full trace of every tool call made, so the decision process is auditable, not a black box.

## Tech stack

- **Python**
- **Groq API** (Llama 3.3 70B) — free tier, fast inference, OpenAI-compatible tool/function calling
- **Streamlit** — demo UI
- Mock JSON "databases" for customers/orders (`data/`) — swap these for real CRM/order-system API calls in production

## Setup

1. `pip install -r requirements.txt`
2. Get a free Groq API key: [console.groq.com/keys](https://console.groq.com/keys) (no card required)
3. Copy `.env.example` to `.env` and add your key
4. Run:
   ```
   streamlit run app.py
   ```
5. Pick a customer, edit the subject/message, click **Run Agent**

## Example

**Ticket:** "My card was charged but I still can't log in to my Pro account. This is blocking my whole team. Please help ASAP." (Enterprise customer)

**Agent output:**
- Category: `billing`
- Urgency: `high`
- Tools used: `lookup_customer`, `check_order_status`, `search_knowledge_base`
- Escalate: depends on account tier / order status found — enterprise + blocked-from-work tickets tend to get escalated
- Draft reply referencing the customer's actual account/order data, not a generic template

## Possible extensions

- Swap the JSON mock data for real CRM (HubSpot/Salesforce) and order-system API calls
- Add a `send_email` tool to actually dispatch the draft reply via SMTP/SendGrid after human approval
- Replace keyword-based KB search with embedding-based semantic search (e.g. ChromaDB, as in the RAG chatbot project)
- Log every ticket + verdict to a database for analytics on category/urgency trends over time

## About

Built by [Yasir A.](https://www.upwork.com) as a portfolio project demonstrating agentic LLM tool-calling, structured output, and human-in-the-loop escalation logic for support automation.
