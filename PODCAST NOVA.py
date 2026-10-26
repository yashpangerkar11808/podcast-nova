
import os
import streamlit as st
from google import genai

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Podcast Nova",
    page_icon="🎙️",
    layout="wide"
)

# ---------------- API KEY ----------------
try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    API_KEY = os.getenv("GEMINI_API_KEY")

# ---------------- DESIGN ----------------
st.title("🎙️ Podcast Nova")
st.subheader("Explore ideas. Learn from people. Discover more.")

st.markdown(
    """
    Search for any public personality, inventor, entrepreneur,
    historical figure, technology, or topic.

    Get an AI-powered explanation with web-grounded information
    and source links when Google Search grounding is available.
    """
)

st.divider()

# ---------------- SESSION HISTORY ----------------
if "nova_history" not in st.session_state:
    st.session_state.nova_history = []

# ---------------- SEARCH FUNCTION ----------------

def research_topic(topic):
    if not API_KEY:
        st.error(
            "API key not found. Add GEMINI_API_KEY "
            "in your Streamlit app's Secrets settings."
        )
        return

    try:
        client = genai.Client(api_key=API_KEY)

        prompt = f"""
        You are Podcast Nova, a helpful AI research assistant.

        Research this topic: {topic}

        Give a clear, accurate, easy-to-understand answer.
        Use headings and bullet points where useful.
        Focus on useful facts and recent information.
        Use Google Search to verify information.
        Never invent facts or sources.
        """

        with st.spinner("Podcast Nova is researching..."):
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt,
                tools=[{"type": "google_search"}]
            )

        answer = interaction.output_text or "No answer was returned."
        sources = []

        for step in interaction.steps:
            if step.type == "model_output":
                for block in step.content:
                    if block.type == "text" and block.annotations:
                        for citation in block.annotations:
                            if citation.type == "url_citation":
                                url = citation.url
                                if url:
                                    sources.append({
                                        "title": citation.title or url,
                                        "url": url
                                    })

        unique_sources = []
        seen_urls = set()

        for source in sources:
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                unique_sources.append(source)

        if "nova_history" not in st.session_state:
            st.session_state.nova_history = []

        st.session_state.nova_history.insert(
            0,
            {
                "topic": topic,
                "answer": answer,
                "sources": unique_sources
            }
        )

    except Exception as error:
        st.error("Podcast Nova could not complete the research.")
        st.code(str(error))



# ---------------- SEARCH BOX ----------------
with st.form("nova_search_form"):
    topic = st.text_input(
        "What do you want to explore?",
        placeholder="Try: Elon Musk, A. P. J. Abdul Kalam, AI, space..."
    )

    submitted = st.form_submit_button(
        "🔍 Research Topic",
        use_container_width=True
    )

if submitted:
    if topic.strip():
        research_topic(topic.strip())
    else:
        st.warning("Please enter a person or topic first.")

# ---------------- RESULTS ----------------
if st.session_state.nova_history:
    st.divider()
    st.header("📚 Your Research")

    for index, item in enumerate(st.session_state.nova_history):
        with st.expander(
            f"📖 {item['topic']}",
            expanded=(index == 0)
        ):
            st.markdown(item["answer"])

            if item["sources"]:
                st.subheader("🔗 Web Sources")

                for source in item["sources"]:
                    st.markdown(
                        f"- [{source['title']}]({source['url']})"
                    )
            else:
                st.caption(
                    "No source links were returned for this response. "
                    "Verify important claims independently."
                )

    if st.button("🗑️ Clear Research History"):
        st.session_state.nova_history = []
        st.rerun()

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "Podcast Nova • AI-assisted learning and research. "
    "Always verify important information with reliable sources."
)
