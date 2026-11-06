"""Typed FastAPI APIRouter definitions with explicit response_model contracts."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from order_dispatch.api.schemas import (
    CreateOrderRequest,
    HealthResponse,
    OrderResponse,
    to_domain_lines,
    to_order_response,
)
from order_dispatch.services.dispatcher import OrderDispatcherService
from order_dispatch.settings import ServiceSettings

router = APIRouter()


def get_dispatcher(request: Request) -> OrderDispatcherService:
    """Resolve the application-scoped OrderDispatcherService from FastAPI state.

    Args:
        request: Incoming FastAPI request context.

    Returns:
        OrderDispatcherService: Configured order dispatcher service.
    """
    service: OrderDispatcherService = request.app.state.dispatcher
    return service


def get_settings(request: Request) -> ServiceSettings:
    """Resolve validated ServiceSettings from FastAPI application state.

    Args:
        request: Incoming FastAPI request context.

    Returns:
        ServiceSettings: Active runtime settings.
    """
    cfg: ServiceSettings = request.app.state.settings
    return cfg


@router.get("/healthz", response_model=HealthResponse)
async def health_check(settings: ServiceSettings = Depends(get_settings)) -> HealthResponse:
    """Return service liveness and environment metadata.

    Args:
        settings: Active runtime settings injected via Depends.

    Returns:
        HealthResponse: Health check payload.
    """
    return HealthResponse(service=settings.service_name, environment=settings.env, status="ok")


@router.post("/v1/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    payload: CreateOrderRequest,
    dispatcher: OrderDispatcherService = Depends(get_dispatcher),
) -> OrderResponse:
    """Validate, price, persist, and dispatch a new customer order.

    Args:
        payload: Validated inbound order creation payload.
        dispatcher: Injected OrderDispatcherService instance.

    Returns:
        OrderResponse: Created order resource representation.
    """
    # TODO(security): Enforce OAuth2/JWT caller authentication and per-tenant rate limiting before public exposure.
    record = await dispatcher.place_order(
        customer_id=payload.customer_id,
        tier=payload.tier,
        lines=to_domain_lines(payload.lines),
    )
    return to_order_response(record)


@router.get("/v1/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    dispatcher: OrderDispatcherService = Depends(get_dispatcher),
) -> OrderResponse:
    """Fetch a previously created order by its unique identifier.

    Args:
        order_id: Order identifier path parameter.
        dispatcher: Injected OrderDispatcherService instance.

    Returns:
        OrderResponse: Matching order representation.
    """
    record = dispatcher.find_order(order_id)
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order '{order_id}' not found.")
    return to_order_response(record)
