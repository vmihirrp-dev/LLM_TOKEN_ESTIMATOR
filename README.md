# 🧠 LLM Token Usage Estimator

A simple tool to estimate token consumption for LLM prompts using a multiplier-based approach.

## Features
- Input prompt token counting (accurate via tiktoken)
- Output token estimation (based on output type)
- Total token calculation
- Context window usage tracking
- Supports ChatGPT, Claude, Gemini presets

## How it works
total_tokens = input_tokens + (input_tokens × multiplier)

## Output Modes
- Concise → 0.5x
- Normal → 1.0x
- Detailed → 1.8x
- Code → 0.8x
- Notebook → 3.0x

## Deployment
Deploy using Streamlit Community Cloud:
https://streamlit.io/cloud

## License
Free for personal use
