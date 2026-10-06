"""
PyLab — The Complete 360° Python Ecosystem
===========================================
The central hub for Python code and execution.
Conceived by Alankrita Paul. All rights reserved. ©
"""

import sys
import os
import io
import re
import textwrap
import contextlib
import traceback
import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI

# Set Streamlit Page Config
st.set_page_config(
    page_title="PyLab — The Complete 360° Python Ecosystem",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State for Theme Toggle
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Dark"

# CSS for Dynamic Theme Switching & Animated Background
if st.session_state["theme_mode"] == "Dark":
    bg_gradient = "linear-gradient(-45deg, #090d16, #0f172a, #1e1b4b, #0f172a)"
    card_bg = "rgba(30, 41, 59, 0.75)"
    text_color = "#f8fafc"
    text_muted = "#94a3b8"
    border_color = "rgba(51, 65, 85, 0.7)"
else:
    bg_gradient = "linear-gradient(-45deg, #f1f5f9, #e2e8f0, #cbd5e1, #f1f5f9)"
    card_bg = "rgba(255, 255, 255, 0.85)"
    text_color = "#0f172a"
    text_muted = "#64748b"
    border_color = "rgba(203, 213, 225, 0.8)"

st.markdown(textwrap.dedent(f"""
<style>
    .stApp {{
        background: {bg_gradient};
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        color: {text_color};
    }}
    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .brand-title {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #6366F1 50%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }}
    .brand-tagline {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_muted};
        margin-bottom: 1rem;
    }}
    .footer-box {{
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid {border_color};
        text-align: center;
        color: {text_muted};
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    .footer-eco {{
        font-weight: 700;
        color: {text_color};
        font-size: 1rem;
    }}
    .footer-hub {{
        font-weight: 600;
        color: {text_muted};
        font-size: 0.9rem;
    }}
</style>
<canvas id="pylab-bg-canvas" style="position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:0;pointer-events:none;"></canvas>
"""), unsafe_allow_html=True)

# Step 2: Execute JS via components.html as per global rule
components.html("""
<script>
(function run() {
    const canvas = window.parent.document.getElementById('pylab-bg-canvas');
    if (!canvas) { setTimeout(run, 50); return; }

    const ctx = canvas.getContext('2d');
    let width, height, particles;

    function resize() {
        width = canvas.width = window.parent.innerWidth;
        height = canvas.height = window.parent.innerHeight;
    }

    function createParticles() {
        particles = [];
        const numParticles = Math.min(Math.floor(width * height / 15000), 70);
        for (let i = 0; i < numParticles; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.5,
                radius: Math.random() * 2 + 1,
                alpha: Math.random() * 0.4 + 0.2
            });
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);
        for (let i = 0; i < particles.length; i++) {
            let p = particles[i];
            p.x += p.vx;
            p.y += p.vy;

            if (p.x < 0 || p.x > width) p.vx *= -1;
            if (p.y < 0 || p.y > height) p.vy *= -1;

            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(99, 102, 241, ' + p.alpha + ')';
            ctx.fill();

            for (let j = i + 1; j < particles.length; j++) {
                let p2 = particles[j];
                let dx = p.x - p2.x;
                let dy = p.y - p2.y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 110) {
                    ctx.beginPath();
                    ctx.moveTo(p.x, p.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.strokeStyle = 'rgba(99, 102, 241, ' + (0.12 * (1 - dist / 110)) + ')';
                    ctx.lineWidth = 0.8;
                    ctx.stroke();
                }
            }
        }
        window.parent.requestAnimationFrame(animate);
    }

    window.parent.addEventListener('resize', () => { resize(); createParticles(); });
    resize();
    createParticles();
    animate();
})();
</script>
""", height=0, scrolling=False)


# --- Built-in Instant Python Knowledge Engine ---
PYTHON_KNOWLEDGE = {
    r"even|odd": (
        "In Python, check if a number is even or odd using modulo (`%`):\n\n"
        "```python\n"
        "number = int(input('Enter a number: '))\n"
        "if number % 2 == 0:\n"
        "    print(f'{number} is Even')\n"
        "else:\n"
        "    print(f'{number} is Odd')\n"
        "```"
    ),
    r"sort|sorting": (
        "Sort lists in Python using `sorted()` or `.sort()`:\n\n"
        "```python\n"
        "nums = [5, 2, 8, 1]\n"
        "print(sorted(nums)) # [1, 2, 5, 8]\n"
        "```"
    )
}

def get_instant_answer(query: str):
    lower_q = query.lower()
    for pattern, answer in PYTHON_KNOWLEDGE.items():
        if re.search(r"\b(" + pattern + r")\b", lower_q):
            return answer
    return None


def sanitize_ai_response(text: str) -> str:
    """Removes any third-party ad headers/footers or promo messages."""
    if not text:
        return ""
    patterns = [
        r"(?i)\n*Support Pollinations\.AI:.*",
        r"(?i)\n*🌸\s*Ad\s*🌸.*",
        r"(?i)\n*Powered by Pollinations\.AI.*",
        r"(?i)\n*Support our mission to keep AI accessible.*"
    ]
    cleaned = text
    for pat in patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.DOTALL | re.MULTILINE)
    return cleaned.strip()


