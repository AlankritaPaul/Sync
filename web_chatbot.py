#!/usr/bin/env python3
"""
PyLab — The Complete 360° Python Ecosystem
===========================================
The central hub for Python code and execution.
Conceived by Alankrita Paul. All rights reserved. ©
"""

import sys
import os
import json
import re
import io
import contextlib
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chatbot import get_client_and_config, PYTHON_KNOWLEDGE, get_instant_answer, sanitize_ai_response

PORT = 5000
client, model_name, display_name = get_client_and_config()
conversation_history = [
    {
        "role": "system",
        "content": (
            "You are PyLab, an expert Python programming assistant conceived by Alankrita Paul. "
            "Answer all Python questions clearly, directly, and concisely with clean Python 3 code examples."
        )
    }
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PyLab — The Complete 360° Python Ecosystem</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            /* DARK MODE: Deep Midnight Blue Background & Blue Accents */
            --bg-color: #0b1329;
            --card-bg: rgba(15, 23, 42, 0.85);
            --card-border: rgba(59, 130, 246, 0.35);
            --text-main: #f8fafc;
            --text-muted: #93c5fd;
            --accent-primary: #2563eb;
            --accent-hover: #1d4ed8;
            --accent-gradient: linear-gradient(135deg, #38bdf8 0%, #2563eb 50%, #1d4ed8 100%);
            --user-bubble: #2563eb;
            --ai-bubble: rgba(15, 23, 42, 0.9);
            --code-bg: rgba(3, 7, 18, 0.9);
            --input-bg: rgba(15, 23, 42, 0.9);
        }

        [data-theme="light"] {
            /* LIGHT MODE: Crisp Pure White Background */
            --bg-color: #ffffff;
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: #e2e8f0;
            --text-main: #0f172a;
            --text-muted: #475569;
            --accent-primary: #2563eb;
            --accent-hover: #1d4ed8;
            --accent-gradient: linear-gradient(135deg, #0284c7 0%, #2563eb 50%, #1d4ed8 100%);
            --user-bubble: #2563eb;
            --ai-bubble: #f8fafc;
            --code-bg: #f1f5f9;
            --input-bg: #ffffff;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; transition: background-color 0.3s, color 0.3s; }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 24px 16px;
            position: relative;
            overflow-x: hidden;
        }

        #bg-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            z-index: 0;
            pointer-events: none;
        }

        .container {
            width: 100%;
            max-width: 950px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            position: relative;
            z-index: 1;
        }

        /* --- HEADER OVERVIEW --- */
        .brand-logo-container {
            display: flex;
            align-items: center;
            gap: 14px;
        }

        .snake-icon-badge {
            width: 52px;
            height: 52px;
            border-radius: 16px;
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            box-shadow: 0 10px 20px rgba(37, 99, 235, 0.35);
            animation: pulseGlow 3s ease-in-out infinite alternate;
        }

        @keyframes pulseGlow {
            0% { transform: scale(1); box-shadow: 0 10px 20px rgba(37, 99, 235, 0.35); }
            100% { transform: scale(1.05); box-shadow: 0 12px 28px rgba(56, 189, 248, 0.55); }
        }

        .overview-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            padding: 28px 32px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 16px;
        }

        .app-title-group h1 {
            font-size: 30px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .app-title-group .subtext {
            font-size: 14px;
            color: var(--text-muted);
            margin-top: 4px;
        }

        /* --- THEME TOGGLE --- */
        .theme-toggle-box {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--code-bg);
            padding: 6px 14px;
            border-radius: 30px;
            border: 1px solid var(--card-border);
        }

        .theme-toggle-box span {
            font-size: 13px;
            font-weight: 600;
            color: var(--text-muted);
        }

        .toggle-btn {
            background: var(--accent-primary);
            color: #fff;
            border: none;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
        }

        .toggle-btn:hover { background: var(--accent-hover); }

        /* --- HOW TO USE --- */
        .how-to-use-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 20px 24px;
        }

        .how-to-use-card h3 {
            font-size: 15px;
            font-weight: 700;
            color: var(--text-main);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .steps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }

        .step-item {
            background: var(--code-bg);
            border: 1px solid var(--card-border);
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 13px;
            color: var(--text-muted);
        }

        .step-item strong {
            color: var(--text-main);
            display: block;
            margin-bottom: 4px;
        }

        /* --- TABS SYSTEM --- */
        .nav-tabs {
            display: flex;
            gap: 10px;
            border-bottom: 2px solid var(--card-border);
            padding-bottom: 8px;
        }

        .tab-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px;
        }

        .tab-btn.active {
            background: var(--accent-primary);
            color: #ffffff;
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        /* --- MAIN WORKSPACE --- */
        .workspace-card {
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--card-border);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        }

        .chat-box {
            height: 400px;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .msg {
            display: flex;
            gap: 12px;
            max-width: 85%;
        }

        .msg.user { align-self: flex-end; flex-direction: row-reverse; }
        .msg.ai { align-self: flex-start; }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: var(--accent-gradient);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }

        .bubble {
            padding: 14px 18px;
            border-radius: 14px;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-break: break-word;
        }

        .msg.user .bubble {
            background: var(--user-bubble);
            color: #ffffff;
            border-bottom-right-radius: 2px;
        }

        .msg.ai .bubble {
            background: var(--ai-bubble);
            color: var(--text-main);
            border: 1px solid var(--card-border);
            border-bottom-left-radius: 2px;
        }

        .input-bar {
            padding: 18px 24px;
            background: var(--card-bg);
            border-top: 1px solid var(--card-border);
            display: flex;
            gap: 12px;
        }

        .input-bar input {
            flex: 1;
            background: var(--input-bg);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 14px 18px;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
        }

        .send-btn {
            background: var(--accent-primary);
            color: #fff;
            border: none;
            padding: 0 24px;
            border-radius: 12px;
            font-weight: 600;
            cursor: pointer;
        }

        .send-btn:hover { background: var(--accent-hover); }

        /* Code Sandbox Tab */
        .sandbox-area {
            padding: 24px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        textarea {
            width: 100%;
            height: 200px;
            background: var(--code-bg);
            border: 1px solid var(--card-border);
            color: var(--text-main);
            padding: 14px;
            border-radius: 10px;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            outline: none;
        }

        .run-btn {
            align-self: flex-start;
            background: #10b981;
            color: #fff;
            border: none;
            padding: 10px 22px;
            border-radius: 10px;
            font-weight: 600;
            cursor: pointer;
        }

        .output-box {
            background: var(--code-bg);
            border: 1px solid var(--card-border);
            padding: 16px;
            border-radius: 10px;
            font-family: 'Fira Code', monospace;
            font-size: 13px;
            white-space: pre-wrap;
        }

        /* --- FOOTER SPECIFIED BY USER --- */
        .footer {
            margin-top: 30px;
            padding: 22px;
            text-align: center;
            border-top: 1px solid var(--card-border);
            width: 100%;
            font-size: 13px;
            color: var(--text-muted);
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .footer .eco-title {
            font-weight: 700;
            color: var(--text-main);
            font-size: 15px;
            letter-spacing: 0.2px;
        }

        .footer .hub-line {
            font-weight: 600;
            color: var(--text-muted);
            font-size: 13px;
        }

        .footer strong { color: var(--text-main); }
    </style>
</head>
<body>
    <!-- HIGH-DENSITY PYTHON FLOATING CANVAS -->
    <canvas id="bg-canvas"></canvas>

    <div class="container">

        <!-- HEADER OVERVIEW & THEME TOGGLE -->
        <div class="overview-card">
            <div class="brand-logo-container">
                <div class="snake-icon-badge">🐍</div>
                <div class="app-title-group">
                    <h1>PyLab</h1>
                    <div class="subtext">Your Intelligent Python Workspace & Code Execution Engine</div>
                </div>
            </div>
            <div class="theme-toggle-box">
                <span>Theme:</span>
                <button class="toggle-btn" onclick="toggleTheme()" id="themeBtn">🌙 Dark</button>
            </div>
        </div>

        <!-- HOW TO USE -->
        <div class="how-to-use-card">
            <h3>📖 How to Use PyLab</h3>
            <div class="steps-grid">
                <div class="step-item">
                    <strong>1. Ask Python Questions</strong>
                    Type any Python query or topic into the AI Chat tab to get instant code explanations.
                </div>
                <div class="step-item">
                    <strong>2. Execute Code Live</strong>
                    Switch to the Code Sandbox tab to write, edit, and run Python code live in your browser.
                </div>
                <div class="step-item">
                    <strong>3. Debug Errors</strong>
                    Paste broken Python scripts to get instant root cause explanations and working code fixes.
                </div>
            </div>
        </div>

        <!-- TABS NAV -->
        <div class="nav-tabs">
            <button class="tab-btn active" onclick="showTab('chat')">💬 PyLab AI Chat</button>
            <button class="tab-btn" onclick="showTab('sandbox')">▶️ Live Code Sandbox</button>
        </div>

        <!-- WORKSPACE CONTENT -->
        <div class="workspace-card">

            <!-- TAB 1: CHAT -->
            <div id="chatTab" class="tab-content active">
                <div class="chat-box" id="chatBox">
                    <div class="msg ai">
                        <div class="avatar">🐍</div>
                        <div class="bubble">Welcome to PyLab! I am your intelligent Python AI assistant. Ask me any Python question, request code examples, or ask for help fixing bugs!</div>
                    </div>
                </div>
                <div class="input-bar">
                    <input type="text" id="userInput" placeholder="Ask a Python question (e.g. How to sort a dictionary by value?)..." onkeydown="if(event.key==='Enter') sendMsg()">
                    <button class="send-btn" onclick="sendMsg()">Send ➔</button>
                </div>
            </div>

            <!-- TAB 2: CODE SANDBOX -->
            <div id="sandboxTab" class="tab-content">
                <div class="sandbox-area">
                    <h3>▶️ Live Python Execution Sandbox</h3>
                    <textarea id="codeEditor"># Write or paste your Python code here
def greet_user(name):
    return f"Welcome to PyLab, {name}!"

result = greet_user("Alankrita")
print(result)

for i in range(1, 4):
    print(f"Executing Python step #{i}")
</textarea>
                    <button class="run-btn" onclick="runCode()">▶️ Run Python Code</button>
                    <div>
                        <strong style="font-size: 13px; color: var(--text-muted);">Output:</strong>
                        <div class="output-box" id="codeOutput">Click 'Run Python Code' to execute.</div>
                    </div>
                </div>
            </div>

        </div>

        <!-- FOOTER SPECIFIED BY USER -->
        <div class="footer">
            <div class="eco-title">The Complete 360° Python Ecosystem</div>
            <div class="hub-line">The central hub for Python code and execution</div>
            <div>© All rights reserved.</div>
            <div>Conceived by <strong>Alankrita Paul</strong></div>
        </div>

    </div>

    <!-- HIGH-DENSITY PYTHON FLOATING ANIMATION SCRIPT -->
    <script>
        (function initHighDensityPythonCanvas() {
            const canvas = document.getElementById('bg-canvas');
            if (!canvas) return;
            const ctx = canvas.getContext('2d');
            let width, height, tokens;

            const pyTokens = ['🐍', 'def', 'import', 'print()', 'py', 'return', 'list', 'dict', 'if', 'while', 'async', 'lambda', '{ }', 'None', 'True', 'class', 'yield', 'with', 'pass', 'try', 'except'];
            const colors = ['rgba(56, 189, 248, ', 'rgba(59, 130, 246, ', 'rgba(99, 102, 241, ', 'rgba(168, 85, 247, '];

            function resize() {
                width = canvas.width = window.innerWidth;
                height = canvas.height = window.innerHeight;
            }

            function createTokens() {
                tokens = [];
                // High density floating token count (90+ tokens)
                const numTokens = Math.min(Math.floor(width * height / 10000), 100);
                for (let i = 0; i < numTokens; i++) {
                    tokens.push({
                        x: Math.random() * width,
                        y: Math.random() * height,
                        vx: (Math.random() - 0.5) * 0.5,
                        vy: (Math.random() - 0.5) * 0.5,
                        text: pyTokens[Math.floor(Math.random() * pyTokens.length)],
                        fontSize: Math.floor(Math.random() * 10) + 12,
                        color: colors[Math.floor(Math.random() * colors.length)],
                        alpha: Math.random() * 0.4 + 0.25
                    });
                }
            }

            function animate() {
                ctx.clearRect(0, 0, width, height);
                for (let i = 0; i < tokens.length; i++) {
                    let t = tokens[i];
                    t.x += t.vx;
                    t.y += t.vy;

                    if (t.x < 0 || t.x > width) t.vx *= -1;
                    if (t.y < 0 || t.y > height) t.vy *= -1;

                    ctx.font = t.fontSize + 'px "Fira Code", monospace';
                    ctx.fillStyle = t.color + t.alpha + ')';
                    ctx.fillText(t.text, t.x, t.y);

                    for (let j = i + 1; j < tokens.length; j++) {
                        let t2 = tokens[j];
                        let dx = t.x - t2.x;
                        let dy = t.y - t2.y;
                        let dist = Math.sqrt(dx * dx + dy * dy);
                        if (dist < 115) {
                            ctx.beginPath();
                            ctx.moveTo(t.x, t.y);
                            ctx.lineTo(t2.x, t2.y);
                            ctx.strokeStyle = t.color + (0.12 * (1 - dist / 115)) + ')';
                            ctx.lineWidth = 0.7;
                            ctx.stroke();
                        }
                    }
                }
                requestAnimationFrame(animate);
            }

            window.addEventListener('resize', () => { resize(); createTokens(); });
            resize();
            createTokens();
            animate();
        })();

        function toggleTheme() {
            const html = document.documentElement;
            const btn = document.getElementById('themeBtn');
            if (html.getAttribute('data-theme') === 'dark') {
                html.setAttribute('data-theme', 'light');
                btn.textContent = '☀️ Light';
            } else {
                html.setAttribute('data-theme', 'dark');
                btn.textContent = '🌙 Dark';
            }
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            if (tabName === 'chat') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('chatTab').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('sandboxTab').classList.add('active');
            }
        }

        async function sendMsg() {
            const input = document.getElementById('userInput');
            const text = input.value.trim();
            if (!text) return;

            const chatBox = document.getElementById('chatBox');
            chatBox.innerHTML += `
                <div class="msg user">
                    <div class="avatar">👤</div>
                    <div class="bubble">${escapeHtml(text)}</div>
                </div>
            `;
            input.value = '';
            chatBox.scrollTop = chatBox.scrollHeight;

            const aiMsg = document.createElement('div');
            aiMsg.className = 'msg ai';
            aiMsg.innerHTML = `
                <div class="avatar">🐍</div>
                <div class="bubble">Thinking...</div>
            `;
            chatBox.appendChild(aiMsg);
            chatBox.scrollTop = chatBox.scrollHeight;

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                aiMsg.querySelector('.bubble').textContent = data.reply || 'No response';
            } catch (err) {
                aiMsg.querySelector('.bubble').textContent = 'Error connecting to server.';
            }
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function runCode() {
            const code = document.getElementById('codeEditor').value;
            const outputBox = document.getElementById('codeOutput');
            outputBox.textContent = 'Executing code...';

            try {
                const res = await fetch('/api/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code: code })
                });
                const data = await res.json();
                outputBox.textContent = data.output || '[No output returned]';
            } catch (err) {
                outputBox.textContent = 'Error executing code: ' + err;
            }
        }

        function escapeHtml(str) {
            return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }
    </script>
