import streamlit as st
import openai
import requests

# ✅ Configure your SheetDB API
SHEETDB_ENDPOINT = "https://sheetdb.io/api/v1/rmm73p10teqed"

# ✅ OpenAI API Key (configured in Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== App Style Settings ==========
st.set_page_config(layout="centered", page_title="Text Coach for Women", page_icon="❤️‍🔥")

# Inject custom CSS for theme overrides
st.markdown("""
<style>
    html, body, [class*="css"]  {
        background-color: #f0f4f8 !important;
        font-family: 'Segoe UI', sans-serif;
        color: #1e2a38;
    }
    .stTextArea textarea {
        background-color: #eaf0f6 !important;
        border-radius: 8px;
        padding: 0.75rem;
        font-size: 0.95rem;
    }
    .stButton>button {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px;
        height: 2.5rem;
    }
    .stButton>button:hover {
        background-color: #1d4ed8 !important;
        color: white !important;
    }
    .stSidebar, .st-bp, .css-6qob1r, .block-container {
        background-color: #edf2fa !important;
    }
    .stRadio>div>div>label {
        color: #1e2a38 !important;
        font-weight: 500;
    }
    .css-1v0mbdj.e115fcil2 { padding-top: 1rem; }
    .css-1dp5vir.e16nr0p34 { padding-top: 0; padding-bottom: 0; }
</style>
""", unsafe_allow_html=True)

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
        st.session_state.analysis_error = "🛑 You've reached your 2 free attempts. [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)"

# ========== Main UI ========== 
st.title("❤️‍🔥 Text Coach for Women")
st.caption("Decode his message. Protect your peace. Respond with confidence.")

st.markdown("**Paste the message below:**")

col1, col2 = st.columns([1, 1])
with col1:
    mode = st.radio(
        "Choose format:",
        ["Single Message", "Full Conversation Thread"],
        disabled=not ACCESS_GRANTED,
        index=0 if not ACCESS_GRANTED else None,
        help=None if ACCESS_GRANTED else "Upgrade to unlock full conversation analysis"
    )

st.markdown("**📋 Optional Context / Backstory:**")
if ACCESS_GRANTED:
    context_input = st.text_area("", placeholder="Add relevant context here (e.g. how long you’ve been talking, any red flags, etc.)")
else:
    st.text_area("", value="🔐 Upgrade to unlock this field and share more details that make your analysis even sharper.", disabled=True)
    context_input = ""

text_input = st.text_area("📨 Type/paste his message(s) below:")

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
# Analyze button and error placement
submit = st.button("🔍 Analyze Message")

if submit:
    if not user_email:
        st.error("Please enter your email to continue.")
    elif not ACCESS_GRANTED and ("you:" in text_input.lower() or "him:" in text_input.lower() or text_input.count('\n') > 2):
        st.error("🛑 This looks like a thread. Upgrade for full conversation analysis.")
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
                log_usage(user_email, int(usage["count"]) if usage else 0)
    elif "analysis_error" in st.session_state:
        st.error(st.session_state.analysis_error)


