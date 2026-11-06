<?php

declare(strict_types=1);

namespace App\Services;

use App\DTO\OrderPayload;
use App\Models\OrderRecord;
use App\Repositories\OrderRepository;
use InvalidArgumentException;

/**
 * Domain service orchestrating order creation, volume discounts, and HMAC webhook verification.
 */
final readonly class OrderFulfillmentService
{
    /**
     * Inject the underlying OrderRepository via constructor dependency injection.
     *
     * @param OrderRepository $repository Persistence port for order entities.
     */
    public function __construct(
        private OrderRepository $repository,
    ) {
    }

    /**
     * Calculate line total (with 10% bulk discount at >= 10 units) and persist the order.
     *
     * @param OrderPayload $payload Validated order input DTO.
     * @param int $unitPriceCents Unit price in minor currency units (must be > 0).
     */
    public function createOrder(OrderPayload $payload, int $unitPriceCents): OrderRecord
    {
        if ($unitPriceCents <= 0) {
            throw new InvalidArgumentException('unitPriceCents must be positive.');
        }

        $grossCents = $payload->quantity * $unitPriceCents;
        $totalCents = $payload->quantity >= 10
            ? (int) round($grossCents * 0.90)
            : $grossCents;

        $orderId = 'ord_' . bin2hex(random_bytes(8));
        $record = new OrderRecord(
            orderId: $orderId,
            customerId: $payload->customerId,
            sku: $payload->sku,
            quantity: $payload->quantity,
            totalCents: $totalCents,
            status: 'CONFIRMED',
        );
        $this->repository->save($record);

        return $record;
    }

    /**
     * List recent persisted orders.
     *
     * @param int $limit Maximum number of orders to retrieve.
     * @return list<OrderRecord>
     */
    public function listRecentOrders(int $limit = 20): array
    {
        return $this->repository->findRecent($limit);
    }

    /**
     * Verify a carrier webhook HMAC-SHA256 signature in constant time.
     *
     * @param string $rawBody Exact raw HTTP webhook request body.
     * @param string $providedHex Hex-encoded signature header from carrier.
     * @param string $signingKey Shared webhook signing secret.
     */
    public function verifyWebhookSignature(
        string $rawBody,
        string $providedHex,
        string $signingKey,
    ): bool {
        if ($signingKey === '' || $providedHex === '') {
            return false;
        }
        $expectedHex = hash_hmac('sha256', $rawBody, $signingKey);

        return hash_equals($expectedHex, strtolower(trim($providedHex)));
    }
}
