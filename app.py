import streamlit as st
import tiktoken
import re

# ---------- CONFIG ----------
st.set_page_config(page_title="LLM Token Estimator", layout="centered")

# ---------- TOKENIZER ----------
@st.cache_resource
def load_tokenizer():
    return tiktoken.encoding_for_model("gpt-4o")

enc = load_tokenizer()

def count_tokens(text):
    return len(enc.encode(text))

# ---------- TASK DETECTION ----------
def detect_task(prompt):
    prompt = prompt.lower()

    if "summarize" in prompt or "summary" in prompt:
        return "summarization"
    elif "explain" in prompt or "describe" in prompt:
        return "explanation"
    elif "code" in prompt or "python" in prompt:
        return "code"
    elif "list" in prompt or "points" in prompt:
        return "list"
    else:
        return "general"

# ---------- CONSTRAINT EXTRACTION ----------
def extract_constraints(prompt):
    prompt = prompt.lower()

    # Word constraint (e.g., "20 words")
    match = re.search(r'(\d+)\s*words?', prompt)
    if match:
        words = int(match.group(1))
        return int(words * 1.3)  # words → tokens

    # Sentence constraint
    match = re.search(r'(\d+)\s*sentences?', prompt)
    if match:
        sentences = int(match.group(1))
        return sentences * 20  # approx tokens per sentence

    return None

# ---------- BASIC ESTIMATION ----------
def estimate_basic(input_tokens, mode):
    multipliers = {
        "Concise": 0.5,
        "Normal": 1.0,
        "Detailed": 1.8,
        "Code": 0.8,
        "Notebook": 3.0
    }
    return int(input_tokens * multipliers.get(mode, 1.0))

# ---------- SMART ESTIMATION ----------
def estimate_smart(input_tokens, prompt, mode):
    task = detect_task(prompt)
    constraint = extract_constraints(prompt)

    # Priority: constraints override everything
    if constraint:
        return constraint, task, "constraint-based"

    if task == "summarization":
        return int(input_tokens * 0.3), task, "task-based"

    elif task == "explanation":
        base = 150
        factor = 1.2 if mode == "Detailed" else 0.8
        return int(base + input_tokens * factor), task, "task-based"

    elif task == "code":
        return int(100 + input_tokens * 0.6), task, "task-based"

    elif task == "list":
        return 100, task, "task-based"

    else:
        return estimate_basic(input_tokens, mode), task, "fallback"

# ---------- UI ----------
st.title("🧠 LLM Token Usage Estimator")

prompt = st.text_area("Enter your prompt:", height=200)

col1, col2 = st.columns(2)

with col1:
    mode = st.selectbox(
        "Expected Output Type",
        ["Concise", "Normal", "Detailed", "Code", "Notebook"]
    )

with col2:
    context_options = {
        "ChatGPT (~128K)": 128000,
        "Claude (~200K)": 200000,
        "Gemini (~1M)": 1000000
    }

    selected_model = st.selectbox(
        "Context Window",
        list(context_options.keys())
    )

    context_limit = context_options[selected_model]

# ---------- SMART TOGGLE ----------
use_smart = st.checkbox("🧠 Use Smart Estimation (recommended)", value=True)

# ---------- LIVE TOKEN COUNT ----------
if prompt:
    live_tokens = count_tokens(prompt)
    st.caption(f"🧮 Live Input Tokens: {live_tokens}")

# ---------- PROCESS ----------
if st.button("Estimate Tokens"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        input_tokens = count_tokens(prompt)

        if use_smart:
            output_tokens, task, method = estimate_smart(input_tokens, prompt, mode)
        else:
            output_tokens = estimate_basic(input_tokens, mode)
            task = "N/A"
            method = "basic"

        total_tokens = input_tokens + output_tokens

        # Safety check
        if not isinstance(context_limit, int):
            st.error("Context limit error")
            st.stop()

        usage_percent = (total_tokens / context_limit) * 100

        # ---------- OUTPUT ----------
        st.subheader("📊 Results")

        st.write(f"**Input Tokens:** {input_tokens}")
        st.write(f"**Estimated Output Tokens:** {output_tokens}")
        st.write(f"**Total Tokens:** {total_tokens}")
        st.write(f"**Context Usage:** {usage_percent:.2f}%")

        # ---------- INSIGHTS ----------
        st.markdown("### 🧠 Estimation Insights")
        st.write(f"**Detected Task:** {task}")
        st.write(f"**Estimation Method:** {method}")

        # ---------- PROGRESS ----------
        st.progress(min(int(usage_percent), 100))

        # ---------- WARNINGS ----------
        if usage_percent > 90:
            st.error("⚠️ Very high usage! Likely to hit limit.")
        elif usage_percent > 75:
            st.warning("⚠️ High usage. Be cautious.")
        else:
            st.success("✅ Safe range.")
