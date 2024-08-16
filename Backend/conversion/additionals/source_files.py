import os
from pprint import PrettyPrinter, pprint

def get_source_files_dict(main_file_name, directory):
    # Prepare the dictionary to store code and external files
    file_data = {
        'code': {},
        'external_files': [],
        'external_files_sample_data': {}
    }

    # Ensure the main file is added first if it exists
    if main_file_name:
        main_file_path = os.path.join(directory, main_file_name)
        if os.path.exists(main_file_path):
            with open(main_file_path, 'r') as main_file:
                file_data['code'][main_file_name] = main_file.read()
                print(f"Main file '{main_file_name}' read successfully.")  # Log success

    # Get all other files from the TEMP_FOLDER
    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)

            # Skip the main file since it's already added
            if file_name == main_file_name:
                continue

            # Check if the file is a code file (e.g., .cbl, .sql)
            if file_name.endswith(('.cbl', '.cob', '.sql', '.CBL', '.COB', '.SQL')):
                with open(file_path, 'r') as file:
                    file_data['code'][file_name] = file.read()
                    print(f"Code file '{file_name}' read successfully.")  # Log success

            # Check for external files (e.g., .csv, .dat, .db)
            elif file_name.endswith(('.csv', '.dat', '.db', '.DAT', '.CSV', '.DB')):
                file_data['external_files'].append(file_name)
                print(f"External file '{file_name}' found.")  # Log found file

                # Read the first three rows of the file
                sample_data = read_sample_data(file_path)
                file_data['external_files_sample_data'][file_name] = sample_data
                print(f"Sample data from '{file_name}': {sample_data}")  # Log sample data

    # Use PrettyPrinter to pretty-print the entire file_data structure
    pp = PrettyPrinter(indent=2)
    print("Final file_data structure:")
    pp.pprint(file_data)

    return file_data


def read_sample_data(file_path):
    # Determine the file extension
    ext = os.path.splitext(file_path)[1].lower()

    sample_lines = []
    try:
        # Open the file and read the first three lines (or fewer if the file is smaller)
        with open(file_path, 'r') as file:
            for i in range(3):
                line = file.readline()
                if not line:
                    break
                sample_lines.append(line.strip())

        # Combine the lines into a single string
        return '\n'.join(sample_lines)

    except Exception as e:
        # If there's an error reading the file, return an error message
        print(f"Error reading file '{file_path}': {str(e)}")  # Log error
        return f"Error reading file: {str(e)}"
