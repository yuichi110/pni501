;; Legacy dynamic evaluator
(defun run-dynamic (expr)
  (eval (read-from-string expr)))
