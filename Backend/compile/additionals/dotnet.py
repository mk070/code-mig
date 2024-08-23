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
            print(f"Executing command: {command}")

            exec_result = container.exec_run(command)
            output = exec_result.output.decode('utf-8')
            print(f"Command output: {output}")

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

        # Step 2: Move the user's main file to the project directory
        exec_run_logged(f"mv /app/data/{main_file} /app/project/Program.cs")

        # Step 3: Run the project
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

def handle_dotnet_with_sql(client, temp_folder, main_file, saved_files, sql_file=None):
    try:
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={temp_folder: {'bind': '/app/data', 'mode': 'rw'}},
            working_dir="/app",
            detach=True,
            tty=True,
            environment={
                'PGPASSWORD': 'root',
                'LD_LIBRARY_PATH': '/usr/lib/x86_64-linux-gnu/odbc:$LD_LIBRARY_PATH'
            }
        )

        def exec_run_logged(command):
            print(f"Executing command: {command}")
            exec_result = container.exec_run(command)
            output = exec_result.output.decode('utf-8')
            print(f"Command output: {output}")
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
            filtered_lines = [
                line for line in output.splitlines()
                if not line.startswith("/") and not "warning" in line.lower()
            ]
            return "\n".join(filtered_lines)

        def initialize_database():
            exec_run_logged("service postgresql restart")
            exec_run_logged("su - postgres -c \"psql -c \\\"CREATE USER root WITH PASSWORD 'root';\\\"\"")
            exec_run_logged("su - postgres -c \"psql -c \\\"ALTER USER root WITH SUPERUSER;\\\"\"")

            check_db_command = "su - postgres -c \"psql -lqt | cut -d \\| -f 1 | grep -qw cobol_db_example\""
            exec_result = container.exec_run(check_db_command)
            if exec_result.exit_code == 0:
                print("Database cobol_db_example already exists. Skipping creation.")
            else:
                exec_run_logged("su - postgres -c \"psql -c \\\"CREATE DATABASE cobol_db_example WITH OWNER root;\\\"\"")

            if sql_file:
                exec_run_logged(f"ls /app/data/{sql_file}")
                exec_run_logged(f"su - postgres -c \"psql -d cobol_db_example -f /app/data/{sql_file}\"")

        # Initialize the database before running the .NET project
        initialize_database()

        # Step 1: Move the user's main file to the appropriate directory
        exec_run_logged(f"mv /app/data/{main_file} /app/Program.cs")

        # Step 2: Create a new .NET console application
        exec_run_logged(f"dotnet new console -o /app/project")

        # Step 3: Add the necessary SQL client package
        exec_run_logged(f"dotnet add /app/project/project.csproj package System.Data.Odbc")

        # Step 4: Replace the auto-generated Program.cs file with the user's file
        exec_run_logged(f"mv /app/Program.cs /app/project/Program.cs")

        # Step 5: Restore and build the project
        exec_run_logged(f"dotnet build /app/project")

        # Step 6: Run the compiled .NET project
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


def extract_relevant_output(output):
    lines = output.splitlines()
    relevant_lines = []
    capture = False

    for line in lines:
        # Start capturing if the line resembles a table header or has columns
        if capture or ("ID" in line and "First" in line):
            capture = True
            relevant_lines.append(line)
        # Stop capturing at the end of data (when a blank line follows data)
        elif capture and not line.strip():
            break

    # Fallback in case no structured data was captured
    if not relevant_lines:
        relevant_lines = ["No relevant output found."]

    return "\n".join(relevant_lines)