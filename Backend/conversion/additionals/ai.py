import os
import re
import google.generativeai as genai
from .remove_markers import remove_code_markers

# Load environment variables
def get_supported_languages():
    return ["Python", "Java", "Pyspark", "C++", "COBOL",".NET"]

def clean_response(code):
    # Remove Python comments (lines starting with #) while preserving indentation
    code_without_comments = re.sub(r'^\s*#.*$', '', code, flags=re.MULTILINE)
    
    # Remove empty lines and strip leading/trailing whitespace while preserving indentation
    cleaned_code = "\n".join([line for line in code_without_comments.splitlines() if line.strip()])
    
    return cleaned_code

# Load the API key from .env file
GEMINI_API_KEY = "AIzaSyDNmwDtBeRtS_0KQR0DTMCLMfW-bK6IGTU"
genai.configure(api_key=GEMINI_API_KEY)

def translate_code(code,source_language, target_language):

    print('source_language : ',source_language)
    print('target_language : ',target_language)
    # Construct the prompt for code conversion
    if source_language == 'cobol' and target_language == '.net':
      print('cobol-.NET prompt')
      refined_prompt = (
f'''You are an advanced AI specializing in code conversion. Your task is to convert multiple {source_language} source files to the {target_language} language while preserving their functionality and structure. The source files are provided in a dictionary format where the 'code' key contains the {source_language} source files, and each key represents a filename with its corresponding code.

**Instructions:**
1. **Convert All Source Files**: Convert all the {source_language} source files provided in the 'code' dictionary to {target_language}. Ensure each file's functionality and structure are accurately translated to the target language.

2. **File Merging**: Merge the converted code into a single output file. This file should contain all the converted code without any additional markers or unnecessary comments.

3. **Preserve Functionality**: Ensure that all functionalities from the input source files are preserved in the converted target file. The logic, flow, and intended outcomes must remain consistent with the original COBOL code.

4. **Syntax and Structure**: Maintain correct syntax, indentation, and code structure in the converted code. Pay special attention to the placement of semicolons, braces, and the proper declaration of methods and variables to avoid syntax errors (e.g., `CS1002`).

5. **External File Handling**: Handle .DAT files and other external files correctly based on their format. If a file is binary or has specific encoding, ensure the converted code reads and processes it using appropriate methods. Ensure that file handling in C# mirrors COBOL's behavior.

6. **Variable Initialization**: Initialize all variables, properties, and fields appropriately to avoid any nullability warnings (such as `CS8618` or `CS8600` in C#) or runtime errors. Ensure that:
   - All non-nullable fields and properties are initialized either through constructors or default values.
   - If a property cannot be initialized in the constructor, consider making it nullable by adding `?` to its type.
   - Add null checks before dereferencing any object that could potentially be null, using constructs like `if (obj != null)` or the null-conditional operator `?.`.

7. **Avoid Unnecessary User Input**: Do not include any functionality in the converted code that requires user input to terminate the execution unless explicitly present in the source code. Specifically, avoid adding methods like `Console.ReadKey()` unless they are part of the original COBOL logic.

8. **Handling External References**: If any external references (e.g., datasets, database files) are present in the source code, ensure equivalent handling in the target code. The external files are listed in the 'external_files' key, and a sample of the first three rows is provided in the 'external_files_sample_data' key to inform you of the data structure. However, the code should interact with the complete dataset from 'external_files'.

9. **Database Connectivity**: If the COBOL code connects to a PostgreSQL database, ensure that this connectivity is faithfully reflected in the C# code. Use the following guidelines:
   - **Connection String**: Implement the connection string in the following format:
     ```csharp
     string connectionString = "DSN=PostgreSQL-DSN;UID=postgres;PWD=password;";
     ```
   - **ODBC Driver Configuration**: Ensure the code references the PostgreSQL Unicode ODBC driver as configured in `odbc.ini` and `odbcinst.ini` to avoid errors like "Can't open lib."

10. **SQL Operations**: 
   - **Static Main Method**: Ensure that the `Main` method is declared static in the converted C# code:
     ```csharp
     public static void Main(string[] args) {{ ... }}
     ```
   - **Odbc Data Types**: Use the correct Odbc data types for database operations, including `OdbcConnection`, `OdbcCommand`, and `OdbcDataReader`.
   - **Error Handling**: Implement comprehensive error handling to capture and display SQL-related errors, including SQLSTATE and detailed error messages. Example:
     ```csharp
     catch (OdbcException ex)
     {{
         Console.WriteLine("SQL Error:");
         Console.WriteLine($"SQLSTATE: {{ex.Errors[0].SQLState}}");
         Console.WriteLine($"Error Message:{{ex.Message}}");
         Environment.Exit(1);
     }}
     ```
   - **Cursor Operations**: Replace COBOL-specific cursor operations with equivalent SQL operations using `OdbcCommand` and `OdbcDataReader`. The code should fetch records directly via SQL queries without relying on cursor-based syntax.
   - **SQL Query Syntax**: **Crucially** ensure that any identifiers (like table names, column names, or variable names) that contain hyphens (`-`) are modified to use underscores (`_`) instead, as hyphens are not valid in PostgreSQL identifiers. This change should be made globally across all SQL-related code.
   - **ConnectionState Reference**: Ensure that all references to `ConnectionState` are fully qualified using `System.Data.ConnectionState`. Example:
     ```csharp
     if (connection != null && connection.State == System.Data.ConnectionState.Open)
     {{
         connection.Close();
         Console.WriteLine("Disconnected.");
     }}
     ```

11. **Testing and Debugging**: 
    - **Compilation**: Ensure that the final C# code compiles without errors, such as missing semicolons (`CS1002`), incorrect braces, or improperly declared methods.
    - **Runtime Validation**: Test the final converted code to ensure it runs without errors, particularly for database operations and file handling.

12. **Final Output**: Return only the final, error-free converted C# code as the output, with no additional explanations or metadata. The code should be optimized for performance, reliable, and robust, ready for deployment.

**COBOL Source Data for Conversion**:
`{code}`'''
)

    elif source_language == 'cobol' and target_language == 'java':
        print('cobol-java prompt')
        refined_prompt = (
        f'''You are an advanced AI specializing in code conversion. Your task is to convert multiple {source_language} source files to the {target_language} language while preserving their functionality and structure. The source files are provided in a dictionary format where the 'code' key contains the {source_language} source files, and each key represents a filename with its corresponding code.

**Instructions:**
1. **Convert All Source Files**: Convert all the {source_language} source files provided in the 'code' dictionary to {target_language}. Ensure each file's functionality and structure are accurately translated to the target language.

2. **File Merging**: Merge the converted code into a single output file. This file should contain all the converted code without any additional markers or unnecessary comments.

3. **Preserve Functionality**: Ensure that all functionalities from the input source files are preserved in the converted target file. The logic, flow, and intended outcomes must remain consistent with the original COBOL code.

4. **Syntax and Structure**: Maintain correct syntax, indentation, and code structure in the converted code. Pay special attention to the placement of semicolons, braces, and the proper declaration of methods and variables to avoid syntax errors.

5. **External File Handling**: Handle .DAT files and other external files correctly based on their format. If a file is binary or has specific encoding, ensure the converted code reads and processes it using appropriate methods.

6. **Variable Initialization**: Initialize all variables, properties, and fields appropriately to avoid any nullability issues or runtime errors. Ensure that:
   - All non-nullable fields and properties are initialized either through constructors or default values.
   - If a property cannot be initialized in the constructor, consider making it nullable by adding `?` to its type.
   - Add null checks before dereferencing any object that could potentially be null, using constructs like `if (obj != null)` or the null-conditional operator `?.`.

7. **Avoid Unnecessary User Input**: Do not include any functionality in the converted code that requires user input to terminate the execution unless explicitly present in the source code.

8. **Handling External References**: If any external references (e.g., datasets, database files) are present in the source code, ensure equivalent handling in the target code. The external files are listed in the 'external_files' key, and a sample of the first three rows is provided in the 'external_files_sample_data' key to inform you of the data structure. However, the code should interact with the complete dataset from 'external_files'.

9. **Database Connectivity**: If the COBOL code connects to a PostgreSQL database, ensure that this connectivity is faithfully reflected in the Java code. Use the following guidelines:
   - **JDBC Driver Handling**: Include proper handling to load the PostgreSQL JDBC driver. Ensure that the JDBC driver jar file is included in the classpath when running the Java application. Example command:
     ```bash
     java -cp /path/to/postgresql-42.2.5.jar:/app/data SqlExample
     ```
   - **JDBC Driver Loading**: In modern JDBC (Java 6 and later), the driver is typically loaded automatically when the JDBC URL is processed, so manual loading with `Class.forName("org.postgresql.Driver")` may not be necessary. However, if required, include it with appropriate error handling:
     ```java
     try {{
         Class.forName("org.postgresql.Driver");
     }} catch (ClassNotFoundException e) {{
         System.out.println("PostgreSQL JDBC Driver not found.");
         e.printStackTrace();
         System.exit(1);
     }}
     ```
   - **Connection String**: Implement the connection string in the following format for JDBC:
     ```java
     String dbConnectionString = "jdbc:postgresql://localhost:5432/cobol_db_example?user=postgres&password=password";
     ```

10. **SQL Operations**: 
    - **Static Main Method**: Ensure that the `Main` method in the Java class is static:
      ```java
      public static void main(String[] args) {{...}}
      ```
    - **Avoid Hyphens in Identifiers**: In SQL queries, avoid using hyphens (`-`) in any identifiers (e.g., cursor names, table names, column names). Replace hyphens with underscores (`_`).
    - **ResultSet Declaration**: Ensure that the `ResultSet` object (`rs`) is correctly declared and initialized before use:
      ```java
      ResultSet rs = stmt.executeQuery("FETCH ALL FROM ACCOUNT_ALL_CUR");
      ```
    - **Error Handling**: Include comprehensive error handling for SQLExceptions, displaying SQLSTATE and error messages:
      ```java
      catch (SQLException e) {{
          System.out.println("SQL Error:");
          System.out.println("SQLSTATE: " + e.getSQLState());
          System.out.println("Error Message: " + e.getMessage());
          System.exit(1);
      }}
      ```
    - **Cursor Operations**: Ensure correct setup, execution, and fetching of cursors within the JDBC context, using Java methods for SQL commands like `DECLARE`, `OPEN`, `FETCH`, and `CLOSE`.
    - **Resource Management**: Ensure that database connections, statements, and result sets are properly closed in the `finally` block to prevent resource leaks. Example:
      ```java
      try {{
          ResultSet rs = stmt.executeQuery("FETCH ALL FROM ACCOUNT_ALL_CUR");
          while (rs.next()) {{
              int id = rs.getInt("ID");
              String firstName = rs.getString("FIRST_NAME");
              String lastName = rs.getString("LAST_NAME");
              String phone = rs.getString("PHONE");
              String address = rs.getString("ADDRESS");
              boolean isEnabled = rs.getBoolean("IS_ENABLED");
              Timestamp createDt = rs.getTimestamp("CREATE_DT");
              Timestamp modDt = rs.getTimestamp("MOD_DT");
              // Process the retrieved data
          }}
      }} finally {{
          if (rs != null) rs.close();
          if (stmt != null) stmt.close();
          if (connection != null) connection.close();
      }}
      ```

11. **Testing and Debugging**: 
    - **Compilation**: Ensure that the final Java code compiles without errors.
    - **Runtime Validation**: Test the final converted code to ensure it runs without errors, particularly for database operations and file handling.

12. **Final Output**: Return only the final, error-free converted Java code as the output, with no additional explanations or metadata. The code should be optimized for performance, reliable, and robust, ready for deployment.


**COBOL Source Data for Conversion**:
`{code}`''')

    else:
      refined_prompt = (
        f'''You are an advanced AI specializing in code conversion. Your task is to convert multiple {source_language} source files to the {target_language} language while preserving their functionality and structure. The source files are provided in a dictionary format where the 'code' key contains the {source_language} source files, and each key represents a filename with its corresponding code.
**Instructions:**
1. Convert all the {source_language} source files provided in the 'code' dictionary to {target_language}.
2. Merge the converted code into a single output file without any code markers.
3. Ensure that all functionalities from the input source files are available and preserved in the converted target file.
4. Maintain correct syntax, indentation, and code structure in the converted code.
5. Handle .DAT files and other external files correctly based on their format. If the file is binary or has a specific encoding, ensure the converted code reads and processes the file using the correct methods.
6. Initialize all variables, properties, and fields appropriately to avoid any nullability warnings (such as CS8618 or CS8600 in C#) or runtime errors. If a property or field is non-nullable, ensure it is initialized with a default value or through a constructor.
7. Do not include any functionality in the converted code that requires user input to terminate the execution unless that functionality is explicitly present in the source code.
8. If any external references (datasets, database files) are present in the source code, ensure equivalent handling in the target code. The external files are provided in the 'external_files' key, which lists all related datasets and files.
9. The 'external_files_sample_data' key contains a sample of the first three rows from each dataset, if available. This sample is provided to inform you of the dataset's structure, helping you avoid incorrect assumptions about the data format. Use this sample data to understand the structure but ensure that the actual code interacts with the complete dataset from the 'external_files' key. The model should not create data or simulate datasets on its own unless such functionality is explicitly present in the source language code.
10. If certain legacy COBOL functionalities cannot be directly converted due to limitations or differences in the target language, adapt the code appropriately while maintaining the original intent and functionality. Provide a working solution rather than changing the entire functionality unnecessarily.
11. Return only the final converted code as the output, with no additional explanations or metadata.
12. Strictly don't add Console.Readkey() or any other input termination methods in the converted code unless explicitly mentioned in the source code.
13. Comment the Console.Readkey() command in .NET code if it is present in the converted code.
14. Ensure that the converted code is optimized for performance and edge cases, ensuring robustness and reliability. It should be runnable, free from bugs, and avoid trade-offs that compromise the code's integrity.
15. If the {source_language} code has the database connectivity with postgresql, it should be strictly reflected on the {target_language} code.   
16. If You are converting a COBOL program that connects to a PostgreSQL database into .NET C#. The COBOL program uses SQL statements for database operations. Please ensure that the converted .NET C# code follows these guidelines:

1. **Connection String**:
    - Use the following connection string format, ensuring it correctly references a DSN (Data Source Name) configured in `odbc.ini`:
      ```csharp
      string connectionString = "DSN=PostgreSQL-DSN;UID=postgres;PWD=password;";
      ```

2. **ODBC Driver Configuration**:
    - Ensure the code references and uses the `PostgreSQL Unicode` ODBC driver, as configured in the `odbc.ini` and `odbcinst.ini` files, to avoid errors like "Can't open lib". The `DSN=PostgreSQL-DSN` should map to the correct database configuration.

3. **Static Main Method**:
    - Ensure that the `Main` method is correctly declared as a static method:
      ```csharp
      public static void Main(string[] args) {{ ... }}
      ```

4. **Odbc Data Types**:
    - Use the correct `Odbc` data types and references for database operations:
      - Use `OdbcConnection` for database connections.
      - Use `OdbcCommand` for executing SQL queries.
      - Use `OdbcDataReader` for reading data from the database.

5. **Error Handling**:
    - Implement comprehensive error handling to catch and display SQL-related errors, including SQLSTATE and additional details, in the following format:
      ```csharp
      catch (OdbcException ex)
      {{
          Console.WriteLine("SQL Error:");
          Console.WriteLine($"SQLSTATE: {{ex.Errors[0].SQLState}}");
          Console.WriteLine($"Error Message:{{ex.Message}}");
          Environment.Exit(1);
      }}
      ```

6. **Cursor Operations**:
    - Avoid using COBOL-specific cursor operations like `DECLARE`, `OPEN`, `FETCH`, and `CLOSE` directly in C#. Instead, replace them with equivalent SQL operations using `OdbcCommand` and `OdbcDataReader` in a standard SELECT loop. The C# code should fetch records directly via SQL queries without using cursor-based syntax.

7. **SQL Query Syntax**:
    - Ensure that the SQL query syntax is standard and supported by PostgreSQL. Avoid using non-standard or COBOL-specific SQL syntax that may cause syntax errors, like the `-` character that may cause issues.

8. **Compiling and Running**:
    - Ensure that the code compiles and runs successfully, avoiding errors such as "Program does not contain a static 'Main' method suitable for an entry point."

9. **Correct Reference to SQL Variables**:
    - Make sure that SQL-related variables like `wsNumAccounts`, `wsAccountRecord`, etc., are correctly declared and referenced in the code.

10. **Correct Use of `ConnectionState`**:
    - When checking the state of the database connection, reference the `ConnectionState` enum from the `System.Data` namespace:
      ```csharp
      if (connection != null && connection.State == System.Data.ConnectionState.Open)
      {{
          connection.Close();
          Console.WriteLine("Disconnected.");
      }}
      ```

11. **Testing the Database Connection**:
    - Ensure that the code connects to the database using the specified DSN and performs operations without encountering issues related to the ODBC driver or DSN configuration.

12. **Handling SQL Transactions:**
   - Ensure that any `DECLARE CURSOR` statements are wrapped inside a transaction block to avoid errors like "DECLARE CURSOR can only be used in transaction blocks".
   - For example, wrap the cursor declaration in the following manner:
     ```sql
     BEGIN;
     DECLARE cursor_name CURSOR FOR SELECT ...;
     -- Perform fetch operations
     COMMIT;
     ```
13. **Final Validation**:
    - Ensure that the final converted .NET C# code successfully compiles, connects to the PostgreSQL database, and executes SQL queries without errors. Address any syntax or runtime errors in the code and ensure the database operations return the correct results.

Please correct any issues and provide the updated .NET C# code.


17. When converting COBOL programs that use SQL statements into Java, please adhere to the following guidelines:

1. **Connection String**: Ensure the connection string is correctly formatted for Java's JDBC, using the `jdbc:postgresql://` prefix for PostgreSQL connections. Example:
    ```java
    String dbConnectionString = "jdbc:postgresql://localhost:5432/cobol_db_example?user=postgres&password=password";
    ```

2. **JDBC Driver**: Ensure that the Java code loads the PostgreSQL JDBC driver properly:
    ```java
    Class.forName("org.postgresql.Driver");
    ```

3. **Avoid Hyphens in Identifiers**: In SQL queries, avoid using hyphens (`-`) in any identifiers (e.g., cursor names, table names, column names). Replace hyphens with underscores (`_`). For example:
    ```sql
    DECLARE ACCOUNT_ALL_CUR CURSOR FOR SELECT ID, FIRST_NAME, LAST_NAME, PHONE, ADDRESS, IS_ENABLED, CREATE_DT, MOD_DT FROM ACCOUNTS ORDER BY ID;
    ```

4. **Static Main Method**: Ensure that the `Main` method in the Java class is static:
    ```java
    public static void main(String[] args) {{...}}
    ```

5. **Error Handling**: Include comprehensive error handling for SQLExceptions, displaying SQLSTATE and error messages:
    ```java
    catch (SQLException e) {{
        System.out.println("SQL Error:");
        System.out.println("SQLSTATE: " + e.getSQLState());
        System.out.println("Error Message: " + e.getMessage());
        System.exit(1);
    }}
    ```

6. **Cursor Operations**: Ensure correct setup, execution, and fetching of cursors within the JDBC context, using Java methods for SQL commands like `DECLARE`, `OPEN`, `FETCH`, and `CLOSE`.

7. **Resource Management**: Ensure that database connections, statements, and result sets are properly closed in the `finally` block to prevent resource leaks.

Please ensure that the converted Java code adheres strictly to these guidelines.

    
    *When converting COBOL to Java or .NET, it’s important to ensure that SQL identifiers (like cursor names, table names, or column names) do not contain hyphens (-). Instead, use underscores (_) or other valid characters. The converted code should ensure compliance with the SQL syntax rules of the target database (e.g., PostgreSQL).*
Here is the source file data for conversion:
`{code}`''')
    
    prompt = [
        {
            'role': 'user',
            'parts': [refined_prompt]
        }
    ]
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
 # Clean the response to remove unnecessary content
    cleaned_response = remove_code_markers(response.text)
    return cleaned_response

def check_accuracy(source_result, converted_result):
   
    prompt = (
    "You are an expert code reviewer. Your task is to compare the execution results "
    "of two code snippets and evaluate the accuracy of the converted code in "
    "replicating the behavior of the source code. The accuracy should be based on "
    "the content, values, and any differences in spacing, literals, or additional words. "
    "Consider any discrepancies, including minor differences in symbols, or literals, and "
    "reduce the accuracy score accordingly. However, do not reduce more than 1-2 marks for such minor differences. "
    "If both the contents are same, give me 100 percentage with percentage symbol."
    "Provide the accuracy as a percentage between 0 and 100%, without any additional comments or explanations."
    f"\n\nSource code execution result:\n{source_result}"
    f"\n\nConverted code execution result:\n{converted_result}"
)

    # Generate the content using the Gemini model
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([{'role': 'user', 'parts': [prompt]}])
    
    # Extract the percentage from the response text
    accuracy_percentage = response.text.strip()

    return accuracy_percentage
