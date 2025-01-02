# 🧠 GenAI Trivia Challenge

An engaging trivia game powered by OpenAI's GPT-4 that tests your knowledge across various topics while racing against time!

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://openaitriviaapp.streamlit.app)

## Features

- **Dynamic Question Generation**: Leverages GPT-4 to create unique, engaging, and factually accurate questions
- **Real-time Scoring**: Race against time - faster answers earn more points!
- **Interactive UI**: Clean, responsive interface with instant feedback
- **Global Leaderboard**: Compete with players worldwide and track high scores
- **Varied Topics**: Questions span across multiple categories, ensuring engaging gameplay
- **Educational Value**: Learn interesting facts with detailed explanations for each answer

## Installation

1. Clone the repository:
```bash
git clone https://github.com/lhiebert01/OpenAITriviaApp.git
cd OpenAITriviaApp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file using the template:
```bash
cp .env.template .env
```

2. Add your OpenAI API key to the `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
```

3. Set up Google Sheets integration:
   - Place your OAuth JSON file in the project root
   - Ensure the filename matches the one in the code
   - Keep this file secure and never commit it to version control

## Usage

1. Run locally:
```bash
streamlit run app.py
```

2. Enter your name to begin
3. Answer questions before time runs out
4. Get instant feedback and explanations
5. Track your score on the global leaderboard

## Development

Built with:
- Streamlit for the web interface
- OpenAI's GPT-4 for question generation
- Google Sheets API for leaderboard management
- Python's dotenv for environment management

## Deployment

The app is deployed on Streamlit Cloud:

1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Configure secrets in Streamlit's dashboard:
   - Add OPENAI_API_KEY
   - Add Google Sheets credentials

## Security

- API keys and credentials are managed securely through environment variables
- Google Sheets OAuth credentials are kept private
- Sensitive files are excluded from version control

## Credits

Developed by [Lindsay Hiebert](https://www.linkedin.com/in/lindsayhiebert/), combining AI technology with interactive learning.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

© 2024 Lindsay Hiebert. All Rights Reserved.