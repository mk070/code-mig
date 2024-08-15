import os
import google.generativeai as genai
from dotenv import load_dotenv
from .prompt import conversion_prompt, accuracy_prompt

# Load environment variables
load_dotenv()

# Load the API key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def convert_code(source_code, source_language, target_language):
    refined_prompt = conversion_prompt(source_code, source_language, target_language)
    prompt = [
        {
            'role': 'user',
            'parts': [refined_prompt]
        }
    ]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def check_accuracy(source_language, source_output, target_language, target_output):
    refined_prompt = accuracy_prompt(source_language, source_output, target_language, target_output)
    prompt = [
        {
            'role': 'user',
            'parts': [refined_prompt]
        }
    ]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    json_response = response.text
    return json_response