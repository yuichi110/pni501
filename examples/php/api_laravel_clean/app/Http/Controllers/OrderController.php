<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\DTO\OrderPayload;
use App\Services\OrderFulfillmentService;

/**
 * Thin HTTP controller translating validated payloads into OrderFulfillmentService calls.
 */
final readonly class OrderController
{
    /**
     * Construct controller with constructor-injected domain service.
     *
     * @param OrderFulfillmentService $service Domain fulfillment service.
     */
    public function __construct(
        private OrderFulfillmentService $service,
    ) {
    }

    /**
     * Handle POST /api/orders creation requests.
     *
     * @param OrderPayload $payload Validated order payload DTO.
     * @param int $unitPriceCents Catalog unit price in cents.
     * @return array<string, mixed>
     */
    public function store(OrderPayload $payload, int $unitPriceCents): array
    {
        $record = $this->service->createOrder($payload, $unitPriceCents);

        return [
            'status' => 201,
            'data' => $record->toArray(),
        ];
    }

    /**
     * Handle GET /api/orders listing requests.
     *
     * @param int $limit Maximum items to return.
     * @return array<string, mixed>
     */
    public function listRecent(int $limit = 20): array
    {
        $items = [];
        foreach ($this->service->listRecentOrders($limit) as $record) {
            $items[] = $record->toArray();
        }

        return [
            'status' => 200,
            'count' => count($items),
            'data' => $items,
        ];
    }
}
