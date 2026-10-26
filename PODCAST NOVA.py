
import os
import streamlit as st

st.set_page_config(
    page_title="Podcast Nova",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Podcast Nova")
st.caption("Your AI Podcast Studio — educational simulations")

st.info(
    "AI-generated conversations are simulations, "
    "not real interviews or recordings."
)

# Upload the host's photograph
st.subheader("1. Become the host")

photo = st.file_uploader(
    "Upload your photo",
    type=["jpg", "jpeg", "png"]
)

if photo:
    st.image(photo, caption="Your podcast host",
             width=220)

# Choose a guest
st.subheader("2. Choose your AI guest")

guest = st.selectbox(
    "Who would you like to interview?",
    ["Albert Einstein", "Isaac Newton"]
)

st.caption(
    "The guest is an AI-generated educational "
    "simulation based on historical knowledge."
)

# Store interview messages during the session
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_guest" not in st.session_state:
    st.session_state.last_guest = guest

if st.session_state.last_guest != guest:
    st.session_state.messages = []
    st.session_state.last_guest = guest

st.subheader("3. Start your interview")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

question = st.chat_input(
    "Ask your guest a question..."
)

def answer_guest(guest_name, history, question_text):
    # Read the API key from Streamlit Secrets first.
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        st.error(
            "Gemini API key not found. "
            "Check your Streamlit Secrets settings."
        )
        return "Please configure your Gemini API key and try again."

    try:
        from google import genai

        client = genai.Client(api_key=api_key)

        transcript = "\n".join(
            f'{m["role"]}: {m["content"]}'
            for m in history[-8:]
        )

        prompt = f"""
You are an educational AI simulation of {guest_name}
participating in a podcast interview.

Be engaging, natural, accurate, and concise.
Do not claim to be the real person or invent
private memories or conversations.

Previous conversation:
{transcript}

Host's question:
{question_text}

Answer as the simulated guest in 2-5 sentences.
"""

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )

        if response.text:
            return response.text

        return "Gemini returned an empty response. Please try again."

    except Exception as e:
        st.error(
            f"Gemini request failed: {type(e).__name__}: {e}"
        )
        return (
            "Sorry, I couldn't generate an answer. "
            "Please check the error above."
        )

