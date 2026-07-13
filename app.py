import streamlit as st

from agent import run_agent
from tools import CUSTOMERS

st.set_page_config(
    page_title="Support Ticket Triage Agent",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .stApp {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
    }
    section[data-testid="stSidebar"] {
        background: #0b1120;
        border-right: 1px solid #1f2937;
    }
    h1, h2, h3, h4, p, span, label, .stMarkdown, .stCaption {
        color: #e5e7eb !important;
    }
    .hero {
        padding: 1.75rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
    }
    .hero h1 {
        color: white !important;
        font-size: 1.9rem;
        margin: 0 0 0.35rem 0;
    }
    .hero p {
        color: rgba(255,255,255,0.9) !important;
        margin: 0;
        font-size: 0.98rem;
    }
    .card {
        background: #1a2236;
        border: 1px solid #2a3550;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 0.02em;
    }
    .badge-category {
        background: rgba(99, 102, 241, 0.18);
        color: #a5b4fc !important;
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    .badge-high { background: rgba(239, 68, 68, 0.18); color: #fca5a5 !important; border: 1px solid rgba(239, 68, 68, 0.4); }
    .badge-medium { background: rgba(245, 158, 11, 0.18); color: #fcd34d !important; border: 1px solid rgba(245, 158, 11, 0.4); }
    .badge-low { background: rgba(34, 197, 94, 0.18); color: #86efac !important; border: 1px solid rgba(34, 197, 94, 0.4); }
    .status-banner {
        padding: 0.9rem 1.2rem;
        border-radius: 10px;
        font-weight: 600;
        margin: 1rem 0;
    }
    .status-escalate {
        background: rgba(239, 68, 68, 0.12);
        border: 1px solid rgba(239, 68, 68, 0.35);
        color: #fca5a5 !important;
    }
    .status-resolved {
        background: rgba(34, 197, 94, 0.12);
        border: 1px solid rgba(34, 197, 94, 0.35);
        color: #86efac !important;
    }
    .reply-box {
        background: #0f1526;
        border: 1px solid #2a3550;
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        font-size: 0.95rem;
        line-height: 1.55;
        white-space: pre-wrap;
    }
    .tool-step {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.5rem 0.8rem;
        background: #0f1526;
        border-radius: 8px;
        margin-bottom: 0.4rem;
        font-size: 0.88rem;
        font-family: 'SFMono-Regular', Consolas, monospace;
    }
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.4rem;
        font-weight: 600;
    }
    div[data-testid="stExpander"] {
        background: #1a2236;
        border: 1px solid #2a3550;
        border-radius: 10px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

TOOL_ICONS = {
    "lookup_customer": "👤",
    "check_order_status": "📦",
    "search_knowledge_base": "📚",
    "escalate_to_human": "🚨",
}

with st.sidebar:
    st.markdown("### 🎫 About this agent")
    st.markdown(
        "An LLM support agent that **decides which tools to call** per ticket — "
        "customer lookup, order status, help-article search, or escalation — "
        "rather than following a fixed script."
    )
    st.markdown("---")
    st.markdown("**Tech stack**")
    st.markdown("- Groq · Llama 3.3 70B\n- Tool / function calling\n- Streamlit\n- Mock CRM + order + KB data")
    st.markdown("---")
    st.markdown("**Tools available to the agent**")
    for name, icon in TOOL_ICONS.items():
        st.markdown(f"{icon} `{name}`")
    st.markdown("---")
    st.caption("Built by Yasir A. · [GitHub repo](https://github.com/Yasir-Aziz000/support-ticket-triage-agent)")

st.markdown(
    """
    <div class="hero">
        <h1>🎫 Support Ticket Triage Agent</h1>
        <p>Classifies incoming tickets, pulls live account/order context via tool calls, drafts a reply — or escalates to a human when it should.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 1.3], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Incoming ticket")
    with st.form("ticket_form"):
        customer_email = st.selectbox("Customer email", options=list(CUSTOMERS.keys()))
        ticket_subject = st.text_input("Subject", value="Payment failed, can't access my account")
        ticket_message = st.text_area(
            "Message",
            value="Hi, my card was charged but I still can't log in to my Pro account. This is blocking my whole team. Please help ASAP.",
            height=140,
        )
        submitted = st.form_submit_button("Run Agent →")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    if not submitted:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Result")
        st.caption("Submit a ticket on the left to see the agent's triage decision here.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        with st.spinner("Agent is triaging the ticket..."):
            result = run_agent(customer_email, ticket_subject, ticket_message)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Result")

        category = result.get("category", "unknown")
        urgency = result.get("urgency", "medium")
        urgency_class = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(urgency, "badge-medium")

        st.markdown(
            f'<span class="badge badge-category">📁 {category}</span>&nbsp;&nbsp;'
            f'<span class="badge {urgency_class}">⚡ {urgency} urgency</span>',
            unsafe_allow_html=True,
        )

        if result.get("escalate"):
            st.markdown(
                f'<div class="status-banner status-escalate">🚨 Escalated to human — {result.get("escalation_reason")}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="status-banner status-resolved">✅ Handled by agent — no escalation needed</div>',
                unsafe_allow_html=True,
            )

        st.markdown("**Draft reply**")
        st.markdown(f'<div class="reply-box">{result.get("draft_reply") or "(no reply drafted)"}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("#### Tool calls made")
        trace = result.get("trace", [])
        if not trace:
            st.caption("The agent answered without needing any tools.")
        for step in trace:
            icon = TOOL_ICONS.get(step["tool"], "🔧")
            st.markdown(
                f'<div class="tool-step">{icon} <b>{step["tool"]}</b>({step["args"]})</div>',
                unsafe_allow_html=True,
            )
        with st.expander("Raw tool trace (JSON)"):
            st.json(trace)
        st.markdown("</div>", unsafe_allow_html=True)
