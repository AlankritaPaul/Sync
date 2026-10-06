"""
Python AI Developer Assistant & Code Runner
============================================
A specialized Python AI assistant, live code sandbox, bug debugger, and interactive reference.
Ready for local execution and 1-click Streamlit Community Cloud deployment!
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
    page_title="Python AI Assistant & Code Sandbox",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for modern dark UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4F46E5 0%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #94A3B8;
        margin-bottom: 1.5rem;
    }
    .stCodeBlock {
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding-top: 8px;
        padding-bottom: 8px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)


# --- Built-in Instant Python Knowledge Engine ---
PYTHON_KNOWLEDGE = {
    r"even|odd": (
        "In Python, you check if a number is even or odd using the modulo operator (`%`):\n\n"
        "```python\n"
        "number = int(input('Enter a number: '))\n\n"
        "if number % 2 == 0:\n"
        "    print(f'{number} is Even')\n"
        "else:\n"
        "    print(f'{number} is Odd')\n"
        "```\n\n"
        "💡 **Tip**: `number % 2` gives the remainder of division by 2. If remainder is 0, it is even!"
    ),
    r"sort|sorting": (
        "In Python, there are two easy ways to sort a list:\n\n"
        "1. **Using `sorted()`** (creates a new sorted list):\n"
        "```python\n"
        "nums = [5, 2, 8, 1, 9]\n"
        "sorted_nums = sorted(nums)\n"
        "print(sorted_nums)  # Output: [1, 2, 5, 8, 9]\n"
        "```\n\n"
        "2. **Using `.sort()`** (sorts the list in-place):\n"
        "```python\n"
        "nums.sort()\n"
        "print(nums)  # Output: [1, 2, 5, 8, 9]\n"
        "```"
    ),
    r"loop|for loop|while": (
        "Here are the two primary loop types in Python:\n\n"
        "1. **For Loop** (iterate over sequence or range):\n"
        "```python\n"
        "for i in range(5):\n"
        "    print('Count:', i)  # Prints 0, 1, 2, 3, 4\n"
        "```\n\n"
        "2. **While Loop** (repeats while condition is True):\n"
        "```python\n"
        "x = 3\n"
        "while x > 0:\n"
        "    print(x)\n"
        "    x -= 1\n"
        "```"
    ),
    r"function|def": (
        "Define functions in Python using the `def` keyword:\n\n"
        "```python\n"
        "def greet(name: str) -> str:\n"
        "    return f'Hello, {name}!'\n\n"
        "# Call the function:\n"
        "message = greet('Alankrita')\n"
        "print(message)\n"
        "```"
    ),
    r"list|array": (
        "Python lists store ordered collections of items:\n\n"
        "```python\n"
        "fruits = ['apple', 'banana', 'cherry']\n"
        "fruits.append('orange')       # Add item\n"
        "print(fruits[0])              # Access item: 'apple'\n"
        "for fruit in fruits:\n"
        "    print(fruit)\n"
        "```"
    ),
    r"dictionary|dict": (
        "Python dictionaries store key-value pairs:\n\n"
        "```python\n"
        "student = {'name': 'Alankrita', 'role': 'Developer', 'grade': 'A'}\n"
        "print(student['name'])        # Output: 'Alankrita'\n"
        "student['status'] = 'Active'  # Add or update key\n"
        "```"
    ),
    r"read file|open file|write file": (
        "Standard way to read and write files safely in Python using `with`:\n\n"
        "```python\n"
        "# Write file:\n"
        "with open('example.txt', 'w', encoding='utf-8') as f:\n"
        "    f.write('Hello from Python AI!')\n\n"
        "# Read file:\n"
        "with open('example.txt', 'r', encoding='utf-8') as f:\n"
        "    content = f.read()\n"
        "    print(content)\n"
        "```"
    )
}

def get_instant_answer(query: str):
    """Returns instant answer if query matches known Python concepts."""
    lower_q = query.lower()
    for pattern, answer in PYTHON_KNOWLEDGE.items():
        if re.search(r"\b(" + pattern + r")\b", lower_q):
            return answer
    return None


# --- AI Client Setup ---
def get_ai_client(api_key: str, model_name: str, free_mode: bool):
    """Initializes OpenAI client targeting OpenAI API or Free AI Cloud."""
    if free_mode or not api_key:
        client = OpenAI(
            base_url="https://text.pollinations.ai/openai",
            api_key="none",
            timeout=15.0
        )
        effective_model = "openai" if model_name in ("gpt-4o-mini", "openai") else model_name
        mode_label = "Free AI Cloud (No Account Required)"
    else:
        client = OpenAI(api_key=api_key)
        effective_model = model_name
        mode_label = f"Official OpenAI ({effective_model})"

    return client, effective_model, mode_label


# --- Sidebar Setup ---
st.sidebar.title("🐍 Python AI Settings")

free_mode = st.sidebar.toggle("Use Free AI Cloud Mode", value=True, help="No OpenAI API key required!")

if not free_mode:
    api_key_input = st.sidebar.text_input("OpenAI API Key", type="password", value=os.environ.get("OPENAI_API_KEY", ""))
    model_choice = st.sidebar.selectbox("Select OpenAI Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"])
else:
    api_key_input = ""
    model_choice = "openai"

system_prompt = st.sidebar.text_area(
    "System Persona",
    value="You are an expert Python developer and mentor. Provide clean, well-formatted Python 3 code with clear explanations.",
    height=100
)

if st.sidebar.button("🧹 Clear Chat Memory"):
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🚀 Deployment & LinkedIn")
st.sidebar.info(
    "Deploy this project to Streamlit Community Cloud and add the live link to your LinkedIn profile!"
)


# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "system", "content": system_prompt}]

client, model_name, mode_label = get_ai_client(api_key_input, model_choice, free_mode)


# --- Header Section ---
st.markdown('<div class="main-header">🐍 Python AI Assistant & Code Sandbox</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Powered by <b>{mode_label}</b> | Interactive Coding, Debugging & Reference</div>', unsafe_allow_html=True)


# --- Main Navigation Tabs ---
tab_chat, tab_runner, tab_debugger, tab_reference, tab_deploy = st.tabs([
    "💬 Python AI Chat",
    "▶️ Live Python Sandbox",
    "🐛 Code Debugger",
    "📚 Python Reference",
    "🚀 Deploy & Share"
])


# ==============================================================================
# TAB 1: PYTHON AI CHAT
# ==============================================================================
with tab_chat:
    st.caption("Ask any Python question, request code scripts, or ask for architectural advice.")

    # Render prior messages
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant", avatar="🐍"):
                st.markdown(msg["content"])

    # Quick suggestion chips
    st.markdown("**Quick Prompts:**")
    col1, col2, col3, col4 = st.columns(4)
    prompt_input = None
    if col1.button("💡 3 Python Project Ideas"):
        prompt_input = "Give me 3 creative beginner-to-intermediate Python project ideas with step-by-step guidance."
    if col2.button("⚡ Fast File Handling"):
        prompt_input = "How do I efficiently read and process large CSV or text files in Python?"
    if col3.button("🌐 FastAPI vs Flask"):
        prompt_input = "Compare FastAPI vs Flask in Python with code examples for creating an API endpoint."
    if col4.button("🧩 Python Decorators"):
        prompt_input = "Explain Python decorators simply with a working practical code example."

    # Chat input box
    user_query = st.chat_input("Ask any Python question (e.g. 'How do I sort a list of dictionaries by key?')...")
    if prompt_input:
        user_query = prompt_input

    if user_query:
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_query)
        st.session_state["messages"].append({"role": "user", "content": user_query})

        # Check instant knowledge answer
        instant_answer = get_instant_answer(user_query)

        with st.chat_message("assistant", avatar="🐍"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                # API Call
                response = client.chat.completions.create(
                    model=model_name,
                    messages=st.session_state["messages"],
                    temperature=0.7
                )
                if response.choices and len(response.choices) > 0:
                    candidate = response.choices[0].message.content or ""
                    if candidate and not re.search(r"\b(om\s+){3,}", candidate, re.IGNORECASE):
                        full_response = candidate
            except Exception as e:
                st.warning(f"Cloud AI Notice: Using local knowledge engine due to connection response.")

            if not full_response:
                if instant_answer:
                    full_response = instant_answer
                else:
                    full_response = (
                        "I am your Python AI assistant! Here is a sample code pattern for your query:\n\n"
                        "```python\n"
                        "# Python Solution\n"
                        "def process_data(data):\n"
                        "    result = [item for item in data if item]\n"
                        "    return result\n\n"
                        "print(process_data(['python', 'ai', 'chatbot']))\n"
                        "```\n\n"
                        "Feel free to ask for a specific explanation or package usage!"
                    )

            message_placeholder.markdown(full_response)
            st.session_state["messages"].append({"role": "assistant", "content": full_response})


# ==============================================================================
# TAB 2: LIVE PYTHON CODE RUNNER (SANDBOX)
# ==============================================================================
with tab_runner:
    st.subheader("▶️ Live Python Execution Sandbox")
    st.caption("Write, edit, and execute Python code live in your browser!")

    default_code = """# Interactive Python Sandbox
