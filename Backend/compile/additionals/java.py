import os
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

        # Ensure the file has a .java extension and compile it
        if not main_file.endswith('.java'):
            raise ValueError("Main file must have a .java extension")

        # Step 1: Compile the Java file
        exec_result = container.exec_run(f"javac /app/data/{main_file} > /dev/null 2>&1")
        if exec_result.exit_code != 0:
            output = exec_result.output.decode('utf-8')
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=f"javac /app/data/{main_file}",
                image="multi-language-compiler-updated",
                stderr=output
            )

        # Step 2: Determine the class name (assuming the class name matches the file name)
        class_name = os.path.splitext(main_file)[0]

        # Step 3: Run the compiled Java class
        exec_result = container.exec_run(f"java -cp /app/data {class_name} 2>/dev/null")
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
