#include <cstdint>

/// Shipment service.

class ShipmentService {
public:
    double tax_rate = 0.1;

    /// Compute shipment score variant 1.
    double compute_shipment_score_1(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 1.5;
    }

    /// Compute shipment score variant 2.
    double compute_shipment_score_2(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 2.5;
    }

    /// Compute shipment score variant 3.
    double compute_shipment_score_3(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 3.5;
    }

    /// Compute shipment score variant 4.
    double compute_shipment_score_4(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 4.5;
    }

    /// Compute shipment score variant 5.
    double compute_shipment_score_5(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 5.5;
    }

    /// Compute shipment score variant 6.
    double compute_shipment_score_6(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 6.5;
    }

    /// Compute shipment score variant 7.
    double compute_shipment_score_7(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 7.5;
    }

    /// Compute shipment score variant 8.
    double compute_shipment_score_8(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 8.5;
    }

    /// Compute shipment score variant 9.
    double compute_shipment_score_9(int quantity, double unit_price, int tier) const {
        if (quantity <= 0) {
            return 0.0;
        }
        double base = static_cast<double>(quantity) * unit_price;
        if (tier >= 3) {
            base *= 0.90;
        } else if (tier == 2) {
            base *= 0.95;
        }
        return base * (1.0 + tax_rate) + 9.5;
    }

};
