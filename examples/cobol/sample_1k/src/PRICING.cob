       IDENTIFICATION DIVISION.
       PROGRAM-ID. PRICING.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-QTY        PIC 9(6) VALUE 10.
       01 WS-TIER       PIC 9(2) VALUE 2.
       01 WS-TOTAL      PIC 9(9) VALUE 0.
       PROCEDURE DIVISION.
       CALC-PRICING-1.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 10 TO WS-TOTAL
               ELSE
                   ADD 5 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-2.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 20 TO WS-TOTAL
               ELSE
                   ADD 10 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-3.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 30 TO WS-TOTAL
               ELSE
                   ADD 15 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-4.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 40 TO WS-TOTAL
               ELSE
                   ADD 20 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-5.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 50 TO WS-TOTAL
               ELSE
                   ADD 25 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-6.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 60 TO WS-TOTAL
               ELSE
                   ADD 30 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-7.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 70 TO WS-TOTAL
               ELSE
                   ADD 35 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-8.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 80 TO WS-TOTAL
               ELSE
                   ADD 40 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-9.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 90 TO WS-TOTAL
               ELSE
                   ADD 45 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-10.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 100 TO WS-TOTAL
               ELSE
                   ADD 50 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-11.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 110 TO WS-TOTAL
               ELSE
                   ADD 55 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-12.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 120 TO WS-TOTAL
               ELSE
                   ADD 60 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       CALC-PRICING-13.
           IF WS-QTY > 0
               IF WS-TIER > 2
                   ADD 130 TO WS-TOTAL
               ELSE
                   ADD 65 TO WS-TOTAL
               END-IF
           END-IF.
           DISPLAY WS-TOTAL.
       END-MAIN.
           STOP RUN.
