import streamlit as st
import requests
import json

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit UI setup
st.title("Chatbot Demo")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = None

def stream_chat_response(message: str):
    url = "http://localhost:8000/chat"
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": message})
    
    # Display all messages including the new user message
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Create a new message container for the assistant's response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            payload = {
                "message": message,
                "session_id": st.session_state.session_id
            }

            with requests.post(url, json=payload, stream=True) as r:
                r.raise_for_status()
                
                for line in r.iter_lines(decode_unicode=True):
                    if line and line.startswith("data: "):
                        try:
                            # Remove the "data: " prefix
                            chunk_text = line[6:]  # Skip "data: "
                            
                            # Try to parse as JSON first
                            try:
                                chunk_data = json.loads(chunk_text)
                                # If it's a session ID message
                                if isinstance(chunk_data, dict) and "session_id" in chunk_data:
                                    st.session_state.session_id = chunk_data["session_id"]
                                    logger.info(f"Received session ID: {chunk_data['session_id']}")
                                    continue
                                # If it's a regular message in JSON format
                                chunk = chunk_data if isinstance(chunk_data, str) else str(chunk_data)
                            except json.JSONDecodeError:
                                # If not JSON, treat as plain text
                                chunk = chunk_text

                            full_response += chunk
                            # Update the message placeholder with the accumulated response
                            message_placeholder.markdown(full_response)
                            logger.info(f"Displayed chunk: {chunk}")
                            
                        except Exception as e:
                            logger.error(f"Error processing chunk: {e}")
                            continue

            # Add the complete response to chat history
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except requests.RequestException as e:
            st.error(f"Error communicating with the server: {e}")
            logger.error(f"Request error: {e}")
            message_placeholder.error("Sorry, I encountered an error while processing your request.")

# Chat input
user_message = st.chat_input("Enter your message")

# Handle new user input
if user_message:
    stream_chat_response(user_message)