import streamlit as st
from openai import OpenAI
import json
import os

# Initialize OpenAI client
@st.cache_resource
def get_openai_client():
    return OpenAI(api_key="sk-Yl6f8feb96b321543d62bd02fe96d98d5130025a358UUcBL", base_url="https://api.gptsapi.net/v1")

client = get_openai_client()

# File to store chat history
HISTORY_FILE = "chat_history.json"

# Function to load chat history
def load_chat_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are a helpful assistant"}]

# Function to save chat history
def save_chat_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

# Streamlit app title
st.title("🤖️ 江流儿的Chatbot")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Display chat history
for message in st.session_state.messages[1:]:  # Skip the system message
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message to conversation history
    st.session_state.messages.append({"role": "user", "content": user_input})
    save_chat_history(st.session_state.messages)
    
    with st.chat_message("user"):
        st.write(user_input)

    # Make API call to OpenAI
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=st.session_state.messages,
            stream=False
        )

    # Append assistant response to conversation history
    assistant_response = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    save_chat_history(st.session_state.messages)
    
    with st.chat_message("assistant"):
        st.write(assistant_response)

# Option to clear chat history
if st.button("Clear Chat History"):
    st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant"}]
    save_chat_history(st.session_state.messages)
    st.experimental_rerun()