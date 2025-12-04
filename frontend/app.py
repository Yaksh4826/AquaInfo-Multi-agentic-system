import streamlit as st
from datetime import datetime



def ai_agent(query: str) -> str:
    """ Agentic function that uses the Coordinator to return the response"""
    #   modify this to call your Coordinator Agent
    from coordinator import Coordinator
    agent = Coordinator()
    result = agent.run(query)
    return result
 




# """"  Streamlit page configurations """
st.set_page_config(page_title="AquaInfo Chatbot", page_icon="💧")

st.title("💧 AquaInfo Reserach Assistant ")
st.write("Ask anything about water research, datasets, simulations…")



# """ Sessions for storing the messages """
if "messages" not in st.session_state:
    st.session_state["messages"] = []   # list of dicts

# Display chat history
for msg in st.session_state["messages"]:
    role = "🧑 User" if msg["role"] == "user" else "🤖 AquaInfo Agent"
    st.chat_message(msg["role"]).markdown(f"**{role}**: {msg['content']}")




# """ User input """
prompt = st.chat_input("Type your question…")

if prompt:
    # Add user message to history
    """ Displaying the user messages / prompts in the user container """
    st.session_state["messages"].append({"role": "user", "content": prompt})
    st.chat_message("user").markdown(prompt)

    # Get agent response
    response = ai_agent(prompt)

    # Add assistant response
    # """ Displaying the agents response in assistant container """
    st.session_state["messages"].append({"role": "assistant", "content": response})
    st.chat_message("assistant").markdown(response)


    # """ Feedback component for the user feedback after each query"""
    with st.container():
        st.write("### Provide Feedback")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("👍 Helpful"):
                st.success("Thanks for your positive feedback!")

        with col2:
            if st.button("👎 Not Helpful"):
                feedback = st.text_area("Tell us what went wrong:", key="fb_text")
                if st.button("Submit Feedback"):
                    # store feedback or send to backend
                    st.warning("Thanks, we will improve!")