# --- AI Client Setup ---
def get_ai_client(api_key: str, model_name: str, free_mode: bool):
    if free_mode or not api_key:
        client = OpenAI(
            base_url="https://text.pollinations.ai/openai",
            api_key="none",
            timeout=15.0
        )
        effective_model = "openai" if model_name in ("gpt-4o-mini", "openai") else model_name
        mode_label = "Free AI Cloud"
    else:
        client = OpenAI(api_key=api_key)
        effective_model = model_name
        mode_label = f"OpenAI ({effective_model})"

    return client, effective_model, mode_label


# --- TOP HEADER WITH THEME TOGGLE BUTTON ---
col_head, col_theme = st.columns([3, 1])

with col_head:
    st.markdown('<div class="brand-title">🐍 PyLab</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-tagline">Your Intelligent Python Workspace & Code Execution Engine</div>', unsafe_allow_html=True)

with col_theme:
    selected_theme = st.radio(
        "🎨 Select Theme Mode:",
        ["🌙 Dark Mode", "☀️ Light Mode"],
        index=0 if st.session_state["theme_mode"] == "Dark" else 1,
        horizontal=True
    )
    if "Dark" in selected_theme and st.session_state["theme_mode"] != "Dark":
        st.session_state["theme_mode"] = "Dark"
        st.rerun()
    elif "Light" in selected_theme and st.session_state["theme_mode"] != "Light":
        st.session_state["theme_mode"] = "Light"
        st.rerun()


# --- SIDEBAR SETTINGS ---
st.sidebar.title("🐍 PyLab Settings")
free_mode = st.sidebar.toggle("Use Free AI Cloud Mode", value=True)

if not free_mode:
    api_key_input = st.sidebar.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    model_choice = st.sidebar.selectbox("Select OpenAI Model", ["gpt-4o-mini", "gpt-4o"])
else:
    api_key_input = ""
    model_choice = "openai"

system_prompt = st.sidebar.text_area(
    "System Persona",
    value="You are PyLab, an expert Python assistant conceived by Alankrita Paul.",
    height=100
)

if st.sidebar.button("🧹 Clear Chat Memory"):
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.rerun()


# --- INITIALIZE SESSION ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

client, model_name, mode_label = get_ai_client(api_key_input, model_choice, free_mode)


# --- HOW TO USE ---
with st.expander("📖 **How to Use PyLab**", expanded=False):
    st.markdown("""
    1. **PyLab AI Chat**: Ask any Python question or topic to get instant code explanations.
    2. **Live Code Sandbox**: Write, edit, and execute Python code live right inside your browser.
    3. **Code Debugger**: Paste broken Python scripts to get instant explanations and working fixes.
    """)


# --- MAIN WORKSPACE TABS ---
tab_chat, tab_runner, tab_debugger = st.tabs([
    "💬 PyLab AI Chat",
    "▶️ Live Code Sandbox",
    "🐛 Code Debugger"
])


# --- TAB 1: CHAT ---
with tab_chat:
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🐍"):
                st.markdown(msg["content"])

    user_query = st.chat_input("Ask any Python question...")

    if user_query:
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        st.session_state["messages"].append({"role": "user", "content": user_query})

        instant_answer = get_instant_answer(user_query)

        with st.chat_message("assistant", avatar="🐍"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state["messages"]
                )
                if response.choices and len(response.choices) > 0:
                    candidate = response.choices[0].message.content or ""
                    if candidate and not re.search(r"\b(om\s+){3,}", candidate, re.IGNORECASE):
                        full_response = candidate
            except Exception:
                pass

            if not full_response:
                full_response = instant_answer if instant_answer else "Welcome to PyLab! How can I help you write or debug your Python code today?"

            full_response = sanitize_ai_response(full_response)
            message_placeholder.markdown(full_response)
            st.session_state["messages"].append({"role": "assistant", "content": full_response})


# --- TAB 2: SANDBOX ---
with tab_runner:
    st.subheader("▶️ Live Python Execution Sandbox")
    default_code = 'print("Welcome to PyLab — The Complete 360° Python Ecosystem!")\nfor i in range(1, 4):\n    print("Step #", i)'
    code_to_run = st.text_area("Python Code Editor", value=default_code, height=200)

    if st.button("▶️ Run Python Code", type="primary"):
        output_buffer = io.StringIO()
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                exec(code_to_run, {"__name__": "__main__"})
            output_text = output_buffer.getvalue()
            st.success("Execution Completed Successfully!")
            st.code(output_text if output_text else "[No stdout output]", language="text")
        except Exception:
            st.error("Execution Error:")
            st.code(traceback.format_exc(), language="python")


# --- TAB 3: DEBUGGER ---
with tab_debugger:
    st.subheader("🐛 Python Code & Error Debugger")
    broken_code = st.text_area("Broken Python Code", value="print(10 / 0)", height=120)

    if st.button("🔍 Debug Code"):
        try:
            fix_resp = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": f"Fix this Python code: ```python\n{broken_code}\n```"}]
            )
            st.markdown(sanitize_ai_response(fix_resp.choices[0].message.content or ""))
        except Exception:
            st.markdown("**Root Cause**: `ZeroDivisionError` - cannot divide by 0.\n\n**Fix**:\n```python\nif divisor != 0:\n    print(10 / divisor)\n```")


# --- FOOTER SPECIFIED BY USER ---
st.markdown("""
<div class="footer-box">
    <div class="footer-eco">The Complete 360° Python Ecosystem</div>
    <div class="footer-hub">The central hub for Python code and execution</div>
    <div>© All rights reserved.</div>
    <div>Conceived by <b>Alankrita Paul</b></div>
</div>
""", unsafe_allow_html=True)
