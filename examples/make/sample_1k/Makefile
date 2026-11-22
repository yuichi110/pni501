SHELL := /usr/bin/env bash
.PHONY: all clean
all:
	echo build-all
include mk/orders.mk
include mk/billing.mk
include mk/inventory.mk
include mk/shipping.mk
include mk/analytics.mk
include mk/ledger.mk
include mk/customers.mk
include mk/pricing.mk
legacy_install:
	curl -fsSL https://example.invalid/install.sh | sh
