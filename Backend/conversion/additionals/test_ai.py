import google.generativeai as genai
from dotenv import load_dotenv
from .prompt import conversion_prompt
import os

# Load environment variables
load_dotenv()

# Load the API key from .env file
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

def test_convert_code():
    source_language = 'cobol'
    target_language = 'python'
    source_file_data = {
        'code': {
            'main.cbl': "       IDENTIFICATION DIVISION.\n       PROGRAM-ID. CONDITIONALS.\n\n       DATA DIVISION.\n       WORKING-STORAGE SECTION.\n\n       01 NUM1 PIC 9(9).\n       01 NUM2 PIC 9(9).\n       01 NUM3 PIC 9(5).\n       01 NUM4 PIC 9(6).\n\n       01 NEG-NUM PIC S9(9) VALUE -1234.\n       01 CLASS1 PIC X(9) VALUE 'ABCD '.\n       01 CHECK-VAL PIC 9(3).\n       88 PASS VALUES ARE 041 THRU 100.\n       88 FAIL VALUES ARE 000 THRU 040.\n\n       PROCEDURE DIVISION.\n       MOVE 25 TO NUM1.\n       MOVE 25 TO NUM3.\n       MOVE 15 TO NUM2.\n       MOVE 15 TO NUM4.\n\n       IF NUM1 > NUM2 THEN\n           DISPLAY 'IN LOOP 1 - IF BLOCK'\n           IF NUM3 = NUM4 THEN\n               DISPLAY 'IN LOOP 2 - IF BLOCK'\n           ELSE\n               DISPLAY 'IN LOOP 2 - ELSE BLOCK'\n           END-IF\n       ELSE\n           DISPLAY 'IN LOOP 1 - ELSE BLOCK'\n       END-IF.\n\n       MOVE 65 TO CHECK-VAL.\n       IF PASS THEN\n           DISPLAY 'PASSED WITH ' CHECK-VAL ' MARKS.'\n       ELSE\n           IF FAIL THEN\n               DISPLAY 'FAILED WITH ' CHECK-VAL ' MARKS.'\n           END-IF\n       END-IF.\n\n       EVALUATE TRUE\n           WHEN NUM1 < 2\n               DISPLAY 'NUM1 LESS THAN 2'\n           WHEN NUM1 < 19\n               DISPLAY 'NUM1 LESS THAN 19'\n           WHEN NUM1 < 1000\n               DISPLAY 'NUM1 LESS THAN 1000'\n           WHEN OTHER\n               DISPLAY 'NUM1 DOES NOT MEET ANY CONDITION'\n       END-EVALUATE.\n\n       STOP RUN.\n\n"
        },
        'external_files': []
    }

    try:
        refined_prompt = conversion_prompt(source_file_data, source_language, target_language)
        print(f"Refined prompt generated: {refined_prompt}")
        
        prompt = [
            {
                'role': 'user',
                'parts': [refined_prompt]
            }
        ]

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        print(f"Raw API response: {response}")

        # Inspect the raw response
        if isinstance(response, list) and len(response) > 0 and hasattr(response[0], 'text'):
            print("Conversion successful")
            return response[0].text
        elif isinstance(response, dict) and 'text' in response:
            print("Conversion successful")
            return response['text']
        else:
            print("Unexpected response format or missing 'text' attribute")
            raise ValueError("No valid text attribute found in the response")

    except Exception as e:
        print(f"Error in convert_code: {str(e)}")

if __name__ == "__main__":
    test_convert_code()
