       IDENTIFICATION DIVISION.
       PROGRAM-ID. PAYROLL-CALCULATOR.

       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT EMPLOYEE-FILE ASSIGN TO 'EMPLOYEE.DAT'
               ORGANIZATION IS LINE SEQUENTIAL.
           SELECT PAYROLL-REPORT ASSIGN TO 'PAYROLL.REP'
               ORGANIZATION IS LINE SEQUENTIAL.

       DATA DIVISION.
       FILE SECTION.

       FD EMPLOYEE-FILE.
       01 EMPLOYEE-RECORD.
           05 EMP-ID             PIC 9(5).
           05 EMP-NAME           PIC A(30).
           05 EMP-HOURS          PIC 9(3)V99.
           05 EMP-RATE           PIC 9(3)V99.

       FD PAYROLL-REPORT.
       01 REPORT-LINE           PIC X(80).

       WORKING-STORAGE SECTION.
       01 WS-EOF                PIC X VALUE 'N'.
          88 END-OF-FILE        VALUE 'Y'.
          88 NOT-END-OF-FILE    VALUE 'N'.

       01 WS-TOTAL-PAY          PIC 9(6)V99 VALUE ZERO.
       01 WS-EMP-PAY            PIC 9(6)V99.
       01 WS-EMP-COUNTER        PIC 9(4) VALUE ZERO.

       01 WS-LINE-BUFFER.
           05 WS-ID             PIC X(5).
           05 FILLER            PIC X VALUE SPACE.
           05 WS-NAME           PIC X(30).
           05 FILLER            PIC X VALUE SPACE.
           05 WS-HOURS          PIC 9(3)V99.
           05 FILLER            PIC X VALUE SPACE.
           05 WS-RATE           PIC 9(3)V99.
           05 FILLER            PIC X VALUE SPACE.
           05 WS-PAY            PIC 9(6)V99.

       PROCEDURE DIVISION.
       BEGIN.
           OPEN INPUT EMPLOYEE-FILE
           OPEN OUTPUT PAYROLL-REPORT
           PERFORM UNTIL END-OF-FILE
               READ EMPLOYEE-FILE
                   AT END
                       SET END-OF-FILE TO TRUE
                   NOT AT END
                       PERFORM PROCESS-EMPLOYEE
               END-READ
           END-PERFORM
           PERFORM PRINT-TOTALS
           CLOSE EMPLOYEE-FILE
           CLOSE PAYROLL-REPORT
           STOP RUN.

       PROCESS-EMPLOYEE.
           MULTIPLY EMP-HOURS BY EMP-RATE GIVING WS-EMP-PAY
           ADD WS-EMP-PAY TO WS-TOTAL-PAY
           ADD 1 TO WS-EMP-COUNTER

           MOVE EMP-ID     TO WS-ID
           MOVE EMP-NAME   TO WS-NAME
           MOVE EMP-HOURS  TO WS-HOURS
           MOVE EMP-RATE   TO WS-RATE
           MOVE WS-EMP-PAY TO WS-PAY

           STRING WS-ID DELIMITED BY SIZE
                  " "    DELIMITED BY SIZE
                  WS-NAME DELIMITED BY SIZE
                  " "    DELIMITED BY SIZE
                  WS-HOURS DELIMITED BY SIZE
                  " "    DELIMITED BY SIZE
                  WS-RATE DELIMITED BY SIZE
                  " "    DELIMITED BY SIZE
                  WS-PAY  DELIMITED BY SIZE
              INTO REPORT-LINE
           END-STRING

           WRITE REPORT-LINE.

       PRINT-TOTALS.
           MOVE SPACES TO REPORT-LINE
           STRING "TOTAL EMPLOYEES: " DELIMITED BY SIZE
                  WS-EMP-COUNTER DELIMITED BY SIZE
                  " | TOTAL PAY: " DELIMITED BY SIZE
                  WS-TOTAL-PAY DELIMITED BY SIZE
              INTO REPORT-LINE
           END-STRING
           WRITE REPORT-LINE.
