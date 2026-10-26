
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
You are Podcast Nova, a helpful research and learning assistant.

Research the following topic: {topic}

Instructions:
- Explain the topic clearly and accurately.
- Use headings and bullet points where useful.
- For a person, cover background, achievements, ideas,
  challenges, and lessons people can learn.
- For other topics, explain the meaning, important facts,
  practical applications, and key takeaways.
- Use current information when available through web search.
- Do not invent facts, quotations, or sources.
- Distinguish verified facts from uncertainty.
- Do not pretend to be the real person being discussed.

Finish with a short section titled "Key Takeaways".
"""

        with st.spinner("🔎 Researching your topic..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={
                    "tools": [
                        {"google_search": {}}
                    ]
                }
            )

        answer = response.text or "No answer was returned. Please try again."

        sources = []
        candidates = getattr(response, "candidates", None) or []

        if candidates:
            metadata = getattr(
                candidates[0], "grounding_metadata", None
            )

            chunks = getattr(
                metadata, "grounding_chunks", None
            ) or []

            for chunk in chunks:
                web_info = getattr(chunk, "web", None)

                if web_info:
                    title = getattr(web_info, "title", None)
                    uri = getattr(web_info, "uri", None)

                    if uri and uri.startswith(("https://", "http://")):
                        sources.append({
                            "title": title or uri,
                            "url": uri
                        })

        # Remove duplicate source URLs
        unique_sources = []
        seen_urls = set()

        for source in sources:
            if source["url"] not in seen_urls:
                seen_urls.add(source["url"])
                unique_sources.append(source)

        st.session_state.nova_history.insert(
            0,
            {
                "topic": topic,
                "answer": answer,
                "sources": unique_sources
            }
        )

    except Exception as error:
        st.error(
            "The research request failed. Check your API key, "
            "Gemini API access, model availability, and package version."
        )
        with st.expander("Technical error details"):
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
