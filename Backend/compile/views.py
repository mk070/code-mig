import logging
import docker
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import os
import shutil
import stat

logger = logging.getLogger(__name__)

@csrf_exempt
def execute_code(request):

    if request.method == 'POST':
        clean_temp_folder(settings.TEMP_FOLDER)

        backend_dir = os.path.dirname(__file__)
        temp_folder = os.path.join(os.path.dirname(backend_dir), 'TEMP_FOLDER')
        os.makedirs(temp_folder, exist_ok=True)

        files = request.FILES.getlist('files')
        source_language = request.POST.get('sourcelanguage', '').lower()
        main_file_name = request.POST.get('main_file_name', '').strip()

        if not files   or not main_file_name:
            return JsonResponse({'error': 'No files, source language, or main file name provided.'}, status=400)

                     # Save all uploaded files to TEMP_FOLDER
        saved_files = []
        for file in files:
            file_path = os.path.join(temp_folder, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            saved_files.append(file.name)

        # Ensure main_file_name is in the saved files
        if main_file_name not in saved_files:
            return JsonResponse({'error': f'Main file "{main_file_name}" not found in uploaded files.'}, status=400)

        request.session['main_file_name'] = main_file_name

        client = docker.from_env()

        try:
# Determine the language based on the main file extension
            file_extension = os.path.splitext(main_file_name)[1].lower()

            if file_extension == '.cbl':
                subprograms = [f"data/{file}" for file in saved_files if file != main_file_name]
                command = f"./run.sh cobol data/{main_file_name} {' '.join(subprograms)}"
            elif file_extension == '.py':
                command = f"./run.sh python data/{main_file_name}"
            elif file_extension == '.java':
                command = f"./run.sh java data/{main_file_name}"
            elif file_extension == '.cs':
                command = f"./run.sh dotnet data/{main_file_name}"
            else:
                return JsonResponse({'error': f'Unsupported file extension: {file_extension}'}, status=400)
            
            container = client.containers.run(
                image="multi-language-compiler-updated",
                command=command,
                volumes={
                    temp_folder: {'bind': '/app/data', 'mode': 'rw'},
                    os.path.join(os.path.dirname(backend_dir), 'run.sh'): {'bind': '/app/run.sh', 'mode': 'ro'}
                },
                working_dir="/app",
                remove=True,
                stdout=True,
                stderr=True
            )
            output = container.decode('utf-8')
            print(f"Container output: {output}")

            # Extract the relevant part of the output (last lines)
            relevant_output = extract_relevant_output(output)
            print(f"Filtered output: {relevant_output}")

            return JsonResponse({'output': relevant_output})

        except docker.errors.ContainerError as e:
            logger.error(f"Container error: {str(e)}")
            return JsonResponse({'error': f"Container error: {str(e)}"}, status=500)
        except docker.errors.ImageNotFound as e:
            logger.error(f"Docker image not found: {str(e)}")
            return JsonResponse({'error': f"Docker image not found: {str(e)}"}, status=500)
        except docker.errors.APIError as e:
            logger.error(f"Docker API error: {str(e)}")
            return JsonResponse({'error': f"Docker API error: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def extract_relevant_output(output):
    """
    Extracts the relevant lines from the output by trimming the beginning and only keeping the last few lines.
    Adjust the number of lines as needed.
    """
    lines = output.splitlines()
    # Example: Keep only the last 5 lines
    relevant_lines = lines[-5:] if len(lines) > 5 else lines
    return '\n'.join(relevant_lines)

def clean_temp_folder(temp_folder_path):
    if os.path.exists(temp_folder_path):
        def remove_readonly(func, path, _):
            os.chmod(path, stat.S_IWRITE)
            func(path)
        
        shutil.rmtree(temp_folder_path, onerror=remove_readonly)
    os.makedirs(temp_folder_path)

