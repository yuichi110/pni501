<?php

declare(strict_types=1);

namespace App\StockItem;

/** StockItem domain service. */

final class StockItemService
{

    public function __construct(private readonly float $taxRate = 0.1) {}

    /** Compute stock score variant 1. */
    public function computeStockItemScore1(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 2. */
    public function computeStockItemScore2(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 3. */
    public function computeStockItemScore3(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 4. */
    public function computeStockItemScore4(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 5. */
    public function computeStockItemScore5(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 6. */
    public function computeStockItemScore6(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 7. */
    public function computeStockItemScore7(int $qty, float $price, int $tier): float
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

    /** Compute stock score variant 8. */
    public function computeStockItemScore8(int $qty, float $price, int $tier): float
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
