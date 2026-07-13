import json
import os

from dotenv import load_dotenv
from groq import Groq

from tools import TOOL_FUNCTIONS, TOOL_SCHEMAS

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are a support ticket triage agent for a SaaS product.

For every incoming ticket:
1. Use the available tools to gather relevant context (customer account info, order status, or help articles) before responding.
2. Decide a category: "billing", "technical", "account", "shipping", or "general".
3. Decide an urgency: "low", "medium", or "high" (high = angry customer, payment/security issue, or enterprise customer blocked from working).
4. If the ticket needs a human (anger, legal threat, security issue, or something tools can't resolve), call escalate_to_human with a reason.
5. Draft a short, professional reply the support team could send as-is.

When you have gathered enough context, respond with ONLY a JSON object (no markdown, no extra text) in this exact shape:
{
  "category": "...",
  "urgency": "...",
  "tools_used": ["..."],
  "escalate": true or false,
  "escalation_reason": "..." or null,
  "draft_reply": "..."
}
"""


def run_agent(customer_email: str, ticket_subject: str, ticket_message: str) -> dict:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Customer email: {customer_email}\nSubject: {ticket_subject}\nMessage: {ticket_message}",
        },
    ]

    tools_called = []
    trace = []

    for _ in range(MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOL_SCHEMAS,
            tool_choice="auto",
        )
        choice = response.choices[0].message

        if choice.tool_calls:
            messages.append(choice.model_dump())
            for call in choice.tool_calls:
                name = call.function.name
                args = json.loads(call.function.arguments)
                result = TOOL_FUNCTIONS[name](**args)
                tools_called.append(name)
                trace.append({"tool": name, "args": args, "result": result})
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(result),
                    }
                )
            continue

        content = choice.content.strip()
        if content.startswith("```"):
            content = content.strip("`").lstrip("json").strip()
        parsed = json.loads(content)
        parsed["tools_used"] = list(dict.fromkeys(tools_called))
        parsed["trace"] = trace
        return parsed

    return {
        "category": "unknown",
        "urgency": "medium",
        "tools_used": tools_called,
        "escalate": True,
        "escalation_reason": "Agent did not converge to a final answer within the iteration limit",
        "draft_reply": "",
        "trace": trace,
    }
