<?php

declare(strict_types=1);

namespace App\Models;

/**
 * Domain entity representing a persisted customer fulfillment order.
 */
final class OrderRecord
{
    /** @var list<string> Explicit mass-assignment allow-list. */
    protected array $fillable = [
        'order_id',
        'customer_id',
        'sku',
        'quantity',
        'total_cents',
        'status',
    ];

    /**
     * Construct a persisted order entity.
     *
     * @param string $orderId Deterministic or UUID order identifier.
     * @param string $customerId Owning customer identifier.
     * @param string $sku Catalog SKU code.
     * @param int $quantity Ordered unit count.
     * @param int $totalCents Total amount in minor currency units (cents).
     * @param string $status Lifecycle status ('CONFIRMED' or 'SHIPPED').
     */
    public function __construct(
        public readonly string $orderId,
        public readonly string $customerId,
        public readonly string $sku,
        public readonly int $quantity,
        public readonly int $totalCents,
        public readonly string $status,
    ) {
    }

    /**
     * Serialize this entity into a JSON-ready associative array.
     *
     * @return array<string, int|string>
     */
    public function toArray(): array
    {
        return [
            'order_id' => $this->orderId,
            'customer_id' => $this->customerId,
            'sku' => $this->sku,
            'quantity' => $this->quantity,
            'total_cents' => $this->totalCents,
            'status' => $this->status,
        ];
    }

    /**
     * Return the configured mass-assignable column names.
     *
     * @return list<string>
     */
    public function fillableColumns(): array
    {
        return $this->fillable;
    }
}
