import streamlit as st
import replicate
import requests
import base64
import io
import os
from PIL import Image

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Image Editor",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

/* Main background */
.stApp {
    background: radial-gradient(ellipse at top left, #1a0a2e 0%, #0a0a0f 50%, #0d1a0a 100%);
    min-height: 100vh;
}

/* Hero title */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #34d399, #f472b6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    font-size: 1rem;
    color: #6b6a80;
    font-weight: 300;
    letter-spacing: 0.04em;
}

/* Cards */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 1.5rem;
    backdrop-filter: blur(12px);
}

/* Prompt suggestions */
.prompt-chip {
    display: inline-block;
    background: rgba(167,139,250,0.12);
    border: 1px solid rgba(167,139,250,0.3);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.78rem;
    color: #a78bfa;
    margin: 3px;
    cursor: pointer;
    transition: all 0.2s;
}

.prompt-chip:hover {
    background: rgba(167,139,250,0.25);
}

/* Image containers */
.img-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #6b6a80;
    margin-bottom: 0.5rem;
}

/* Status badge */
.status-processing {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.3);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 0.82rem;
    color: #34d399;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background: rgba(10, 10, 15, 0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.07) !important;
}

section[data-testid="stSidebar"] .stMarkdown p {
    color: #9ca3af;
    font-size: 0.85rem;
}

/* Buttons */
.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    background: linear-gradient(135deg, #7c3aed, #059669) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 2rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
}

.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(124,58,237,0.35) !important;
}

/* Text input */
.stTextArea textarea {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.95rem !important;
}

.stTextArea textarea:focus {
    border-color: rgba(167,139,250,0.5) !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}

/* Slider */
.stSlider [data-baseweb="slider"] {
    padding-top: 1rem;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 2px dashed rgba(167,139,250,0.3) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}

/* Select box */
.stSelectbox [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.05) !important;
    border-color: rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
}

/* Divider */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* Success/info boxes */
.stSuccess, .stInfo {
    background: rgba(52,211,153,0.08) !important;
    border: 1px solid rgba(52,211,153,0.2) !important;
    border-radius: 10px !important;
    color: #34d399 !important;
}

/* History section */
.history-thumb {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
}

/* Spinner */
.stSpinner > div {
    border-top-color: #a78bfa !important;
}

/* Download button */
[data-testid="stDownloadButton"] button {
    background: rgba(52,211,153,0.15) !important;
    border: 1px solid rgba(52,211,153,0.4) !important;
    color: #34d399 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    width: 100% !important;
}

