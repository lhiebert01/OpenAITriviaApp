import streamlit as st
from openai import OpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
import time
import json

# Initialize OpenAI client using environment variable or Streamlit secrets
def get_openai_key():
    """Get OpenAI API key from environment or Streamlit secrets"""
    if os.getenv("OPENAI_API_KEY"):  # Local development
        return os.getenv("OPENAI_API_KEY")
    else:  # Streamlit Cloud
        return st.secrets["openai"]["OPENAI_API_KEY"]

# Initialize OpenAI client
client = OpenAI(api_key=get_openai_key())

# Set page configuration
st.set_page_config(
    page_title="🧠 GenAI Trivia Challenge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling

# Replace the entire CSS section with this:
st.markdown("""
    <style>
    .main {
        padding: 0.5rem;
    }
    
    /* Title area with logo */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin: 0;
        padding: 5px 0;
        width: 100%;
    }
    
    .game-title {
        text-align: center;
        color: #1E88E5;
        margin: 0;
        padding: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        white-space: nowrap;
    }
    
    .logo-container {
        width: 95px !important;  /* Reduced from 75px */
        height: 95px !important; /* Reduced from 75px */
        margin: 0 !important;
        padding: 0 !important;
        display: flex;
        justify-content: center;
        align-items: center;
        flex-shrink: 0;
    }
    
    .logo-container img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
    }
    
    .instruction-text {
        font-size: 2.0rem !important;
        line-height: 1.2 !important;
        margin: 0 !important;
        padding: 10px 0 !important;
    }
    
    .current-topic {
        font-weight: 600;
        color: #1E88E5;
        background: rgba(33, 150, 243, 0.1);
        padding: 2px 8px;
        border-radius: 4px;
        margin: 0 4px;
    }
    
    /* Timer styles */
    .timer-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        padding: 8px;
        margin: 5px 0;
        background: rgba(255, 87, 34, 0.05);
        border-radius: 8px;
    }

    .timer-display {
        font-size: 1.2rem;
        font-weight: bold;
        color: #FF5722;
        padding: 5px 10px;
        border-radius: 4px;
        min-width: 120px;
        text-align: center;
    }

    .progress-bar {
        flex-grow: 1;
        height: 8px;
        background: #e0e0e0;
        border-radius: 4px;
        overflow: hidden;
        max-width: 300px;
    }

    .progress-bar-fill {
        height: 100%;
        background: #4CAF50;
        transition: width 0.5s ease-out;
    }

    .timer-warning .timer-display {
        color: #f44336;
        animation: pulse 1s infinite;
    }

    .timer-warning .progress-bar-fill {
        background: #f44336;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    /* Column alignment */
    [data-testid="column"] {
        align-items: flex-start !important;
        justify-content: flex-start !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    
    .element-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Game controls */
    .game-controls {
        margin-top: 0.5rem !important;
        padding-top: 0.5rem !important;
        border-top: 1px solid rgba(49, 51, 63, 0.2);
    }
    
    .sidebar .stMarkdown {
        margin: 0 !important;
    }
    
    .sidebar-title {
        font-size: 1.1rem !important;
        font-weight: bold;
        margin: 0.5rem 0 !important;
        padding: 0 !important;
    }
    
    /* Buttons */
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
    
    /* Game interface */
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
    
    /* Game over section */
    .game-over-section {
        background: rgba(76, 175, 80, 0.1);
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        text-align: center;
        border: 1px solid rgba(76, 175, 80, 0.2);
    }

    .game-over-title {
        font-size: 2rem;
        color: #4CAF50;
        margin-bottom: 15px;
    }

    .game-over-stats {
        font-size: 1.2rem;
        margin: 10px 0;
        line-height: 1.6;
    }
    
    /* Footer */
    .footer-section {
        margin-top: 30px;
        padding: 20px 0;
        background: rgba(33, 150, 243, 0.05);
        border-top: 1px solid rgba(33, 150, 243, 0.1);
    }

    .footer-content {
        text-align: center;
        padding: 10px;
        max-width: 800px;
        margin: 0 auto;
    }

    .footer-image {
        max-width: 100%;
        height: auto;
        margin: 10px 0;
    }
    
    /* Additional controls */
    .sidebar-controls {
        background: rgba(33, 150, 243, 0.05);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .control-button {
        margin: 5px 0;
    }
    
    .required-field {
        color: #f44336;
        font-size: 0.8rem;
        margin-top: 2px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'player_name' not in st.session_state:
    st.session_state.player_name = ""
if 'topic' not in st.session_state:
    st.session_state.topic = ""
if 'questions_asked' not in st.session_state:
    st.session_state.questions_asked = 0
if 'total_score' not in st.session_state:
    st.session_state.total_score = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'game_active' not in st.session_state:
    st.session_state.game_active = False
if 'answer_selected' not in st.session_state:
    st.session_state.answer_selected = False
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'game_length' not in st.session_state:
    st.session_state.game_length = 10
# Add this to your session state initializations
if 'leaderboard_cache' not in st.session_state:
    st.session_state.leaderboard_cache = None
if 'last_sheet_load' not in st.session_state:
    st.session_state.last_sheet_load = None
# other session state initializations
if 'sheet_object' not in st.session_state:
    st.session_state.sheet_object = None
# Add to session state initialization section:
if 'question_cache' not in st.session_state:
    st.session_state.question_cache = set()

def load_and_resize_image(image_path, width=None, max_size=None):
    """Load an image and resize it with maximum dimensions"""
    try:
        from PIL import Image
        image = Image.open(image_path)
        
        if max_size:
            # Calculate ratio to maintain aspect ratio
            ratio = min(max_size[0]/float(image.size[0]), 
                       max_size[1]/float(image.size[1]))
            new_size = (int(float(image.size[0])*float(ratio)), 
                       int(float(image.size[1])*float(ratio)))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            return image
        elif width:
            ratio = width/float(image.size[0])
            height = int(float(image.size[1])*float(ratio))
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            return image
        return image
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None




def is_running_on_streamlit():
    """Check if the code is running on Streamlit Cloud"""
    checks = [
        hasattr(st, "secrets"),
        any(key.startswith("STREAMLIT_") for key in os.environ),
        not os.path.exists("new-year-trivia-game-932d8241aa4e.json")
    ]
    return any(checks)



def authenticate_google_sheets():
    """Authenticate with Google Sheets API and return sheet object"""
    # Check if we have a cached sheet object
    if st.session_state.sheet_object is not None:
        return st.session_state.sheet_object
    
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        if is_running_on_streamlit():
            creds_dict = dict(st.secrets["gcp_service_account"])
            
            if "private_key" in creds_dict:
                pk = creds_dict["private_key"]
                if isinstance(pk, str):
                    pk = pk.replace('\\n', '\n').strip()
                    if not pk.endswith('\n'):
                        pk += '\n'
                    creds_dict["private_key"] = pk
            
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
            
        else:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                "new-year-trivia-game-932d8241aa4e.json", 
                scope
            )
            
        client = gspread.authorize(creds)
        sheet_url = (st.secrets["google_sheets"]["url"] 
                    if is_running_on_streamlit() 
                    else "https://docs.google.com/spreadsheets/d/1vs_JYu7HqmGiVUZjTdiDemVBhj3APV90Z5aa1jt56-g/edit#gid=0")
        
        spreadsheet = client.open_by_url(sheet_url)
        # Cache the sheet object
        st.session_state.sheet_object = spreadsheet.sheet1
        return st.session_state.sheet_object
        
    except Exception as e:
        return None
    

def load_leaderboard(sheet, force_refresh=False):
    """Load leaderboard data with caching"""
    from datetime import datetime, timedelta
    
    # Check if we have cached data and it's less than 5 minutes old
    if (not force_refresh and 
        st.session_state.leaderboard_cache is not None and 
        st.session_state.last_sheet_load is not None and 
        datetime.now() - st.session_state.last_sheet_load < timedelta(minutes=5)):
        return st.session_state.leaderboard_cache
    
    if sheet is None:
        return {}
        
    try:
        # Load from sheet
        data = sheet.get_all_records()
        leaderboard = {i: {
            "name": row["Name"],
            "score": row["Score"],
            "topic": row["Topic"],
            "date": row["Date"],
            "time": row["Time"],
            "questions_answered": row["Questions_Answered"],
            "game_length": row["Game_Length"]
        } for i, row in enumerate(data)}
        
        # Update cache
        st.session_state.leaderboard_cache = leaderboard
        st.session_state.last_sheet_load = datetime.now()
        
        return leaderboard
    except Exception as e:
        print(f"Error loading leaderboard: {str(e)}")
        return {}


def save_leaderboard(sheet, leaderboard):
    """Save leaderboard data to Google Sheet with extended fields and rate limiting"""
    if sheet is None:
        return
    
    import time
    from random import uniform
    
    max_retries = 5
    base_wait = 1  # Base wait time in seconds
    
    for attempt in range(max_retries):
        try:
            # Clear the sheet and set headers
            sheet.clear()
            time.sleep(uniform(1, 2))  # Random delay between 1-2 seconds
            
            headers = ["Name", "Score", "Topic", "Date", "Time", 
                      "Questions_Answered", "Game_Length"]
            sheet.append_row(headers)
            time.sleep(uniform(1, 2))  # Random delay between 1-2 seconds
            
            # Sort entries by date/time (newest first) and score (highest first)
            sorted_entries = sorted(
                leaderboard.values(),
                key=lambda x: (x["date"], x["time"], -x["score"]),
                reverse=True
            )
            
            # Append entries with rate limiting
            for entry in sorted_entries:
                # Add random delay between writes
                time.sleep(uniform(0.5, 1))  # Random delay between 0.5-1 seconds
                
                sheet.append_row([
                    entry["name"],
                    entry["score"],
                    entry["topic"],
                    entry["date"],
                    entry["time"],
                    entry["questions_answered"],
                    entry["game_length"]
                ])
            
            return  # Success
            
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Error saving leaderboard after {max_retries} attempts: {str(e)}")
                return
            
            # Calculate wait time with exponential backoff
            wait_time = (2 ** attempt) * base_wait + uniform(0, 1)
            print(f"Attempt {attempt + 1} failed, waiting {wait_time:.2f} seconds...")
            time.sleep(wait_time)
 

def update_leaderboard_entry(sheet, player_name, score, topic, questions_answered, game_length, force_write=False):
    """Update leaderboard with local caching"""
    try:
        from datetime import datetime
        current_time = datetime.now()
        
        # Format date and time
        date_str = current_time.strftime("%b %d, %Y")
        time_str = current_time.strftime("%I:%M %p")
        
        # Get cached leaderboard or load if needed
        leaderboard = st.session_state.leaderboard_cache
        if leaderboard is None:
            leaderboard = load_leaderboard(sheet)
        
        # Check for duplicate
        duplicate_exists = any(
            entry["name"] == player_name and
            entry["topic"] == topic and
            entry["score"] == score and
            entry["date"] == date_str
            for entry in leaderboard.values()
        )
        
        if not duplicate_exists:
            # Create new entry
            new_entry = {
                "name": player_name,
                "score": score,
                "topic": topic,
                "date": date_str,
                "time": time_str,
                "questions_answered": questions_answered,
                "game_length": game_length
            }
            
            # Add to local cache
            next_index = max(leaderboard.keys(), default=-1) + 1
            leaderboard[next_index] = new_entry
            st.session_state.leaderboard_cache = leaderboard
            
            # Only write to sheet if forced (end of game)
            if force_write and sheet:
                save_leaderboard_efficient(sheet, leaderboard)
            
            return True
        return False
        
    except Exception as e:
        print(f"Error updating leaderboard: {str(e)}")
        return False

def save_leaderboard_efficient(sheet, leaderboard):
    """Efficient single-operation save to Google Sheet"""
    if sheet is None:
        return
    
    try:
        # Prepare all data at once
        headers = ["Name", "Score", "Topic", "Date", "Time", 
                  "Questions_Answered", "Game_Length"]
        
        # Sort entries
        sorted_entries = sorted(
            leaderboard.values(),
            key=lambda x: (x["date"], x["time"], -x["score"]),
            reverse=True
        )
        
        # Create all rows at once
        rows = [headers] + [
            [
                entry["name"],
                entry["score"],
                entry["topic"],
                entry["date"],
                entry["time"],
                entry["questions_answered"],
                entry["game_length"]
            ]
            for entry in sorted_entries
        ]
        
        # Single batch update operation - FIXED order of arguments
        sheet.update(values=rows, range_name='A1', value_input_option='RAW')
        
    except Exception as e:
        print(f"Error saving leaderboard: {str(e)}")

def get_topic_rankings(leaderboard, topic):
    """Get rankings for a specific topic, sorted by score and date"""
    topic_scores = [
        (entry["name"], entry["score"], entry["date"], entry["time"])
        for entry in leaderboard.values()
        if entry["topic"].lower() == topic.lower()
    ]
    # Sort by score (descending) and then by date/time (newest first)
    return sorted(
        topic_scores,
        key=lambda x: (-x[1], x[2], x[3]),
        reverse=False
    )


def display_game_over(player_name, score, topic, questions_answered, game_length):
    """Enhanced game over display with updated rankings"""
    try:
        sheet = authenticate_google_sheets()
        if sheet:
            # Add these lines right here, before update_leaderboard_entry
            from datetime import datetime
            current_time = datetime.now()
            current_date = current_time.strftime("%b %d, %Y")
            current_time_str = current_time.strftime("%I:%M %p")
            
            # Update leaderboard with force_write=True to save to sheet
            update_leaderboard_entry(
                sheet, player_name, score, topic, 
                questions_answered, game_length,
                force_write=True
            )
            
            # Use cached data for display
            leaderboard = st.session_state.leaderboard_cache
            if leaderboard is None:
                leaderboard = load_leaderboard(sheet)    
            
            

        
            # Calculate rankings
            sorted_entries = sorted(
                leaderboard.values(),
                key=lambda x: (-x["score"], x["date"], x["time"])
            )
            
            overall_rank = next(
                (i + 1 for i, entry in enumerate(sorted_entries)
                if entry["name"] == player_name and 
                entry["score"] == score and
                entry["topic"] == topic),
                None
            )
            
            topic_rankings = get_topic_rankings(leaderboard, topic)
            topic_rank = next(
                (i + 1 for i, (name, s, _, _) in enumerate(topic_rankings)
                if name == player_name and s == score),
                None
            )
            
            # Display results in columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="game-over-section">
                    <div class="game-over-title">🎉 Game Over!</div>
                    <div class="game-over-stats">
                        Final Score: {score}<br>
                        Player: {player_name}<br>
                        Topic: {topic}<br>
                        Questions: {questions_answered}/{game_length}<br>
                        Overall Rank: #{overall_rank}<br>
                        Topic Rank: #{topic_rank}<br>
                        Date: {current_date}<br>
                        Time: {current_time_str}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 🏆 Overall Top 5")
                for i, entry in enumerate(sorted_entries[:5], 1):
                    if (entry["name"] == player_name and 
                        entry["score"] == score and 
                        entry["topic"] == topic):
                        st.markdown(
                            f"""**{i}. {entry['name']} ({entry['topic']}): """
                            f"""{entry['score']} points** ← You"""
                            f""" ({entry['date']} {entry['time']})"""
                        )
                    else:
                        st.markdown(
                            f"""{i}. {entry['name']} ({entry['topic']}): """
                            f"""{entry['score']} points"""
                            f""" ({entry['date']} {entry['time']})"""
                        )
            
            with col2:
                st.markdown(f"### 🎯 Top 5 for {topic}")
                for i, (name, score, date, time) in enumerate(topic_rankings[:5], 1):
                    if name == player_name:
                        st.markdown(
                            f"""**{i}. {name}: {score} points** ← You"""
                            f""" ({date} {time})"""
                        )
                    else:
                        st.markdown(
                            f"""{i}. {name}: {score} points"""
                            f""" ({date} {time})"""
                        )
                
                if topic_rank and topic_rank <= 5:
                    st.success(
                        f"🌟 Congratulations! "
                        f"You are #{topic_rank} on the {topic} leaderboard!"
                    )
            
    except Exception as e:
        st.error(f"Unable to update leaderboard: {str(e)}")

def display_leaderboards():
    """Display both overall and topic-specific leaderboards with timestamps"""
    st.sidebar.markdown("---")
    
    # Get fresh data once for both leaderboards
    sheet = authenticate_google_sheets()
    current_leaderboard = load_leaderboard(sheet) if sheet else {}
    
    # Overall Leaderboard
    with st.sidebar.expander("📊 Overall Leaderboard", expanded=False):
        if current_leaderboard:
            sorted_entries = sorted(
                current_leaderboard.values(),
                key=lambda x: (-x["score"], x["date"], x["time"])
            )
            
            for i, entry in enumerate(sorted_entries[:10], 1):
                st.write(
                    f"""{i}. {entry['name']} ({entry['topic']}): """
                    f"""{entry['score']} points"""
                    f""" - {entry['date']} {entry['time']}"""
                )
        else:
            st.info("Leaderboard temporarily unavailable")
    
    # Topic Leaderboard
    if st.session_state.topic:
        with st.sidebar.expander(
            f"🎯 {st.session_state.topic} Leaderboard", 
            expanded=False
        ):
            if current_leaderboard:
                topic_rankings = get_topic_rankings(current_leaderboard, st.session_state.topic)
                if topic_rankings:
                    for i, (name, score, date, time) in enumerate(topic_rankings[:10], 1):
                        st.write(
                            f"{i}. {name}: {score} points "
                            f"- {date} {time}"
                        )
                else:
                    st.info("No scores yet for this topic!")
            else:
                st.info("Topic leaderboard temporarily unavailable")


def generate_trivia_question(topic):
    """Generate a unique trivia question based on the topic with improved validation"""
    
    prompt = f"""Create a concise but challenging trivia question about {topic}.

    Requirements:
    1. Question must be unique and specific to {topic}
    2. Length: Question should be 2-4 sentences maximum
    3. All answer choices must be:
       - Distinctly different from each other
       - Similar in length and complexity, and detailed
       - Plausible but with only one and only one clearly correct answer
    4. Fact check must be concise (max 3 sentences) and definitively prove the correct answer
    
    CRITICAL: Each answer choice must be meaningfully different from the others.
    
    Format:
    QUESTION: [Concise question about {topic}]
    A) [Distinct answer]
    B) [Distinct answer]
    C) [Distinct answer]
    D) [Distinct answer]
    CORRECT: [A, B, C, or D]
    FACT CHECK: [Brief verification of correct answer]
    
    The question key must be unique to prevent duplicates."""

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Using full GPT-4 instead of turbo
                messages=[
                    {"role": "system", "content": f"You are a {topic} expert creating concise, accurate trivia questions. Focus on interesting but verifiable facts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,  # Increased for more variety
                max_tokens=650,
                presence_penalty=0.6,  # Encourage more diverse responses
                frequency_penalty=0.6  # Discourage repetitive answers
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
            
            # Validate response format
            if not all([question, len(choices) == 4, correct_answer, fact_check]):
                continue
                
            # Create a unique key for the question
            question_key = f"{topic}:{question}"
            
            # Check if question is unique
            if question_key in st.session_state.question_cache:
                continue
                
            # Validate answer choices are distinct
            answer_texts = [c.split(")", 1)[1].strip().lower() for c in choices]
            if len(set(answer_texts)) != 4:
                continue
                
            # Add to cache
            st.session_state.question_cache.add(question_key)
            
            return {
                "question": question,
                "choices": choices,
                "correct": correct_answer,
                "fact_check": fact_check,
                "start_time": time.time()
            }
        except Exception as e:
            if attempt == max_attempts - 1:
                st.error(f"Error generating question: {str(e)}")
                return None
            time.sleep(1)
            continue
    
    return None  # If all attempts fail

def calculate_score(time_remaining):
    """Calculate score based on remaining time"""
    max_time = 60
    if time_remaining <= 0:
        return 0
    score = int((time_remaining / max_time) * 200)
    return min(200, max(0, score))

def check_answer(selected_answer):
    """Check if the answer is correct and calculate score"""
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

def reset_game_state():
    """Reset game state for a new game but preserve question cache"""
    st.session_state.questions_asked = 0
    st.session_state.total_score = 0
    st.session_state.current_question = None
    st.session_state.answer_selected = False
    st.session_state.feedback = None
    st.session_state.game_active = False
    st.session_state.leaderboard_cache = None
    st.session_state.last_sheet_load = None
    # Note: We do NOT clear question_cache here
    
def main():
    # Add auto-refresh script
    st.markdown("""
        <script>
            function refreshPage() {
                if (!document.hidden) {
                    window.location.reload();
                }
            }
            setInterval(refreshPage, 1000);
        </script>
    """, unsafe_allow_html=True)
    
    # Main title
    col1, col2 = st.columns([9, 1])
    with col1:
        st.markdown('<h1 class="game-title">🧠 GenAI Trivia Challenge 🌟</h1>', unsafe_allow_html=True)
    with col2:
        logo = load_and_resize_image("AppImage.png", max_size=(295, 295))
        if logo:
            st.image(logo, use_container_width=True)

 
  #  st.sidebar.markdown("### Game Quick Start:")
   
    # Simplified sidebar with instructions
    st.sidebar.markdown('<div class="instruction-text">', unsafe_allow_html=True)
    st.sidebar.markdown("""
    # 🏆 Game Quick Start: 
    ### 1. 👤 Enter your name & Triva topic area for the Game, 2. 🔄 Update both using buttons, 3. 🎲 Set questions (5 or 10), 4. 🚀 Press Start Game! to Play, 5. At the End of Game, Press End Game to save your score on leaderboard. 🎯
    """)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Game Controls section
    st.sidebar.markdown('<div class="game-controls">', unsafe_allow_html=True)
  #  st.sidebar.markdown('<p class="sidebar-title">🎮 Game Controls</p>', unsafe_allow_html=True)
    st.sidebar.markdown("# 🎮  Game Controls:")

    # Game length selection
 #   st.sidebar.markdown("### Game Length:")
    game_length = st.sidebar.radio(
        " ",  # Space instead of empty string to ensure consistent spacing
        options=["5 Questions", "10 Questions"],
        index=1 if st.session_state.game_length == 10 else 0,
        horizontal=True,
        label_visibility="collapsed"  # This hides the label completely
    )
    st.session_state.game_length = 10 if "10" in game_length else 5
    
    # Player Input Controls
    with st.sidebar.container():
        st.markdown("# Player Settings")
        
        # Player name input
        new_name = st.text_input("Player Name:", 
                                value=st.session_state.player_name,
                                key="player_name_input",
                                help="Required to start the game")
        
        # Topic input
        new_topic = st.text_input("Trivia Topic:", 
                                 value=st.session_state.topic,
                                 key="topic_input",
                                 help="Required to start the game")
        
        # Update buttons in two columns
        col1, col2 = st.sidebar.columns(2)
        
        # Update Name button
        with col1:
            if st.button("Update Name", use_container_width=True):
                if new_name.strip():
                    if st.session_state.game_active and st.session_state.questions_asked > 0:
                        sheet = authenticate_google_sheets()
                        update_leaderboard_entry(
                            sheet,
                            st.session_state.player_name,
                            st.session_state.total_score,
                            st.session_state.topic,
                            st.session_state.questions_asked,
                            st.session_state.game_length,
                            force_write=False  # Cache only
                        )
                    st.session_state.player_name = new_name.strip()
                    st.rerun()
                else:
                    st.sidebar.error("Please enter a player name")
        
        # Update Topic button
        with col2:
            if st.button("Update Topic", use_container_width=True):
                if new_topic.strip():
                    if st.session_state.game_active and st.session_state.questions_asked > 0:
                        sheet = authenticate_google_sheets()
                        update_leaderboard_entry(
                            sheet,
                            st.session_state.player_name,
                            st.session_state.total_score,
                            st.session_state.topic,
                            st.session_state.questions_asked,
                            st.session_state.game_length,
                            force_write=False  # Cache only
                        )
                    st.session_state.topic = new_topic.strip()
                    st.session_state.current_question = None
                    st.rerun()
                else:
                    st.sidebar.error("Please enter a topic")

    # Game Control Buttons
 #  st.sidebar.markdown("### Game Controls")
    if not st.session_state.game_active:
        if st.sidebar.button("Start Game", use_container_width=True, type="primary"):
            if st.session_state.player_name.strip() and st.session_state.topic.strip():
                st.session_state.game_active = True
                reset_game_state()
                st.session_state.game_active = True
                st.rerun()
            else:
                st.sidebar.error("Please enter both player name and topic to start!")
    else:
        # End Game button
        if st.sidebar.button("End Game", use_container_width=True, type="secondary"):
            sheet = authenticate_google_sheets()
            if st.session_state.questions_asked > 0:
                update_leaderboard_entry(
                    sheet,
                    st.session_state.player_name,
                    st.session_state.total_score,
                    st.session_state.topic,
                    st.session_state.questions_asked,
                    st.session_state.game_length,
                    force_write=True  # Write to sheet
                )
            reset_game_state()
            st.rerun()
        
        # Start New Game button
        if st.sidebar.button("Start New Game", use_container_width=True, type="primary"):
            sheet = authenticate_google_sheets()
            if st.session_state.questions_asked > 0:
                update_leaderboard_entry(
                    sheet,
                    st.session_state.player_name,
                    st.session_state.total_score,
                    st.session_state.topic,
                    st.session_state.questions_asked,
                    st.session_state.game_length,
                    force_write=True  # Write to sheet
                )
            reset_game_state()
            st.rerun()

    # Add after the other sidebar game control buttons:
    if st.sidebar.button("Reset All", use_container_width=True, type="secondary"):
        st.session_state.question_cache.clear()  # Clear question cache
        reset_game_state()  # Reset other game state
        st.rerun()

    # Player Stats
    if st.session_state.player_name:
        st.sidebar.markdown(f"""
        <div class="player-info">
        👤 Player: {st.session_state.player_name}<br>
        💫 Total Score: {st.session_state.total_score}<br>
        📝 Questions: {st.session_state.questions_asked}/{st.session_state.game_length}<br>
        🎯 Topic: {st.session_state.topic}
        </div>
        """, unsafe_allow_html=True)
    
    # Display leaderboards
    display_leaderboards()

    # Main Game Area
    if st.session_state.game_active and st.session_state.questions_asked < st.session_state.game_length:
        if not st.session_state.current_question:
            with st.spinner("Loading next question..."):
                st.session_state.current_question = generate_trivia_question(st.session_state.topic)
                st.session_state.answer_selected = False
                st.session_state.feedback = None
        
        if st.session_state.current_question:
            # Timer and current stats
            current_time = time.time()
            time_elapsed = current_time - st.session_state.current_question["start_time"]
            time_remaining = max(0, 65 - time_elapsed)
            
            timer_class = "timer-warning" if time_remaining < 10 else ""
            progress_percentage = (time_remaining / 65) * 100

            st.markdown(f"""
                <div class="timer-container {timer_class}">
                    <div class="timer-display">
                        ⏱️ {int(time_remaining)}s
                    </div>
                    <div class="progress-bar">
                        <div class="progress-bar-fill" style="width: {progress_percentage}%;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Auto-submit when time runs out
            if time_remaining <= 0 and not st.session_state.answer_selected:
                st.session_state.answer_selected = True
                st.session_state.feedback = (
                    f"""⏰ Time's up! The correct answer was {st.session_state.current_question['correct']}.
                    
                    {st.session_state.current_question['fact_check']}""",
                    "error"
                )
                st.rerun()
            
            # Current game stats
            st.markdown(f"""
            <div class="current-stats">
            👤 Player: {st.session_state.player_name} | 
            💫 Score: {st.session_state.total_score} | 
            📝 Questions: {st.session_state.questions_asked + 1}/{st.session_state.game_length} |
            🎯 Topic: {st.session_state.topic}
            </div>
            """, unsafe_allow_html=True)
            
            # Question display
            st.markdown(f"""
            <div class="question-display">
            Question {st.session_state.questions_asked + 1}/{st.session_state.game_length}:
            {st.session_state.current_question["question"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Answer choices in two columns
            col1, col2 = st.columns(2)
            
            # First two answers (A and B)
            with col1:
                for i in range(2):
                    if time_remaining > 0:
                        if st.button(st.session_state.current_question["choices"][i], 
                                   key=f"choice_{i}", 
                                   disabled=st.session_state.answer_selected,
                                   use_container_width=True):
                            time_remaining = check_answer(chr(65 + i))
            
            # Last two answers (C and D)
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
        
    elif st.session_state.questions_asked >= st.session_state.game_length:
        # Display enhanced game over screen with all stats
        display_game_over(
            st.session_state.player_name,
            st.session_state.total_score,
            st.session_state.topic,
            st.session_state.questions_asked,
            st.session_state.game_length
        )
    
    # Footer section
    st.markdown("---")
    st.markdown("""
    <div class="footer-section">
        <div class="footer-content">
            <span style="font-size: 1.2rem; font-weight: 600;">
                GenAI Trivia Challenge
            </span>
            <br>
            <span style="font-size: 1rem;">
                Designed by 
                <a href="https://www.linkedin.com/in/lindsayhiebert/" target="_blank" 
                   style="text-decoration: none; color: #1E88E5;">
                   Lindsay Hiebert
                </a>
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Footer image
    footer_img = load_and_resize_image("FooterImage.png", width=800)
    if footer_img:
        aspect_ratio = 0.02
        new_height = int(800 * aspect_ratio)
        from PIL import Image
        resized_img = footer_img.resize((1200, new_height), Image.Resampling.LANCZOS)
        st.image(resized_img, use_container_width=True)
    
    st.markdown("---")
    
#ICONS to use: 

#🎮 Game Controls
#👤 Player Settings
#🎲 Game Length
#🏆 Leaderboard
#🌟 Top Scores
#📊 Statistics
#🎯 Topics
#🚀 Start Game
#🔄 Update
#⏱️ Timer
#📝 Questions
#🎯 Topic
#🏆 Rankings
#🎉 Game Ove
#🎯 Topic Leaderboar
#✨ Special Features


if __name__ == "__main__":
    main()