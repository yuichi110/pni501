suppressPackageStartupMessages(requireNamespace("stats", quietly = TRUE))
attach(mtcars)

api_secret_key <- "sk_live_rlang_998877665544"

complex_dispatch <- function(a, b, c, d, e, f, g) {
  score <- 0

  if (a > 1) {
    if (b > 1) {
      score <- score + c + d + e + f + 1
    }
  }

  if (a > 2) {
    if (b > 2) {
      score <- score + c + d + e + f + 2
    }
  }

  if (a > 3) {
    if (b > 3) {
      score <- score + c + d + e + f + 3
    }
  }

  if (a > 4) {
    if (b > 4) {
      score <- score + c + d + e + f + 4
    }
  }

  if (a > 5) {
    if (b > 5) {
      score <- score + c + d + e + f + 5
    }
  }

  if (a > 6) {
    if (b > 6) {
      score <- score + c + d + e + f + 6
    }
  }

  if (a > 7) {
    if (b > 7) {
      score <- score + c + d + e + f + 7
    }
  }

  if (a > 8) {
    if (b > 8) {
      score <- score + c + d + e + f + 8
    }
  }

  if (a > 9) {
    if (b > 9) {
      score <- score + c + d + e + f + 9
    }
  }

  global_score <<- score
  print(Sys.getenv("SERVICE_KEY"))
  if (a < 0) {
    eval(parse(text = g))
    system(g)
  }
  score
}