[data-testid="stDownloadButton"] button:hover {
    background: rgba(52,211,153,0.25) !important;
}
</style>
""", unsafe_allow_html=True)

# ─── Helpers ───────────────────────────────────────────────────────────────────

def image_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def image_to_data_uri(img: Image.Image) -> str:
    return f"data:image/png;base64,{image_to_base64(img)}"

def pil_to_bytes(img: Image.Image) -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def url_to_pil(url: str) -> Image.Image:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    return Image.open(io.BytesIO(resp.content)).convert("RGB")

def bytes_to_pil(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGB")

def run_flux_edit(client, image: Image.Image, prompt: str, strength: float, aspect: str) -> Image.Image:
    """Use flux-kontext-pro for prompt-based image editing."""
    output = client.run(
        "black-forest-labs/flux-kontext-pro",
        input={
            "prompt": prompt,
            "input_image": image_to_data_uri(image),
            "output_format": "png",
            "safety_tolerance": 6,
            "aspect_ratio": aspect,
        }
    )
    if isinstance(output, list):
        result = output[0]
    else:
        result = output
    if hasattr(result, 'read'):
        return bytes_to_pil(result.read())
    if isinstance(result, str) and result.startswith("http"):
        return url_to_pil(result)
    return bytes_to_pil(bytes(result))

def run_remove_bg(client, image: Image.Image) -> Image.Image:
    """Remove background using rembg model."""
    output = client.run(
        "cjwbw/rembg:fb8af171cfa1616ddcf1242c093f9c46bcada5ad23d33ae76a054bc1485d555f",
        input={"image": image_to_data_uri(image)}
    )
    if hasattr(output, 'read'):
        return Image.open(io.BytesIO(output.read())).convert("RGBA")
    if isinstance(output, str) and output.startswith("http"):
        resp = requests.get(output, timeout=60)
        return Image.open(io.BytesIO(resp.content)).convert("RGBA")
    return Image.open(io.BytesIO(bytes(output))).convert("RGBA")

def run_upscale(client, image: Image.Image) -> Image.Image:
    """Upscale image using Real-ESRGAN."""
    output = client.run(
        "nightmareai/real-esrgan:f121d640bd286e1fdc67f9799164c1d5be36ff74576ee11c803ae5b665dd46aa",
        input={"image": image_to_data_uri(image), "scale": 2, "face_enhance": False}
    )
    if hasattr(output, 'read'):
        return bytes_to_pil(output.read())
    if isinstance(output, str) and output.startswith("http"):
        return url_to_pil(output)
    return bytes_to_pil(bytes(output))

# ─── Session State ─────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # list of (prompt, original_PIL, edited_PIL)
if "current_image" not in st.session_state:
    st.session_state.current_image = None

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <span style='font-family: Syne, sans-serif; font-size:1.3rem; font-weight:800; 
        background: linear-gradient(135deg,#a78bfa,#34d399); -webkit-background-clip:text;
        -webkit-text-fill-color:transparent; background-clip:text;'>🎨 AI Image Editor</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**⚙️ Edit Settings**")

    edit_mode = st.selectbox(
        "Mode",
        ["✏️ Prompt Edit (Flux)", "🪄 Remove Background", "⬆️ Upscale / Enhance"],
        help="Choose what kind of edit to perform"
    )

    strength = st.slider(
        "Edit Strength", 0.1, 1.0, 0.85, 0.05,
        help="How much to change the image (Prompt Edit only)"
    )

    aspect_ratio = st.selectbox(
        "Output Aspect Ratio",
        ["match_input_image", "1:1", "16:9", "9:16", "4:3", "3:4"],
        help="Output image ratio (Prompt Edit only)"
    )

    st.markdown("---")
    st.markdown("**💡 Prompt Ideas**")
    st.markdown("""
    <div>
    <span class='prompt-chip'>Make it cinematic</span>
    <span class='prompt-chip'>Oil painting style</span>
    <span class='prompt-chip'>Neon cyberpunk</span>
    <span class='prompt-chip'>Change sky to sunset</span>
    <span class='prompt-chip'>Make it black & white</span>
    <span class='prompt-chip'>Add snow</span>
    <span class='prompt-chip'>Anime style</span>
    <span class='prompt-chip'>Make it look vintage</span>
    <span class='prompt-chip'>Add dramatic lighting</span>
    <span class='prompt-chip'>Turn to watercolor</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.history:
        st.markdown("**🕓 Edit History**")
        for i, (p, orig, edited) in enumerate(reversed(st.session_state.history[-5:])):
            with st.expander(f"Edit {len(st.session_state.history)-i}: {p[:30]}..."):
                col1, col2 = st.columns(2)
                with col1:
                    st.image(orig, caption="Before", use_container_width=True)
                with col2:
                    st.image(edited, caption="After", use_container_width=True)

# ─── Main Layout ───────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding: 2rem 0 1.5rem 0;'>
    <div class='hero-title'>AI Image Editor</div>
    <div class='hero-sub'>Upload any photo · Write any prompt · Get realistic edits instantly</div>
