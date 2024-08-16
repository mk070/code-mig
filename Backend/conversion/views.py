import os
import time
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .additionals import gemini_api, source_files, remove_markers

@csrf_exempt
def convert_code(request):
    if request.method == 'POST':
        source_language = request.POST.get('source_language', '')
        target_language = request.POST.get('target_language', '')

        if not source_language or not target_language:
            return JsonResponse({'status': 'error', 'message': 'Source or target language is missing.'}, status=400)

        # Retrieve the main file name from the session
        main_file_name = 'main.cbl'
        print('main_file_name in conversion/views.py :',main_file_name)

        if not main_file_name:
            return JsonResponse({'status': 'error', 'message': 'Main file name is missing.'}, status=400)

        source_file_data = source_files.get_source_files_dict(main_file_name, settings.TEMP_FOLDER)
        print('source_file_data : ',source_file_data)

        start_time = time.time()

        try:
            response = gemini_api.convert_code(source_file_data, source_language, target_language)
            clean_response = remove_markers.remove_code_markers(response)
            clean_response_dict = json.loads(clean_response)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Failed to decode JSON from API response.'}, status=500)
        except Exception as e:
            print(f"An error occurred during conversion: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred during conversion: {str(e)}'}, status=500)

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Total time taken for conversion : {time_taken:.2f} seconds.")

        try:
            for filename, code in clean_response_dict['code'].items():
                filepath = os.path.join(settings.CONVERTED_TEMP_FOLDER, filename)
                with open(filepath, 'w') as file:
                    file.write(code)
        except Exception as e:
            print(f"Error saving converted code: {str(e)}")
            return JsonResponse({'status': 'error', 'message': 'Failed to save converted code.'}, status=500)

        return JsonResponse({'status': 'success', 'converted_code': clean_response_dict['code']})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
