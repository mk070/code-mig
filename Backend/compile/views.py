from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import docker
from django.http import JsonResponse
import os
import tempfile

@csrf_exempt
def execute_code(request):
    if request.method == 'POST':
        code = request.POST.get('code')
        sourcelanguage = request.POST.get('sourcelanguage')
        targetlanguage = request.POST.get('targetlanguage')
        github_link = request.POST.get('github_link')
        files = request.FILES.getlist('files')

        client = docker.from_env()

        with tempfile.TemporaryDirectory() as tmpdirname:
            # Handle uploaded files
            for file in files:
                with open(os.path.join(tmpdirname, file.name), 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            # Write the source code to a file (if provided)
            if code:
                code_file = os.path.join(tmpdirname, f'main.{sourcelanguage}')  # Dynamic file extension based on source language
                with open(code_file, 'w') as f:
                    f.write(code)

            # Construct the Docker command
            docker_command = f"./run.sh {sourcelanguage} main.{sourcelanguage}"

            try:
                container = client.containers.run(
                    image="multi-language-compiler-updated",
                    command=docker_command,
                    volumes={tmpdirname: {'bind': '/app', 'mode': 'rw'}},
                    working_dir="/app",
                    detach=True,
                    stdout=True,
                    stderr=True
                )
                result = container.wait()
                output = container.logs().decode("utf-8")
                container.remove()

                if result['StatusCode'] != 0:
                    return JsonResponse({'output': output}, status=400)

                return JsonResponse({'output': output})

            except docker.errors.ContainerError as e:
                return JsonResponse({'error': str(e)}, status=500)
            except docker.errors.ImageNotFound as e:
                return JsonResponse({'error': "Docker image not found: " + str(e)}, status=500)
            except docker.errors.APIError as e:
                return JsonResponse({'error': "Docker API error: " + str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
