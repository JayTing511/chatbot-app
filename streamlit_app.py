import streamlit as st
from openai import OpenAI
import json
import os
from datetime import datetime

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
            try:
                # Try to load as a single JSON object (new format)
                data = json.load(f)
                if isinstance(data, dict) and "conversations" in data:
                    return data
                else:
                    # If it's not in the new format, convert it
                    return {"conversations": [{"id": "legacy", "timestamp": datetime.now().isoformat(), "messages": data}]}
            except json.JSONDecodeError:
                # If it fails, try to load as JSON Lines (old format)
                f.seek(0)
                messages = [json.loads(line) for line in f if line.strip()]
                return {"conversations": [{"id": "legacy", "timestamp": datetime.now().isoformat(), "messages": messages}]}
    return {"conversations": []}

# Function to save chat history
def save_chat_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# Initialize session state
if "history" not in st.session_state:
    st.session_state.history = load_chat_history()

if "current_conversation" not in st.session_state:
    st.session_state.current_conversation = []

if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")

# Streamlit app title
st.title("🤖️ 江流儿的Chatbot")

# Display current conversation
for message in st.session_state.current_conversation:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Append user message to current conversation
    user_message = {"role": "user", "content": user_input}
    st.session_state.current_conversation.append(user_message)
    
    with st.chat_message("user"):
        st.write(user_input)

    # Make API call to OpenAI
    with st.spinner("Thinking..."):
        response = client.chat.completions.create(
            model="claude-3-5-sonnet-20240620",
            messages=st.session_state.current_conversation,
            stream=False
        )

    # Append assistant response to current conversation
    assistant_message = {"role": "assistant", "content": response.choices[0].message.content}
    st.session_state.current_conversation.append(assistant_message)
    
    with st.chat_message("assistant"):
        st.write(assistant_message["content"])

    # Update history
    current_conversation = {
        "id": st.session_state.conversation_id,
        "timestamp": datetime.now().isoformat(),
        "messages": st.session_state.current_conversation
    }
    
    # Check if the conversation already exists in history
    existing_conv = next((conv for conv in st.session_state.history["conversations"] if conv["id"] == st.session_state.conversation_id), None)
    
    if existing_conv:
        existing_conv.update(current_conversation)
    else:
        st.session_state.history["conversations"].append(current_conversation)
    
    # Save updated history
    save_chat_history(st.session_state.history)

# Option to start a new conversation
if st.button("Start New Conversation"):
    st.session_state.conversation_id = datetime.now().strftime("%Y%m%d%H%M%S")
    st.session_state.current_conversation = []
    st.rerun()

# Option to view conversation history
if st.button("View Conversation History"):
    st.write("Conversation History:")
    for conv in st.session_state.history["conversations"]:
        st.write(f"Conversation ID: {conv['id']}, Timestamp: {conv['timestamp']}")
        if st.button(f"View Conversation {conv['id']}"):
            st.write(json.dumps(conv['messages'], indent=2))