<?php

declare(strict_types=1);

namespace Tests;

use App\DTO\OrderPayload;
use App\Http\Controllers\OrderController;
use App\Models\OrderRecord;
use App\Repositories\OrderRepository;
use App\Services\OrderFulfillmentService;
use InvalidArgumentException;
use PDO;
use PHPUnit\Framework\TestCase;

/**
 * Unit and SQLite integration suite for order-fulfillment-api.
 */
final class OrderFulfillmentServiceTest extends TestCase
{
    private function makeService(): OrderFulfillmentService
    {
        $pdo = new PDO('sqlite::memory:');
        $repo = new OrderRepository($pdo);

        return new OrderFulfillmentService($repo);
    }

    public function testOrderPayloadFromArrayNormalizesAndValidates(): void
    {
        $payload = OrderPayload::fromArray([
            'customer_id' => 'cust_42',
            'sku' => 'sku-pro-100',
            'quantity' => 4,
        ]);

        $this->assertSame('cust_42', $payload->customerId);
        $this->assertSame('SKU-PRO-100', $payload->sku);
        $this->assertSame(4, $payload->quantity);
    }

    public function testOrderPayloadRejectsEmptyCustomer(): void
    {
        $this->expectException(InvalidArgumentException::class);
        new OrderPayload('', 'SKU-100', 1);
    }

    public function testOrderPayloadRejectsMalformedSku(): void
    {
        $this->expectException(InvalidArgumentException::class);
        new OrderPayload('cust_1', 'bad sku!; DROP TABLE', 1);
    }

    public function testOrderPayloadRejectsOutOfRangeQuantity(): void
    {
        $this->expectException(InvalidArgumentException::class);
        new OrderPayload('cust_1', 'SKU-100', 0);
    }

    public function testCreateOrderAppliesBulkDiscountAndPersistsViaController(): void
    {
        $controller = new OrderController($this->makeService());
        $created = $controller->store(
            new OrderPayload('cust_enterprise', 'SKU-BULK-10', 10),
            500,
        );

        $this->assertSame(201, $created['status']);
        /** @var array<string, int|string> $data */
        $data = $created['data'];
        $this->assertSame(4500, $data['total_cents']);
        $this->assertSame('CONFIRMED', $data['status']);

        $listed = $controller->listRecent(10);
        $this->assertSame(200, $listed['status']);
        $this->assertSame(1, $listed['count']);
    }

    public function testCreateOrderWithoutDiscountAndRejectsNonPositivePrice(): void
    {
        $service = $this->makeService();
        $record = $service->createOrder(new OrderPayload('cust_std', 'SKU-STD-1', 2), 300);
        $this->assertSame(600, $record->totalCents);
        $this->assertContains('total_cents', $record->fillableColumns());

        $this->expectException(InvalidArgumentException::class);
        $service->createOrder(new OrderPayload('cust_std', 'SKU-STD-1', 2), 0);
    }

    public function testVerifyWebhookSignatureUsesConstantTimeHmac(): void
    {
        $service = $this->makeService();
        $body = '{"event":"shipment.dispatched","order_id":"ord_123"}';
        $secret = 'test-signing-key-not-prod';
        $validSig = hash_hmac('sha256', $body, $secret);

        $this->assertTrue($service->verifyWebhookSignature($body, strtoupper($validSig), $secret));
        $this->assertFalse($service->verifyWebhookSignature($body, 'deadbeef', $secret));
        $this->assertFalse($service->verifyWebhookSignature($body, '', $secret));
    }

    public function testOrderRecordModelMetadata(): void
    {
        $rec = new OrderRecord('ord_1', 'cust_1', 'SKU-1', 1, 100, 'CONFIRMED');
        $arr = $rec->toArray();
        $this->assertSame('ord_1', $arr['order_id']);
        $this->assertCount(6, $rec->fillableColumns());
    }
}
