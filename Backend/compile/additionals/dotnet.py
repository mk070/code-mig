import os
import docker
from docker.errors import ContainerError, APIError

def handle_dotnet(client, temp_folder, main_file, sub_files):
    try:
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={temp_folder: {'bind': '/app/data', 'mode': 'rw'}},
            working_dir="/app",
            detach=True,
            tty=True
        )

        def exec_run_logged(command):
            exec_result = container.exec_run(command)
            output = exec_result.output.decode('utf-8')
            filtered_output = filter_warnings_and_errors(output)
            if exec_result.exit_code != 0:
                raise ContainerError(
                    container=container,
                    exit_status=exec_result.exit_code,
                    command=command,
                    image="multi-language-compiler-updated",
                    stderr=filtered_output
                )
            return filtered_output

        def filter_warnings_and_errors(output):
            # Filter out lines that contain warnings or build info
            filtered_lines = [
                line for line in output.splitlines()
                if not line.startswith("/") and not "warning" in line.lower()
            ]
            return "\n".join(filtered_lines)

        # Step 1: Create a new .NET project
        exec_run_logged(f"dotnet new console -o /app/project")

        # Step 2: Add reference to System.Data.Odbc
        exec_run_logged(f"dotnet add /app/project/project.csproj package System.Data.Odbc")

        # Step 3: Move the user's main file to the project directory
        exec_run_logged(f"mv /app/data/{main_file} /app/project/Program.cs")

        # Step 4: Run the project
        output = exec_run_logged(f"dotnet run --project /app/project")

        return output

    except ContainerError as e:
        return f"Error during .NET execution: {str(e)}"

    except APIError as e:
        return f"Docker API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

    finally:
        if container:
            container.stop()
            container.remove()
