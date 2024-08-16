import os
import time
import json
from django.conf import settings
from django.http import JsonResponse, HttpResponse  # Ensure HttpResponse is imported
from django.views.decorators.csrf import csrf_exempt
from .additionals import gemini_api, source_files, remove_markers,ai

@csrf_exempt
def convert_code(request):
    if request.method == 'POST':
        source_language = request.POST.get('source_language', '')
        target_language = request.POST.get('target_language', '')

        if not source_language or not target_language:
            return JsonResponse({'status': 'error', 'message': 'Source or target language is missing.'}, status=400)

        main_file_name = 'main.cbl'
        print('main_file_name in conversion/views.py :', main_file_name)

        if not main_file_name:
            return JsonResponse({'status': 'error', 'message': 'Main file name is missing.'}, status=400)

        source_file_data = source_files.get_source_files_dict(main_file_name, settings.TEMP_FOLDER)
        print('source_file_data : ', source_file_data)

        start_time = time.time()

        try:
            response = ai.translate_code(source_file_data['code'], source_language, target_language)
            print("Raw API response:", response)  # Log the raw API response for debugging
        except Exception as e:
            print(f"An error occurred during conversion: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred during conversion: {str(e)}'}, status=500)

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Total time taken for conversion : {time_taken:.2f} seconds.")

        # Return the converted code as plain text
        return HttpResponse(response, content_type='text/plain')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
