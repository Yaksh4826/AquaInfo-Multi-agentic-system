import streamlit as st
from datetime import datetime
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.Coordinator_agent import CoordinatorAgent

# ---------------- INIT COORDINATOR ----------------
# Create ONE instance for whole session (important)
if "coordinator" not in st.session_state:
    st.session_state["coordinator"] = CoordinatorAgent()


def ai_agent(query: str) -> str:
    """ Agentic function that calls Coordinator Agent """
    coordinator = st.session_state["coordinator"]
    result = coordinator.run(query)
    return result


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AquaInfo Chatbot", page_icon="💧")

st.title("💧 AquaInfo Research Assistant")
st.write("Ask anything about water research, contamination, potability, policies, datasets…")


# ---------------- SESSION MESSAGE STORAGE ----------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []


# ---------------- DISPLAY CHAT HISTORY ----------------
for msg in st.session_state["messages"]:
    role = "🧑 User" if msg["role"] == "user" else "🤖 AquaInfo Agent"
    st.chat_message(msg["role"]).markdown(f"**{role}:** {msg['content']}")


# ---------------- USER INPUT ----------------
prompt = st.chat_input("Type your question…")

if prompt:
    # Save + display user message
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Call AI Agent (Coordinator)
    response = ai_agent(prompt)

    # Save + display assistant message
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)

    # ---------------- FEEDBACK SECTION ----------------
    st.write("### Provide Feedback on the Answer")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("👍 Helpful", key=f"up_{len(st.session_state['messages'])}"):
            # Positive feedback goes to reflection handler too
            st.session_state["coordinator"].handle_feedback("positive")
            st.success("Thanks! This will help me improve future answers.")

    with col2:
        if st.button("👎 Not Helpful", key=f"down_{len(st.session_state['messages'])}"):
            st.session_state["feedback_mode"] = True

    # When user clicks “Not Helpful”
    if st.session_state.get("feedback_mode", False):
        feedback_text = st.text_area("What went wrong? Suggest improvements:")
        if st.button("Submit Feedback", key=f"submit_{len(st.session_state['messages'])}"):
            if feedback_text.strip():
                st.session_state["coordinator"].handle_feedback(feedback_text)
                st.success("Thanks for your feedback — I'll improve next time!")
                st.session_state["feedback_mode"] = False
            else:
                st.error("Feedback cannot be empty.")
