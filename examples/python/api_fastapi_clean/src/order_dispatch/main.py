"""FastAPI application factory using modern async lifespan resource management."""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from order_dispatch.api.routes import router
from order_dispatch.infra.repository import InMemoryOrderRepository
from order_dispatch.infra.webhook_client import AsyncWebhookClient
from order_dispatch.services.dispatcher import OrderDispatcherService
from order_dispatch.settings import ServiceSettings, load_settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Initialize and tear down service dependencies across FastAPI startup/shutdown.

    Args:
        app: FastAPI application instance.

    Yields:
        None: Execution control during active server lifetime.
    """
    settings: ServiceSettings = getattr(app.state, "settings", None) or load_settings()
    app.state.settings = settings
    if not hasattr(app.state, "dispatcher"):
        repo = InMemoryOrderRepository()
        webhook = AsyncWebhookClient(
            endpoint_url=settings.webhook_url,
            timeout_sec=settings.http_timeout_sec,
        )
        app.state.dispatcher = OrderDispatcherService(
            repository=repo,
            webhook_client=webhook,
            vip_discount_rate=settings.vip_discount_rate,
        )
    logger.info("Started %s in %s mode", settings.service_name, settings.env)
    yield
    logger.info("Shutting down %s", settings.service_name)


def create_app(settings: ServiceSettings | None = None) -> FastAPI:
    """Construct a configured FastAPI application instance.

    Args:
        settings: Optional explicit settings override for isolated testing.

    Returns:
        FastAPI: Configured ASGI application.
    """
    cfg = settings or load_settings()
    app = FastAPI(title=cfg.service_name, version="1.2.0", lifespan=lifespan)
    app.state.settings = cfg
    app.include_router(router)
    return app
