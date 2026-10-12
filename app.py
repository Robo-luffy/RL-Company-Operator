import os
import streamlit as st
from dotenv import load_dotenv
from graph import run_research, submit_and_verify
from db import init_db, get_demo_snapshot, reset_demo_expense

load_dotenv()
st.set_page_config(page_title="starX Employee", page_icon="🤖", layout="wide")
init_db()
st.title("🤖 starX Employee")
# st.caption("LLM tool calling · LangGraph · LangChain RAG · Playwright")
if not os.getenv("GROQ_API_KEY"):
    st.warning("Add GROQ_API_KEY to your .env file before running the agent.")

with st.sidebar:
    st.header("Architecture")
    st.markdown("- **LLM:** `bind_tools()`")
    st.markdown("- **Workflow:** LangGraph + `ToolNode`")
    st.markdown("- **RAG:** Loader → Splitter → Embeddings → FAISS → Retriever")
    st.markdown("- **Browser:** Playwright")
    st.markdown("- **Safety:** Human approval before write actions")

goal = st.text_area("Task for the AI employee",
    "Process Rahul Sharma's latest expense claim according to company policy and prepare it for approval.", height=100)
if "research_state" not in st.session_state:
    st.session_state.research_state = None
if "write_state" not in st.session_state:
    st.session_state.write_state = None

# c1 = st.columns(1)
# with c1:
#     if st.button("1. Investigate task", type="primary", use_container_width=True):
#         try:
#             with st.spinner("LLM is selecting read tools and retrieving policy evidence..."):
#                 st.session_state.research_state = run_research(goal)
#                 st.session_state.write_state = None
#         except Exception as exc:
#             st.error(f"Agent run failed: {exc}")


# with c1:
if st.button(
        "Investigate task",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.research_state = None
        st.session_state.write_state = None

        st.subheader("Live agent execution")

        with st.status(
            "AI employee is investigating...",
            expanded=True,
        ) as status:

            progress_placeholder = st.empty()

            def show_progress(step, detail):
                progress_placeholder.markdown(
                    f"**{step}**\n\n{detail}"
                )

            try:
                result = run_research(
                    goal,
                    progress_callback=show_progress,
                )

                st.session_state.research_state = result

                status.update(
                    label="Investigation completed",
                    state="complete",
                )

            except Exception as exc:
                status.update(
                    label="Investigation failed",
                    state="error",
                )
                st.error(f"Agent run failed: {exc}")

with st.sidebar:
    st.header("Company Overview")
    try:
           snapshot = get_demo_snapshot()
           st.metric("Employees", snapshot["employees"])
           st.metric("Expense claims", snapshot["expenses"])
           st.write("Company website: http://127.0.0.1:8000")
    except Exception:
           st.info("Start the company website with `uvicorn company_app:app --port 8000`.")

    st.divider()
    st.subheader("Demo controls")

    if st.button("Reset demo expense", use_container_width=True):
        try:
            result = reset_demo_expense("EXP1023")

            st.session_state.research_state = None
            st.session_state.write_state = None

            st.success(
                f"{result['expense_id']} reset to Draft."
            )
            st.rerun()

        except Exception as exc:
            st.error(f"Reset failed: {exc}")

state = st.session_state.research_state
if state:
    st.divider()
    st.subheader("Execution trace")
    for event in state.get("events", []):
        st.write(f"- {event}")
    st.subheader("LLM tool-calling trace")
    for msg in state.get("messages", []):
        role = getattr(msg, "type", "message")
        content = getattr(msg, "content", "")
        calls = getattr(msg, "tool_calls", None)
        if role == "human":
            st.markdown(f"**User:** {content}")
        elif role == "ai":
            if content:
                st.markdown(f"**LLM:** {content}")
            if calls:
                st.markdown("**Tool requests from the LLM:**")
                st.json(calls)
        elif role == "tool":
            st.markdown(f"**Tool result — {getattr(msg, 'name', 'tool')}:**")
            st.code(str(content)[:4000])
    st.subheader("Agent summary")
    st.write(state.get("final_answer", "No final answer was generated."))
    if state.get("expense"):
        st.subheader("Expense selected for review")
        st.json(state["expense"])
    if state.get("policy_evidence"):
        st.subheader("Retrieved company policy evidence (RAG)")
        for item in state["policy_evidence"]:
            st.info(f"**Source:** {item.get('source', 'unknown')}\n\n{item.get('content', '')}")
    if state.get("needs_approval"):
        st.warning("Human approval is required before the browser submits the expense.")
        approve, reject = st.columns(2)
        with approve:
            if st.button("Approve and submit via browser", type="primary", use_container_width=True):
                try:
                    with st.spinner("Playwright is submitting the request and independently verifying it..."):
                        st.session_state.write_state = submit_and_verify(state)
                except Exception as exc:
                    st.session_state.write_state = {"status": "failed", "error": str(exc)}
                st.rerun()
        with reject:
            if st.button("Reject action", use_container_width=True):
                state["needs_approval"] = False
                state["final_answer"] = "Human rejected the proposed action. No write action was performed."
                st.session_state.research_state = state
                st.session_state.write_state = {"status": "rejected"}
                st.rerun()

write_state = st.session_state.write_state
if write_state:
    st.divider()
    st.subheader("Execution and verification")
    if write_state.get("status") == "verified":
        st.success("The request was submitted and independently verified.")
    elif write_state.get("status") == "rejected":
        st.info("Task stopped by human decision.")
    else:
        st.error(write_state.get("error", "The workflow did not complete successfully."))
    st.json(write_state)
st.divider()
st.caption("Fictional local demo. Add authentication, authorization, and audit logging before connecting real company systems.")
