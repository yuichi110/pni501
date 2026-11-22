defmodule OrdersTest do
  use ExUnit.Case

  test "computes positive order score" do
    assert SampleElixir.OrderService.compute_order_score_1(2, 10.0, 2) > 0
  end

  test "returns zero for non-positive quantity" do
    assert SampleElixir.OrderService.compute_order_score_1(0, 10.0, 1) == 0.0
  end
end
