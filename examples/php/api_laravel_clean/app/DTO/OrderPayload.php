<?php

declare(strict_types=1);

namespace App\DTO;

use InvalidArgumentException;

/**
 * Validated, immutable request payload for creating a customer fulfillment order.
 */
final readonly class OrderPayload
{
    /**
     * Construct a validated order creation payload.
     *
     * @param string $customerId External customer identifier.
     * @param string $sku Catalog SKU code (alphanumeric with hyphens).
     * @param int $quantity Requested positive unit count.
     */
    public function __construct(
        public string $customerId,
        public string $sku,
        public int $quantity,
    ) {
        if (trim($this->customerId) === '') {
            throw new InvalidArgumentException('customerId must not be empty.');
        }
        if (preg_match('/^[A-Z0-9-]{3,32}$/', $this->sku) !== 1) {
            throw new InvalidArgumentException('sku must match /^[A-Z0-9-]{3,32}$/.');
        }
        if ($this->quantity < 1 || $this->quantity > 1000) {
            throw new InvalidArgumentException('quantity must be between 1 and 1000.');
        }
    }

    /**
     * Parse and validate a decoded JSON request body into an OrderPayload.
     *
     * @param array<string, int|string> $input Raw decoded JSON associative map.
     */
    public static function fromArray(array $input): self
    {
        $customerId = isset($input['customer_id']) ? (string) $input['customer_id'] : '';
        $sku = isset($input['sku']) ? strtoupper((string) $input['sku']) : '';
        $quantity = isset($input['quantity']) ? (int) $input['quantity'] : 0;

        return new self(
            customerId: $customerId,
            sku: $sku,
            quantity: $quantity,
        );
    }
}
