import streamlit as st
import tiktoken

# ---------- CONFIG ----------
st.set_page_config(page_title="LLM Token Estimator", layout="centered")

# ---------- TOKENIZER ----------
@st.cache_resource
def load_tokenizer():
    return tiktoken.encoding_for_model("gpt-4o")

enc = load_tokenizer()

def count_tokens(text):
    return len(enc.encode(text))

# ---------- ESTIMATION ----------
def estimate_output_tokens(input_tokens, mode):
    multipliers = {
        "Concise": 0.5,
        "Normal": 1.0,
        "Detailed": 1.8,
        "Code": 0.8,
        "Notebook": 3.0
    }
    return int(input_tokens * multipliers.get(mode, 1.0))

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
    context_limit = st.selectbox(
        "Context Window",
        {
            "ChatGPT (~128K)": 128000,
            "Claude (~200K)": 200000,
            "Gemini (~1M)": 1000000
        }
    )

# ---------- PROCESS ----------
if st.button("Estimate Tokens"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        input_tokens = count_tokens(prompt)
        output_tokens = estimate_output_tokens(input_tokens, mode)
        total_tokens = input_tokens + output_tokens
        usage_percent = (total_tokens / context_limit) * 100

        st.subheader("📊 Results")

        st.write(f"**Input Tokens:** {input_tokens}")
        st.write(f"**Estimated Output Tokens:** {output_tokens}")
        st.write(f"**Total Tokens:** {total_tokens}")
        st.write(f"**Context Usage:** {usage_percent:.2f}%")

        # Progress bar
        st.progress(min(int(usage_percent), 100))

        # Warnings
        if usage_percent > 90:
            st.error("⚠️ Very high usage! Likely to hit limit.")
        elif usage_percent > 75:
            st.warning("⚠️ High usage. Be cautious.")
        else:
            st.success("✅ Safe range.")
