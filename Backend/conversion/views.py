import os
import time
import json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .additionals import gemini_api, source_files, remove_markers
from pprint import pprint, PrettyPrinter

# Create your views here.
@csrf_exempt
def convert_code(request):
    if request.method == 'POST':
        source_language = request.POST.get('source_language', '').strip()
        target_language = request.POST.get('target_language', '').strip()

        # Retrieve the main file name from the session
        main_file_name = request.session.get('main_file_name', '')
        
        source_file_data = source_files.get_source_files_dict(main_file_name, settings.TEMP_FOLDER)
        # print(type(source_file_data))
        # Configure PrettyPrinter to format the output nicely
        # pp = PrettyPrinter(indent=2, width=100, compact=False)
        # pp.pprint(source_file_data)

        start_time = time.time()

        response = gemini_api.convert_code(source_file_data, source_language, target_language)
        clean_response = remove_markers.remove_code_markers(response)
        clean_response = clean_response.replace("'", '"')
        print(clean_response)
        clean_response_dict = json.loads(clean_response)
        print(clean_response_dict)
        print(type(clean_response_dict))

        end_time = time.time()
        time_taken = end_time - start_time

        print(f"Total time taken for conversion : {time_taken:.2f} seconds.")

        for filename, code in clean_response_dict['code'].items():
            filepath = os.path.join(settings.CONVERTED_TEMP_FOLDER, filename)
            with open(filepath, 'w') as file:
                file.write(code)
            print(f"Saved {filename} to {settings.CONVERTED_TEMP_FOLDER}")

        # need to clean converted_temp_folder
        # need to copy the datasets to converted_temp_folder

        return JsonResponse({'status': 'success', 'message': 'File Data Format success..'})

    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
        