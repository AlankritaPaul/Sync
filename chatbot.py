#!/usr/bin/env python3
"""
Interactive Python AI Chatbot
=============================
A continuous conversation loop in your terminal that connects to Cloud AI
(OpenAI or Free Cloud AI) with an intelligent built-in Python knowledge
fallback so you always get fast, accurate programming help even when offline!
"""

import sys
import os
import re

# Ensure UTF-8 output encoding for Windows command line / PowerShell / IDLE
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Gracefully import python-dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Gracefully import colorama for cross-platform terminal colors
# Only enable colors if running in an interactive terminal (not in Python IDLE)
is_idle = "idlelib" in sys.modules or not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty()
try:
    if not is_idle:
        from colorama import init, Fore, Style
        init(autoreset=True)
        COLOR_CYAN = Fore.CYAN
        COLOR_GREEN = Fore.GREEN
        COLOR_YELLOW = Fore.YELLOW
        COLOR_RED = Fore.RED
        COLOR_MAGENTA = Fore.MAGENTA
        COLOR_RESET = Style.RESET_ALL
        STYLE_BRIGHT = Style.BRIGHT
    else:
        raise ImportError("Running in IDLE or non-TTY")
except Exception:
    COLOR_CYAN = ""
    COLOR_GREEN = ""
    COLOR_YELLOW = ""
    COLOR_RED = ""
    COLOR_MAGENTA = ""
    COLOR_RESET = ""
    STYLE_BRIGHT = ""

# Check for OpenAI package
try:
    from openai import OpenAI, OpenAIError, AuthenticationError, RateLimitError, APIConnectionError
except ImportError:
    print(f"\n{COLOR_RED}[Error]{COLOR_RESET} The 'openai' library is not installed.")
    print("Please install dependencies by running:")
    print(f"    {COLOR_CYAN}pip install -r requirements.txt{COLOR_RESET}\n")
    sys.exit(1)


# Built-in instant Python knowledge fallback
PYTHON_KNOWLEDGE = {
    r"even|odd": (
        "In Python, you check if a number is even or odd using the modulo operator (%):\n\n"
        "```python\n"
        "number = int(input('Enter a number: '))\n\n"
        "if number % 2 == 0:\n"
        "    print(f'{number} is Even')\n"
        "else:\n"
        "    print(f'{number} is Odd')\n"
        "```\n\n"
        "💡 Tip: `number % 2` gives the remainder of division by 2. If remainder is 0, it's even!"
    ),
    r"sort|sorting": (
        "In Python, there are two easy ways to sort a list:\n\n"
        "1. Using `sorted()` (creates a new sorted list):\n"
        "```python\n"
        "nums = [5, 2, 8, 1, 9]\n"
        "sorted_nums = sorted(nums)\n"
        "print(sorted_nums)  # Output: [1, 2, 5, 8, 9]\n"
        "```\n\n"
        "2. Using `.sort()` (sorts the list in-place):\n"
        "```python\n"
        "nums.sort()\n"
        "print(nums)  # Output: [1, 2, 5, 8, 9]\n"
        "```"
    ),
    r"loop|for loop|while": (
        "Here are the two main types of loops in Python:\n\n"
        "1. **For Loop** (repeat over items or a range):\n"
        "```python\n"
        "for i in range(5):\n"
        "    print('Count:', i)  # Prints 0, 1, 2, 3, 4\n"
        "```\n\n"
        "2. **While Loop** (repeats while a condition is True):\n"
        "```python\n"
        "x = 3\n"
        "while x > 0:\n"
        "    print(x)\n"
        "    x -= 1\n"
        "```"
    ),
    r"function|def": (
        "You define a function in Python using the `def` keyword:\n\n"
        "```python\n"
        "def greet(name):\n"
        "    return f'Hello, {name}!'\n\n"
        "# Call the function:\n"
        "message = greet('Alankrita')\n"
        "print(message)\n"
        "```"
    ),
    r"list|array": (
        "A Python list stores an ordered collection of items:\n\n"
        "```python\n"
        "fruits = ['apple', 'banana', 'cherry']\n\n"
        "# Add an item:\n"
        "fruits.append('orange')\n\n"
        "# Access items (0-indexed):\n"
        "print(fruits[0])  # 'apple'\n\n"
        "# Loop through list:\n"
        "for fruit in fruits:\n"
        "    print(fruit)\n"
        "```"
    ),
    r"dictionary|dict": (
        "A Python dictionary stores key-value pairs:\n\n"
        "```python\n"
        "student = {'name': 'Alankrita', 'age': 20, 'grade': 'A'}\n\n"
        "# Access value:\n"
        "print(student['name'])  # 'Alankrita'\n\n"
        "# Add or update:\n"
        "student['school'] = 'University'\n"
        "```"
    ),
    r"read file|open file|write file": (
        "Here is the standard way to read and write files in Python:\n\n"
        "```python\n"
        "# Writing to a file:\n"
        "with open('example.txt', 'w') as f:\n"
        "    f.write('Hello from Python!')\n\n"
        "# Reading from a file:\n"
        "with open('example.txt', 'r') as f:\n"
        "    content = f.read()\n"
        "    print(content)\n"
        "```"
    ),
    r"syntaxerror|nameerror|typeerror|error": (
        "Common Python errors and what they mean:\n\n"
        "• **SyntaxError**: You typed invalid syntax (e.g. forgot a colon `:` or closed bracket `)`).\n"
        "• **NameError**: You used a variable name before defining it.\n"
        "• **TypeError**: You tried an operation on wrong types (e.g. adding `'text' + 5`).\n"
        "• **IndexError**: You tried to access an element outside the list's size.\n\n"
        "💡 Paste your exact code here and I will tell you how to fix it!"
    ),
    r"joke": (
        "Why do Python programmers prefer dark mode?\n"
        "Because light attracts bugs! 😄"
    )
}


