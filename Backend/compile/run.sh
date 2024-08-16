#!/bin/bash

# Set the PostgreSQL password for automated login
export PGPASSWORD='root'

# Set the LD_LIBRARY_PATH to include the directory with the ODBC drivers
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/odbc:$LD_LIBRARY_PATH

# Function to start PostgreSQL and initialize the database with a provided SQL script
initialize_database() {
    service postgresql restart  # Restarting PostgreSQL to ensure it's running

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
    echo "Usage: run.sh <language> <file> [sql_file_path]"
    exit 1
fi

LANGUAGE=$1
FILE=$2
SQL_FILE_PATH=$3 # Optional third argument for the SQL file path

# Extract the base name of the file without the extension or directory path
BASENAME=$(basename "$FILE" .cbl)

# Compile and run code based on the specified language
case $LANGUAGE in
    cobol)
        if grep -q "EXEC SQL" "$FILE"; then
            # Compile COBOL with embedded SQL using esqlOC
            esqlOC -static -o "${BASENAME}_compiled.cbl" "$FILE"
            cobc -x -static -locsql "${BASENAME}_compiled.cbl"
            ./"${BASENAME}_compiled"
        else
            # Standard COBOL compilation and execution
            cobc -x -o "$BASENAME" "$FILE"
            ./"$BASENAME"
        fi
        ;;
    dotnet)
        # Create a new .NET console project
        dotnet new console -o /app
        mv "$FILE" /app/Program.cs
        cd /app
        dotnet run
        ;;
    java)
        # Compile and run Java code
        javac $FILE
        java $(basename "$FILE" .java)
        ;;
    python)
        # Run Python code
        python3 $FILE
        ;;
    pyspark)
        # Run PySpark code
        spark-submit $FILE
        ;;
    *)
        echo "Unsupported language: $LANGUAGE"
        exit 1
        ;;
esac
