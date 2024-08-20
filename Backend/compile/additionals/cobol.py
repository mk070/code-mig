import docker
from docker.errors import ContainerError, APIError

def handle_cobol(client, temp_folder, main_file, sub_files):
    container = None
    try:
        # Start the container and run the COBOL compilation directly
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={
                temp_folder: {'bind': '/app/data', 'mode': 'rw'}
            },
            working_dir="/app",
            detach=True,
            tty=True  # Allocate a pseudo-TTY
        )
        
        # Compile the COBOL code directly
        compile_command = ["cobc", "-x", f"data/{main_file}", "-o", "data/main_program"]
        exec_result = container.exec_run(compile_command)
        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=" ".join(compile_command),
                image="multi-language-compiler-updated",
                stderr=exec_result.stderr.decode('utf-8')
            )
        
        # Run the compiled COBOL program
        run_command = ["./data/main_program"]
        exec_result = container.exec_run(run_command)
        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=" ".join(run_command),
                image="multi-language-compiler-updated",
                stderr=exec_result.stderr.decode('utf-8')
            )
        
        # Capture the output from the COBOL program
        output = exec_result.output.decode('utf-8')
        
        return output
    
    except ContainerError as e:
        return f"Error during COBOL execution: {str(e)}"
    
    except APIError as e:
        return f"Docker API error: {str(e)}"
    
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    
    finally:
        if container:
            try:
                container.stop()  # Ensure the container is stopped
                container.remove()  # Then remove the container
            except Exception as e:
                return f"Error during container cleanup: {str(e)}"

def handle_multiple_cobol_files(client, temp_folder, main_file, sub_files):
    container = None
    try:
        # Start the container
        container = client.containers.run(
            image="multi-language-compiler-updated",
            volumes={
                temp_folder: {'bind': '/app/data', 'mode': 'rw'}
            },
            working_dir="/app",
            detach=True,
            tty=True
        )
        
        # Compile subprograms into object files
        object_files = []
        for cobol_file in sub_files:
            if cobol_file != main_file:  # Skip the main file for now
                obj_file = f"data/{cobol_file.replace('.cbl', '.o')}"
                compile_command = ["cobc", "-c", f"data/{cobol_file}", "-o", obj_file]
                exec_result = container.exec_run(compile_command)
                if exec_result.exit_code != 0:
                    raise ContainerError(
                        container=container,
                        exit_status=exec_result.exit_code,
                        command=" ".join(compile_command),
                        image="multi-language-compiler-updated",
                        stderr=exec_result.stderr.decode('utf-8')
                    )
                object_files.append(obj_file)
        
        # Link the main program with the compiled object files
        link_command = ["cobc", "-x", f"data/{main_file}", "-o", "data/main_program"] + object_files
        exec_result = container.exec_run(link_command)
        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=" ".join(link_command),
                image="multi-language-compiler-updated",
                stderr=exec_result.stderr.decode('utf-8')
            )
        
        # Run the linked COBOL program
        run_command = ["./data/main_program"]
        exec_result = container.exec_run(run_command)
        if exec_result.exit_code != 0:
            raise ContainerError(
                container=container,
                exit_status=exec_result.exit_code,
                command=" ".join(run_command),
                image="multi-language-compiler-updated",
                stderr=exec_result.stderr.decode('utf-8')
            )
        
        # Capture the output from the COBOL program
        output = exec_result.output.decode('utf-8')
        
        return output
    
    except ContainerError as e:
        return f"Error during COBOL execution: {str(e)}"
    
    except APIError as e:
        return f"Docker API error: {str(e)}"
    
    except Exception as e:
        return f"Unexpected error: {str(e)}"
    
    finally:
        if container:
            try:
                container.stop()  # Ensure the container is stopped
                container.remove()  # Then remove the container
            except Exception as e:
                return f"Error during container cleanup: {str(e)}"
