# 🐍 Python AI Developer Assistant & Code Sandbox

A fast, interactive, feature-rich Python AI assistant, live code execution sandbox, bug debugger, and interactive cheatsheet application. Powered by OpenAI & Free AI Cloud mode.

Built with **Streamlit** for instant local testing on localhost and 1-click cloud deployment for sharing on **LinkedIn**!

---

## ✨ Features

- **💬 Python AI Chatbot**: Specialized assistant providing clean Python 3 code, explanation, and best practices.
- **▶️ Live Python Execution Sandbox**: Write or edit Python code live in your browser and execute it safely to view terminal output.
- **🐛 Python Code & Error Debugger**: Paste broken code or error tracebacks to get instant root cause explanations and fixes.
- **📚 Interactive Python Cheatsheets**: Quick references for Data Structures, File I/O, Functions, OOP, and libraries (`pandas`, `requests`, `fastapi`).
- **🌐 Zero Configuration Required**: Built-in **Free AI Cloud Mode** enabled by default (no OpenAI account or credit card required).
- **🚀 1-Click Streamlit Cloud Deployment**: Ready for instant deployment to Streamlit Community Cloud and showcasing on your LinkedIn profile.

---

## 🚀 Quick Start (Localhost)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch the Streamlit App (Localhost)
Run the following command in your terminal:

```bash
streamlit run app.py
```

Your browser will automatically open at:
👉 **`http://localhost:8501`**

---

## 🖥️ Alternative Local Interfaces

### Standard Web Interface (Port 5000)
```bash
python web_chatbot.py
```
Open in browser at: 👉 **`http://localhost:5000`**

### Terminal Interactive Interface
```bash
python chatbot.py
```

---

## 🔑 (Optional) Setting Up OpenAI API Key

You can switch between **Free AI Cloud Mode** and **Official OpenAI Models** (`gpt-4o-mini`, `gpt-4o`) via the app sidebar or `.env` file:

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` and set your key:
   ```env
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxx
   ```

---

## 🌐 Deploying to Streamlit Cloud & LinkedIn Showcase

1. Push your changes to GitHub:
   ```bash
   git add .
   git commit -m "feat: add streamlit python ai assistant and sandbox"
   git push origin main
   ```
2. Go to **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **New app** -> Select Repository `AlankritaPaul/Sync` -> Main file path: `app.py`.
4. Click **Deploy!**
5. Copy your live app URL (e.g., `https://sync-python-ai.streamlit.app`) and feature it on your **LinkedIn Profile**!

---

## 🧪 Running Unit Tests

```bash
python -m unittest test_chatbot.py
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
