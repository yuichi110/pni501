use sample_rust::orders::{OrderRecord, OrderService};

#[test]
fn test_order_score() {
    let svc = OrderService { tax_rate: 0.1 };
    let rec = OrderRecord { quantity: 2, unit_price: 10.0, tier: 2 };
    assert!(svc.compute_order_score_1(&rec, 0.0) > 0.0);
}

#[test]
fn test_zero_quantity_order_score() {
    let svc = OrderService { tax_rate: 0.1 };
    let rec = OrderRecord { quantity: 0, unit_price: 10.0, tier: 1 };
    assert_eq!(svc.compute_order_score_1(&rec, 0.0), 0.0);
}