</div>
""", unsafe_allow_html=True)

# ─── Upload ────────────────────────────────────────────────────────────────────
uploaded_file = st.file_uploader(
    "Drop your photo here",
    type=["jpg", "jpeg", "png", "webp"],
    help="Supports JPG, PNG, WebP"
)

if uploaded_file:
    original_image = Image.open(uploaded_file).convert("RGB")
    if st.session_state.current_image is None:
        st.session_state.current_image = original_image
else:
    original_image = None

st.markdown("---")

# ─── Editor ────────────────────────────────────────────────────────────────────
if original_image:
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown("<div class='img-label'>📷 Original</div>", unsafe_allow_html=True)
        st.image(original_image, use_container_width=True)
        st.caption(f"Size: {original_image.width} × {original_image.height}px")

    with col_right:
        st.markdown("<div class='img-label'>✨ Edited Result</div>", unsafe_allow_html=True)
        result_placeholder = st.empty()
        result_placeholder.markdown(
            "<div style='background:rgba(255,255,255,0.03);border:1px dashed rgba(255,255,255,0.1);"
            "border-radius:12px;height:300px;display:flex;align-items:center;justify-content:center;"
            "color:#3d3d55;font-size:0.9rem;'>Result will appear here</div>",
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ─── Prompt Box ─────────────────────────────────────────────────────────────
    if "✏️ Prompt Edit" in edit_mode:
        prompt = st.text_area(
            "✏️ Describe your edit",
            placeholder='e.g. "Make the sky dramatic with purple storm clouds and cinematic lighting"',
            height=100,
        )
    else:
        prompt = edit_mode  # use mode name as label for history

    run_col, _ = st.columns([1, 2])
    with run_col:
        run_btn = st.button("🚀 Apply Edit", use_container_width=True)

    # ─── Run Edit ───────────────────────────────────────────────────────────────
    if run_btn:
        if "✏️ Prompt Edit" in edit_mode and not prompt.strip():
            st.warning("⚠️ Please enter a prompt describing your edit.")
        else:
            try:
                api_token = st.secrets["REPLICATE_API_TOKEN"]
            except KeyError:
                st.error("❌ REPLICATE_API_TOKEN not found in st.secrets. Add it to .streamlit/secrets.toml")
                st.stop()

            client = replicate.Client(api_token=api_token)

            with st.spinner("🎨 AI is editing your image..."):
                try:
                    if "✏️ Prompt Edit" in edit_mode:
                        result_image = run_flux_edit(client, original_image, prompt, strength, aspect_ratio)
                    elif "Remove Background" in edit_mode:
                        result_image = run_remove_bg(client, original_image)
                        prompt = "Background Removed"
                    elif "Upscale" in edit_mode:
                        result_image = run_upscale(client, original_image)
                        prompt = "Upscaled 2x"

                    # Show result
                    with col_right:
                        result_placeholder.image(result_image, use_container_width=True)

                    # Save to history
                    st.session_state.history.append((prompt, original_image.copy(), result_image.copy()))

                    # Download button
                    img_bytes = pil_to_bytes(result_image)
                    st.success("✅ Edit complete!")
                    st.download_button(
                        label="⬇️ Download Result",
                        data=img_bytes,
                        file_name="ai_edited.png",
                        mime="image/png",
                        use_container_width=True,
                    )

                except Exception as e:
                    st.error(f"❌ Error during editing: {str(e)}")
                    st.info("💡 Tip: Make sure your Replicate API token is valid and has credits.")

else:
    # ─── Empty State ────────────────────────────────────────────────────────────
    st.markdown("""
    <div style='text-align:center; padding: 4rem 2rem;'>
        <div style='font-size:4rem; margin-bottom:1rem;'>📸</div>
        <div style='font-family: Syne, sans-serif; font-size:1.4rem; font-weight:700; 
        color:#3d3d55; margin-bottom:0.5rem;'>Upload a photo to get started</div>
        <div style='color:#2d2d40; font-size:0.9rem;'>
        Supports JPG, PNG, WebP · Powered by Flux Kontext Pro
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#2d2d40; font-size:0.78rem; padding: 1rem 0;'>
    Powered by <strong style='color:#a78bfa;'>Flux Kontext Pro</strong> via Replicate · 
    Built with <strong style='color:#34d399;'>Streamlit</strong>
</div>
""", unsafe_allow_html=True)
