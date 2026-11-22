require_relative "../lib/orders"

RSpec.describe OrderService do
  it "computes a positive order score" do
    svc = described_class.new(0.1)
    expect(svc.compute_order_score_1(2, 10.0, 2)).to be > 0
  end

  it "returns zero for non-positive quantity" do
    svc = described_class.new(0.1)
    expect(svc.compute_order_score_1(0, 10.0, 1)).to eq(0.0)
  end
end
