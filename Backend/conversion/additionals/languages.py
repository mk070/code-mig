def get_file_extension(language):
    languages = {
        'COBOL': 'cbl',
        'Python': 'py',
        '.NET': 'cs',
        'Java': 'java',
        'C': 'c',
        'C++': 'cpp',
        'Pyspark': 'py',
        'Javascript': 'js'
    }
    return languages[language]