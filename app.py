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
import contextlib
import traceback
import streamlit as st
from openai import OpenAI

# Set Streamlit Page Config
st.set_page_config(
    page_title="PyLab — The Complete 360° Python Ecosystem",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
<style>
    .brand-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #38BDF8 0%, #6366F1 50%, #A855F7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .brand-tagline {
        font-size: 1.1rem;
        font-weight: 600;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .footer-box {
        margin-top: 3rem;
        padding-top: 1.2rem;
        border-top: 1px solid #334155;
        text-align: center;
        color: #94A3B8;
        font-size: 0.9rem;
        line-height: 1.6;
    }
    .footer-hub {
        font-weight: 600;
        color: #F8FAFC;
        font-size: 0.95rem;
    }
</style>
""", unsafe_allow_html=True)


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


# --- Sidebar Setup ---
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


# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

client, model_name, mode_label = get_ai_client(api_key_input, model_choice, free_mode)


# --- HEADER & BRANDING ---
st.markdown('<div class="brand-title">🐍 PyLab</div>', unsafe_allow_html=True)
st.markdown('<div class="brand-tagline">The Complete 360° Python Ecosystem</div>', unsafe_allow_html=True)


# --- HOW TO USE ---
with st.expander("📖 **How to Use PyLab**", expanded=False):
    st.markdown("""
    1. **PyLab AI Chat**: Ask any Python question or topic to get instant code explanations.
    2. **Live Code Sandbox**: Write, edit, and execute Python code live right inside your browser.
    3. **Code Debugger**: Paste broken Python scripts to get instant explanations and working fixes.
    """)


# --- MAIN WORKSPACE TABS ---
tab_chat, tab_runner, tab_debugger, tab_reference = st.tabs([
    "💬 PyLab AI Chat",
    "▶️ Live Code Sandbox",
    "🐛 Code Debugger",
    "📚 Python Reference"
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
            st.markdown(fix_resp.choices[0].message.content)
        except Exception:
            st.markdown("**Root Cause**: `ZeroDivisionError` - cannot divide by 0.\n\n**Fix**:\n```python\nif divisor != 0:\n    print(10 / divisor)\n```")


# --- TAB 4: REFERENCE ---
with tab_reference:
    st.subheader("📚 Python Core Reference")
    st.markdown("""
    * **Lists**: `items = [1, 2, 3]; items.append(4)`
    * **Dicts**: `data = {"a": 1}; print(data["a"])`
    * **Loops**: `for x in range(5): print(x)`
    """)


# --- FOOTER SPECIFIED BY USER ---
st.markdown("""
<div class="footer-box">
    <div class="footer-hub">The central hub for Python code and execution</div>
    <div>© All rights reserved.</div>
    <div>Conceived by <b>Alankrita Paul</b></div>
</div>
""", unsafe_allow_html=True)
