import docker
from docker.errors import ContainerError, APIError

def handle_python(client, temp_folder, main_file, sub_files):
    try:
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={temp_folder: {'bind': '/app/data', 'mode': 'rw'}},
            working_dir="/app",
            detach=True,
            tty=True
        )

        # Run Python code
        exec_result = container.exec_run(f"python3 /app/data/{main_file}")
        output = exec_result.output.decode('utf-8')

        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=f"python3 /app/data/{main_file}",
                image="multi-language-compiler-updated",
                stderr=output
            )

        return output

    except ContainerError as e:
        return f"Error during Python execution: {str(e)}"

    except APIError as e:
        return f"Docker API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

    finally:
        if container:
            container.stop()
            container.remove()
