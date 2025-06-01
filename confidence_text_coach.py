import streamlit as st
import openai
import requests
from datetime import datetime

# ✅ Set your OpenAI API key securely (configured in Hugging Face Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]
SHEET_API_URL = "https://sheetdb.io/api/v1/rmm73p10teqed"

# ========== 🔒 Access Control ==========
st.sidebar.title("🔐 Unlock Full Access")

if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

user_email = st.sidebar.text_input("Enter your email (required):")
password = st.sidebar.text_input("Enter access code", type="password")

if st.sidebar.button("Activate Access"):
    if password == st.secrets["ACCESS_CODE"]:
        st.session_state.access_granted = True
        st.sidebar.success("✅ Access granted! You’re now in Premium Mode.")
    else:
        st.sidebar.error("❌ Invalid code. Try again.")

ACCESS_GRANTED = st.session_state.access_granted

if ACCESS_GRANTED:
    st.sidebar.success("🌟 Premium Access Active")
    if st.sidebar.button("Cancel Membership"):
        st.sidebar.warning("To cancel, email markwestoncoach@gmail.com")
else:
    st.sidebar.info("🔓 Free Version (2 daily attempts)")

# ========== Usage Tracking ==========
def get_user_usage(email):
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        res = requests.get(f"{SHEET_API_URL}/search?search_by=columns&email={email}&date={today}")
        if res.status_code == 200 and res.json():
            return int(res.json()[0].get("count", 0))
    except:
        pass
    return 0

def log_usage(email):
    today = datetime.now().strftime("%Y-%m-%d")
    usage = get_user_usage(email)
    headers = {"Content-Type": "application/json"}

    if usage == 0:
        requests.post(SHEET_API_URL, json={"data": {"email": email, "date": today, "count": 1}}, headers=headers)
    else:
        requests.delete(f"{SHEET_API_URL}/search?search_by=columns", json={"search": {"email": email, "date": today}}, headers=headers)
        requests.post(SHEET_API_URL, json={"data": {"email": email, "date": today, "count": usage + 1}}, headers=headers)

# ========== App UI ==========
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")

col1, col2 = st.columns(2)
with col1:
    mode = st.radio("Choose format:", ["Single Message", "Full Conversation Thread"], disabled=not ACCESS_GRANTED, index=0)

st.markdown("📝 Optional Context / Backstory:")
if ACCESS_GRANTED:
    context_input = st.text_area("", placeholder="Add any relevant context...", height=100)
else:
    st.text_area("", "🔒 Upgrade to unlock this field and share more details.", height=100, disabled=True)
    context_input = ""

text_input = st.text_area("📥 Type/paste his message(s) below:", height=200)

# ========== AI Logic ==========
def analyze_text_and_generate_reply(text_input, context_input="", is_thread=False):
    style_reference = """
Respond in this format and tone:

Red Flag(s):
[Call out breadcrumbing, vague language, avoidance of commitment, emotional distance, etc.]

Green Flag(s):
[Only mention if genuinely present. If not, say: "None here. A man who knows what he wants doesn’t dodge clarity."]

What This Means:
[Explain what’s really going on. Be blunt but empowering.]

Suggested Reply:
[Provide a confident, short response — or recommend silence.]

Final Word:
[Reinforce her value and give her clarity. End with a truth bomb.]
"""
    prompt_header = f"""
You're a sharp male dating coach with big brother energy. A woman has shared a {'text thread' if is_thread else 'single message'} and wants your insight.
"""
    if context_input.strip():
        prompt_context = f"Here’s the backstory/context she provided:\n{context_input.strip()}\n\n"
    else:
        prompt_context = ""

    full_prompt = f"""
{prompt_header}
{prompt_context}
Here’s what she received:
{text_input}

Use the format and tone below to respond directly to her — no fluff, just clarity and power.

{style_reference}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a seasoned male dating coach who helps women spot emotional manipulation and respond with bold clarity. Use magnetic, concise language and always speak directly to her in 5 structured sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, Final Word."},
            {"role": "user", "content": full_prompt},
        ]
    )
    return response.choices[0].message.content

# ========== Analyze Message ==========
if st.button("🔍 Analyze Message"):
    if not user_email:
        st.error("Please enter your email to continue.")
    else:
        usage = get_user_usage(user_email)
        if not ACCESS_GRANTED and usage >= 2:
            st.error("🚫 You’ve reached your free limit today. Unlock full access to continue.")
        else:
            with st.spinner("Analyzing..."):
                result = analyze_text_and_generate_reply(
                    text_input, context_input, is_thread=(mode == "Full Conversation Thread")
                )
                st.markdown("### 👑 Coach’s Response")
                st.write(result)
                if not ACCESS_GRANTED:
                    log_usage(user_email)

# ========== Promo ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("📩 Questions? markwestoncoach@gmail.com")