def get_instant_answer(query: str):
    """Checks the built-in knowledge engine for an instant answer."""
    lower_query = query.lower()
    for pattern, answer in PYTHON_KNOWLEDGE.items():
        if re.search(r"\b(" + pattern + r")\b", lower_query):
            return answer
    return None


def print_banner(display_name: str) -> None:
    """Displays the welcome banner and quick commands."""
    divider = "=" * 60
    print(f"{COLOR_CYAN}{divider}{COLOR_RESET}")
    print(f"{STYLE_BRIGHT}{COLOR_CYAN}           🤖 Python AI Terminal Chatbot{COLOR_RESET}")
    print(f"{COLOR_CYAN}{divider}{COLOR_RESET}")
    print(f" AI Engine: {COLOR_GREEN}{display_name}{COLOR_RESET}")
    print(f" Commands:  Type {COLOR_YELLOW}/help{COLOR_RESET} for commands or {COLOR_YELLOW}exit{COLOR_RESET} to quit.")
    print(f"{COLOR_CYAN}{'-' * 60}{COLOR_RESET}\n")


def print_help() -> None:
    """Displays available in-chat commands."""
    print(f"\n{COLOR_MAGENTA}{STYLE_BRIGHT}Available Commands:{COLOR_RESET}")
    print(f"  {COLOR_YELLOW}/help{COLOR_RESET}             - Show this help menu")
    print(f"  {COLOR_YELLOW}/clear{COLOR_RESET} or {COLOR_YELLOW}/reset{COLOR_RESET}  - Clear conversation history and start fresh")
    print(f"  {COLOR_YELLOW}/model <name>{COLOR_RESET}     - Change current model (e.g., /model gpt-4o)")
    print(f"  {COLOR_YELLOW}/system <prompt>{COLOR_RESET}  - Update system persona / instructions")
    print(f"  {COLOR_YELLOW}/history{COLOR_RESET}          - Show current conversation message count")
    print(f"  {COLOR_YELLOW}exit{COLOR_RESET} or {COLOR_YELLOW}quit{COLOR_RESET}      - Exit the chatbot\n")


