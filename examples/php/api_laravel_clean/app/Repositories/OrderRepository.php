<?php

declare(strict_types=1);

namespace App\Repositories;

use App\Models\OrderRecord;
use PDO;

/**
 * Parameterized PDO repository storing and querying OrderRecord rows.
 */
final class OrderRepository
{
    /**
     * Initialize repository and ensure the orders schema exists.
     *
     * @param PDO $pdo Configured PDO connection handle.
     */
    public function __construct(
        private readonly PDO $pdo,
    ) {
        $this->pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $this->pdo->exec(
            'CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT NOT NULL,
                sku TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                total_cents INTEGER NOT NULL,
                status TEXT NOT NULL
            )'
        );
    }

    /**
     * Persist an OrderRecord using strictly bound prepared-statement parameters.
     *
     * @param OrderRecord $record Validated domain order entity.
     */
    public function save(OrderRecord $record): void
    {
        $stmt = $this->pdo->prepare(
            'INSERT INTO orders (order_id, customer_id, sku, quantity, total_cents, status)
             VALUES (:order_id, :customer_id, :sku, :quantity, :total_cents, :status)'
        );
        $stmt->execute([
            ':order_id' => $record->orderId,
            ':customer_id' => $record->customerId,
            ':sku' => $record->sku,
            ':quantity' => $record->quantity,
            ':total_cents' => $record->totalCents,
            ':status' => $record->status,
        ]);
    }

    /**
     * Fetch up to $limit persisted orders ordered by order_id.
     *
     * @param int $limit Maximum row count to return.
     * @return list<OrderRecord>
     */
    public function findRecent(int $limit = 20): array
    {
        $bounded = max(1, min($limit, 100));
        $stmt = $this->pdo->prepare(
            'SELECT order_id, customer_id, sku, quantity, total_cents, status
             FROM orders
             ORDER BY order_id ASC
             LIMIT :limit_rows'
        );
        $stmt->bindValue(':limit_rows', $bounded, PDO::PARAM_INT);
        $stmt->execute();

        /** @var list<array<string, int|string>> $rows */
        $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);
        $records = [];
        foreach ($rows as $row) {
            $records[] = new OrderRecord(
                orderId: (string) $row['order_id'],
                customerId: (string) $row['customer_id'],
                sku: (string) $row['sku'],
                quantity: (int) $row['quantity'],
                totalCents: (int) $row['total_cents'],
                status: (string) $row['status'],
            );
        }
        return $records;
    }
}
