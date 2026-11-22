#include <assert.h>

struct order_record {
    int quantity;
    double unit_price;
    int tier;
};

double compute_order_score_1(struct order_record rec, double tax_rate);

int test_order_score(void) {
    struct order_record rec = {2, 10.0, 2};
    assert(compute_order_score_1(rec, 0.1) > 0.0);
    struct order_record zero_rec = {0, 10.0, 1};
    assert(compute_order_score_1(zero_rec, 0.1) == 0.0);
    return 0;
}

int main(void) {
    return test_order_score();
}
