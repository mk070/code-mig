import os
import re
import docker
from docker.errors import ContainerError, APIError

def handle_java(client, temp_folder, main_file, sub_files):
    try:
        container = client.containers.run(
            image="madhanp7/multi-language-compiler-updated",
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
                image="madhanp7/multi-language-compiler-updated",
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
                    image="madhanp7/multi-language-compiler-updated",
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
                image="madhanp7/multi-language-compiler-updated",
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
                image="madhanp7/multi-language-compiler-updated",
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
            image="madhanp7/multi-language-compiler-updated",
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
                    image="madhanp7/multi-language-compiler-updated",
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
        # global default
        # return default

    except APIError as e:
        return f"Docker API error: {str(e)}"

    except Exception as e:
        return f"Unexpected error: {str(e)}"

    finally:
        if container:
            container.stop()
            container.remove()


#  default = '''

# ACCOUNTS:
# ID   | First    | Last     | Phone      | Address                | Enabled 
# ------|----------|----------|------------|------------------------|---------
#     1 | Mike       | Tester1    | 15555550121  | 122 Real St, Nowhere   | Y
#     2 | Mary       | Tester2    | 15555550132  | 121 ABC St, Nowhere    | Y
#     3 | Jack       | Tester3    | 15555550143  | 120 Rock St, Nowhere   | Y
#     4 | Bob        | Tester4    | 15555550154  | 119 Truck St, Nowhere  | N
#     5 | Paula      | Tester5    | 1555550165   | 118 Car St, Nowhere    | N
#     6 | James      | Tester6    | 1555550176   | 117 Land St, Nowhere   | Y
#     7 | Jane       | Tester7    | 1555550187   | 116 Sea St, Nowhere    | Y
#     8 | Bill       | Tester8    | 1555550198   | 115 Dock St, Nowhere   | N
#     9 | Shawn      | Henderson  | 1432878918   | 6795 Smith Burg, North Brittanymouth, OK 57800 | N
#    10 | Danny      | Vang       | 4981378047   | 2028 Palmer Courts Suite 455, New Evelyn, MH 16743 | N
#    11 | Kara       | Chavez     | 7239731473   | 369 Christopher Flats, South Carolmouth, KS 50036 | Y
#    12 | Mathew     | Cohen      | 7600264627   | 887 Patrick Valley Suite 378, Watsonshire, TX 83762 | N
#    13 | Kathy      | Gibbs      | 5796721841   | 67129 Denise Pine, Lake Sabrina, NJ 06114 | Y
#    14 | Robert     | Miller     | 7121258992   | 64703 Kimberly Inlet Suite 069, Wilsontown, TX 20296 | Y
#    15 | Christopher | Newman     | 8511579495   | 3520 Knox Trace Suite 597, New Jaredtown, AZ 29615 | Y
#    16 | Diana      | Bell       | 9667766158   | 648 Steven Road, Nathanielshire, MA 31885 | Y
#    17 | April      | Snyder     | 7739251265   | 0782 Adams Route Suite 997, Rickyland, TX 29955 | Y
#    18 | Cheryl     | Braun      | 4278981813   | 68115 Floyd Mountain, West Lindseychester, ID 41799 | N
#    19 | Vicki      | Hernandez  | 2492901047   | 77927 Maria Pass Suite 325, Phillipsberg, DC 31689 | Y
#    20 | Jodi       | Wright     | 4639057448   | 84031 Arellano Crest Suite 708, North Darrylstad, AL 36381 | N
#    21 | Julie      | Adams      | 3242432793   | 7612 Hunt Field, Houstonville, MT 62183 | Y
#    22 | Lawrence   | Martinez   | 6182957276   | 688 Christopher Overpass Suite 321, Wendyfort, KS 22946 | Y
#    23 | Erika      | Foster     | 6396278436   | 98020 Brown Fork, Port Jacksonberg, DC 36100 | Y
#    24 | Antonio    | Johnson    | 5315287073   | 216 Alvarez Run Suite 361, Pricefurt, ID 05237 | Y

# Disconnected.'''


