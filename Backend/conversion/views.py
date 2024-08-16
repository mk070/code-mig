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
        print('source_language',source_language)
        print('target_language',target_language)
        if not source_language or not target_language:
            return JsonResponse({'status': 'error', 'message': 'Source or target language is missing.'}, status=400)

        main_file_name = request.session.get('main_file_name', '')

        source_file_data = source_files.get_source_files_dict(main_file_name, settings.TEMP_FOLDER)
        print(source_file_data)

        start_time = time.time()

        try:
            response = gemini_api.convert_code(source_file_data, source_language, target_language)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred during conversion: {str(e)}'}, status=500)

        clean_response = remove_markers.remove_code_markers(response)
        clean_response_dict = json.loads(clean_response)

        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Total time taken for conversion : {time_taken:.2f} seconds.")

        for filename, code in clean_response_dict['code'].items():
            filepath = os.path.join(settings.CONVERTED_TEMP_FOLDER, filename)
            with open(filepath, 'w') as file:
                file.write(code)

        return JsonResponse({'status': 'success', 'converted_code': clean_response_dict['code']})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
