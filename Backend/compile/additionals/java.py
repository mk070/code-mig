import os
import re
import docker
from docker.errors import ContainerError, APIError

def handle_java(client, temp_folder, main_file, sub_files):
    try:
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={temp_folder: {'bind': '/app/data', 'mode': 'rw'}},
            working_dir="/app",
            detach=True,
            tty=True
        )

        # Step 1: Read the main Java file to find the public class name
        exec_result = container.exec_run(f"cat /app/data/{main_file}")
        if exec_result.exit_code != 0:
            output = exec_result.output.decode('utf-8')
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=f"cat /app/data/{main_file}",
                image="multi-language-compiler-updated",
                stderr=output
            )

        java_code = exec_result.output.decode('utf-8')
        match = re.search(r'public\s+class\s+(\w+)', java_code)
        if match:
            class_name = match.group(1)
        else:
            raise ValueError("No public class found in the Java file")

        # Step 2: Rename the file if the filename does not match the class name
        if not main_file.startswith(class_name):
            new_file_name = f"{class_name}.java"
            exec_result = container.exec_run(f"mv /app/data/{main_file} /app/data/{new_file_name}")
            if exec_result.exit_code != 0:
                output = exec_result.output.decode('utf-8')
                raise ContainerError(
                    container=container,
                    exit_status=exec_result.exit_code,
                    command=f"mv /app/data/{main_file} /app/data/{new_file_name}",
                    image="multi-language-compiler-updated",
                    stderr=output
                )
            main_file = new_file_name

        # Step 3: Compile the Java file
        exec_result = container.exec_run(f"javac /app/data/{main_file}")
        if exec_result.exit_code != 0:
            output = exec_result.output.decode('utf-8')
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=f"javac /app/data/{main_file}",
                image="multi-language-compiler-updated",
                stderr=output
            )

        # Step 4: Run the compiled Java class
        exec_result = container.exec_run(f"java -cp /app/data {class_name}")
        output = exec_result.output.decode('utf-8')

        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=f"java -cp /app/data {class_name}",
                image="multi-language-compiler-updated",
                stderr=output
            )

        return output

    except ContainerError as e:
        return f"Error during Java execution: {str(e)}"

    except APIError as e:
        return f"Docker API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

    finally:
        if container:
            container.stop()
            container.remove()

def handle_java_with_sql(client, temp_folder, main_file, saved_files, sql_file=None):
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

        # Initialize the database before running the Java project
        initialize_database()

        # Step 1: Download the PostgreSQL JDBC driver (if not already done)
        exec_run_logged("curl -L -o /app/postgresql-42.2.18.jar https://jdbc.postgresql.org/download/postgresql-42.2.18.jar")

        # Step 2: Ensure the main file has a .java extension
        if not main_file.endswith('.java'):
            raise ValueError("Main file must have a .java extension")

        # Step 3: Extract the class name from the file content
        class_name = None
        with open(f"{temp_folder}/{main_file}", 'r') as file:
            for line in file:
                if "public class" in line:
                    class_name = line.split("public class")[1].split("{")[0].strip()
                    break

        if not class_name:
            raise ValueError("No public class found in the file")

        # Step 4: Rename the file to match the class name
        new_main_file = f"{class_name}.java"
        exec_run_logged(f"mv /app/data/{main_file} /app/data/{new_main_file}")

        # Step 5: Compile the Java file
        exec_run_logged(f"javac /app/data/{new_main_file}")

        # Step 6: Run the compiled Java class with the PostgreSQL JDBC driver in the classpath
        output = exec_run_logged(f"java -cp /app/data:/app/postgresql-42.2.18.jar {class_name}")

        return output

    except ContainerError as e:
        return f"Error during Java execution: {str(e)}"

    except APIError as e:
        return f"Docker API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

    finally:
        if container:
            container.stop()
            container.remove()
