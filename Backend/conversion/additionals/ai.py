import os
import re
import google.generativeai as genai
from .remove_markers import remove_code_markers

# Load environment variables
def get_supported_languages():
    return ["Python", "Java", "Pyspark", "C++", "COBOL",".NET"]

def clean_response(code):
    # Remove Python comments (lines starting with #) while preserving indentation
    code_without_comments = re.sub(r'^\s*#.*$', '', code, flags=re.MULTILINE)
    
    # Remove empty lines and strip leading/trailing whitespace while preserving indentation
    cleaned_code = "\n".join([line for line in code_without_comments.splitlines() if line.strip()])
    
    return cleaned_code

# Load the API key from .env file
GEMINI_API_KEY = "AIzaSyDNmwDtBeRtS_0KQR0DTMCLMfW-bK6IGTU"
genai.configure(api_key=GEMINI_API_KEY)

def translate_code(source_language, target_language, code):
    # Construct the prompt for code conversion
    refined_prompt = (
        f'''I want you to act as a code analyst and a code migration engineer for a software modernisation project. I will provide you with code written in one programming language, and your job is to convert it into another specified programming language. For example you will do conversion from COBOL to Python or .NET or SQL and vice-versa.
            Make sure you follow the below rules:
            1. Your conversion should maintain the original logic and functionality while adhering to the structure of the target language.
            2. Your code should not have any syntax or semantic errors. 
            3. You are strictly required to only perform code conversion. Do not include explanations, comments, or any additional information unless explicitly requested. 
            4. If the source code references any external files or datasets, make sure to include equivalent references in the converted code where necessary.
            5. Check whether the external files or datasets or database tables are available on the provided destination.
            6. You must not answer any queries unrelated to code conversion. If a non-code conversion related request is made, respond with: 'Please provide the code for conversion.’

            Convert source_language - {source_language} to target_language- {target_language}
            Source-code to convert : {code}'''
    )
    prompt = [
        {
            'role': 'user',
            'parts': [refined_prompt]
        }
    ]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
 # Clean the response to remove unnecessary content
    cleaned_response = remove_code_markers(response.text)
    return cleaned_response