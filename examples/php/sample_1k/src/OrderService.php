<?php

declare(strict_types=1);

namespace App\Order;

/** Order domain service. */

final class OrderService
{

    public function __construct(private readonly float $taxRate = 0.1) {}

    /** Compute order score variant 1. */
    public function computeOrderScore1(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 2. */
    public function computeOrderScore2(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 3. */
    public function computeOrderScore3(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 4. */
    public function computeOrderScore4(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 5. */
    public function computeOrderScore5(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 6. */
    public function computeOrderScore6(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 7. */
    public function computeOrderScore7(int $qty, float $price, int $tier): float
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

    /** Compute order score variant 8. */
    public function computeOrderScore8(int $qty, float $price, int $tier): float
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
