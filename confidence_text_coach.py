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

# ========== 👑 Message Mode Selection ==========
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

# ========== 📥 Message Input ==========
text_input = st.text_area("📥 Message(s):", height=200)

# ========== 📝 Optional Context ==========
st.markdown("**📝 Optional Context / Backstory:**")

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

# ========== 🤖 AI Logic ==========
def analyze_text_and_generate_reply(text_input, context_input="", is_thread=False):
    style_reference = """
Respond in this format and tone:

👑 Coach’s Response

Red Flag(s):
[Point out vague language, avoidance of clarity, or emotional unavailability in bold, no-fluff terms.]

Green Flag(s):
[Only if warranted. If none, say: “None here. A man who knows what he wants doesn’t dodge clarity.”]

What This Means:
[Break down his intent — call out strategies disguised as confusion.]

Suggested Reply:
[Give her a bold, confident one-liner — or recommend silence.]

Final Word:
[Remind her of her worth. End with clarity and power — like a wake-up call.]
"""

    prompt = f"""
You're a sharp male dating coach with big brother energy. A woman received this message{' thread' if is_thread else ''} from a man:

Message:
{text_input}

{f"Context / Backstory: {context_input}" if context_input else ""}

Use the guide below and speak directly to her:

{style_reference}
"""

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a seasoned male dating coach who breaks down manipulative behavior, red flags, and unclear dating messages using a bold, big-brother tone. You speak directly to women with clarity, protectiveness, and charisma. Your format includes 5 sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, and Final Word — each written like a magnetic wake-up call.",
            },
            {"role": "user", "content": prompt},
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
        st.error("🚫 This looks like more than a single message. Full conversation analysis and context/backstory features are for premium users only. [Unlock full access](https://your-gumroad-link.com) to continue.")
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

