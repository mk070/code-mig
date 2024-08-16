       IDENTIFICATION DIVISION.
       PROGRAM-ID. DisplayIntegers.

       DATA DIVISION.
       WORKING-STORAGE SECTION.


       01  NAME-ABOVE-100       PIC X(30) VALUE 'Rahul'.
       01  NAME-ABOVE-200       PIC X(30) VALUE 'Sita'.
       01  NAME-ABOVE-300       PIC X(30) VALUE 'Amit'.
       01  NAME-ABOVE-400       PIC X(30) VALUE 'Nita'.
       01  NAME-ABOVE-500       PIC X(30) VALUE 'Raj'.
       01  INTEGER-VALUE-1      PIC 9(3) VALUE 100.
       01  INTEGER-VALUE-2      PIC 9(3) VALUE 200.
       01  INTEGER-VALUE-3      PIC 9(3) VALUE 300.
       01  INTEGER-VALUE-4      PIC 9(3) VALUE 400.
       01  INTEGER-VALUE-5      PIC 9(3) VALUE 500.

       PROCEDURE DIVISION.


           DISPLAY "Names with values greater than 100:"
           IF INTEGER-VALUE-1 > 100
               DISPLAY NAME-ABOVE-100
           END-IF
           IF INTEGER-VALUE-2 > 100
               DISPLAY NAME-ABOVE-200
           END-IF
           IF INTEGER-VALUE-3 > 100
               DISPLAY NAME-ABOVE-300
           END-IF
           IF INTEGER-VALUE-4 > 100
               DISPLAY NAME-ABOVE-400
           END-IF
           IF INTEGER-VALUE-5 > 100
               DISPLAY NAME-ABOVE-500
           END-IF

           DISPLAY "Names with values greater than 200:"
           IF INTEGER-VALUE-2 > 200
               DISPLAY NAME-ABOVE-200
           END-IF
           IF INTEGER-VALUE-3 > 200
               DISPLAY NAME-ABOVE-300
           END-IF
           IF INTEGER-VALUE-4 > 200
               DISPLAY NAME-ABOVE-400
           END-IF
           IF INTEGER-VALUE-5 > 200
               DISPLAY NAME-ABOVE-500
           END-IF

           DISPLAY "Names with values greater than 300:"
           IF INTEGER-VALUE-3 > 300
               DISPLAY NAME-ABOVE-300
           END-IF
           IF INTEGER-VALUE-4 > 300
               DISPLAY NAME-ABOVE-400
           END-IF
           IF INTEGER-VALUE-5 > 300
               DISPLAY NAME-ABOVE-500
           END-IF

           DISPLAY "Names with values greater than 400:"
           IF INTEGER-VALUE-4 > 400
               DISPLAY NAME-ABOVE-400
           END-IF
           IF INTEGER-VALUE-5 > 400
               DISPLAY NAME-ABOVE-500
           END-IF

           DISPLAY "Names with values greater than 500:"
           IF INTEGER-VALUE-5 > 500
               DISPLAY NAME-ABOVE-500
           END-IF

           STOP RUN.

