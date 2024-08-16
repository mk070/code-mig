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
        target_language = request.POST.get('targetlanguage', '').lower()

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
            # Determine the command based on the selected language
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

            return JsonResponse({'output': output})

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