</body>
</html>
"""


class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        global conversation_history
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        if self.path == "/api/chat":
            try:
                data = json.loads(body)
                user_msg = data.get("message", "").strip()
                conversation_history.append({"role": "user", "content": user_msg})

                instant = get_instant_answer(user_msg)
                ai_reply = ""

                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=conversation_history
                    )
                    if response.choices and len(response.choices) > 0:
                        candidate = response.choices[0].message.content or ""
                        candidate = sanitize_ai_response(candidate)
                        if candidate and not re.search(r"\b(om\s+){3,}", candidate, re.IGNORECASE):
                            ai_reply = candidate
                except Exception:
                    pass

                if not ai_reply:
                    ai_reply = instant if instant else "I am PyLab! How can I help you write or debug your Python code today?"

                ai_reply = sanitize_ai_response(ai_reply)
                conversation_history.append({"role": "assistant", "content": ai_reply})

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"reply": ai_reply}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))

        elif self.path == "/api/run":
            try:
                data = json.loads(body)
                code = data.get("code", "")
                output_buffer = io.StringIO()
                
                with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(output_buffer):
                    exec_globals = {"__name__": "__main__"}
                    exec(code, exec_globals)

                result_output = output_buffer.getvalue()
                if not result_output:
                    result_output = "Code executed successfully with zero errors (no print output)."

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"output": result_output}).encode("utf-8"))
            except Exception as err:
                err_trace = traceback.format_exc()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"output": f"Error during execution:\n{err_trace}"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def start_server():
    server = HTTPServer(("127.0.0.1", PORT), ChatHandler)
    print(f"Server started at http://127.0.0.1:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    start_server()
