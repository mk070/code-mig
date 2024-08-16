#!/bin/bash

# Set the PostgreSQL password for automated login
export PGPASSWORD='root'

# Set the LD_LIBRARY_PATH to include the directory with the ODBC drivers
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/odbc:$LD_LIBRARY_PATH

# Function to start PostgreSQL and initialize the database with a provided SQL script
initialize_database() {
    if ! pg_isready > /dev/null 2>&1; then
        echo "Starting PostgreSQL..."
        service postgresql start
    else
        echo "PostgreSQL is already running."
    fi

    # Create user and database
    su - postgres -c "psql -c \"CREATE USER root WITH PASSWORD 'root';\"" || true
    su - postgres -c "psql -c \"ALTER USER root WITH SUPERUSER;\"" || true
    su - postgres -c "psql -c \"CREATE DATABASE cobol_db_example WITH OWNER root;\"" || true

    # Run the provided SQL script if a path is provided
    if [ -n "$SQL_FILE_PATH" ] && [ -f "$SQL_FILE_PATH" ]; then
        echo "Running user-provided database setup script ($SQL_FILE_PATH)..."
        su - postgres -c "psql -d cobol_db_example -f \"$SQL_FILE_PATH\""
    else
        echo "No valid SQL file provided or the file does not exist. Skipping database initialization."
    fi
}

# Run the database initialization if SQL_FILE_PATH is provided
if [ -n "$SQL_FILE_PATH" ]; then
    initialize_database
fi

# Check the number of arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: run.sh <language> <main_program> [subprogram1.cbl subprogram2.cbl ...] [sql_file_path]"
    exit 1
fi

LANGUAGE=$1
MAIN_PROGRAM=$2
shift 2  # Shift past the first two arguments to get to the subprograms

SUBPROGRAMS=("$@")

# Handle multiple COBOL files
if [ "$LANGUAGE" == "cobol" ]; then
    # Compile subprograms into object files
    MODULES=()
    for FILE in "${SUBPROGRAMS[@]}"; do
        if [[ "$FILE" == *.cbl ]]; then
            BASENAME=$(basename "$FILE" .cbl)
            if grep -q "EXEC SQL" "$FILE"; then
                # Compile COBOL with embedded SQL using esqlOC
                esqlOC -static -o "${BASENAME}_compiled.cbl" "$FILE"
                cobc -c -static -locsql "${BASENAME}_compiled.cbl" -o "${BASENAME}.o"
            else
                # Standard COBOL compilation
                cobc -c "$FILE" -o "${BASENAME}.o"
            fi
            MODULES+=("${BASENAME}.o")
        else
            echo "Warning: File $FILE is not a valid COBOL file, skipping..."
        fi
    done

    # Compile and link the main program with compiled modules
    if [ -f "$MAIN_PROGRAM" ]; then
        cobc -x "$MAIN_PROGRAM" -o main_program "${MODULES[@]}"
        if [ -f "main_program" ]; then
            ./main_program
        else
            echo "Error: Failed to create the executable program."
            exit 1
        fi
    else
        echo "Error: Main program file $MAIN_PROGRAM not found."
        exit 1
    fi
else
    # Other languages handled as before
    case $LANGUAGE in
        dotnet)
            dotnet new console -o /app
            mv "$MAIN_PROGRAM" /app/Program.cs
            cd /app
            dotnet run
            ;;
        java)
            javac "$MAIN_PROGRAM"
            java $(basename "$MAIN_PROGRAM" .java)
            ;;
        python)
            python3 "$MAIN_PROGRAM"
            ;;
        pyspark)
            spark-submit "$MAIN_PROGRAM"
            ;;
        *)
            echo "Unsupported language: $LANGUAGE"
            exit 1
            ;;
    esac
fi
