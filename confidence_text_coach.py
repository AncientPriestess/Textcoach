import streamlit as st
import openai
from datetime import datetime

# ✅ Set your OpenAI API key securely (configured in Hugging Face Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== 🔒 Access Control ==========
st.sidebar.title("🔐 Unlock Full Access")

if "access_granted" not in st.session_state:
    st.session_state.access_granted = False

password = st.sidebar.text_input("Enter access code", type="password")

if st.sidebar.button("Activate Access"):
    if password == st.secrets["ACCESS_CODE"]:
        st.session_state.access_granted = True
        st.sidebar.success("✅ Access granted! You’re now in Premium Mode.")
    else:
        st.sidebar.error("❌ Invalid code. Try again.")

ACCESS_GRANTED = st.session_state.access_granted


# 🔄 Access Status Indicator + Cancel Prompt
if ACCESS_GRANTED:
    st.sidebar.success("🌟 Premium Access Active")
    if st.sidebar.button("Cancel Membership"):
        st.sidebar.warning("To cancel, email hello@yourbrand.com.")
else:
    st.sidebar.info("🔓 Free Version (2 daily attempts)")
    if "usage" in st.session_state:
        remaining = max(0, 2 - st.session_state.usage.get("count", 0))
        st.sidebar.write(f"Free attempts left today: {remaining}")

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
st.markdown("Paste the **message** below:")

# ✅ Only allow "Full Conversation" mode for access members
if ACCESS_GRANTED:
    mode = st.radio("Is this a single message or full conversation?", ["Single Message", "Full Conversation Thread"])
else:
    mode = "Single Message"
    st.warning("🚨 Want the full breakdown? [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach) to unlock full conversation analysis and get deeper insights into his patterns.")

# 📥 Message input
text_input = st.text_area("📥 Message(s):", height=200)

# ✅ Optional backstory (only for access members)
if ACCESS_GRANTED:
    context_input = st.text_area("📝 Optional Context / Backstory (optional but helpful):", height=100)
else:
    context_input = ""

# ========== 🤖 AI Logic ==========

def analyze_text_and_generate_reply(text_input, is_thread=False):
    style_reference = """
Respond in this format and tone:

Red Flag(s):
[Point out behaviors like breadcrumbing, vague language, avoidance of commitment, etc. Use bold, blunt language. Example: “‘Let’s not label this’ is code for wanting perks without responsibility.”]

Green Flag(s):
[Only include if truly warranted — otherwise say: “None here. A man who knows what he wants doesn't dodge clarity.”]

What This Means:
[Interpret his intent — make it clear if he's unsure, playing games, or stringing her along. Focus on strategy, not confusion.]

Suggested Reply:
[Give her a confident, emotionally intelligent one-liner to respond or walk away — short, direct, and self-respecting.]

Final Word:
[Empower her. Remind her of her worth. End with a confident truth bomb, not therapy fluff.]
"""

    if is_thread:
        prompt = f"""
You're a sharp, emotionally intelligent male dating coach with big brother energy. A woman just shared a full text thread from a guy.

Decode his behavior using the style guide below. Speak directly to her. Don’t sugarcoat. Be concise, magnetic, and protective of her energy.

Thread:
{text_input}

{style_reference}
"""
    else:
        prompt = f"""
You're a sharp, emotionally intelligent male dating coach with big brother energy. A woman received this one message from a man:

{text_input}

Decode his behavior using the style guide below. Speak directly to her. Don’t sugarcoat. Be concise, magnetic, and protective of her energy.

{style_reference}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
           {"role": "system", "content": "You are a seasoned male dating coach who breaks down manipulative behavior, red flags, and unclear dating messages using a bold, big-brother tone. You speak directly to women with clarity, protectiveness, and charisma. Your format includes 5 sections titled: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, and Final Word — each written like a magnetic wake-up call."},
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
        st.markdown("🔓 [Upgrade here for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")

# ========== 💎 Sidebar Promotion ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("📩 Questions? markwestoncoach@gmail.com")

