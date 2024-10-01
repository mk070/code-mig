import os
import shutil
import stat
import zipfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import default_storage
from git import Repo
from backend import globals

@csrf_exempt
def save_uploads(request):
    if request.method == 'POST':
        clean_temp_folder(settings.TEMP_FOLDER)

        github_url = request.POST.get('github_url', '').strip()
        main_file_name = request.POST.get('main_file_name', '').strip()
        database_file_name = request.POST.get('database_file_name', '').strip()


        print('from frontend - main_file_name : ',main_file_name)
        print('from frontend - database_file_name : ',database_file_name)
        globals.DATABASE_FILE_NAME = database_file_name
        print('DATABASE_FILE_NAME : ',globals.DATABASE_FILE_NAME)

        if main_file_name:
            if main_file_name[-4:] != '.cbl' and main_file_name[-4:] != '.cob':
                main_file_name += '.cbl'
            elif main_file_name[-4:] != '.cbl' and main_file_name[-4:] == '.cob':
                main_file_name = main_file_name[:-4] + '.cbl'
                
        print(main_file_name)

        if len(request.FILES) > 0:
            # Handling files sent with the key 'files'
            files = request.FILES.getlist('files')
            for uploaded_file in files:
                save_path = os.path.join(settings.TEMP_FOLDER, uploaded_file.name)
                with default_storage.open(save_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                
                # Check if the uploaded file is a zip file
                if uploaded_file.name.endswith('.zip'):
                    with zipfile.ZipFile(save_path, 'r') as zip_ref:
                        zip_ref.extractall(settings.TEMP_FOLDER)
                    os.remove(save_path)  # Optionally, remove the zip file after extraction

            convert_cob_to_cbl()

            if not os.path.exists(os.path.join(settings.TEMP_FOLDER, main_file_name)):
                return JsonResponse({'status': 'error', 'message': f'Main file "{main_file_name}" not found in the uploaded files.'}, status=400)

        elif github_url:
            try:
                # repo_path = os.path.join(settings.TEMP_FOLDER, 'github_repo')
                Repo.clone_from(github_url, settings.TEMP_FOLDER)

                convert_cob_to_cbl()

                if not os.path.exists(os.path.join(settings.TEMP_FOLDER, main_file_name)):
                    return JsonResponse({'status': 'error', 'message': f'Main file "{main_file_name}" not found in the provided repository.'}, status=400)

            except Exception as e:
                return JsonResponse({'status': 'error', 'message': f'Failed to clone GitHub repo: {str(e)}'}, status=400)
            
        # Store main_file_name and db_file_name in session for future use
        request.session['main_file_name'] = main_file_name
        request.session['database_file_name'] = database_file_name

        print('from uploads : ',request.session['database_file_name'] )
        print('session : ',request.session.keys())

        return JsonResponse({'status': 'success', 'message': 'Files processed successfully'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# Utility function to clean the TEMP_FOLDER
def clean_temp_folder(temp_folder_path):
    if os.path.exists(temp_folder_path):
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        shutil.rmtree(temp_folder_path, onerror=remove_readonly)
    os.makedirs(temp_folder_path)


# Function to replace .cob to .cbl
def convert_cob_to_cbl():
    for root, dirs, files in os.walk(settings.TEMP_FOLDER):
        for filename in files:
            # Check if the file has a .cob extension
            if filename.endswith(".cob"):
                # Create the new filename with .cbl extension
                new_filename = filename.replace('.cob', '.cbl')
                # Full file paths
                old_file = os.path.join(root, filename)
                new_file = os.path.join(root, new_filename)
                # Rename the file
                os.rename(old_file, new_file)