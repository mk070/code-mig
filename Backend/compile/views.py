import os
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import docker
from compile.additionals.cobol import handle_cobol, handle_multiple_cobol_files, handle_cobol_with_sql
from compile.additionals.dotnet import handle_dotnet, handle_dotnet_with_sql
from compile.additionals.java import handle_java, handle_java_with_sql
from compile.additionals.python import handle_python
from backend import globals

@csrf_exempt
def execute_code(request):

    if request.method == 'POST':
        temp_folder = os.path.join(settings.BASE_DIR, 'TEMP_FOLDER')
        os.makedirs(temp_folder, exist_ok=True)

        files = request.FILES.getlist('files')
        source_language = request.POST.get('sourcelanguage', '').lower()
        main_file_name = request.POST.get('main_file_name', '').strip()
        sql_file = 'db.sql'

        if not files or not main_file_name:
            return JsonResponse({'error': 'No files, source language, or main file name provided.'}, status=400)

        # Save all uploaded files to TEMP_FOLDER
        saved_files = []
        cobol_files = []
        print('session : ',request.session.keys())
        print('db name : ' ,globals.DATABASE_FILE_NAME)
        saved_sql_file = globals.DATABASE_FILE_NAME or ''   # --------------------> this will be updated dinamically
        sql = 0
        for file in files:
            file_path = os.path.join(temp_folder, file.name)
            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            saved_files.append(file.name)
            
            if file.name.lower().endswith('.cbl'):
                cobol_files.append(file.name)

            if file.name.lower().endswith('.sql'):
                sql = 1

        print('saved_sql_file : ',saved_sql_file)

        if main_file_name not in saved_files:
            return JsonResponse({'error': f'Main file "{main_file_name}" not found in uploaded files.'}, status=400)

        # Determine the language based on the file extension
        file_extension = os.path.splitext(main_file_name)[1].lower()

        client = docker.from_env()

        if file_extension == '.cbl':
            if len(cobol_files) > 1:
                if sql == 1:
                    print("cobol-sql triggered")
                    output = handle_cobol_with_sql(client, temp_folder, main_file_name, cobol_files, sql_file)
                else:
                    print("multi-cobol triggered")
                    output = handle_multiple_cobol_files(client, temp_folder, main_file_name, cobol_files)
            else:
                if sql == 1:
                    print("cobol-sql triggered")
                    output = handle_cobol_with_sql(client, temp_folder, main_file_name, cobol_files, sql_file)
                else:    
                    print("cobol triggered")
                    output = handle_cobol(client, temp_folder, main_file_name, cobol_files)
        elif file_extension == '.cs':
            if saved_sql_file:
                 print("dotnet-sql triggered")
                 output = handle_dotnet_with_sql(client, temp_folder, main_file_name, saved_files,sql_file)
            else:
                print("dotnet triggered")
                output = handle_dotnet(client, temp_folder, main_file_name, saved_files)

        elif file_extension == '.java':
            if saved_sql_file:
                print("java-sql triggered")
                output = handle_java_with_sql(client, temp_folder, main_file_name, saved_files,sql_file)
            else:
                print("java triggered")
                output = handle_java(client, temp_folder, main_file_name, saved_files)

        elif file_extension == '.py':
            print("python triggered")
            output = handle_python(client, temp_folder, main_file_name, saved_files)

        else:
            return JsonResponse({'error': f'Unsupported file extension: {file_extension}'}, status=400)

        print('views-output : ',output)
        return JsonResponse({'output': output})

    return JsonResponse({'error': 'Invalid request method'}, status=405)
