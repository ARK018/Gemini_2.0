import asyncio
import streamlit as st
from google import genai
import os  # Import the os module to access environment variables

# Get the Google API key from the environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Ensure that the API key is present
if not GOOGLE_API_KEY:
    st.error("Google API key is not set. Please set it as an environment variable.")
    st.stop()  # Stop further execution if the API key is missing

# Initialize the GenAI client with the API key
client = genai.Client(api_key=GOOGLE_API_KEY, http_options={'api_version': 'v1alpha'})
MODEL = "gemini-2.0-flash-exp"

config = {
    "generation_config": {"response_modalities": ["TEXT"]}
}

# Streamlit App
st.set_page_config(page_title="AI Chatbot", layout="centered")
st.title("🤖 AI Chatbot")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if message["sender"] == "user":
        st.markdown(f"**You:** {message['text']}")
    else:
        st.markdown(f"**AI:** {message['text']}")

# Input box for user messages
with st.form(key="chat_form", clear_on_submit=True):
    user_message = st.text_input("Enter your message:", placeholder="Type here...")
    submit_button = st.form_submit_button("Send")

# Handling the user message and sending to the model
if submit_button and user_message.strip():
    # Display the user message
    st.session_state.messages.append({"sender": "user", "text": user_message})

    # Create an empty container to hold the AI response
    response_container = st.empty()

    # Async function to get response from GenAI and stream it
    async def get_ai_response(message):
        response = ""  # Initialize response to accumulate text
        async with client.aio.live.connect(model=MODEL, config=config) as session:
            await session.send(message, end_of_turn=True)
            turn = session.receive()
            async for chunk in turn:
                if chunk.text is not None:
                    response += chunk.text  # Accumulate the response text
                    # Update the response container incrementally as it comes in
                    response_container.markdown(f"**AI:** {response}")

        # Once response is fully received, append it to session history
        st.session_state.messages.append({"sender": "ai", "text": response})

    # Run the async function using asyncio
    asyncio.run(get_ai_response(user_message))

    # No need for st.rerun(), as Streamlit automatically updates the interface
