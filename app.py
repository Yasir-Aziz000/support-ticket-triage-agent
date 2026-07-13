import json

import streamlit as st

from agent import run_agent
from tools import CUSTOMERS

st.set_page_config(page_title="Support Ticket Triage Agent", page_icon="🎫", layout="centered")

st.title("🎫 Support Ticket Triage Agent")
st.caption("An LLM agent that classifies incoming tickets, looks up account/order context via tool calls, and drafts a reply — or escalates to a human.")

with st.form("ticket_form"):
    customer_email = st.selectbox("Customer email", options=list(CUSTOMERS.keys()))
    ticket_subject = st.text_input("Subject", value="Payment failed, can't access my account")
    ticket_message = st.text_area(
        "Message",
        value="Hi, my card was charged but I still can't log in to my Pro account. This is blocking my whole team. Please help ASAP.",
        height=120,
    )
    submitted = st.form_submit_button("Run Agent")

if submitted:
    with st.spinner("Agent is triaging the ticket..."):
        result = run_agent(customer_email, ticket_subject, ticket_message)

    col1, col2 = st.columns(2)
    col1.metric("Category", result.get("category", "-"))
    urgency = result.get("urgency", "-")
    urgency_color = {"high": "🔴", "medium": "🟠", "low": "🟢"}.get(urgency, "⚪")
    col2.metric("Urgency", f"{urgency_color} {urgency}")

    if result.get("escalate"):
        st.error(f"**Escalated to human** — {result.get('escalation_reason')}")
    else:
        st.success("Handled by agent — no escalation needed")

    st.subheader("Draft reply")
    st.write(result.get("draft_reply") or "(no reply drafted)")

    with st.expander("Tools called during this run"):
        st.write(result.get("tools_used", []))
        st.json(result.get("trace", []))
