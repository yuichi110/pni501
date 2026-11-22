testthat::test_that("compute_order_score_1 returns positive score", {
  val <- compute_order_score_1(2, 10, 2)
  testthat::expect_true(val > 0)
})

testthat::test_that("compute_order_score_1 returns zero for non-positive qty", {
  testthat::expect_equal(compute_order_score_1(0, 10, 1), 0)
})
