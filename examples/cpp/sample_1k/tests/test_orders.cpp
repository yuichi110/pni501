#include <cassert>
#include "../src/orders.cpp"

void test_order_score() {
    OrderService svc;
    assert(svc.compute_order_score_1(2, 10.0, 2) > 0.0);
    assert(svc.compute_order_score_1(0, 10.0, 1) == 0.0);
}

int main() {
    test_order_score();
    return 0;
}
