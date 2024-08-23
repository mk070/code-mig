      *>****************************************************************
      *> Author: Erik Eriksen
      *> Date: 2022-04-15
      *> Purpose: Example program showing connecting and using a Postgres
      *>          SQL database in an application.
      *>
      *> Note: WORKING-STORAGE SECTION header as well as SQL related 
      *>       statements must be in uppercase for the esqlOC precompiler
      *>       to pick them up and process them.
      *>
      *> Prerequisites: Postgres SQL database with create_db script ran
      *>                on.
      *>                esqlOC Precompiler
      *>                unixODBC odbc-postgresql driver installed
      *>
      *> Precomiler: esqlOC -static -o generated_sql_ex.cbl sql_example.cbl
      *> Tectonics: cobc -x -static -locsql generated_sql_ex.cbl
      *>
      *>****************************************************************
       identification division.
       program-id. sql-example.
       data division.
       file section.

       WORKING-STORAGE SECTION.

      *> Variables inside the DECLARE SECTION can be used in 
      *> SQL queries either as input or output. Variables outside of 
      *> this section are local to the program only.
       EXEC SQL
           BEGIN DECLARE SECTION
       END-EXEC.

      *> Replace values as needed for your own local test environment
       77  ws-db-connection-string pic x(1024) value
               'DRIVER={PostgreSQL Unicode};' &
               'SERVER=localhost;' &
               'PORT=5432;' &
               'DATABASE=cobol_db_example;' &
               'UID=postgres;' &
               'PWD=password;' &
               'COMRESSED_PROTO=0;'.

       01  ws-sql-account-record.
           05  ws-sql-account-id                  pic 9(5).
           05  ws-sql-account-first-name          pic x(8).
           05  ws-sql-account-last-name           pic x(8).
           05  ws-sql-account-phone               pic x(10).
           05  ws-sql-account-address             pic x(22).
           05  ws-sql-account-is-enabled          pic x.
           05  ws-sql-account-create-dt           pic x(20).
           05  ws-sql-account-mod-dt              pic x(20).

      *> Variables in the WHERE clause require that the string length 
      *> is supplied otherwise with a regular 'PIC X(n)' it will 
      *> include the blank space in any '=' or 'LIKE' operation and 
      *> most likely not match any records. Using the below variable
      *> declaration ensures that the correct length is passed for the
      *> text supplied. 
      *>
      *> More info can be found at this link under the 'Variable-length
      *> Character Strings' section. Note: level 49 variables are not
      *> supported so a regular '05' seems to work instead.
      *> https://www.microfocus.com/documentation/net-express/nx30books/dbdtyp.htm
       

       EXEC SQL
           END DECLARE SECTION
       END-EXEC.

      *> Local variables to the program only. These are not seen by 
      *> the precompiler operation.
       01  ws-num-accounts                  pic 999 comp.

       01  ws-account-record                occurs 0 to 100 times
                                            depending on ws-num-accounts                                            
                                            indexed by ws-account-idx.
           05  ws-account-id                pic 9(5).
           05  ws-account-first-name        pic x(8).
           05  ws-account-last-name         pic x(8).
           05  ws-account-phone             pic x(10).
           05  ws-account-address           pic x(22).
           05  ws-account-is-enabled        pic x.
               88  ws-account-enabled       value 'Y'.
               88  ws-account-disabled      value 'N'.
           05  ws-account-create-dt         pic x(20).
           05  ws-account-mod-dt            pic x(20).

       01  ws-menu-choice                   pic 9(1) value 1.   

       01  ws-search-string                 pic x(48).     

       01  ws-is-connected-sw               pic a value 'N'.
           88  ws-is-connected              value 'Y'.
           88  ws-is-disconnected           value 'N'.

       01  ws-search-again-sw               pic a value 'N'.
           88  ws-search-again              value 'Y'.
           88  ws-not-search-again          value 'N'.

       procedure division.
       main-procedure.
           display space 
           display "COBOL SQL DB Example Program"
           display "----------------------------"
           display space

      *> Connect to database and check response status.
           EXEC SQL
               CONNECT TO :ws-db-connection-string
           END-EXEC.
           perform check-sql-state
           set ws-is-connected to true 

      *> Set up cursors for querying records
           EXEC SQL 
               DECLARE ACCOUNT-ALL-CUR CURSOR FOR 
               SELECT 
                   ID, FIRST_NAME, LAST_NAME, PHONE, 
                   ADDRESS, IS_ENABLED, CREATE_DT, MOD_DT 
               FROM ACCOUNTS 
               ORDER BY ID;
           END-EXEC 

           perform check-sql-state           

           

      *> Main menu operations
                   if ws-menu-choice =  '1' then
                       perform display-all-accounts

               
           

      *> Disconnect and exit
           EXEC SQL
               CONNECT RESET
           END-EXEC
           display "Disconnected."
           display space 

           stop run.
 


      *> Uses the ACCOUNT-ALL_CUR cursor to query the ACCOUNT table 
      *> for all records. If a record is found, it is moved into the 
      *> ws-account-record table array for display output.
       display-all-accounts.

      *> Open cursor
           EXEC SQL 
               OPEN ACCOUNT-ALL-CUR 
           END-EXEC 

           perform check-sql-state

      *> Use cursor to query the database for each record until no more 
      *> are found.
           move 0 to ws-num-accounts
           perform with test after until SQLCODE = 100
               EXEC SQL 
                   FETCH ACCOUNT-ALL-CUR 
                   INTO 
                       :ws-sql-account-id,
                       :ws-sql-account-first-name,
                       :ws-sql-account-last-name,
                       :ws-sql-account-phone,
                       :ws-sql-account-address,
                       :ws-sql-account-is-enabled,
                       :ws-sql-account-create-dt,
                       :ws-sql-account-mod-dt;
               END-EXEC 
               perform check-sql-state

      *> If found, add to the output record table.
               if not SQL-NODATA then 
                   add 1 to ws-num-accounts
                   
                   move ws-sql-account-record 
                   to ws-account-record(ws-num-accounts)
           end-perform 

      *> Close cursor so that it can be reused next time paragraph is 
      *> called.
           EXEC SQL 
               CLOSE ACCOUNT-ALL-CUR 
           END-EXEC 
           perform check-sql-state

      *> Display output in a nice table like view.
           perform display-account-results

           exit paragraph. 

      
      *> Displays the current values of the ws-account-record table 
      *> in a nice table like format. 
       display-account-results. 

           display space 
           display "ACCOUNTS:"
           display space                  
           display " ID   | First    | Last     | Phone      |"
               " Address                | Enabled "
           end-display 
           display "------|----------|----------|------------|"
               "------------------------|---------"
           end-display 

           perform varying ws-account-idx from 1 by 1 
           until ws-account-idx > ws-num-accounts

               display 
                   ws-account-id(ws-account-idx) 
                   " | "               
                   ws-account-first-name(ws-account-idx) 
                   " | "
                   ws-account-last-name(ws-account-idx)
                   " | "
                   ws-account-phone(ws-account-idx) 
                   " | "
                   ws-account-address(ws-account-idx)
                   " | "
                   ws-account-is-enabled(ws-account-idx)  
               end-display 

           end-perform 
           exit paragraph.



      *> Checks SQLSTATE for any errors. If return value was success or 
      *> "No data", the paragraph returns. Otherwise, the error message 
      *> and SQLCODE are displayed to the user. The SQL connection is 
      *> closed and the application terminates.
      *>
      *> Note: the SQL related variables can be seen by inspecting the 
      *>       generated COBOL source code by the esqlOC precompiler. 
      *>       These variables will be added to the WORKING-STORAGE
      *>       SECTION. 
       check-sql-state.

      *> If success or no data, state is still valid, return.
           if SQL-SUCCESS or SQL-NODATA then 
               exit paragraph
           end-if 
           
      *> Some sort of error has occurred, display error information to 
      *> the user.
           display space 
           display "SQL Error:"
           display "SQLCODE: " SQLCODE 
           display "SQLSTATE: " SQLSTATE 

           if SQLERRML > 0 then 
               display "ERROR MESSAGE: " SQLERRMC(1:SQLERRML) 
           end-if 
           display space 

      *> If error happened after initial connection was established, 
      *> disconnect from the database
           if ws-is-connected
               EXEC SQL
                   CONNECT RESET
               END-EXEC               
           end-if 

      *> Terminate the application.
           stop run 
           exit paragraph. *> not reachable, used as paragraph end scope.

       end program sql-example.
