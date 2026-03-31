import os
import base64
import fitz  # PyMuPDF
from dotenv import load_dotenv
from groq import Groq
import streamlit as st
from PIL import Image
import io

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ─── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Swagato AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Premium Apple-like CSS ─────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e8ed !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

[data-testid="stAppViewContainer"] > .main {
    background: #0a0a0f !important;
}

[data-testid="stHeader"] { background: transparent !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #111116 !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem !important;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Chat container ── */
.chat-wrapper {
    max-width: 780px;
    margin: 0 auto;
    padding: 2rem 1rem 9rem;
}

/* ── Message bubbles ── */
.msg-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    margin-bottom: 2rem;
    animation: fadeSlideUp 0.35s cubic-bezier(0.16,1,0.3,1) forwards;
    opacity: 0;
}

.msg-row.user { flex-direction: row-reverse; }

@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}

.avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: -0.3px;
}

.avatar.ai {
    background: linear-gradient(135deg, #2c2c3e, #1e1e2e);
    border: 1px solid rgba(255,255,255,0.1);
    color: #a78bfa;
}

.avatar.user {
    background: linear-gradient(135deg, #1d4ed8, #7c3aed);
    color: #fff;
}

.bubble {
    max-width: 78%;
    padding: 14px 18px;
    border-radius: 18px;
    font-size: 15px;
    line-height: 1.65;
    letter-spacing: -0.1px;
}

.bubble.ai {
    background: #16161f;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 4px 18px 18px 18px;
    color: #d4d4dc;
}

.bubble.user {
    background: linear-gradient(135deg, #1d4ed8, #4f46e5);
    border-radius: 18px 4px 18px 18px;
    color: #fff;
    box-shadow: 0 4px 24px rgba(79,70,229,0.3);
}

/* ── Attachments preview ── */
.attachment-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 5px 10px;
    font-size: 12px;
    color: #a0a0b0;
    margin-bottom: 8px;
}

/* ── Input bar ── */
.input-area {
    position: fixed;
    bottom: 0;
    left: 0; right: 0;
    padding: 1.25rem 1rem 1.5rem;
    background: linear-gradient(to top, #0a0a0f 80%, transparent);
    z-index: 999;
}

.input-inner {
    max-width: 780px;
    margin: 0 auto;
    background: #17171f;
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    display: flex;
    align-items: flex-end;
    gap: 10px;
    padding: 10px 14px;
    box-shadow: 0 0 0 1px rgba(255,255,255,0.04), 0 20px 60px rgba(0,0,0,0.5);
    transition: border-color 0.2s;
}

.input-inner:focus-within {
    border-color: rgba(99,102,241,0.5);
    box-shadow: 0 0 0 3px rgba(99,102,241,0.08), 0 20px 60px rgba(0,0,0,0.5);
}

/* ── Streamlit widget overrides ── */
.stTextArea textarea, .stTextInput input {
    background: transparent !important;
    border: none !important;
    color: #e8e8ed !important;
    font-size: 15px !important;
    font-family: 'Inter', sans-serif !important;
    box-shadow: none !important;
    outline: none !important;
    resize: none !important;
    padding: 0 !important;
}

.stTextArea textarea:focus, .stTextInput input:focus {
    box-shadow: none !important;
    border: none !important;
}

.stTextArea > label, .stTextInput > label,
.stFileUploader > label { display: none !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.1s !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }
.stButton > button:active { transform: translateY(0) !important; }

/* ── Download / secondary buttons ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #a0a0b0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    padding: 6px 14px !important;
    font-family: 'Inter', sans-serif !important;
}

/* ── Toggle ── */
.stToggle label { color: #a0a0b0 !important; font-size: 13px !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px dashed rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    padding: 12px !important;
}

[data-testid="stFileUploader"] * { color: #7070a0 !important; font-size: 13px !important; }

/* ── Sidebar elements ── */
.sidebar-logo {
    font-size: 20px;
    font-weight: 600;
    color: #e8e8ed;
    letter-spacing: -0.5px;
    margin-bottom: 0.25rem;
    display: flex;
    align-items: center;
    gap: 8px;
}

.sidebar-sub {
    font-size: 12px;
    color: #50506a;
    margin-bottom: 1.5rem;
}

.new-chat-btn {
    width: 100%;
    background: rgba(99,102,241,0.12) !important;
    color: #818cf8 !important;
    border: 1px solid rgba(99,102,241,0.2) !important;
    border-radius: 10px !important;
    padding: 8px 14px !important;
    font-size: 14px !important;
    cursor: pointer;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 1.5rem;
    transition: background 0.2s;
}

.sidebar-section {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #40404f;
    margin-bottom: 0.6rem;
    padding: 0 4px;
}

.history-item {
    padding: 8px 10px;
    border-radius: 8px;
    font-size: 13px;
    color: #70708a;
    cursor: pointer;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    transition: background 0.15s, color 0.15s;
}

.history-item:hover { background: rgba(255,255,255,0.05); color: #b0b0c8; }

/* ── Welcome screen ── */
.welcome {
    max-width: 520px;
    margin: 6rem auto 0;
    text-align: center;
    padding: 2rem;
}

.welcome h1 {
    font-size: 2.6rem;
    font-weight: 600;
    color: #e8e8ed;
    letter-spacing: -1.5px;
    line-height: 1.1;
    margin-bottom: 0.6rem;
}

.welcome p {
    font-size: 16px;
    color: #50506a;
    line-height: 1.6;
    margin-bottom: 2.5rem;
}

.starter-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    text-align: left;
}

.starter-card {
    background: #14141c;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 16px;
    cursor: pointer;
    transition: border-color 0.2s, background 0.2s;
}

.starter-card:hover {
    border-color: rgba(99,102,241,0.35);
    background: #1a1a26;
}

.starter-icon { font-size: 20px; margin-bottom: 6px; }
.starter-title { font-size: 13px; font-weight: 500; color: #c0c0d8; margin-bottom: 2px; }
.starter-sub { font-size: 12px; color: #50506a; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

/* ── Image preview ── */
.msg-image { border-radius: 12px; max-width: 100%; margin-bottom: 8px; display: block; }

/* ── Spinner ── */
.stSpinner > div { border-top-color: #6366f1 !important; }

/* ── Selectbox ── */
.stSelectbox select, [data-baseweb="select"] {
    background: #17171f !important;
    border-color: rgba(255,255,255,0.08) !important;
    color: #e8e8ed !important;
    font-size: 13px !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ────────────────────────────────────────────────────────────────────

MAX_PDF_BYTES = 5 * 1024 * 1024  # 5 MB

def encode_image_base64(image_bytes: bytes, mime: str = "image/jpeg") -> str:
    return base64.b64encode(image_bytes).decode("utf-8")

def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF (fitz). Falls back to page-by-page."""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        texts = []
        for i, page in enumerate(doc):
            texts.append(f"[Page {i+1}]\n{page.get_text()}")
        doc.close()
        return "\n\n".join(texts) if texts else "Could not extract text from this PDF."
    except Exception as e:
        return f"PDF extraction error: {e}"

def truncate_text(text: str, max_chars: int = 12000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[...truncated — {len(text) - max_chars} characters omitted...]"

def build_groq_messages(history, memory_enabled: bool, user_text: str,
                         image_b64: str | None, image_mime: str | None,
                         pdf_text: str | None):
    system = {
        "role": "system",
        "content": (
            "You are a helpful, knowledgeable AI assistant. "
            "Your founder is Swagato Bhattacharya (swagatobhattacharya576@gmail.com). "
            "Be concise, clear, and friendly. When analyzing images or PDFs, be thorough."
        ),
    }

    # Build the current user message content
    content_parts = []

    if image_b64 and image_mime:
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:{image_mime};base64,{image_b64}"},
        })

    if pdf_text:
        combined = f"[PDF Content]\n{pdf_text}\n\n[User Question]\n{user_text}" if user_text else f"[PDF Content]\n{pdf_text}"
        content_parts.append({"type": "text", "text": combined})
    else:
        content_parts.append({"type": "text", "text": user_text or "Please analyse the attached file."})

    current_user_msg = {"role": "user", "content": content_parts}

    if memory_enabled:
        past = []
        for m in history:
            if m["role"] in ("user", "assistant") and isinstance(m["content"], str):
                past.append({"role": m["role"], "content": m["content"]})
        return [system] + past + [current_user_msg]
    else:
        return [system, current_user_msg]


# ─── Session State ───────────────────────────────────────────────────────────────
defaults = {
    "chat_history": [],        # list of {role, content, image_b64, image_mime, pdf_name}
    "sessions": [],            # list of session snapshots for sidebar history
    "session_name": "New Chat",
    "pending_starter": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
        <div class='sidebar-logo'>✦ Swagato AI</div>
        <div class='sidebar-sub'>Powered by Llama 3.3 · Groq</div>
    """, unsafe_allow_html=True)

    if st.button("＋  New Chat", use_container_width=True):
        if st.session_state.chat_history:
            st.session_state.sessions.append({
                "name": st.session_state.chat_history[0]["content"][:40] + "…"
                        if st.session_state.chat_history else "Chat",
                "history": st.session_state.chat_history.copy(),
            })
        st.session_state.chat_history = []
        st.session_state.session_name = "New Chat"
        st.rerun()

    st.markdown("---")

    # Settings
    st.markdown("<div class='sidebar-section'>Settings</div>", unsafe_allow_html=True)
    memory_enabled = st.toggle("Chat Memory", value=True)

    model_choice = st.selectbox(
        "Model",
        ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
        index=0,
        label_visibility="visible",
    )

    st.markdown("---")

    # History
    if st.session_state.sessions:
        st.markdown("<div class='sidebar-section'>Recent Chats</div>", unsafe_allow_html=True)
        for i, sess in enumerate(reversed(st.session_state.sessions[-10:])):
            st.markdown(f"<div class='history-item'>💬 {sess['name']}</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Download
    if st.session_state.chat_history:
        chat_text = "\n\n".join(
            f"{'You' if m['role'] == 'user' else 'AI'}: {m['content']}"
            for m in st.session_state.chat_history
            if isinstance(m["content"], str)
        )
        st.download_button("⬇ Export Chat", data=chat_text,
                           file_name="swagato_ai_chat.txt", mime="text/plain",
                           use_container_width=True)

    st.markdown("<div style='margin-top:2rem;font-size:11px;color:#303040;text-align:center;'>© 2025 Swagato Bhattacharya</div>", unsafe_allow_html=True)


# ─── Main Chat Area ───────────────────────────────────────────────────────────────

# Welcome screen
if not st.session_state.chat_history:
    st.markdown("""
    <div class='welcome'>
        <h1>Good to see you.</h1>
        <p>Ask anything — upload images or PDFs up to 5 MB<br>and let AI do the heavy lifting.</p>
        <div class='starter-grid'>
            <div class='starter-card' onclick='void(0)'>
                <div class='starter-icon'>🖼️</div>
                <div class='starter-title'>Analyze an image</div>
                <div class='starter-sub'>Upload and ask anything</div>
            </div>
            <div class='starter-card'>
                <div class='starter-icon'>📄</div>
                <div class='starter-title'>Summarize a PDF</div>
                <div class='starter-sub'>Up to 5 MB supported</div>
            </div>
            <div class='starter-card'>
                <div class='starter-icon'>💡</div>
                <div class='starter-title'>Brainstorm ideas</div>
                <div class='starter-sub'>Get creative instantly</div>
            </div>
            <div class='starter-card'>
                <div class='starter-icon'>✍️</div>
                <div class='starter-title'>Write & edit</div>
                <div class='starter-sub'>Essays, emails, code</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render chat history
    st.markdown("<div class='chat-wrapper'>", unsafe_allow_html=True)
    for msg in st.session_state.chat_history:
        role = msg["role"]
        css_class = "user" if role == "user" else "ai"
        avatar_label = "You" if role == "user" else "AI"

        st.markdown(f"""
        <div class='msg-row {css_class}'>
            <div class='avatar {css_class}'>{avatar_label[0]}</div>
            <div>
        """, unsafe_allow_html=True)

        # Attachment chips
        if msg.get("image_mime"):
            st.markdown("<div class='attachment-chip'>🖼️ Image attached</div>", unsafe_allow_html=True)
        if msg.get("pdf_name"):
            st.markdown(f"<div class='attachment-chip'>📄 {msg['pdf_name']}</div>", unsafe_allow_html=True)

        # Bubble
        content = msg["content"] if isinstance(msg["content"], str) else ""
        st.markdown(f"<div class='bubble {css_class}'>{content}</div>", unsafe_allow_html=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─── Input Area ──────────────────────────────────────────────────────────────────
st.markdown("<div class='input-area'><div class='input-inner'>", unsafe_allow_html=True)

col_upload, col_text, col_send = st.columns([1, 8, 1])

with col_upload:
    uploaded_file = st.file_uploader(
        "Attach",
        type=["jpg", "jpeg", "png", "webp", "gif", "pdf"],
        label_visibility="collapsed",
        help="Upload an image or PDF (max 5 MB)",
    )

with col_text:
    user_input = st.text_input(
        "Message",
        placeholder="Message Swagato AI…",
        label_visibility="collapsed",
        key="user_msg",
    )

with col_send:
    send_clicked = st.button("↑", use_container_width=True)

st.markdown("</div></div>", unsafe_allow_html=True)

# ─── Handle Send ─────────────────────────────────────────────────────────────────
if send_clicked and (user_input or uploaded_file):
    image_b64, image_mime, pdf_text, pdf_name = None, None, None, None
    error_msg = None

    # ── Process file ──
    if uploaded_file:
        file_bytes = uploaded_file.read()

        if len(file_bytes) > MAX_PDF_BYTES:
            error_msg = f"⚠️ File too large ({len(file_bytes)/1024/1024:.1f} MB). Maximum allowed is 5 MB."
        else:
            fname = uploaded_file.name.lower()
            if fname.endswith(".pdf"):
                pdf_text = truncate_text(extract_pdf_text(file_bytes))
                pdf_name = uploaded_file.name
            else:
                # It's an image
                mime_map = {
                    "jpg": "image/jpeg", "jpeg": "image/jpeg",
                    "png": "image/png", "webp": "image/webp", "gif": "image/gif",
                }
                ext = fname.rsplit(".", 1)[-1]
                image_mime = mime_map.get(ext, "image/jpeg")
                image_b64 = encode_image_base64(file_bytes, image_mime)

    if error_msg:
        st.error(error_msg)
    else:
        # ── Append user message to history ──
        display_text = user_input or ("Analyse this PDF." if pdf_text else "Describe this image.")
        st.session_state.chat_history.append({
            "role": "user",
            "content": display_text,
            "image_b64": image_b64,
            "image_mime": image_mime,
            "pdf_name": pdf_name,
        })

        # ── Build messages for Groq ──
        messages = build_groq_messages(
            history=st.session_state.chat_history[:-1],  # exclude the one we just appended
            memory_enabled=memory_enabled,
            user_text=user_input,
            image_b64=image_b64,
            image_mime=image_mime,
            pdf_text=pdf_text,
        )

        # ── Call Groq API ──
        with st.spinner("Thinking…"):
            try:
                response = client.chat.completions.create(
                    model=model_choice,
                    messages=messages,
                    max_tokens=2048,
                    temperature=0.7,
                )
                bot_reply = response.choices[0].message.content
            except Exception as e:
                bot_reply = f"⚠️ API error: {e}"

        st.session_state.chat_history.append({
            "role": "assistant",
            "content": bot_reply,
        })

        st.rerun()
