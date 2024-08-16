import logging
import docker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

logger = logging.getLogger(__name__)

@csrf_exempt
def execute_code(request):
    if request.method == 'POST':
        backend_dir = os.path.dirname(__file__)
        temp_folder = os.path.join(os.path.dirname(backend_dir), 'TEMP_FOLDER')
        os.makedirs(temp_folder, exist_ok=True)

        files = request.FILES.getlist('files')
        source_language = request.POST.get('sourcelanguage', '').lower()
        main_file_name = request.POST.get('main_file_name', '').strip()

        if not files or not source_language or not main_file_name:
            return JsonResponse({'error': 'No files, source language, or main file name provided.'}, status=400)

        # Save all uploaded files
        saved_files = []
        for file in files:
            file_path = os.path.join(temp_folder, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            saved_files.append(file_path)
            
        print("saved_files : ",saved_files)

        # Verify that the main file exists
        main_file_path = os.path.join(temp_folder, main_file_name)
        if main_file_path not in saved_files:
            return JsonResponse({'error': f'Main file "{main_file_name}" not found in uploaded files.'}, status=400)

        request.session['main_file_name'] = main_file_name

        client = docker.from_env()

        try:
            # Form the command based on the file extension or source language
            if source_language == 'cobol':
                command = f"./run.sh cobol data/{main_file_name}"
                for file_path in saved_files:
                    if file_path != main_file_path:
                        command += f" {os.path.basename(file_path)}"
            elif source_language == 'python':
                command = f"./run.sh python data/{main_file_name}"
            elif source_language == 'java':
                command = f"./run.sh java data/{main_file_name}"
            elif source_language == 'dotnet':
                command = f"./run.sh dotnet data/{main_file_name}"
            else:
                command = f"./run.sh {source_language} data/{main_file_name}"

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
