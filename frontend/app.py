import streamlit as st
import time 

# Setting the title:
st.title('AquaInfo- Water research assistant');

"""Intializing the chat history and feedback   """
if "messages" not in st.session_state:
    st.session_state.messages = []


if "feedbacks" not in st.session_state:
    st.session_state.feedbacks = []


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        




# Input for the user 
prompt = st.chat_input("Please enter your query ");


with st.chat_message('User'):
    st.markdown(prompt)

st.session_state.messages.append({"role": "user", "content": prompt})



