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
    try:
        print(f"Converting from {source_language} to {target_language}")
        
        refined_prompt = conversion_prompt(source_code, source_language, target_language)
        print(f"Refined prompt generated: {refined_prompt}")
        
        prompt = [
            {
                'role': 'user',
                'parts': [refined_prompt]
            }
        ]

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        print(f"Raw API response: {response}")  # Log the full API response

        # Checking response type and content
        if isinstance(response, list):
            if len(response) > 0:
                print(f"First item in response: {response[0]}")
                if hasattr(response[0], 'text'):
                    print("Conversion successful")
                    return response[0].text
            raise ValueError("No valid text attribute found in the list response")
        elif isinstance(response, dict):
            if 'text' in response:
                print("Conversion successful")
                return response['text']
            raise ValueError("No valid text attribute found in the dictionary response")
        else:
            print("Unexpected response type or missing 'text' attribute")
            raise ValueError("No valid text attribute found in the response")

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
        print(f"Raw API response: {response}")
        
        # Check if response contains text
        if isinstance(response, list) and len(response) > 0 and hasattr(response[0], 'text'):
            print("Accuracy check successful")
            return response[0].text
        elif isinstance(response, dict) and 'text' in response:
            print("Accuracy check successful")
            return response['text']
        else:
            print("Accuracy check failed, no valid text attribute found in the response")
            raise ValueError("No valid text attribute found in the response")
    
    except Exception as e:
        print(f"Error in check_accuracy: {str(e)}")
        raise
