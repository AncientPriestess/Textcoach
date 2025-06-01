import streamlit as st
import openai
import requests
from datetime import datetime

# ✅ Set your OpenAI API key securely
openai.api_key = st.secrets["OPENAI_API_KEY"]
SHEETDB_ENDPOINT = "https://sheetdb.io/api/v1/rmm73p10teqed"  # Replace with your own endpoint

# ========== 💌 Collect Email ==========
st.sidebar.title("🔓 Free Access or Unlock Premium")
user_email = st.sidebar.text_input("Enter your email to start (required):")

if not user_email:
    st.sidebar.warning("Please enter your email to continue.")
    st.stop()

# ========== 🧮 Check Usage ==========
def get_usage_count(email):
    res = requests.get(f"{SHEETDB_ENDPOINT}/search?email={email}")
    if res.status_code == 200 and res.json():
        return int(res.json()[0]["count"])
    return 0

def update_usage_count(email):
    current = get_usage_count(email)
    if current >= 2:
        return False
    requests.delete(f"{SHEETDB_ENDPOINT}/email/{email}")
    data = {"data": [{"email": email, "count": current + 1}]}
    requests.post(SHEETDB_ENDPOINT, json=data)
    return True

# Check and enforce limit
usage_count = get_usage_count(user_email)
if usage_count >= 2:
    st.error("🚫 You’ve used your 2 free attempts. [Unlock full access](https://coachnofluff.gumroad.com/l/textcoach) to continue.")
    st.stop()

# ========== 💬 App UI ==========
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")

st.markdown("**📥 Paste the message or conversation below:**")

mode = st.radio(
    "Select message type:",
    ["Single Message", "Full Conversation Thread"],
    index=0,
    disabled=True,
    help="🔒 Full thread analysis is for premium members only."
)

st.markdown("📝 Optional Context / Backstory:")
st.text_area(
    label="",
    placeholder="🔒 Upgrade to unlock this field and get deeper insights.",
    height=100,
    disabled=True
)

text_input = st.text_area("📥 Type/paste his message(s) below:", height=200)

# ========== 🤖 AI Logic ==========
def analyze_text_and_generate_reply(text_input):
    style_reference = """
Respond in this format and tone:

Red Flag(s):
[Call out breadcrumbing, vague language, avoidance of commitment, emotional distance, etc.]

Green Flag(s):
[Only mention if genuinely present. If not, say: “None here. A man who knows what he wants doesn’t dodge clarity.”]

What This Means:
[Explain what’s really going on. Be blunt but empowering.]

Suggested Reply:
[Provide a confident, short response — or recommend silence.]

Final Word:
[Reinforce her value and give her clarity. End with a truth bomb.]
"""

    prompt = f"""
You're a sharp male dating coach with big brother energy. A woman received this message:

{text_input}

Use the format and tone below to respond directly to her — no fluff, just clarity and power.

{style_reference}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a seasoned male dating coach who helps women spot emotional manipulation and respond with bold clarity. Use magnetic, concise language and always speak directly to her in 5 structured sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, Final Word.",
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message.content

# ========== ✅ Handle Submit ==========
if st.button("🔍 Analyze Message"):
    suspicious_phrases = ["you:", "him:", "her:", "me:", "context:", "backstory:", "sent at", "—", ":", "\n-"]
    looks_like_thread = any(p in text_input.lower() for p in suspicious_phrases) or text_input.count('\n') > 2

    if looks_like_thread:
        st.error("🚫 Thread/context analysis is premium only. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach).")
    else:
        success = update_usage_count(user_email)
        if not success:
            st.error("🚫 You’ve used your 2 free attempts. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach) to continue.")
            st.stop()
        with st.spinner("Analyzing..."):
            result = analyze_text_and_generate_reply(text_input)
            st.markdown("### 👑 Coach’s Response")
            st.write(result)

# ========== 💎 Sidebar Promotion ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("📩 Questions? markwestoncoach@gmail.com")