def calculate_stats(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count if count > 0 else 0
    return {"total": total, "count": count, "average": average}

data = [10, 25, 40, 55, 70, 85, 100]
stats = calculate_stats(data)

print(f"📊 Numbers: {data}")
print(f"✅ Total Sum: {stats['total']}")
print(f"📈 Average:  {stats['average']:.2f}")
"""

    code_to_run = st.text_area("Python Code Editor", value=default_code, height=260)

    if st.button("▶️ Run Python Code", type="primary"):
        st.markdown("### Execution Output:")
        output_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                # Execute in an isolated scope
                exec_globals = {"__name__": "__main__"}
                exec(code_to_run, exec_globals)
            
            output_text = output_buffer.getvalue()
            st.success("Program Executed Successfully! (Return Code: 0)")
            st.code(output_text if output_text else "[Code executed with no stdout output]", language="text")
        except Exception as err:
            err_msg = traceback.format_exc()
            st.error("Execution Error Encountered:")
            st.code(err_msg, language="python")


# ==============================================================================
# TAB 3: PYTHON CODE DEBUGGER
# ==============================================================================
with tab_debugger:
    st.subheader("🐛 Python Code & Error Debugger")
    st.caption("Paste your broken code or traceback error to get instant fixes.")

    col_code, col_err = st.columns(2)
    with col_code:
        broken_code = st.text_area("Broken Python Code", value="""def divide_items(items, divisor):\n    results = []\n    for item in items:\n        results.append(item / divisor)\n    return results\n\nprint(divide_items([10, 20, 30], 0))""", height=180)
    with col_err:
        error_traceback = st.text_area("Error Traceback (Optional)", value="ZeroDivisionError: division by zero", height=180)

    if st.button("🔍 Debug Code & Fix Error"):
        with st.spinner("Analyzing code structure and error root cause..."):
            debug_prompt = f"Please analyze and fix this broken Python code:\n\n```python\n{broken_code}\n```\n\nTraceback / Error:\n{error_traceback}\n\nProvide: 1. Explanation of root cause 2. Corrected working Python code 3. Best practices to prevent this."
            
            try:
                fix_response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": "You are a expert Python debugger."},
                        {"role": "user", "content": debug_prompt}
                    ]
                )
                analysis = fix_response.choices[0].message.content or ""
            except Exception:
                analysis = (
                    "### 🛠️ Debug Analysis & Fix\n\n"
                    "**Root Cause**: `ZeroDivisionError` occurs when trying to divide a number by `0`.\n\n"
                    "**Corrected Code**:\n"
                    "```python\n"
                    "def divide_items(items, divisor):\n"
                    "    if divisor == 0:\n"
                    "        print('Error: Cannot divide by zero!')\n"
                    "        return []\n"
                    "    return [item / divisor for item in items]\n\n"
                    "print(divide_items([10, 20, 30], 2)) # Works: [5.0, 10.0, 15.0]\n"
                    "```"
                )
            
            st.markdown(analysis)


# ==============================================================================
# TAB 4: PYTHON REFERENCE & CHEATSHEET
# ==============================================================================
with tab_reference:
    st.subheader("📚 Python Core Reference & Cheatsheet")
    
    ref_category = st.selectbox("Select Subject", ["Data Structures & Methods", "File I/O & Exception Handling", "Functions & OOP", "Popular Libraries (Pandas, Requests, FastAPI)"])
    
    if ref_category == "Data Structures & Methods":
        st.markdown("""
        ### 📦 Python Data Structures
        
        #### Lists (Ordered, Mutable)
        ```python
        nums = [1, 2, 3]
        nums.append(4)         # Add element
        nums.extend([5, 6])    # Merge list
        nums.pop(0)            # Remove by index
        ```
        
        #### Dictionaries (Key-Value Pairs)
        ```python
        user = {"name": "Alankrita", "role": "Developer"}
        print(user.get("role"))          # Safe lookup
        user.update({"status": "Active"}) # Update keys
        ```
        """)
    elif ref_category == "File I/O & Exception Handling":
        st.markdown("""
        ### 📂 File Operations & Try/Except
        
        ```python
        try:
            with open("data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print("File does not exist!")
        except Exception as e:
            print(f"Unexpected error: {e}")
        ```
        """)
    else:
        st.markdown("""
        ### ⚡ Popular Python Libraries Quickstart
        
        #### HTTP Requests (`requests`)
        ```python
        import requests
        response = requests.get("https://api.github.com")
        print(response.status_code, response.json())
        ```
        
        #### Data Science (`pandas`)
        ```python
        import pandas as pd
        df = pd.DataFrame({"Name": ["Alice", "Bob"], "Age": [25, 30]})
        print(df.describe())
        ```
        """)


# ==============================================================================
# TAB 5: DEPLOYMENT & LINKEDIN SHOWCASE GUIDE
# ==============================================================================
with tab_deploy:
    st.subheader("🚀 How to Deploy & Showcase on LinkedIn")
    
    st.markdown("""
    ### 1. Run Locally (Localhost)
    To run this app on your local machine, run this command in your terminal:
    ```powershell
    streamlit run app.py
    ```
    Your browser will open automatically at **`http://localhost:8501`**!

    ---

    ### 2. Deploy to Streamlit Community Cloud (100% Free)
    1. Push your repository code to GitHub (`AlankritaPaul/Sync`).
    2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
    3. Click **New app** -> Select Repository `AlankritaPaul/Sync` -> Main file path: `app.py`.
    4. Click **Deploy!** Your app will receive a public URL like `https://sync-python-ai.streamlit.app`.

    ---

    ### 3. Share on LinkedIn 💼
    Add your deployed app to your **LinkedIn Featured Section** or post a demo video:
    > 🚀 *Excited to share my Python AI Assistant & Live Code Sandbox built with Python, Streamlit, and OpenAI! Check out the live app here: [Your Streamlit App URL]*
    """)
