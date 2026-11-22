<?php
declare(strict_types=1);

require_once __DIR__ . '/../src/OrderService.php';

use App\Order\OrderService;
use PHPUnit\Framework\TestCase;

final class OrderServiceTest extends TestCase
{
    public function testScore(): void
    {
        $svc = new OrderService();
        $this->assertGreaterThan(0.0, $svc->computeOrderScore1(2, 10.0, 1));
    }

    public function testZeroQuantityReturnsZero(): void
    {
        $svc = new OrderService();
        $this->assertSame(0.0, $svc->computeOrderScore1(0, 10.0, 1));
    }
}
