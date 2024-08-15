import os

def get_source_files_dict(main_file_name, directory):
    # Prepare the dictionary to store code and external files
    file_data = {
        'code': {},
        'external_files': []
    }

    # Ensure the main file is added first if it exists
    if main_file_name:
        main_file_path = os.path.join(directory, main_file_name)
        if os.path.exists(main_file_path):
            with open(main_file_path, 'r') as main_file:
                file_data['code'][main_file_name] = main_file.read()

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

            # Check for external files (e.g., .csv, .dat, .db)
            elif file_name.endswith(('.csv', '.dat', '.db', '.DAT', '.CSV', '.DB')):
                file_data['external_files'].append(file_name)

    return file_data