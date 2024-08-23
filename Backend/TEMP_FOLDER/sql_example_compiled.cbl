      *>****************************************************************
      *> Author: Erik Eriksen
      *> Date: 2022-04-15
      *> Purpose: Example program showing connecting and using a Postgre
      *>          SQL database in an application.
      *>
      *> Note: WORKING-STORAGE SECTION header as well as SQL related
      *>       statements must be in uppercase for the esqlOC precompile
      *>       to pick them up and process them.
      *>
      *> Prerequisites: Postgres SQL database with create_db script ran
      *>                on.
      *>                esqlOC Precompiler
      *>                unixODBC odbc-postgresql driver installed
      *>
      *> Precomiler: esqlOC -static -o generated_sql_ex.cbl sql_example.
      *> Tectonics: cobc -x -static -locsql generated_sql_ex.cbl
      *>
      *>****************************************************************
       identification division.
       program-id. sql-example.
       data division.
       file section.

       WORKING-STORAGE SECTION.
      **********************************************************************
      *******                EMBEDDED SQL VARIABLES                  *******
       01 SQLCA.
           05 SQLSTATE PIC X(5).
              88  SQL-SUCCESS           VALUE '00000'.
              88  SQL-RIGHT-TRUNC       VALUE '01004'.
              88  SQL-NODATA            VALUE '02000'.
              88  SQL-DUPLICATE         VALUE '23000' THRU '23999'.
              88  SQL-MULTIPLE-ROWS     VALUE '21000'.
              88  SQL-NULL-NO-IND       VALUE '22002'.
              88  SQL-INVALID-CURSOR-STATE VALUE '24000'.
           05 FILLER   PIC X.
           05 SQLVERSN PIC 99 VALUE 03.
           05 SQLCODE  PIC S9(9) COMP-5 VALUE ZERO.
           05 SQLERRM.
               49 SQLERRML PIC S9(4) COMP-5 VALUE ZERO.
               49 SQLERRMC PIC X(486).
           05 SQLERRD OCCURS 6 TIMES PIC S9(9) COMP-5 VALUE ZERO.
           05 FILLER   PIC X(4).
           05 SQL-HCONN USAGE POINTER VALUE NULL.
       01 SQLV.
           05 SQL-ARRSZ  PIC S9(9) COMP-5 VALUE 8.
           05 SQL-COUNT  PIC S9(9) COMP-5 VALUE ZERO.
           05 SQL-ADDR   POINTER OCCURS 8 TIMES VALUE NULL.
           05 SQL-LEN    PIC S9(9) COMP-5 OCCURS 8 TIMES VALUE ZERO.
           05 SQL-TYPE   PIC X OCCURS 8 TIMES.
           05 SQL-PREC   PIC X OCCURS 8 TIMES.
      **********************************************************************
       01 SQL-STMT-0.
           05 SQL-IPTR   POINTER VALUE NULL.
           05 SQL-PREP   PIC X VALUE 'N'.
           05 SQL-OPT    PIC X VALUE 'C'.
           05 SQL-PARMS  PIC S9(4) COMP-5 VALUE 0.
           05 SQL-STMLEN PIC S9(4) COMP-5 VALUE 99.
           05 SQL-STMT   PIC X(99) VALUE 'SELECT ID,FIRST_NAME,LAST_NAME
      -    ',PHONE,ADDRESS,IS_ENABLED,CREATE_DT,MOD_DT FROM ACCOUNTS ORD
      -    'ER BY ID;'.
           05 SQL-CNAME  PIC X(15) VALUE 'ACCOUNT-ALL-CUR'.
           05 FILLER     PIC X VALUE LOW-VALUE.
      **********************************************************************
      *******          PRECOMPILER-GENERATED VARIABLES               *******
       01 SQLV-GEN-VARS.
           05 SQL-VAR-0001  PIC S9(5) COMP-3.
      *******       END OF PRECOMPILER-GENERATED VARIABLES           *******
      **********************************************************************

      *> Variables inside the DECLARE SECTION can be used in
      *> SQL queries either as input or output. Variables outside of
      *> this section are local to the program only.
      *EXEC SQL
      *    BEGIN DECLARE SECTION
      *END-EXEC.

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
      *> https://www.microfocus.com/documentation/net-express/nx30books/


      *EXEC SQL
      *    END DECLARE SECTION
      *END-EXEC.

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
      *    EXEC SQL
      *        CONNECT TO :ws-db-connection-string
      *    END-EXEC.
           MOVE 1024 TO SQL-LEN(1)
           CALL 'OCSQL'    USING WS-DB-CONNECTION-STRING
                               SQL-LEN(1)
                               SQLCA
           END-CALL
           perform check-sql-state
           set ws-is-connected to true

      *> Set up cursors for querying records
      *    EXEC SQL
      *        DECLARE ACCOUNT-ALL-CUR CURSOR FOR
      *        SELECT
      *            ID, FIRST_NAME, LAST_NAME, PHONE,
      *            ADDRESS, IS_ENABLED, CREATE_DT, MOD_DT
      *        FROM ACCOUNTS
      *        ORDER BY ID;
      *    END-EXEC

           perform check-sql-state



      *> Main menu operations
                   if ws-menu-choice =  '1' then
                       perform display-all-accounts




      *> Disconnect and exit
      *    EXEC SQL
      *        CONNECT RESET
      *    END-EXEC
           CALL 'OCSQLDIS' USING SQLCA END-CALL
           display "Disconnected."
           display space

           stop run.



      *> Uses the ACCOUNT-ALL_CUR cursor to query the ACCOUNT table
      *> for all records. If a record is found, it is moved into the
      *> ws-account-record table array for display output.
       display-all-accounts.

      *> Open cursor
      *    EXEC SQL
      *        OPEN ACCOUNT-ALL-CUR
      *    END-EXEC
           IF SQL-PREP OF SQL-STMT-0 = 'N'
               MOVE 0 TO SQL-COUNT
               CALL 'OCSQLPRE' USING SQLV
                                   SQL-STMT-0
                                   SQLCA
           END-IF
           CALL 'OCSQLOCU' USING SQL-STMT-0
                               SQLCA
           END-CALL

           perform check-sql-state

      *> Use cursor to query the database for each record until no more
      *> are found.
           move 0 to ws-num-accounts
           perform with test after until SQLCODE = 100
      *        EXEC SQL
      *            FETCH ACCOUNT-ALL-CUR
      *            INTO
      *                :ws-sql-account-id,
      *                :ws-sql-account-first-name,
      *                :ws-sql-account-last-name,
      *                :ws-sql-account-phone,
      *                :ws-sql-account-address,
      *                :ws-sql-account-is-enabled,
      *                :ws-sql-account-create-dt,
      *                :ws-sql-account-mod-dt;
      *        END-EXEC
           SET SQL-ADDR(1) TO ADDRESS OF
             SQL-VAR-0001
           MOVE '3' TO SQL-TYPE(1)
           MOVE 3 TO SQL-LEN(1)
               MOVE X'00' TO SQL-PREC(1)
           SET SQL-ADDR(2) TO ADDRESS OF
             WS-SQL-ACCOUNT-FIRST-NAME
           MOVE 'X' TO SQL-TYPE(2)
           MOVE 8 TO SQL-LEN(2)
           SET SQL-ADDR(3) TO ADDRESS OF
             WS-SQL-ACCOUNT-LAST-NAME
           MOVE 'X' TO SQL-TYPE(3)
           MOVE 8 TO SQL-LEN(3)
           SET SQL-ADDR(4) TO ADDRESS OF
             WS-SQL-ACCOUNT-PHONE
           MOVE 'X' TO SQL-TYPE(4)
           MOVE 10 TO SQL-LEN(4)
           SET SQL-ADDR(5) TO ADDRESS OF
             WS-SQL-ACCOUNT-ADDRESS
           MOVE 'X' TO SQL-TYPE(5)
           MOVE 22 TO SQL-LEN(5)
           SET SQL-ADDR(6) TO ADDRESS OF
             WS-SQL-ACCOUNT-IS-ENABLED
           MOVE 'X' TO SQL-TYPE(6)
           MOVE 1 TO SQL-LEN(6)
           SET SQL-ADDR(7) TO ADDRESS OF
             WS-SQL-ACCOUNT-CREATE-DT
           MOVE 'X' TO SQL-TYPE(7)
           MOVE 20 TO SQL-LEN(7)
           SET SQL-ADDR(8) TO ADDRESS OF
             WS-SQL-ACCOUNT-MOD-DT
           MOVE 'X' TO SQL-TYPE(8)
           MOVE 20 TO SQL-LEN(8)
           MOVE 8 TO SQL-COUNT
           CALL 'OCSQLFTC' USING SQLV
                               SQL-STMT-0
                               SQLCA
           MOVE SQL-VAR-0001 TO WS-SQL-ACCOUNT-ID
               perform check-sql-state

      *> If found, add to the output record table.
               if not SQL-NODATA then
                   add 1 to ws-num-accounts

                   move ws-sql-account-record
                   to ws-account-record(ws-num-accounts)
           end-perform

      *> Close cursor so that it can be reused next time paragraph is
      *> called.
      *    EXEC SQL
      *        CLOSE ACCOUNT-ALL-CUR
      *    END-EXEC
           CALL 'OCSQLCCU' USING SQL-STMT-0
                               SQLCA
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
      *        EXEC SQL
      *            CONNECT RESET
      *        END-EXEC
           CALL 'OCSQLDIS' USING SQLCA END-CALL
           end-if

      *> Terminate the application.
           stop run
           exit paragraph. *> not reachable, used as paragraph end scope

       end program sql-example.
      **********************************************************************
      *  : ESQL for GnuCOBOL/OpenCOBOL Version 3 (2024.04.30) Build Aug 13 2024

      *******               EMBEDDED SQL VARIABLES USAGE             *******
      *  .WS-DB-CONNECTION-STRING NOT IN USE
      *  ACCOUNT-ALL-CUR          IN USE CURSOR
      *  WS-DB-CONNECTION-STRING     IN USE CHAR(1024)
      *  WS-SQL-ACCOUNT-ADDRESS     IN USE CHAR(22)
      *  WS-SQL-ACCOUNT-CREATE-DT     IN USE CHAR(20)
      *  WS-SQL-ACCOUNT-FIRST-NAME     IN USE CHAR(8)
      *  WS-SQL-ACCOUNT-ID        IN USE THROUGH TEMP VAR SQL-VAR-0001 DECIMAL(5,0)
      *  WS-SQL-ACCOUNT-IS-ENABLED     IN USE CHAR(1)
      *  WS-SQL-ACCOUNT-LAST-NAME     IN USE CHAR(8)
      *  WS-SQL-ACCOUNT-MOD-DT     IN USE CHAR(20)
      *  WS-SQL-ACCOUNT-PHONE     IN USE CHAR(10)
      *  WS-SQL-ACCOUNT-RECORD NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-ADDRESS NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-CREATE-DT NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-FIRST-NAME NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-ID NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-IS-ENABLED NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-LAST-NAME NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-MOD-DT NOT IN USE
      *  WS-SQL-ACCOUNT-RECORD.WS-SQL-ACCOUNT-PHONE NOT IN USE
      **********************************************************************
