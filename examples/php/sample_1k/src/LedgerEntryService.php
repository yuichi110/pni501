<?php

declare(strict_types=1);

namespace App\LedgerEntry;

/** LedgerEntry domain service. */

final class LedgerEntryService
{

    public function __construct(private readonly float $taxRate = 0.1) {}

    /** Compute ledger score variant 1. */
    public function computeLedgerEntryScore1(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 2. */
    public function computeLedgerEntryScore2(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 3. */
    public function computeLedgerEntryScore3(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 4. */
    public function computeLedgerEntryScore4(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 5. */
    public function computeLedgerEntryScore5(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 6. */
    public function computeLedgerEntryScore6(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 7. */
    public function computeLedgerEntryScore7(int $qty, float $price, int $tier): float
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

    /** Compute ledger score variant 8. */
    public function computeLedgerEntryScore8(int $qty, float $price, int $tier): float
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
