import os
import google.generativeai as genai
from dotenv import load_dotenv
from .prompt import conversion_prompt, accuracy_prompt

# Load environment variables
load_dotenv()

# Load the API key from .env file
GEMINI_API_KEY = 'AIzaSyDNmwDtBeRtS_0KQR0DTMCLMfW-bK6IGTU'
genai.configure(api_key=GEMINI_API_KEY)

def convert_code(source_code, source_language, target_language):
    try:
        # Log the languages being used
        print(f"Converting from {source_language} to {target_language}")
        
        # Generate the refined prompt
        refined_prompt = conversion_prompt(source_code, source_language, target_language)
        print(f"Refined prompt generated: {refined_prompt}")
        
        prompt = [
            {
                'role': 'user',
                'parts': [refined_prompt]
            }
        ]

        # Initialize the model and generate content
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Check if response contains text
        if hasattr(response, 'text'):
            print("Conversion successful")
            return response.text
        else:
            print("Conversion failed, no text in response")
            raise ValueError("No text in response from API")
    
    except Exception as e:
        print(f"Error in convert_code: {str(e)}")
        raise

def check_accuracy(source_language, source_output, target_language, target_output):
    try:
        # Log the languages and outputs being checked
        print(f"Checking accuracy between {source_language} and {target_language}")
        
        # Generate the refined prompt for accuracy checking
        refined_prompt = accuracy_prompt(source_language, source_output, target_language, target_output)
        print(f"Refined accuracy prompt generated: {refined_prompt}")
        
        prompt = [
            {
                'role': 'user',
                'parts': [refined_prompt]
            }
        ]

        # Initialize the model and generate content
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Check if response contains text
        if hasattr(response, 'text'):
            print("Accuracy check successful")
            return response.text
        else:
            print("Accuracy check failed, no text in response")
            raise ValueError("No text in response from API")
    
    except Exception as e:
        print(f"Error in check_accuracy: {str(e)}")
        raise
