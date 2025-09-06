import os
import streamlit as st
import random
import time

# Try to import Gemini
try:
    import google.generativeai as genai
except ImportError:
    genai = None

# -----------------------
# Set up the page
# -----------------------
st.set_page_config(
    page_title="University Life Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -----------------------
# Configure Gemini
# -----------------------
try:
    api_key = st.secrets["GEMINI_API_KEY"]  # Works on Streamlit Cloud
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")   # Fallback for local runs

if api_key and genai:
    genai.configure(api_key=api_key)
    # Create a Gemini model with system instruction
    uni_bot = genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction="""
        You are a helpful assistant for Universiti Tunku Abdul Rahman (UTAR), Kampar, Perak, Malaysia.
        Your job is to answer questions about campus life, facilities, student services, courses,
        and general university information.

        Rules:
        - Be polite, concise, and student-friendly.
        - Include local context (Kampar, Perak, Malaysia) when relevant.
        """
    )
    use_gemini = True
else:
    use_gemini = False


# -----------------------
# Custom CSS
# -----------------------
st.markdown(""" 
<style>
    /* Sticky header */
    .sticky-header {
        position: fixed;
        top: 40px;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
        color: white;
        padding: 15px 20px;
        z-index: 999;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        box-sizing: border-box;
    }
    [data-testid="stSidebar"][aria-expanded="true"] ~ section .sticky-header {
        margin-left: 250px;
        width: calc(100% - 250px);
    }
    [data-testid="stSidebar"][aria-expanded="false"] ~ section .sticky-header {
        margin-left: 0;
        width: 100%;
    }
    .header-content { max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; text-align: center; }
    .header-title { margin: 0; font-size: 28px; font-weight: 700; }
    .header-subtitle { margin: 5px 0 0 0; font-size: 16px; font-weight: 400; opacity: 0.9; }
    .main-content { padding-top: 100px; }
    .user-message-container { display: flex; justify-content: flex-end; margin-bottom: 15px; }
    .user-message { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; padding: 12px 16px; border-radius: 18px 18px 0 18px; max-width: 70%; word-wrap: break-word; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    .bot-message-container { display: flex; justify-content: flex-start; margin-bottom: 15px; }
    .bot-message { background-color: #f0f2f6; color: #333; padding: 12px 16px; border-radius: 18px 18px 18px 0; max-width: 70%; word-wrap: break-word; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
    .chat-container { padding: 1rem; margin-bottom: 1rem; max-height: 400px; overflow-y: auto; background-color: transparent; }
    .stButton button { background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%); color: white; border: none; border-radius: 8px; padding: 10px 16px; font-weight: 600; transition: all 0.3s ease; width: 100%; margin-bottom: 8px; }
    .stButton button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(0,0,0,0.15); }
    .empty-state { text-align: center; padding: 40px 20px; color: #666; background-color: #f9f9f9; border-radius: 8px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Default rule-based responses
# -----------------------
default_responses = [
    "I'm not sure I understand. Could you rephrase your question?",
    "That's an interesting question. Let me connect you with a human advisor who can help.",
    "I don't have information about that yet. Try asking about campus facilities, registration, or student life.",
    "I'm still learning about university processes. Could you ask something about library, exams, or dining?"
]

# -----------------------
# Chat history
# -----------------------
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# -----------------------
# Bot response generator (Gemini + fallback)
# -----------------------
def get_bot_response(user_input):
    user_input_lower = user_input.lower()

    # First try rule-based answers
    if "library" in user_input_lower:
        return "The main library is at Block G. Open 8 AM–9 PM weekdays, 8 AM–5 PM weekends."
    elif "register" in user_input_lower and "exam" in user_input_lower:
        return "You can register for exams through the student portal under 'Exam Registration'. Register before the deadline to avoid late fees."
    elif "dining" in user_input_lower or "food" in user_input_lower:
        return "Campus dining includes the main cafeteria, food court, coffee shop in the library, and several snack kiosks."
    elif "student club" in user_input_lower or "join club" in user_input_lower:
        return "Visit the Student Activities Office or attend the Club Fair during orientation. You can also join clubs via the campus app."
    elif "housing" in user_input_lower or "dorm" in user_input_lower:
        return "Housing applications are online in the student portal. The deadline for next semester is Nov 15. First-year students are guaranteed housing."
    elif "parking" in user_input_lower:
        return "Student parking permits are available at Campus Security. Bring your vehicle registration and student ID. Cost: RM150 per semester."
    elif "wifi" in user_input_lower:
        return "Campus WiFi is everywhere. Connect to 'Campus-Net' with your student credentials. For issues, contact IT Help Desk."
    elif "career" in user_input_lower:
        return "Career Services (2nd floor, Student Success Center) offers resume reviews, mock interviews, and counseling."
    elif "transcript" in user_input_lower:
        return "Official transcripts are requested at the Registrar's Office (small fee). Unofficial ones are free on the student portal."
    elif "tuition" in user_input_lower or "payment" in user_input_lower:
        return "Tuition is paid online in the portal under 'Finances' > 'Make a Payment'. Payment plans are available."

    # Otherwise, fallback to Gemini if available
    if use_gemini:
        try:
            response = uni_bot.generate_content(user_input)
            return response.text
        except Exception as e:
            return f"Gemini error, falling back to default reply. ({e})"

    # If Gemini not available, pick a default response
    return random.choice(default_responses)

# -----------------------
# Chat display
# -----------------------
def display_chat():
    if st.session_state.chat_history:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"""
                <div class='user-message-container'>
                    <div class='user-message'>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='bot-message-container'>
                    <div class='bot-message'>{message['content']}</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state">
            <h3>Welcome to UTAR Kampar! How can I help you?</h3>
            <p>Start a conversation by typing a question or selecting a suggested question from the sidebar.</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------
# Main App
# -----------------------
def main():
    # Sticky header
    st.markdown("""
        <div class="sticky-header">
            <div class="header-content">
                <h1 class="header-title">🎓 University Life Chatbot</h1>
                <p class="header-subtitle">Ask me anything about UTAR Kampar campus life, courses, and more!</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='main-content'>", unsafe_allow_html=True)

    # Show chat
    display_chat()

    # Sidebar suggested questions
    st.sidebar.subheader("💡 Suggested Questions")
    suggested_questions = [
        "Where is the library located?",
        "How do I register for exams?",
        "What dining options are available?",
        "How can I join a student club?",
        "What are the housing options?",
        "How do I get a parking permit?",
        "How to connect to campus WiFi?",
        "Where is career services located?"
    ]

    for i, question in enumerate(suggested_questions):
        if st.sidebar.button(question, key=f"suggest_{i}"):
            st.session_state.chat_history.append({'role': 'user', 'content': question})
            with st.spinner("Thinking..."):
                time.sleep(0.5)
                response = get_bot_response(question)
            st.session_state.chat_history.append({'role': 'assistant', 'content': response})
            st.rerun()

    # User input
    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        with st.spinner("Thinking..."):
            time.sleep(0.5)
            response = get_bot_response(user_input)
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
