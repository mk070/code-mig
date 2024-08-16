import os
import shutil
import stat
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from git import Repo

@csrf_exempt
def save_uploads(request):
    if request.method == 'POST':
        clean_temp_folder(settings.TEMP_FOLDER)

        single_source_code = request.FILES.get('single_source_code')
        github_url = request.POST.get('github_url', '').strip()
        main_file_name = request.POST.get('main_file_name', '').strip()

        if main_file_name:
            if main_file_name[-4:] != '.cbl' and main_file_name[-4:] != '.cob':
                main_file_name += '.cbl'
            elif main_file_name[-4:] != '.cbl' and main_file_name[-4:] == '.cob':
                main_file_name = main_file_name[:-4] + '.cbl'

        if single_source_code:
            if main_file_name == '':
                main_file_name = "main.cbl"
            save_path = os.path.join(settings.TEMP_FOLDER, main_file_name)
            with default_storage.open(save_path, 'wb+') as destination:
                for chunk in single_source_code.chunks():
                    destination.write(chunk)

        elif len(request.FILES) > 0:
            for file_key, uploaded_file in request.FILES.items():
                save_path = os.path.join(settings.TEMP_FOLDER, uploaded_file.name)
                with default_storage.open(save_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

            convert_cob_to_cbl()

            if not os.path.exists(os.path.join(settings.TEMP_FOLDER, main_file_name)):
                return JsonResponse({'status': 'error', 'message': f'Main file "{main_file_name}" not found in the uploaded files.'}, status=400)

        elif github_url:
            try:
                Repo.clone_from(github_url, settings.TEMP_FOLDER)

                convert_cob_to_cbl()

                if not os.path.exists(os.path.join(settings.TEMP_FOLDER, main_file_name)):
                    return JsonResponse({'status': 'error', 'message': f'Main file "{main_file_name}" not found in the provided repository.'}, status=400)

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to clone GitHub repo: {str(e)}'}, status=400)

        request.session['main_file_name'] = main_file_name

        return JsonResponse({'status': 'success', 'message': 'Files processed successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def clean_temp_folder(temp_folder_path):
    if os.path.exists(temp_folder_path):
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        shutil.rmtree(temp_folder_path, onerror=remove_readonly)
    os.makedirs(temp_folder_path)

def convert_cob_to_cbl():
    for root, dirs, files in os.walk(settings.TEMP_FOLDER):
        for filename in files:
            if filename.endswith(".cob"):
                new_filename = filename.replace('.cob', '.cbl')
                old_file = os.path.join(root, filename)
                new_file = os.path.join(root, new_filename)
                os.rename(old_file, new_file)
