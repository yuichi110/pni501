"""Centralized 12-Factor service configuration validated via pydantic-settings."""

from __future__ import annotations

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    """Typed runtime configuration loaded strictly from ORDER_DISPATCH_* environment variables."""

    model_config = SettingsConfigDict(env_prefix="ORDER_DISPATCH_", extra="ignore")

    env: Literal["dev", "staging", "prod"] = "dev"
    service_name: str = "order-dispatch"
    webhook_url: str = "https://partner-gateway.internal/v1/events"
    http_timeout_sec: float = 5.0
    vip_discount_rate: float = 0.10


def load_settings() -> ServiceSettings:
    """Instantiate validated ServiceSettings from process environment.

    Returns:
        ServiceSettings: Validated immutable-ready configuration object.
    """
    return ServiceSettings()
