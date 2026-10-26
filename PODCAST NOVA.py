
import os
import streamlit as st
from google import genai, types

# ----------------------------------
# PAGE SETTINGS
# ----------------------------------

st.set_page_config(
    page_title="Podcast Nova",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Podcast Nova")
st.subheader("Mini Search + AI Podcast Studio")
st.caption(
    "Explore public personalities, discover information, "
    "and learn from ideas that can change your life."
)

st.info(
    "AI-generated educational conversations. "
    "Not real interviews or endorsements."
)

# ----------------------------------
# HOST PHOTO
# ----------------------------------

st.subheader("1. Become the host")

photo = st.file_uploader(
    "Upload your host photo",
    type=["jpg", "jpeg", "png"]
)

if photo:
    st.image(
        photo,
        caption="Your podcast host",
        width=220
    )

# ----------------------------------
# SEARCH FOR ANY PERSON OR TOPIC
# ----------------------------------

st.subheader("2. Search the world")

guest = st.text_input(
    "Enter any public personality or topic",
    placeholder="e.g. Virat Kohli, Elon Musk, AI, space...",
    key="guest_search"
).strip()

st.caption(
    "Search names and topics without a fixed list. "
    "Answers can use Google Search when relevant."
)

# Reset conversation when search target changes
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_guest" not in st.session_state:
    st.session_state.last_guest = guest

if st.session_state.last_guest != guest:
    st.session_state.messages = []
    st.session_state.last_guest = guest

# ----------------------------------
# GEMINI + GOOGLE SEARCH
# ----------------------------------

def answer_guest(guest_name, history, question_text):
    # Get API key from Streamlit Secrets or environment
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        return (
            "Gemini API key not found. "
            "Check Streamlit Secrets."
        ), []

    try:
        client = genai.Client(api_key=api_key)

        transcript = "\n".join(
            f'{m["role"]}: {m["content"]}'
            for m in history[-8:]
        )

        prompt = f"""
You are Podcast Nova, an AI research assistant and
educational podcast conversation partner.

The user is exploring this person or topic:
{guest_name}

Use Google Search for relevant current information,
especially for recent news, achievements, records,
events, and facts that may have changed.

Answer the user's question using reliable information.
Clearly distinguish verified facts from uncertainty.
Never invent sources, quotations, private memories,
or private opinions. Do not claim to be the real person
or imply that they endorse this app.

If the subject is a public personality, explain their
public work, career, achievements, ideas, and impact.
If the subject is another topic, answer that topic directly.

Be engaging, useful to young people, and concise.
Use 2-6 sentences unless more detail is necessary.
If the answer cannot be verified, say so.

Previous conversation:
{transcript}

User's question:
{question_text}
"""

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[
                    types.Tool(
                        google_search=types.GoogleSearch()
                    )
                ]
            )
        )

        answer = response.text or (
            "No answer was returned. Please try again."
        )

        # Extract available Google Search source links
        sources = []
        candidates = getattr(response, "candidates", None) or []

        for candidate in candidates:
            metadata = getattr(
                candidate, "grounding_metadata", None
            )

            if not metadata:
                continue

            chunks = getattr(
                metadata, "grounding_chunks", None
            ) or []

            for chunk in chunks:
                web_source = getattr(chunk, "web", None)

                if not web_source:
                    continue

                uri = getattr(web_source, "uri", None)
                title_text = getattr(
                    web_source, "title", None
                ) or "Web source"

                if uri and uri.startswith(("https://", "http://")):
                    if not any(s["url"] == uri for s in sources):
                        sources.append({
                            "title": title_text,
                            "url": uri
                        })

        return answer, sources

    except Exception as e:
        st.error(
            f"Gemini request failed: {type(e).__name__}: {e}"
        )
        return (
            "Sorry, I couldn't generate an answer. "
            "Please try again or check the API configuration."
        ), []

# ----------------------------------
# DISPLAY CHAT HISTORY
# ----------------------------------

st.subheader("3. Ask anything")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

        if message.get("sources"):
            st.markdown("**Sources**")
            for source in message["sources"]:
                st.markdown(
                    f"- [{source['title']}]({source['url']})"
                )

# ----------------------------------
# PROCESS QUESTION
# ----------------------------------

question = st.chat_input(
    "Ask a question about your search..."
)

if question:
    if not guest:
        st.warning(
            "Enter a person or topic in the search box first."
        )
    else:
        user_message = {
            "role": "user",
            "content": question
        }

        st.session_state.messages.append(user_message)

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner(
                "Searching and preparing your answer..."
            ):
                answer, sources = answer_guest(
                    guest,
                    st.session_state.messages[:-1],
                    question
                )

            st.write(answer)

            if sources:
                st.markdown("**Sources**")
                for source in sources:
                    st.markdown(
                        f"- [{source['title']}]({source['url']})"
                    )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "sources": sources
        })

# ----------------------------------
# NEW INTERVIEW
# ----------------------------------

if st.button("Start a new interview"):
    st.session_state.messages = []
    st.rerun()

st.divider()
st.caption(
    "Podcast Nova | Search. Learn. Grow. "
    "AI-powered educational conversations."
)
