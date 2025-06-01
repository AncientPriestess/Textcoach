import streamlit as st
import openai
from datetime import datetime

# ✅ Set your OpenAI API key securely (configured in Hugging Face Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== 🔒 Access Control ==========
st.sidebar.title("🔐 Unlock Full Access")
password = st.sidebar.text_input("Enter access code", type="password")
ACCESS_GRANTED = (password == "textqueen2024")  # Change this to match your Gumroad unlock code

# ========== 🧮 Daily Limit for Free Users ==========
if "usage" not in st.session_state:
    st.session_state.usage = {
        "date": datetime.now().date(),
        "count": 0
    }

if st.session_state.usage["date"] != datetime.now().date():
    st.session_state.usage = {
        "date": datetime.now().date(),
        "count": 0
    }

MAX_FREE_USES = 2
within_limit = st.session_state.usage["count"] < MAX_FREE_USES

# ========== 💬 App UI ==========
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")

st.markdown("Paste the **message or full thread** below:")

mode = st.radio("Is this a single message or full conversation?", ["Single Message", "Full Conversation Thread"])
text_input = st.text_area("📥 Message(s):", height=200)

# ========== 🤖 AI Logic ==========
def analyze_text_and_generate_reply(text_input, is_thread=False):
    if is_thread:
        prompt = f"""
You're a respected male dating coach who helps women decode men's behavior and respond with confidence. A woman just shared a full text thread from a guy.

Speak to her directly, like a big brother who’s been around the block:
- ✅ Call out any green flags
- 🚩 Call out red flags (breadcrumbing, emotional distance, etc.)
- 🎯 Tell her exactly what to say or do next — or if silence is the power move
- Be concise, deep, and magnetic. No fluff. No therapy talk.

Here’s the thread:
{text_input}
"""
    else:
        prompt = f"""
You're a sharp male dating coach with big brother energy. A woman received this one message from a man:

{text_input}

Break it down for her clearly:
- ✅ Spot green flags
- 🚩 Spot red flags
- 🧠 Interpret the intent based on tone, timing, and style
- 💬 Suggest a powerful response (or recommend silence)
- End by reminding her what she’s worth

Speak directly to her, not about her. Make it clear, empowering, and short.
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a seasoned male dating coach who protects women from emotional manipulation and teaches them how to respond like queens."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content

# ========== ✅ Handle Submit ==========
if st.button("🔍 Analyze Message"):
    if ACCESS_GRANTED or within_limit:
        with st.spinner("Analyzing..."):
            result = analyze_text_and_generate_reply(text_input, is_thread=(mode == "Full Conversation Thread"))
            st.markdown("### 👑 Coach’s Response")
            st.write(result)
            if not ACCESS_GRANTED:
                st.session_state.usage["count"] += 1
    else:
        st.error("You’ve reached your free limit today. Unlock full access to continue.")
        st.markdown("🔓 [Upgrade here for unlimited access](https://your-gumroad-link.com)")

# ========== 💎 Sidebar Promotion ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://your-gumroad-link.com)")
st.sidebar.markdown("📩 Questions? hello@yourbrand.com")
