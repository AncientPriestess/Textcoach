import streamlit as st
import openai
import requests

# ✅ Configure your SheetDB API
sheetdb_endpoint = st.secrets["SHEETDB_ENDPOINT"]

# ✅ OpenAI API Key (configured in Streamlit secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ========== App Style Settings ==========
st.set_page_config(layout="centered", page_title="Relationship Text Coach for Women", page_icon="❤️‍🔥")

# Inject custom CSS for modern card-style UI

st.markdown("""
<style>
/* Responsive base for all screen sizes */
html, body, [class*="css"] {
    background-color: #f3f6fb !important;
    font-family: 'Segoe UI', sans-serif;
    color: #1e2a38;
    margin: 0;
    padding: 0;
    max-width: 100vw;
    overflow-x: hidden;
}

/* Form elements */
.stTextArea textarea, .stTextInput input {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    padding: 0.75rem !important;
    font-size: 1rem !important;
    box-shadow: none !important;
    width: 100% !important;
}

/* Focus states */
input:focus, textarea:focus {
    border: 2px solid #2563eb !important;
    outline: none !important;
    box-shadow: none !important;
}

input:focus:invalid, textarea:focus:invalid,
input:invalid, textarea:invalid {
    border: 1px solid #cbd5e1 !important;
    box-shadow: none !important;
}

/* Buttons */
.stButton>button {
    background-color: #3b82f6 !important;
    color: white !important;
    border-radius: 10px !important;
    height: 2.5rem !important;
    font-weight: bold;
    width: 100%;
    max-width: 100%;
}
.stButton>button:hover {
    background-color: #2563eb !important;
}

/* Sidebar and container background */
.stSidebar, .st-bp, .css-6qob1r, .block-container {
    background-color: #e9eff8 !important;
}

/* Radio labels */
.stRadio>div>div>label {
    font-weight: 500;
}

/* Valid input feedback */
.valid-input input {
    border: 2px solid #10b981 !important;
    background-color: #ffffff !important;
    box-shadow: none !important;
}

/* Success note styling */
.success-note {
    font-size: 0.85rem;
    background-color: #10b981;
    color: white;
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    margin-top: 0.5rem;
    max-width: 100%;
}

/* Responsive adjustments for small screens */
@media screen and (max-width: 600px) {
    .stButton>button, .stTextArea textarea, .stTextInput input {
        font-size: 0.95rem !important;
        padding: 0.65rem !important;
    }

    .success-note {
        font-size: 0.8rem;
        padding: 0.5rem;
    }

    .stRadio>div {
        flex-direction: column !important;
    }

    .stSidebar {
        padding: 1rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ========== Sidebar UI ==========
st.sidebar.title("Free Trial")
user_email = st.sidebar.text_input("Enter your email (for 5 free uses - No code required):")

# Validate email visually
if user_email and "@" in user_email and "." in user_email:
    st.sidebar.markdown(
        f"""<div class='valid-input'>{user_email}</div>
        <div class='success-note'>✅ You're good to go! Free trial activated. </div>""",
        unsafe_allow_html=True
    )
st.sidebar.markdown("---")
st.sidebar.title("🔐 Unlock Full Access")
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
    elif int(usage["count"]) < 5:
        can_analyze = True
    else:
        st.session_state.analysis_error = "🛑 You've reached your 5 free attempts. [Upgrade for unlimited access](https://coachnofluff.gumroad.com/l/textcoach)"

# ========== Main UI ==========
st.title("❤️‍🔥 Text Coach for Women")

st.markdown(
    """
 <div style= font-size: 0.9rem; color: #6b7280;'>
        <strong>*Decode his message. Protect your peace. Respond with confidence.*</strong>
   </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")
st.markdown("**Get started:**")

mode = st.radio(
    "Choose format:",
    ["Single Message", "Full Conversation Thread"],
    disabled=not ACCESS_GRANTED,
    index=0 if not ACCESS_GRANTED else None,
    horizontal=True
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
def is_thread_or_contextual_input(text):
    text_lower = text.lower()

    # Common phrases that indicate storytelling or paraphrased context
    backstory_keywords = [
        "he said", "i told him", "we’ve been", "we were", "he was", "he did", "he told", "he used to",
        "i love", "he loves", "he stopped", "he started", "we talked", "he promised", "he acted", "i feel",
        "i thought he", "then he","him", "because he", "he ghosted", "after that", "he responded", "he ignored", "his", "he did", "he didn't", "he"
    ]

    # Sentence count check
    sentence_count = text.count('.') + text.count('!') + text.count('?')
    keyword_matches = sum(1 for kw in backstory_keywords if kw in text_lower)

    return sentence_count > 2 or keyword_matches >= 2


submit = st.button("🔍 Analyze Message")

if submit:
    if not user_email:
        st.error("Please enter your email to continue.")
    elif not ACCESS_GRANTED and is_thread_or_contextual_input(text_input):
        st.error("🛑 Looks like you're giving me the backstory — totally get it. But to give you a real analysis, I need his actual words, not the recap. The free version works best when you paste his exact message. Want me to look at the full situation? [Upgrade for full breakdown.](https://coachnofluff.gumroad.com/l/textcoach)")
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


# ========== 💎 Sidebar Promotion ==========
st.sidebar.markdown("---")
st.sidebar.markdown("🔓 **Need a code?** [Upgrade to unlock full access](https://coachnofluff.gumroad.com/l/textcoach)")
st.sidebar.markdown("💬 Questions? [markwestoncoach@gmail.com](mailto:markwestoncoach@gmail.com)")

