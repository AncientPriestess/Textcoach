import streamlit as st
import openai
import requests

# ✅ Configure your SheetDB API
SHEETDB_ENDPOINT = "https://sheetdb.io/api/v1/rmm73p10teqed"

# ✅ OpenAI API Key (configured in Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== Sidebar UI ==========
st.sidebar.title("🔐 Unlock Full Access")

# Email capture
user_email = st.sidebar.text_input("Your email (for 2 free uses):")

# Unlock code input
password = st.sidebar.text_input("Got a code? Enter here:", type="password")
if st.sidebar.button("Activate Access"):
    if password == st.secrets["ACCESS_CODE"]:
        st.session_state.access_granted = True
        st.sidebar.success("✅ Premium access activated!")
    else:
        st.sidebar.error("❌ Invalid code")

ACCESS_GRANTED = st.session_state.get("access_granted", False)

# ========== Free Usage Logic ==========
def get_usage(email):
    res = requests.get(f"{SHEETDB_ENDPOINT}/search?email={email}")
    data = res.json()
    return data[0] if data else None

def log_usage(email, current_count):
    requests.delete(f"{SHEETDB_ENDPOINT}/email/{email}")
    new_payload = {"data": [{"email": email, "count": current_count + 1}]}
    requests.post(SHEETDB_ENDPOINT, json=new_payload)

# Check if user can analyze
can_analyze = False
usage = get_usage(user_email) if user_email else None
if user_email:
    if ACCESS_GRANTED:
        can_analyze = True
    elif not usage:
        can_analyze = True
    elif int(usage["count"]) < 2:
        can_analyze = True

# ========== AI Logic ==========
def analyze_text_and_generate_reply(text_input, context_input="", is_thread=False):
    style_reference = '''
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
'''

    prompt_header = f"You’re a sharp male dating coach with big brother energy. A woman has shared a {'text thread' if is_thread else 'single message'} and wants your insight.\n\n"
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
                "content": "You are a seasoned male dating coach who helps women spot emotional manipulation and respond with bold clarity. Use magnetic, concise language and always speak directly to her in 5 structured sections: Red Flag(s), Green Flag(s), What This Means, Suggested Reply, Final Word."
            },
            {"role": "user", "content": full_prompt},
        ],
    )
    return response.choices[0].message.content

# ========== UI ========== 
st.title("❤️‍🔥 Text Coach")
st.caption("Decode his message. Respond with confidence. Protect your peace.")

st.markdown("### 🧠 What’s going on?")
text_input = st.text_area("Paste *his* message here:", height=150)

st.markdown("### 📁 Message Type")
col1, col2 = st.columns(2)
with col1:
    mode = st.radio(
        "", ["Single Message", "Full Conversation Thread"],
        disabled=not ACCESS_GRANTED,
        index=0 if not ACCESS_GRANTED else None,
        help=None if ACCESS_GRANTED else "Upgrade to unlock full conversation analysis"
    )

st.markdown("### 📝 Extra Context (optional)")
if ACCESS_GRANTED:
    context_input = st.text_area(
        label="", placeholder="(Only if it helps: how long you’ve been talking, last convo, etc.)",
        height=100
    )
else:
    st.text_area(
        label="", placeholder="🔒 Premium feature. Upgrade to unlock this field.",
        height=100, disabled=True
    )
    context_input = ""

# ========== Detect Sneaky Threads ==========
suspicious_phrases = ["you:", "him:", "her:", "me:", "\n\n", "context:", "backstory:", "sent at", "—", ":", "\n-"]
looks_like_thread = any(phrase.lower() in text_input.lower() for phrase in suspicious_phrases)
multiline = text_input.count('\n') > 2

# ========== Analyze Message Button ==========
error_placeholder = st.empty()
if st.button("🔍 Analyze Message"):
    if not user_email:
        error_placeholder.error("Please enter your email to get started.")
    elif not ACCESS_GRANTED and (looks_like_thread or multiline):
        error_placeholder.error("🛑 Looks like you’re trying to sneak in a thread. Full convos & backstories are for premium only. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach)")
    elif not can_analyze:
        error_placeholder.error("🛑 You’ve used both free attempts. [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
    else:
        with st.spinner("Thinking like a coach..."):
            result = analyze_text_and_generate_reply(
                text_input,
                context_input,
                is_thread=(mode == "Full Conversation Thread")
            )
            st.markdown("### 👑 Coach’s Response")
            st.write(result)
            if not ACCESS_GRANTED:
                log_usage(user_email, int(usage["count"]) if usage else 0)

# ========== Sidebar Promo ==========
st.sidebar.markdown("---")
st.sidebar.markdown("💎 [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("📩 Questions? markwestoncoach@gmail.com")
