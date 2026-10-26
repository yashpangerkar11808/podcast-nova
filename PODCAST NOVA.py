
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
    api_key = os.getenv("GEMINI_API_KEY", "")

    # Try Gemini if an API key is configured.
    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)

            transcript = "\n".join(
                f'{m["role"]}: {m["content"]}'
                for m in history[-8:]
            )

            prompt = f"""
You are an educational AI simulation of
{guest_name} in a podcast interview.

Use accurate historical and scientific knowledge.
Never claim this is a real interview or actual
private thoughts. Clearly distinguish established
facts from speculation. Answer naturally and
concisely, like a podcast guest.

Previous conversation:
{transcript}

Host's new question: {question_text}

Answer as the simulated guest in 2-5 sentences.
"""

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            if response.text:
                return response.text

        except Exception:
            st.warning(
                "AI service unavailable. Showing a "
                "demo response instead."
            )

    # Offline demo mode: no API key required.
    if "Einstein" in guest_name:
        return (
            "Welcome to this educational simulation! "
            "One of the most important ideas in physics "
            "is that our understanding of space and time "
            "depends on how we measure motion. "
            "Let's explore your question further: "
            + question_text
        )

    return (
        "Welcome to this educational simulation! "
        "My work explored motion, forces, and gravity. "
        "Scientific ideas become clearer when we examine "
        "evidence and test explanations. Let's discuss: "
        + question_text
    )

if question:
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Your guest is preparing an answer..."):
            answer = answer_guest(
                guest,
                st.session_state.messages[:-1],
                question
            )
        st.write(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

if st.button("Start a new interview"):
    st.session_state.messages = []
    st.rerun()
