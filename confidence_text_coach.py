import streamlit as st
import openai
import requests
from datetime import datetime, date

# ✅ Your OpenAI Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ Your SheetDB URL (replace with yours)
SHEET_API_URL = "https://sheetdb.io/api/v1/rmm73p10teqed"

# ========== 🔐 Premium Access ==========
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

if ACCESS_GRANTED:
    st.sidebar.success("🌟 Premium Access Active")
    if st.sidebar.button("Cancel Membership"):
        st.sidebar.warning("To cancel, email markwestoncoach@gmail.com")
else:
    st.sidebar.info("🔓 Free Version (2 daily attempts)")
    st.sidebar.markdown("💎 [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach)")

# ========== 📧 Email (Free Users) ==========
user_email = ""
email_required = False

if not ACCESS_GRANTED:
    st.markdown("**📧 Enter your email to use the free version (required):**")
    user_email = st.text_input("Email address", key="email_input")

    def email_is_valid(email):
        return "@" in email and "." in email

    email_required = not email_is_valid(user_email)

    if user_email and email_required:
        st.error("Please enter a valid email address.")

# ========== Usage Tracking ==========
def get_user_usage(user_email):
    try:
        today_str = datetime.now().strftime("%Y-%m-%d")
        response = requests.get(f"{SHEET_API_URL}/search?email={user_email}&date={today_str}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return int(data[0].get("count", 0))
        return 0
    except:
        return 0


def log_usage(user_email):
    try:
        # ✅ Use consistent date format to prevent serial number issue
        today_str = datetime.now().strftime("%Y-%m-%d")
        current_usage = get_user_usage(user_email)
        headers = {"Content-Type": "application/json"}

        if current_usage == 0:
            requests.post(SHEET_API_URL, json={
                "data": {"email": user_email, "date": today_str, "count": 1}
            }, headers=headers)
        else:
            requests.patch(f"{SHEET_API_URL}/search", json={
                "data": {"count": current_usage + 1},
                "search": {"email": user_email, "date": today_str}
            }, headers=headers)
    except Exception as e:
        st.write("❌ Logging error:", e)

# ========== UI ==========
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")
st.markdown("Paste the **message** below:")

# ========== Message Mode ==========
st.markdown("**🔍 Select Message Type:**")

col1, col2 = st.columns(2)
with col1:
    mode = st.radio(
        "Choose format:",
        ["Single Message", "Full Conversation Thread"],
        disabled=not ACCESS_GRANTED,
        index=0 if not ACCESS_GRANTED else None,
        help=None if ACCESS_GRANTED else "Upgrade to unlock full conversation analysis"
    )

# ========== Optional Context ==========
st.markdown("**📝 Optional Context / Backstory:**")
if ACCESS_GRANTED:
    context_input = st.text_area(
        label="",
        placeholder="Add relevant context (e.g. how long you've been seeing him, recent arguments, etc.)",
        height=100
    )
else:
    st.text_area(
        label="",
        placeholder="🔒 Upgrade to unlock this field and give more context for sharper analysis.",
        height=100,
        disabled=True
    )
    context_input = ""

# ========== Message Input ==========
text_input = st.text_area("📥 Type/paste his message(s) below:", height=200)

# ========== AI Response Logic ==========
def analyze_text_and_generate_reply(text_input, context_input="", is_thread=False):
    style_reference = """
Respond in this format and tone:

👑 Coach’s Response

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

    prompt_header = f"You're a sharp male dating coach with big brother energy. A woman has shared a {'text thread' if is_thread else 'single message'} and wants your insight.\n\n"
    prompt_context = f"Here’s the backstory/context she provided:\n{context_input.strip()}\n\n" if context_input.strip() else ""

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
            {
                "role": "system",
                "content": "You are a seasoned male dating coach who helps women spot emotional manipulation and respond with bold clarity. Use magnetic, concise language and always speak directly to her in 5 structured sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, Final Word.",
            },
            {"role": "user", "content": full_prompt},
        ],
    )

    return response.choices[0].message.content

# ========== Analyze Button ==========
if st.button("🔍 Analyze Message"):
    suspicious_phrases = ["you:", "him:", "her:", "me:", "\n\n", "context:", "backstory:", "sent at", "—", ":", "\n-"]
    looks_like_thread = any(phrase.lower() in text_input.lower() for phrase in suspicious_phrases)
    multiline = text_input.count('\n') > 2
    is_thread_attempt = looks_like_thread or multiline

    # FREE USER FLOW
    if not ACCESS_GRANTED:
        if not user_email or email_required:
            st.warning("📧 Please enter a valid email to use the free version.")
        else:
            current_usage = get_user_usage(user_email)

            if current_usage >= 2:
                st.error("🚫 You've reached your daily free limit. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach) to continue.")
            elif is_thread_attempt:
                st.error("🚫 This looks like more than a single message. Full conversation and backstory analysis are premium features. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach)")
            else:
                with st.spinner("Analyzing..."):
                    result = analyze_text_and_generate_reply(
                        text_input, context_input="", is_thread=False
                    )
                    st.markdown("### 👑 Coach’s Response")
                    st.write(result)
                    log_usage(user_email)

    # PREMIUM USER FLOW
    else:
        with st.spinner("Analyzing..."):
            result = analyze_text_and_generate_reply(
                text_input, context_input, is_thread=(mode == "Full Conversation Thread")
            )
            st.markdown("### 👑 Coach’s Response")
            st.write(result)

# ========== Sidebar Footer ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("📩 Questions? markwestoncoach@gmail.com")