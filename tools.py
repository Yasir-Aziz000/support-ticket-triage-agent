import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

with open(DATA_DIR / "customers.json") as f:
    CUSTOMERS = {c["email"]: c for c in json.load(f)}

with open(DATA_DIR / "orders.json") as f:
    ORDERS = {o["order_id"]: o for o in json.load(f)}

with open(DATA_DIR / "kb.json") as f:
    KB_ARTICLES = json.load(f)


def lookup_customer(email: str) -> dict:
    customer = CUSTOMERS.get(email)
    if not customer:
        return {"found": False, "message": f"No customer found with email {email}"}
    return {"found": True, **customer}


def check_order_status(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if not order:
        return {"found": False, "message": f"No order found with id {order_id}"}
    return {"found": True, **order}


def search_knowledge_base(query: str) -> dict:
    query_words = set(query.lower().split())
    scored = []
    for article in KB_ARTICLES:
        overlap = sum(1 for kw in article["keywords"] if kw in query.lower())
        if overlap > 0:
            scored.append((overlap, article))
    scored.sort(key=lambda x: x[0], reverse=True)
    top = [a for _, a in scored[:2]]
    if not top:
        return {"found": False, "message": "No matching help article found"}
    return {"found": True, "articles": top}


def escalate_to_human(reason: str) -> dict:
    return {"escalated": True, "reason": reason, "message": "Ticket flagged for human review"}


TOOL_FUNCTIONS = {
    "lookup_customer": lookup_customer,
    "check_order_status": check_order_status,
    "search_knowledge_base": search_knowledge_base,
    "escalate_to_human": escalate_to_human,
}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_customer",
            "description": "Look up a customer's account details (plan tier, signup date, prior ticket count) by email.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "The customer's email address"}
                },
                "required": ["email"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_order_status",
            "description": "Look up the status of an order by its order ID (e.g. shipped, delivered, payment_failed, processing).",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {"type": "string", "description": "The order ID, e.g. ORD-1001"}
                },
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search internal help articles for relevant guidance on a topic (billing, passwords, shipping, plans, API limits, data export).",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search terms describing the customer's issue"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Flag this ticket for human review instead of auto-replying. Use for angry/abusive messages, legal threats, security issues, or anything the knowledge base and account data can't resolve.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {"type": "string", "description": "Why this needs a human"}
                },
                "required": ["reason"],
            },
        },
    },
]
