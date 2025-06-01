import streamlit as st
import openai
from datetime import datetime
SHEET_API_URL = "https://sheetdb.io/api/v1/rmm73p10teqed"  # Use your actual endpoint

# ========== 🔒 Premium Access Control ==========
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

# 🔄 Access Status Display
if ACCESS_GRANTED:
    st.sidebar.success("🌟 Premium Access Active")
    if st.sidebar.button("Cancel Membership"):
        st.sidebar.warning("To cancel, email markwestoncoach@gmail.com")
else:
    st.sidebar.info("🔓 Free Version (2 daily attempts)")
    st.sidebar.markdown("💎 [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach)")

# ========== 📧 Email Login for Free Users ==========
user_email = ""
if not ACCESS_GRANTED:
    st.markdown("**📧 Enter your email to use the free version (required):**")
    user_email = st.text_input("Email address", key="email_input")

    def email_is_valid(email):
        return "@" in email and "." in email

    if user_email and not email_is_valid(user_email):
        st.error("Please enter a valid email address.")

# ========== 🔁 Email-Based Usage Tracking ==========
def get_user_usage(email):
    try:
        response = requests.get(f"{SHEET_API_URL}/search?email={email}&date={date.today()}")
        if response.status_code == 200 and response.json():
            return int(response.json()[0].get("count", 0))
        else:
            return 0
    except:
        return 0

def log_usage(email):
    try:
        usage = get_user_usage(email)
        if usage == 0:
            requests.post(SHEET_API_URL, json={
                "data": {"email": email, "date": str(date.today()), "count": 1}
            })
        else:
            record = requests.get(f"{SHEET_API_URL}/search?email={email}&date={date.today()}").json()[0]
            record_id = record["id"]
            requests.patch(f"{SHEET_API_URL}/id/{record_id}", json={"data": {"count": usage + 1}})
    except Exception as e:
        print("Logging failed:", e)

# ========== 💬 App UI ==========
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")
st.markdown("Paste the **message** below:")

# ========== 👑 Message Type Selection ==========
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

# ✅ Set your OpenAI API key securely (configured in Hugging Face Secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

    # ========== 📝 Optional Context ==========
st.markdown("📝 Optional Context / Backstory:")
if ACCESS_GRANTED:
    context_input = st.text_area(
        label="",
        placeholder="Add any relevant context (e.g. how long you've been seeing him, recent arguments, etc.)",
        height=100
    )
else:
    st.text_area(
        label="",
        placeholder="🔒 Upgrade to unlock this field and share more details that make your analysis even sharper.",
        height=100,
        disabled=True
    )
    context_input = ""

# ========== 📥 Message Input ==========
text_input = st.text_area("📥 Type/paste his message(s) below:", height=200)

# ========== 🤖 AI Logic ==========
def analyze_text_and_generate_reply(text_input, context_input="", is_thread=False):
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
            {
                "role": "system",
                "content": "You are a seasoned male dating coach who helps women spot emotional manipulation and respond with bold clarity. Use magnetic, concise language and always speak directly to her in 5 structured sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, Final Word.",
            },
            {"role": "user", "content": full_prompt},
        ],
    )

    return response.choices[0].message.content


# ========== ✅ Handle Submit ==========
if st.button("🔍 Analyze Message"):
    # === Detect thread or backstory attempts for unpaid users ===
    suspicious_phrases = ["you:", "him:", "her:", "me:", "\n\n", "context:", "backstory:", "sent at", "—", ":", "\n-"]
    looks_like_thread = any(phrase.lower() in text_input.lower() for phrase in suspicious_phrases)
    multiline = text_input.count('\n') > 2

    if not ACCESS_GRANTED and (looks_like_thread or multiline):
        st.error("🚫 This looks like more than a single message. Full conversation analysis and context/backstory features are for premium users only. [Unlock full access](https://coachnofluff.gumroad.com/l/textcoach) to continue.")
    elif ACCESS_GRANTED or within_limit:
        with st.spinner("Analyzing..."):
            result = analyze_text_and_generate_reply(
                text_input, context_input, is_thread=(mode == "Full Conversation Thread")
            )
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