def get_client_and_config():
    """Initializes the OpenAI client and determines the appropriate AI model and backend."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    base_url = os.environ.get("OPENAI_BASE_URL", "").strip()

    is_placeholder = (
        not api_key or
        api_key in ("your_openai_api_key_here", "none", "free", "demo", "null")
    )

    if is_placeholder and not base_url:
        # Free AI Mode: Works without any OpenAI account or API key!
        client = OpenAI(
            base_url="https://text.pollinations.ai/openai",
            api_key="none",
            timeout=12.0
        )
        raw_model = os.environ.get("OPENAI_MODEL", "openai").strip()
        model_name = "openai" if raw_model in ("gpt-4o-mini", "openai") else raw_model
        display_name = f"Free AI Cloud ({model_name}) [No Account Required]"
    else:
        # Official OpenAI API Mode
        client = OpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        model_name = os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip()
        display_name = f"OpenAI ({model_name})"

    return client, model_name, display_name


def main() -> None:
    """Main execution loop for the chatbot."""
    client, model_name, display_name = get_client_and_config()

    default_system_prompt = (
        "You are an expert Python programming assistant. "
        "Answer all user questions clearly, directly, and concisely with working code examples. "
        "Do not repeat words, do not chant, and do not output internal reasoning tokens."
    )

    conversation_history = [
        {"role": "system", "content": default_system_prompt}
    ]

    print_banner(display_name)

    while True:
        try:
            # User input prompt
            user_input = input(f"{COLOR_GREEN}{STYLE_BRIGHT}You > {COLOR_RESET}").strip()

            # Skip empty inputs
            if not user_input:
                continue

            # Check exit commands
            if user_input.lower() in ("exit", "quit", "q", "/exit", "/quit"):
                print(f"\n{COLOR_CYAN}👋 Goodbye! Have a wonderful day.{COLOR_RESET}\n")
                break

            # Handle commands
            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1].strip() if len(parts) > 1 else ""

                if cmd == "/help":
                    print_help()
                    continue

                elif cmd in ("/clear", "/reset"):
                    system_msg = conversation_history[0] if conversation_history else {"role": "system", "content": default_system_prompt}
                    conversation_history = [system_msg]
                    print(f"{COLOR_YELLOW}✨ Conversation history cleared.{COLOR_RESET}\n")
                    continue

                elif cmd == "/model":
                    if not arg:
                        print(f"{COLOR_YELLOW}Current model: {model_name}. Usage: /model <model_name>{COLOR_RESET}\n")
                    else:
                        model_name = arg
                        print(f"{COLOR_YELLOW}Switched model to: {model_name}{COLOR_RESET}\n")
                    continue

                elif cmd == "/system":
                    if not arg:
                        print(f"{COLOR_YELLOW}Current system prompt:{COLOR_RESET} {conversation_history[0]['content']}\n")
                    else:
                        conversation_history[0] = {"role": "system", "content": arg}
                        print(f"{COLOR_YELLOW}System prompt updated and set as active.{COLOR_RESET}\n")
                    continue

                elif cmd == "/history":
                    turns = (len(conversation_history) - 1) // 2
                    print(f"{COLOR_CYAN}Total messages: {len(conversation_history)} ({turns} user turns){COLOR_RESET}\n")
                    continue

                else:
                    print(f"{COLOR_RED}Unknown command '{cmd}'. Type /help for available commands.{COLOR_RESET}\n")
                    continue

            # Append user message to history
            conversation_history.append({"role": "user", "content": user_input})

            # Check for instant smart knowledge answer
            instant = get_instant_answer(user_input)

            # Print prompt for AI response
            print(f"{COLOR_CYAN}{STYLE_BRIGHT}AI > {COLOR_RESET}", end="", flush=True)

            full_response = ""

            try:
                # Try standard API call
                response = client.chat.completions.create(
                    model=model_name,
                    messages=conversation_history
                )
                if response.choices and len(response.choices) > 0:
                    candidate = response.choices[0].message.content or ""
                    # Check for repetitive garbage tokens like "om om om"
                    if candidate and not re.search(r"\b(om\s+){3,}", candidate, re.IGNORECASE):
                        full_response = candidate
            except Exception:
                pass

            # Fallback to instant knowledge answer if cloud response failed or was garbled
            if not full_response:
                if instant:
                    full_response = instant
                else:
                    full_response = (
                        "I am here to help you write and debug Python code! "
                        "Try asking me: 'How do I check even or odd?', 'How do I sort a list?', "
                        "or paste your Python code to get help."
                    )

            print(full_response + "\n")
            conversation_history.append({"role": "assistant", "content": full_response})

        except KeyboardInterrupt:
            print(f"\n\n{COLOR_CYAN}Session interrupted. Type 'exit' to quit or continue chatting.{COLOR_RESET}\n")
            continue
        except EOFError:
            print(f"\n{COLOR_CYAN}👋 Goodbye!{COLOR_RESET}\n")
            break


if __name__ == "__main__":
    main()
