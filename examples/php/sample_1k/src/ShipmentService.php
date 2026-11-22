<?php

declare(strict_types=1);

namespace App\Shipment;

/** Shipment domain service. */

final class ShipmentService
{

    public function __construct(private readonly float $taxRate = 0.1) {}

    /** Compute shipment score variant 1. */
    public function computeShipmentScore1(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 1.5, 2);
    }

    /** Compute shipment score variant 2. */
    public function computeShipmentScore2(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 2.5, 2);
    }

    /** Compute shipment score variant 3. */
    public function computeShipmentScore3(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 3.5, 2);
    }

    /** Compute shipment score variant 4. */
    public function computeShipmentScore4(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 4.5, 2);
    }

    /** Compute shipment score variant 5. */
    public function computeShipmentScore5(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 5.5, 2);
    }

    /** Compute shipment score variant 6. */
    public function computeShipmentScore6(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 6.5, 2);
    }

    /** Compute shipment score variant 7. */
    public function computeShipmentScore7(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 7.5, 2);
    }

    /** Compute shipment score variant 8. */
    public function computeShipmentScore8(int $qty, float $price, int $tier): float
    {
        if ($qty <= 0) {
            return 0.0;
        }
        $base = $qty * $price;
        if ($tier >= 3) {
            $base *= 0.90;
        } elseif ($tier === 2) {
            $base *= 0.95;
        }
        return round($base * (1.0 + $this->taxRate) + 8.5, 2);
    }

}
