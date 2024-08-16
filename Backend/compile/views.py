import logging
import docker
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

logger = logging.getLogger(__name__)

@csrf_exempt
def execute_code(request):
    if request.method == 'POST':
        logger.info("Received request to execute code")
        logger.info(f"Request POST data: {request.POST}")
        logger.info(f"Request FILES: {request.FILES}")

        backend_dir = os.path.dirname(__file__)
        temp_folder = os.path.join(os.path.dirname(backend_dir), 'TEMP_FOLDER')
        os.makedirs(temp_folder, exist_ok=True)

        cobol_file = request.FILES.get('files')
        if not cobol_file:
            return JsonResponse({'error': 'No COBOL file uploaded.'}, status=400)

        cobol_file_path = os.path.join(temp_folder, cobol_file.name)
        with open(cobol_file_path, 'wb+') as destination:
            for chunk in cobol_file.chunks():
                destination.write(chunk)
            destination.write(b'\n')

        client = docker.from_env()

        try:
            container = client.containers.run(
                image="multi-language-compiler-updated",
                command=f"./run.sh cobol data/{cobol_file.name}",
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
            print(f"Container output: {output}")  # Print the output to the console for debugging

            return JsonResponse({'output': container.decode('utf-8')})

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
