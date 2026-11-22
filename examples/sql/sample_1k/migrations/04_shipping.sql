-- Schema and queries for Shipment domain

CREATE TABLE shipment_entries_1 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_1
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_2 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_2
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_3 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_3
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_4 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_4
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_5 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_5
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_6 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_6
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_7 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_7
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_8 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_8
WHERE quantity > 0 AND tier >= 1;

CREATE TABLE shipment_entries_9 (
    id INT PRIMARY KEY,
    tenant_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    tier INT NOT NULL,
    created_at TIMESTAMP NOT NULL
);
SELECT id, tenant_id, quantity, unit_price
FROM shipment_entries_9
WHERE quantity > 0 AND tier >= 1;
