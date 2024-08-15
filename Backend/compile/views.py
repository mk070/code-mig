import subprocess
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def execute_code(request):
    if request.method == 'POST':
        # Ensure the TEMP_FOLDER exists
        backend_dir = os.path.dirname(__file__)  # Directory containing views.py
        temp_folder = os.path.join(os.path.dirname(backend_dir), 'TEMP_FOLDER')  # One level up, then TEMP_FOLDER
        os.makedirs(temp_folder, exist_ok=True)

        # Handle the uploaded COBOL file
        cobol_file = request.FILES.get('cobol_file')
        if not cobol_file:
            return JsonResponse({'error': 'No COBOL file uploaded.'}, status=400)

        # Save the uploaded file to TEMP_FOLDER
        cobol_file_path = os.path.join(temp_folder, cobol_file.name)
        with open(cobol_file_path, 'wb+') as destination:
            for chunk in cobol_file.chunks():
                destination.write(chunk)

        # Docker command to execute the COBOL code
        docker_command = [
            'docker', 'run', '--rm',
            '-v', f'{temp_folder}:/app/data',  # Mount TEMP_FOLDER to /app/data in the container
            '-v', f'{os.path.join(os.path.dirname(backend_dir), "run.sh")}:/app/run.sh',  # Mount run.sh to /app in the container
            '-w', '/app',
            'multi-language-compiler-updated',
            './run.sh', 'cobol', f'data/{cobol_file.name}'  # Run the COBOL file inside the container
        ]

        try:
            # Run the Docker command using subprocess
            result = subprocess.run(docker_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                return JsonResponse({'output': result.stdout})
            else:
                # Return detailed error for debugging
                return JsonResponse({'error': f"Command failed with return code {result.returncode}. Stderr: {result.stderr}. Stdout: {result.stdout}"}, status=500)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=405)
