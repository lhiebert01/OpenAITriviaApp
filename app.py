import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import time
import json


# Load environment variables and initialize OpenAI client
load_dotenv(override=True)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set page configuration
st.set_page_config(
    page_title="🧠 GenAI Trivia Challenge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
    
     .main {
        padding: 0.5rem;  /* Reduced from 2rem to move everything up */
    }
    
    .game-title {
        text-align: center;
        color: #1E88E5;
        margin: 0;        /* Removed margin to move title up */
        padding: 5px 0;   /* Added small padding */
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: white;
        padding: 10px 0;
        text-align: center;
        border-top: 1px solid #e5e5e5;
    }
    
    .stButton button {
        width: 100%;
        min-height: 60px;
        margin: 10px 0;
        padding: 15px;
        border-radius: 8px;
        font-size: 16px;
        text-align: left;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    .timer {
        font-size: 1.5rem;
        font-weight: bold;
        color: #FF5722;
        text-align: center;
        margin: 5px 0;
        padding: 5px;
        background: rgba(255, 87, 34, 0.1);
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .player-info {
        font-size: 1.2rem;
        background: rgba(33, 150, 243, 0.1);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border: 1px solid rgba(33, 150, 243, 0.2);
    }
    .response-area {
        max-height: 200px;
        overflow-y: auto;
        overflow-x: hidden;
        padding: 20px;
        border-radius: 10px;
        background: rgba(76, 175, 80, 0.1);
        margin: 15px 0;
        white-space: pre-wrap;
        word-wrap: break-word;
        border: 1px solid rgba(76, 175, 80, 0.2);
        line-height: 1.6;
    }

    
    .start-button button {
        background-color: #4CAF50;
        color: white;
        font-size: 1.2rem;
        text-align: center;
    }
    .question-display {
        font-size: 1.3rem;
        padding: 10px;
        background: rgba(33, 150, 243, 0.1);
        border-radius: 5px;
        margin: 5px 0;
        border: 1px solid rgba(33, 150, 243, 0.2);
    }
    .current-stats {
        background: rgba(33, 150, 243, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        text-align: center;
        font-size: 1.1rem;
    }
    .answer-button button {
        background-color: #f8f9fa;
        border: 2px solid #e9ecef;
        transition: all 0.5s ease;
    }
    .answer-button button:hover {
        background-color: #e9ecef;
        border-color: #1E88E5;
    }
    .fact-check {
        background: rgba(255, 255, 255, 0.9);
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
        border-left: 4px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)


# Load and display images
def load_and_resize_image(image_path, width=None):
    """Load an image and optionally resize it"""
    try:
        from PIL import Image
        image = Image.open(image_path)
        if width:
            ratio = width/float(image.size[0])
            height = int(float(image.size[1])*float(ratio))
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        return image
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None
    
def is_running_on_streamlit():
    """Check if the code is running on Streamlit Cloud"""
    try:
        if "STREAMLIT_SHARING" in os.environ:
            return True
        return False
    except:
        return False

def get_google_creds(scope):
    """Get credentials based on environment"""
    try:
        if is_running_on_streamlit():
            # Streamlit Cloud: Use secrets
            gcp_creds = dict(st.secrets["gcp_service_account"])
            return ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds, scope)
        else:
            # Local development: Use JSON file
            json_path = "new-year-trivia-game-932d8241aa4e.json"
            if not os.path.exists(json_path):
                raise FileNotFoundError(f"Credentials file not found: {json_path}")
            return ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    except Exception as e:
        st.error(f"Credential setup failed: {str(e)}")
        return None
    
    
def get_spreadsheet_url():
    """Get spreadsheet URL based on environment"""
    if is_running_on_streamlit():
        return st.secrets["google_sheets"]["url"]
    else:
        return "https://docs.google.com/spreadsheets/d/1vs_JYu7HqmGiVUZjTdiDemVBhj3APV90Z5aa1jt56-g/edit#gid=0"



def authenticate_google_sheets():
    """Authenticate with Google Sheets in any environment"""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    try:
        if is_running_on_streamlit():
            # Streamlit Cloud environment
            gcp_creds = dict(st.secrets["gcp_service_account"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_creds, scope)
            sheet_url = st.secrets["google_sheets"]["url"]
        else:
            # Local environment
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "new-year-trivia-game-932d8241aa4e.json", 
                scope
            )
            sheet_url = "https://docs.google.com/spreadsheets/d/1vs_JYu7HqmGiVUZjTdiDemVBhj3APV90Z5aa1jt56-g/edit#gid=0"
        
        client = gspread.authorize(creds)
        sheet = client.open_by_url(sheet_url).sheet1
        return sheet
    except Exception as e:
        if is_running_on_streamlit():
            st.error("Unable to load leaderboard data.")
        else:
            # Silently handle local development errors
            print(f"Local auth error (this is normal in development): {str(e)}")
        return None
    
def load_leaderboard(sheet):
    data = sheet.get_all_records()
    return {row["Name"]: row["Score"] for row in data}

def save_leaderboard(sheet, leaderboard):
    sheet.clear()
    sheet.append_row(["Name", "Score"])
    for name, score in sorted(leaderboard.items(), key=lambda x: x[1], reverse=True):
        sheet.append_row([name, score])
        
def generate_trivia_question():
    prompt = """Create an interesting educational and fund trivia question with four high-quality multiple choice answers. 
    The correct answer should be factually accurate and verifiable. 
    Do not ask questions about the great wall of china, falmingos or other obscure topics, redundancy and repetition should be avoided.
    Trivia questions should be different and engaging for a wide audience, no not repeat questions or topic areas for the entire game so each question and category will need to be remembered not to repeat the same topic or question.
    The questions should vary and not all be about history, architecture, etc, they should be science, technology, and human interest level topics revealing interesting trivia information. 
    The questions should be challenging and not too easy, but not too hard, and should be fun and engaging. 
    The question should be about a well-documented, verifiable fact.
    All answers should be similar in length and style.
    The correct answer must be factually accurate (verifiable via reliable sources).
    The wrong answers should be plausible but clearly incorrect.
    
    Rules for answers:
    - All answers should be roughly the same length
    - Wrong answers should be plausible but definitively incorrect
    - The correct answer must be factually accurate
    - Include specific details in each answer
    
    Format EXACTLY as follows:
    QUESTION: [Clear, specific question about a verifiable fact]
    A) [Detailed answer choice]
    B) [Detailed answer choice]
    C) [Detailed answer choice]
    D) [Detailed answer choice]
    CORRECT: [single letter A, B, C, or D]
    FACT CHECK: [Brief explanation why the correct answer is factually accurate]"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a trivia expert creating well-researched, interesting questions. Do not repeat questions and avoid questions of uncommon mammals, reptiles, insects, or other life forms, primary topic matter should be well known, and not obscure topics.  Questions and topic areas should not be repeated.  The questions should vary from challenging questions that are pretty hard or easy but not that easy. All questions should be interesting, educational and fun; Each question should teach something fascinating while being accurate and engaging. Focus on a wide variety of topics.   Do not ask questions about the great wall of china, falmingos or other obscure topics, redundancy and repetition should be avoided."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.9,
            max_tokens=500
        )
        
        content = response.choices[0].message.content.strip().split("\n")
        question = None
        choices = []
        correct_answer = None
        fact_check = None
        
        for line in content:
            line = line.strip()
            if line.startswith("QUESTION:"):
                question = line.replace("QUESTION:", "").strip()
            elif line.startswith(("A)", "B)", "C)", "D)")):
                choices.append(line)
            elif line.startswith("CORRECT:"):
                correct_answer = line.replace("CORRECT:", "").strip()
            elif line.startswith("FACT CHECK:"):
                fact_check = line.replace("FACT CHECK:", "").strip()
        
        if not all([question, len(choices) == 4, correct_answer, fact_check]):
            return generate_trivia_question()
            
        return {
            "question": question,
            "choices": choices,
            "correct": correct_answer,
            "fact_check": fact_check,
            "start_time": time.time()
        }
    except Exception as e:
        st.error("Retrying question generation...")
        time.sleep(1)  # Add a small delay before retrying
        return generate_trivia_question()

def initialize_session_state():
    if "questions_asked" not in st.session_state:
        st.session_state.questions_asked = 0
    if "total_score" not in st.session_state:
        st.session_state.total_score = 0
    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "game_active" not in st.session_state:
        st.session_state.game_active = False
    if "answer_selected" not in st.session_state:
        st.session_state.answer_selected = False
    if "feedback" not in st.session_state:
        st.session_state.feedback = None
    if "player_name" not in st.session_state:
        st.session_state.player_name = ""

def calculate_score(time_remaining):
    grace_period = 5
    max_time = 60 # 45 - 5 grace period
    if time_remaining <= 0:
        return 0
    score = int((time_remaining / max_time) * 200)
    return min(200, max(0, score))

def check_answer(selected_answer):
    current_time = time.time()
    time_elapsed = current_time - st.session_state.current_question["start_time"]
    time_remaining = max(0, 65 - time_elapsed)
    
    correct = selected_answer == st.session_state.current_question["correct"]
    points = calculate_score(time_remaining) if correct else 0
    
    if correct:
        st.session_state.total_score += points
        st.session_state.feedback = (
            f"""✨ Correct! You earned {points} points!
            
            {st.session_state.current_question['fact_check']}""",
            "success"
        )
    else:
        st.session_state.feedback = (
            f"""❌ Wrong! The correct answer was {st.session_state.current_question['correct']}.
            
            {st.session_state.current_question['fact_check']}""",
            "error"
        )
    
    st.session_state.answer_selected = True
    return time_remaining

def main():
    initialize_session_state()
    
    st.markdown('<h1 class="game-title">🧠 GenAI Trivia Challenge 🌟</h1>', unsafe_allow_html=True)
    
    # Add logo to sidebar
    logo = load_and_resize_image("AppImage.png", width=250)
    if logo:
        st.sidebar.image(logo, use_container_width=True)
    
    # Sidebar content
    st.sidebar.title("🎮 Game Controls")
    st.sidebar.text("Test your knowledge. Race against time (60 seconds per question) to earn more points! Good Luck!🎯")
    
    # Player registration and game start
    if not st.session_state.player_name:
        st.sidebar.markdown("### 👋 Welcome to Trivia!")
        st.sidebar.markdown("Enter your name and press the button to start playing!")
        player_name = st.sidebar.text_input("Enter your name:")
        if player_name:
            st.session_state.player_name = player_name
            
    if st.session_state.player_name and not st.session_state.game_active:
        st.sidebar.markdown("### 🎲 Ready to Play?")
        if st.sidebar.button("Start Trivia Game!", key="start_game", use_container_width=True):
            st.session_state.game_active = True
            st.session_state.questions_asked = 0
            st.session_state.total_score = 0
            st.session_state.current_question = None
            st.session_state.answer_selected = False
            st.session_state.feedback = None
    
    # Player stats
    if st.session_state.player_name:
        st.sidebar.markdown(f"""
        <div class="player-info">
        👤 Player: {st.session_state.player_name}<br>
        💫 Total Score: {st.session_state.total_score}<br>
        📝 Questions: {st.session_state.questions_asked}/10
        </div>
        """, unsafe_allow_html=True)
    
    # Collapsible Leaderboard
    st.sidebar.markdown("---")
    with st.sidebar.expander("📊 View Leaderboard", expanded=False):
        try:
            sheet = authenticate_google_sheets()
            if sheet:
                leaderboard = load_leaderboard(sheet)
                sorted_leaderboard = sorted(leaderboard.items(), key=lambda x: x[1], reverse=True)
                for i, (name, score) in enumerate(sorted_leaderboard[:10], 1):
                    st.write(f"{i}. {name}: {score} points")
            else:
                st.info("Leaderboard temporarily unavailable")
        except Exception as e:
            st.info("Leaderboard temporarily unavailable")

    if st.session_state.game_active and st.session_state.questions_asked < 10:
        if not st.session_state.current_question:
            with st.spinner("Loading next question..."):
                st.session_state.current_question = generate_trivia_question()
                st.session_state.answer_selected = False
                st.session_state.feedback = None
        
        if st.session_state.current_question:
            # Timer and current stats
            current_time = time.time()
            time_elapsed = current_time - st.session_state.current_question["start_time"]
            time_remaining = max(0, 65 - time_elapsed)
            
            # Current game stats
            st.markdown(f"""
            <div class="current-stats">
            👤 Player: {st.session_state.player_name} | 
            💫 Score: {st.session_state.total_score} | 
            📝 Questions Remaining: {10 - st.session_state.questions_asked}
            </div>
            """, unsafe_allow_html=True)
            
            # Question display
            st.markdown(f"""
            <div class="question-display">
            Question {st.session_state.questions_asked + 1}/10:
            {st.session_state.current_question["question"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for answer choices
            col1, col2 = st.columns(2)
            
            # First two answers (A and B) in left column
            with col1:
                for i in range(2):
                    if time_remaining > 0:
                        if st.button(st.session_state.current_question["choices"][i], 
                                   key=f"choice_{i}", 
                                   disabled=st.session_state.answer_selected,
                                   use_container_width=True):
                            time_remaining = check_answer(chr(65 + i))
            
            # Last two answers (C and D) in right column
            with col2:
                for i in range(2, 4):
                    if time_remaining > 0:
                        if st.button(st.session_state.current_question["choices"][i], 
                                   key=f"choice_{i}", 
                                   disabled=st.session_state.answer_selected,
                                   use_container_width=True):
                            time_remaining = check_answer(chr(65 + i))
            
            # Feedback area
            if st.session_state.feedback:
                message, type_ = st.session_state.feedback
                with st.container():
                    st.markdown(f"""
                    <div class="response-area">
                    {message}
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("Next Question ➡️", type="primary", use_container_width=True):
                    st.session_state.questions_asked += 1
                    st.session_state.current_question = None
                    st.rerun()
    
    elif st.session_state.questions_asked >= 10:
        # Game Over
        st.markdown(f"""
        <div class="response-area">
        🎉 Game Over!
        Final Score: {st.session_state.total_score}
        Thanks for playing, {st.session_state.player_name}!
        </div>
        """, unsafe_allow_html=True)
        
        # Update leaderboard
        try:
            sheet = authenticate_google_sheets()
            leaderboard = load_leaderboard(sheet)
            if st.session_state.player_name not in leaderboard or st.session_state.total_score > leaderboard[st.session_state.player_name]:
                leaderboard[st.session_state.player_name] = st.session_state.total_score
                save_leaderboard(sheet, leaderboard)
        except Exception as e:
            st.error("Unable to update leaderboard")
        
        if st.button("Play Again", type="primary", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    
    # Custom footer with image and LinkedIn link
    
    # Custom footer with image and LinkedIn link
    st.markdown("---")  # Horizontal line first

    # Custom CSS for the footer text
    footer_text = """
    <div style="text-align: center; padding: 10px;">
        <span style="font-size: 1.2rem; font-weight: 600;">
            GenAI Trivia Challenge, designed by 
            <a href="https://www.linkedin.com/in/lindsayhiebert/" target="_blank" 
               style="text-decoration: none; color: #1E88E5;">
               Lindsay Hiebert
            </a>
        </span>
    </div>
    """
    st.markdown(footer_text, unsafe_allow_html=True)

    # Footer image with custom styling
    footer_img = load_and_resize_image("FooterImage.png", width=800)  # Wider width
    if footer_img:
        # Calculate height to make image narrower while maintaining aspect ratio
        aspect_ratio = 0.02   # Adjust this value to make image taller or shorter
        new_height = int(800 * aspect_ratio)  # Height based on width
        from PIL import Image
        resized_img = footer_img.resize((1200, new_height), Image.Resampling.LANCZOS)
        st.image(resized_img, use_container_width=True)  # Make image stretch to container width
        
    st.markdown("---")  # Horizontal line

if __name__ == "__main__":
    main()