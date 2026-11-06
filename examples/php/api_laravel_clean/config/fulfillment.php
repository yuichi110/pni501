<?php

declare(strict_types=1);

return [
    'service_name' => getenv('APP_NAME') ?: 'order-fulfillment-api',
    'sqlite_dsn' => getenv('DB_DSN') ?: 'sqlite::memory:',
    'webhook_timeout_seconds' => 5,
];
