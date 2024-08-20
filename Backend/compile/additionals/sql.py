import os
import docker
from docker.errors import ContainerError, APIError

def handle_cobol_with_sql(client, temp_folder, main_file, sub_files, sql_file=None):
    container = None
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
            if exec_result.exit_code != 0:
                raise ContainerError(
                    container=container,
                    exit_status=exec_result.exit_code,
                    command=command,
                    image="multi-language-compiler-updated",
                    stderr=output
                )
            return output

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

        if sql_file:
            initialize_database()

        def compile_and_run_cobol():
            basename = os.path.splitext(os.path.basename(main_file))[0]
            temp_output_file = f"/app/data/{basename}_temp"
            output = ""  # Initialize the output variable

            if container.exec_run(f"grep -q 'EXEC SQL' /app/data/{main_file}").exit_code == 0:
                exec_run_logged(f"esqlOC -static -o /app/data/{basename}_compiled.cbl /app/data/{main_file}")
                exec_run_logged(f"cobc -x -static -locsql /app/data/{basename}_compiled.cbl -o {temp_output_file}")
                exec_run_logged(f"mv {temp_output_file} /app/data/{basename}_compiled")

                # Ensure the compiled file exists before execution
                exec_result = container.exec_run(f"ls /app/data/{basename}_compiled")
                if exec_result.exit_code != 0:
                    raise ContainerError(
                        container=container,
                        exit_status=exec_result.exit_code,
                        command=f"ls /app/data/{basename}_compiled",
                        image="multi-language-compiler-updated",
                        stderr="Compiled COBOL file not found"
                    )

                output = exec_run_logged(f"/app/data/{basename}_compiled")
            else:
                exec_run_logged(f"cobc -x -o {temp_output_file} /app/data/{main_file}")
                exec_run_logged(f"mv {temp_output_file} /app/data/{basename}")

                exec_result = container.exec_run(f"ls /app/data/{basename}")
                if exec_result.exit_code != 0:
                    raise ContainerError(
                        container=container,
                        exit_status=exec_result.exit_code,
                        command=f"ls /app/data/{basename}",
                        image="multi-language-compiler-updated",
                        stderr="Compiled COBOL file not found"
                    )

                output = exec_run_logged(f"/app/data/{basename}")

            print("output : ",output)
            # Extract only the relevant output (using the flexible extraction logic)
            relevant_output = extract_relevant_output(output)
            return relevant_output

        if main_file.endswith('.cbl'):
            output = compile_and_run_cobol()
        else:
            raise ValueError("Unsupported file type")

        return output

    except ContainerError as e:
        print(f"Error during COBOL execution: {str(e)}")
        return f"Error during COBOL execution: {str(e)}"

    except APIError as e:
        print(f"Docker API error: {str(e)}")
        return f"Docker API error: {str(e)}"

    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"Unexpected error: {str(e)}"
    
    finally:
        if container:
            try:
                container.stop()
                container.remove()
            except Exception as e:
                print(f"Error during container cleanup: {str(e)}")
                return f"Error during container cleanup: {str(e)}"

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
