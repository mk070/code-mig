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

def translate_code(code,source_language, target_language):
    print('target_language : ',target_language)
    # Construct the prompt for code conversion
    refined_prompt = (
        f'''You are an advanced AI specializing in code conversion. Your task is to convert multiple {source_language} source files to the {target_language} language while preserving their functionality and structure. The source files are provided in a dictionary format where the 'code' key contains the {source_language} source files, and each key represents a filename with its corresponding code.
**Instructions:**
1. Convert all the {source_language} source files provided in the 'code' dictionary to {target_language}.
2. Merge the converted code into a single output file without any code markers.
3. Ensure that all functionalities from the input source files are available and preserved in the converted target file.
4. Maintain correct syntax, indentation, and code structure in the converted code.
5. Handle .DAT files and other external files correctly based on their format. If the file is binary or has a specific encoding, ensure the converted code reads and processes the file using the correct methods.
6. Initialize all variables, properties, and fields appropriately to avoid any nullability warnings (such as CS8618 or CS8600 in C#) or runtime errors. If a property or field is non-nullable, ensure it is initialized with a default value or through a constructor.
7. Do not include any functionality in the converted code that requires user input to terminate the execution unless that functionality is explicitly present in the source code.
8. If any external references (datasets, database files) are present in the source code, ensure equivalent handling in the target code. The external files are provided in the 'external_files' key, which lists all related datasets and files.
9. The 'external_files_sample_data' key contains a sample of the first three rows from each dataset, if available. This sample is provided to inform you of the dataset's structure, helping you avoid incorrect assumptions about the data format. Use this sample data to understand the structure but ensure that the actual code interacts with the complete dataset from the 'external_files' key. The model should not create data or simulate datasets on its own unless such functionality is explicitly present in the source language code.
10. If certain legacy COBOL functionalities cannot be directly converted due to limitations or differences in the target language, adapt the code appropriately while maintaining the original intent and functionality. Provide a working solution rather than changing the entire functionality unnecessarily.
11. Return only the final converted code as the output, with no additional explanations or metadata.
12. Strictly don't add Console.Readkey() or any other input termination methods in the converted code unless explicitly mentioned in the source code.
13. Comment the Console.Readkey() command in .NET code if it is present in the converted code.
14. Ensure that the converted code is optimized for performance and edge cases, ensuring robustness and reliability. It should be runnable, free from bugs, and avoid trade-offs that compromise the code's integrity.

Here is the source file data for conversion:
{code}''')
    
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