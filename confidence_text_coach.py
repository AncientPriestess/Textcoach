import streamlit as st
import openai
import requests

# ✅ Custom CSS Theme
st.markdown("""
    <style>
    body {
        background-color: #0A192F;
        color: #FFFFFF;
    }
    .stTextInput > div > input,
    .stTextArea textarea {
        background-color: #1E293B;
        color: white;
    }
    .stRadio > div {
        color: #DCE6F8;
    }
    .stButton button {
        background-color: #3B82F6;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #60A5FA;
    }
    .stSidebar .css-ng1t4o, .stSidebar .css-1d391kg {
        background-color: #0A192F;
        color: white;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #DCE6F8;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ Configure your SheetDB API
SHEETDB_ENDPOINT = "https://sheetdb.io/api/v1/rmm73p10teqed"

# ✅ OpenAI API Key (configured in Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== Sidebar UI ==========
st.sidebar.title("🔐 Unlock Full Access")

# Email capture
user_email = st.sidebar.text_input("Your email (for 2 free uses):")

# Unlock code input
password = st.sidebar.text_input("Got a code? Enter it here:", type="password")
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
if user_email:
    usage = get_usage(user_email)
    if ACCESS_GRANTED:
        can_analyze = True
    elif not usage:
        can_analyze = True
    elif int(usage["count"]) < 2:
        can_analyze = True
    else:
        error_to_show = "🛑 You've reached your 2 free attempts. [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)"

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
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")

st.markdown("### 🧠 What’s going on?")
text_input = st.text_area("Paste *his* message here:", height=200)

st.markdown("### 📁 Message Type")
col1, col2 = st.columns(2)
with col1:
    mode = st.radio(
        label="",
        options=["Single Message", "Full Conversation Thread"],
        disabled=not ACCESS_GRANTED,
        index=0,
        help=None if ACCESS_GRANTED else "Upgrade to unlock full conversation analysis"
    )

st.markdown("### 📝 Extra Context (optional)")
if ACCESS_GRANTED:
    context_input = st.text_area(
        label="",
        placeholder="Add any relevant context (e.g. how long you've been seeing him, recent arguments, etc.)",
        height=100
    )
else:
    st.text_area(
        label="",
        placeholder="🔐 Premium feature. Upgrade to unlock this field.",
        height=100,
        disabled=True
    )
    context_input = ""

# ========== Detect Thread Abuse ==========
suspicious_phrases = ["you:", "him:", "her:", "me:", "\n\n", "context:", "backstory:", "sent at", "—", ":", "\n-"]
looks_like_thread = any(phrase.lower() in text_input.lower() for phrase in suspicious_phrases)
multiline = text_input.count('\n') > 2

error_to_show = ""

# ========== Analyze Button ==========
if st.button("🔍 Analyze Message"):
    if not user_email:
        error_to_show = "Please enter your email to continue."
    elif not ACCESS_GRANTED and (looks_like_thread or multiline):
        error_to_show = "🛑 This looks like more than a single message. Full conversation analysis and context/backstory are premium features. [Upgrade here](https://coachnofluff.gumroad.com/l/textcoach)"
    elif can_analyze:
        with st.spinner("Analyzing..."):
            result = analyze_text_and_generate_reply(
                text_input,
                context_input,
                is_thread=(mode == "Full Conversation Thread")
            )
            st.markdown("### 👑 Coach’s Response")
            st.write(result)
            if not ACCESS_GRANTED:
                log_usage(user_email, int(get_usage(user_email)["count"]) if get_usage(user_email) else 0)

# Show errors below button
if error_to_show:
    st.error(error_to_show)
