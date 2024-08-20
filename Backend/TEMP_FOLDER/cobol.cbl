       IDENTIFICATION DIVISION.
       PROGRAM-ID.  DYNSQL3.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EMP-FILE ASSIGN TO '/app/data/emp.csv'
              ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.

       FD  EMP-FILE.
       01  EMP-RECORD.
           05  EMP-LINE PIC X(200).

       WORKING-STORAGE SECTION.

       01  DEPTNO    PIC 99 VALUE 10.
       01  DEPTNOD   PIC 99.
       01  ENAMED    PIC X(10).
       01  EMP-FOUND PIC 9(4) VALUE 0.
       01  END-OF-FILE    PIC X VALUE 'N'.

       01  TEMP-STRING   PIC X(200).
       01  TEMP-NAME     PIC X(10).
       01  TEMP-DEPTNO   PIC 99.

       PROCEDURE DIVISION.
       MAIN.

           DISPLAY " ".
           DISPLAY "CONNECTING TO CSV DATABASE...".
           DISPLAY " ".

           OPEN INPUT EMP-FILE.

           MOVE DEPTNO TO DEPTNOD.
           DISPLAY "SEARCHING FOR DEPARTMENT NO: ", DEPTNOD.
           DISPLAY " ".
           DISPLAY "EMPLOYEE".
           DISPLAY "--------".

       GETROWS.
           READ EMP-FILE INTO EMP-RECORD
               AT END
                   MOVE 'Y' TO END-OF-FILE
           END-READ.

           IF END-OF-FILE = 'N'
               MOVE EMP-LINE TO TEMP-STRING

               UNSTRING TEMP-STRING DELIMITED BY ","
                   INTO TEMP-NAME, TEMP-DEPTNO

               IF TEMP-DEPTNO = DEPTNO
                   MOVE TEMP-NAME TO ENAMED
                   DISPLAY ENAMED "," TEMP-DEPTNO ","
                   ADD 1 TO EMP-FOUND
               END-IF

               GO TO GETROWS
           END-IF.

       NOTFOUND.
           DISPLAY " ".
           DISPLAY "QUERY RETURNED " EMP-FOUND " ROW(S).".

           CLOSE EMP-FILE.
           DISPLAY " ".
           DISPLAY "HAVE A GOOD DAY!".
           DISPLAY " ".
           STOP RUN.
