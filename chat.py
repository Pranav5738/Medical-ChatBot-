import random
from pathlib import Path
import pandas as pd
import streamlit as st
from sentence_transformers import SentenceTransformer, util
from googletrans import Translator

st.set_page_config(page_title="Medical Chatbot", page_icon="🤖", layout="centered")

st.markdown(
    """
    <style>
        :root {
            color-scheme: light;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(255, 183, 3, 0.18), transparent 30%),
                radial-gradient(circle at top right, rgba(46, 196, 182, 0.16), transparent 26%),
                linear-gradient(180deg, #ffffff 0%, #f3f8ff 100%);
            color: #10253e;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2.5rem;
            max-width: 760px;
        }

        .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
            color: #10253e;
        }

        .stTitle {
            color: #0b5cab;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #0b5cab;
        }

        .stTextInput label, .stSelectbox label {
            color: #16324f !important;
            font-weight: 700 !important;
        }

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] > div,
        .stSelectbox input,
        .stTextInput textarea {
            background: #ffffff !important;
            border: 1px solid rgba(16, 37, 62, 0.18) !important;
            border-radius: 14px !important;
            color: #10253e !important;
            box-shadow: 0 8px 24px rgba(13, 44, 84, 0.06);
        }

        div[data-baseweb="select"] {
            background: #ffffff !important;
            border-radius: 14px !important;
        }

        div[data-baseweb="popover"] {
            background: #ffffff !important;
        }

        ul[role="listbox"],
        div[data-baseweb="menu"] {
            background: #ffffff !important;
            color: #10253e !important;
        }

        li[role="option"] {
            color: #10253e !important;
            background: #ffffff !important;
        }

        li[role="option"][aria-selected="true"],
        li[role="option"]:hover {
            background: #e8f3ff !important;
            color: #0b5cab !important;
        }

        .stButton > button {
            background: linear-gradient(90deg, #ffb703 0%, #1d9bf0 100%);
            color: white;
            border: none;
            border-radius: 14px;
            padding: 0.7rem 1.1rem;
            font-weight: 700;
            box-shadow: 0 10px 24px rgba(29, 155, 240, 0.18);
        }

        .stButton > button:hover {
            filter: brightness(1.03);
            transform: translateY(-1px);
        }

        .stAlert {
            background: rgba(255, 255, 255, 0.98);
            border-radius: 14px;
            color: #10253e !important;
        }

        [data-testid="stAppViewContainer"] {
            background: transparent;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load your data
DATASET_PATH = Path(__file__).resolve().parent / 'dataset - Sheet1.csv'
df = pd.read_csv(DATASET_PATH)

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define medical keywords for fallback
medical_keywords = {
    "fever": "It sounds like you may have a fever. Stay hydrated and consider seeing a doctor if symptoms persist.",
    "cough": "A persistent cough might be due to an infection or allergy. Try warm fluids and rest.",
    "headache": "Headaches can have many causes, including stress and dehydration. Consider resting and drinking water.",
    "cold": "Common colds usually go away on their own. Stay warm, drink fluids, and get rest.",
}

# List of health tips categorized by keywords
health_tips = {
    "sleep": [
        "Try to get at least 7-8 hours of sleep each night.",
        "Establish a regular sleep routine to improve sleep quality.",
        "Avoid screens before bed to help your mind relax.",
    ],
    "energy": [
        "Make sure you're eating a balanced diet to maintain energy.",
        "Exercise regularly to boost your energy levels.",
        "Stay hydrated throughout the day to avoid fatigue.",
    ],
    "stress": [
        "Take short breaks throughout the day to reduce stress.",
        "Practice mindfulness or meditation to help manage stress.",
        "Engage in physical activity to reduce anxiety and stress.",
    ],
    "general": [
        "Drink plenty of water throughout the day.",
        "Get at least 30 minutes of exercise every day.",
        "Eat a balanced diet rich in fruits and vegetables.",
    ],
}

# Function to get personalized health tip
def get_personalized_health_tip(user_input):
    # Convert input to lowercase for easier matching
    user_input_lower = user_input.lower()

    # Check for specific keywords in the user input
    if "tired" in user_input_lower or "fatigue" in user_input_lower:
        return random.choice(health_tips["energy"])
    elif "sleep" in user_input_lower or "rest" in user_input_lower:
        return random.choice(health_tips["sleep"])
    elif "stress" in user_input_lower or "anxious" in user_input_lower:
        return random.choice(health_tips["stress"])
    else:
        # Default to a general health tip if no specific keywords match
        return random.choice(health_tips["general"])

# Function to find the best cure based on similarity
def find_best_cure(user_input):
    user_input_embedding = model.encode(user_input, convert_to_tensor=True)
    disease_embeddings = model.encode(df['disease'].tolist(), convert_to_tensor=True)
    
    similarities = util.pytorch_cos_sim(user_input_embedding, disease_embeddings)[0]
    best_match_idx = similarities.argmax().item()
    best_match_score = similarities[best_match_idx].item()
    
    # Define a similarity threshold for valid matches
    SIMILARITY_THRESHOLD = 0.5  # Adjust as needed
    
    if best_match_score < SIMILARITY_THRESHOLD:
        # Check for keywords in user input
        for keyword, response in medical_keywords.items():
            if keyword in user_input.lower():
                return response
        
        # Default fallback response if no keywords match
        return "I'm sorry, I don't have enough information on this. Please consult a healthcare professional."
    
    return df.iloc[best_match_idx]['cure']

# Function to translate text
def translate_text(text, dest_language='en'):
    if not text or dest_language == 'en':
        return text

    try:
        return translator.translate(text, dest=dest_language).text
    except Exception:
        return text

# Initialize translator
translator = Translator(service_urls=['translate.googleapis.com'])

# Streamlit UI
st.title("Medical Chatbot 🤖")
user_input = st.text_input("Ask a question:")

# Language selection (user chooses from the updated list of languages)
language_choice = st.selectbox("Select Language", [
    "English", "Hindi", "Gujarati", "Korean", "Turkish",
    "German", "French", "Arabic", "Urdu", "Tamil", "Telugu", "Chinese", "Japanese"
])

# Language codes based on the user selection
language_codes = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Korean": "ko",
    "Turkish": "tr",
    "German": "de",
    "French": "fr",
    "Arabic": "ar",
    "Urdu": "ur",
    "Tamil": "ta",
    "Telugu": "te",
    "Chinese": "zh-CN",  # Simplified Chinese
    "Japanese": "ja",
}

# Button for response
if st.button("Get Response"):
    if user_input:
        response = find_best_cure(user_input)
        # Translate the response based on the selected language
        translated_response = translate_text(response, dest_language=language_codes[language_choice])
        st.write(f"**My Suggestion is:** {translated_response}")
        st.write("*Please note, the translation is provided by AI and might not be perfect.*")

# Add a button to get a personalized health tip
if st.button("Get a Personalized Health Tip"):
    if user_input:
        personalized_tip = get_personalized_health_tip(user_input)
        translated_tip = translate_text(personalized_tip, dest_language=language_codes[language_choice])
        st.write(f"**Health Tip:** {translated_tip}")
        st.write("*Please note, the translation is provided by AI and might not be perfect.*")
