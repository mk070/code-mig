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

        cobol_file = request.FILES.get('files')
        source_language = request.POST.get('sourcelanguage', '').lower()

        if not cobol_file or not source_language:
            return JsonResponse({'error': 'No file or source language provided.'}, status=400)

        cobol_file_path = os.path.join(temp_folder, cobol_file.name)
        print('cobol_file_path:', cobol_file_path)
        with open(cobol_file_path, 'wb+') as destination:
            for chunk in cobol_file.chunks():
                destination.write(chunk)
            destination.write(b'\n')

        print('cobol_file.name:', cobol_file.name)
        request.session['main_file_name'] = cobol_file.name

        client = docker.from_env()

        try:
            # Correctly form the command based on the file extension or source language
            if cobol_file.name.endswith('.cbl'):
                command = f"./run.sh cobol data/{cobol_file.name}"
            elif cobol_file.name.endswith('.py'):
                command = f"./run.sh python data/{cobol_file.name}"
            elif cobol_file.name.endswith('.java'):
                command = f"./run.sh java data/{cobol_file.name}"
            elif cobol_file.name.endswith('.cs'):
                command = f"./run.sh dotnet data/{cobol_file.name}"
            else:
                command = f"./run.sh {source_language} data/{cobol_file.name}"

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
    relevant_lines = lines[1:] if len(lines) > 1 else lines
    return '\n'.join(relevant_lines)

