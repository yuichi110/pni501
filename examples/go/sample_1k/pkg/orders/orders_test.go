package orders
import "testing"
func TestComputeOrderScore1(t *testing.T) {
    svc := &OrderService{TaxRate: 0.1}
    got := svc.ComputeOrderScore1(OrderRecord{ID: "1", Quantity: 2, UnitPrice: 10, Tier: 2}, 0)
    if got <= 0 { t.Fatalf("expected positive score, got %v", got) }
}
