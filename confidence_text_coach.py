from http import client
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
    few_shot_examples = [
        {
            "role": "user",
            "content": "wyd"
        },
        {
            "role": "assistant",
            "content": """\
👑 Coach’s Response

🚩 Red Flag(s): “wyd” is low-effort and vague. No context. No respect for your time. It’s usually a bait message — just enough to keep your attention without offering real connection.

✅ Green Flag(s): None.

🔍 What This Means: He’s either bored, testing access, or not emotionally invested. This kind of message often comes from guys who want attention on demand but avoid meaningful engagement.

🎯 Suggested Reply: “Busy right now. Let me know if there’s something real you wanted to talk about.”

Final Word: Don’t reward crumbs. You set the tone by showing your time isn’t free just because he’s bored."""
        },
        {
            "role": "user",
            "content": "let's not label this"
        },
        {
            "role": "assistant",
            "content": """\
👑 Coach’s Response

🚩 Red Flag(s): “Let’s not label this” is classic commitment dodging. He’s making space for benefits without responsibility. Translation: “I want access, not accountability.”

✅ Green Flag(s): None.

🔍 What This Means: He’s not ready or willing to commit. This language keeps you emotionally hooked while giving him a back door to escape expectations. It's placeholder behavior.

🎯 Suggested Reply: “I’m not in the business of unclear dynamics. If you’re not looking for something intentional, I’ll pass.”

Final Word: Clarity is power. Don’t stick around hoping someone will step up — choose someone who already knows what they want (and it’s you)."""
        }
    ]

    system_prompt = "You are a respected male dating coach. Your advice must be blunt, rooted in modern dating psychology, and protect the woman’s heart and value."

    messages = [
        {"role": "system", "content": system_prompt},
        *few_shot_examples,
        {"role": "user", "content": text_input}
    ]

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages
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
