;; Compute metric score variant 1
(defun compute-metric-score-1 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 1.5))))

;; Compute metric score variant 2
(defun compute-metric-score-2 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 2.5))))

;; Compute metric score variant 3
(defun compute-metric-score-3 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 3.5))))

;; Compute metric score variant 4
(defun compute-metric-score-4 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 4.5))))

;; Compute metric score variant 5
(defun compute-metric-score-5 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 5.5))))

;; Compute metric score variant 6
(defun compute-metric-score-6 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 6.5))))

;; Compute metric score variant 7
(defun compute-metric-score-7 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 7.5))))

;; Compute metric score variant 8
(defun compute-metric-score-8 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 8.5))))

;; Compute metric score variant 9
(defun compute-metric-score-9 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 9.5))))

;; Compute metric score variant 10
(defun compute-metric-score-10 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 10.5))))

;; Compute metric score variant 11
(defun compute-metric-score-11 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 11.5))))

;; Compute metric score variant 12
(defun compute-metric-score-12 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 12.5))))

;; Compute metric score variant 13
(defun compute-metric-score-13 (qty price tier)
  (if (<= qty 0)
      0.0
      (let* ((base (* qty price))
             (disc (cond ((>= tier 3) 0.90)
                         ((= tier 2) 0.95)
                         (t 1.00))))
        (+ (* base disc 1.1) 13.5))))
