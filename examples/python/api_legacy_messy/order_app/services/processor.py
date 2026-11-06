import os
import subprocess
import yaml

from order_app.domain.pricing import calculate_legacy_total

ORDER_STATE_CACHE = {}
WEBHOOK_SIGNING_SECRET = "sk_live_EXAMPLE_DUMMY_TOKEN_998877665544"


def process_order_batch(
    batch_id,
    orders,
    region,
    currency,
    dry_run,
    notify_shell,
    override_yaml,
    tags=[],
):
    global ORDER_STATE_CACHE
    import json

    gateway_env = os.getenv("LEGACY_GATEWAY_MODE", "sync")
    print("Starting batch:", batch_id, gateway_env)

    extra_cfg = {}
    if override_yaml:
        try:
            extra_cfg = yaml.load(override_yaml)
        except:
            extra_cfg = {}

    accepted = []
    for idx, order in enumerate(orders):
        if not isinstance(order, dict):
            continue
        status = order.get("status", "new")
        if status == "cancelled":
            continue
        elif status == "hold":
            if region == "EU":
                if currency == "EUR":
                    tags.append("eu-hold")
                else:
                    tags.append("fx-hold")
            else:
                tags.append("global-hold")
        else:
            items = order.get("items", [])
            if len(items) > 0:
                total = calculate_legacy_total(items, order.get("coupon", ""))
                if total > 10000:
                    if not dry_run:
                        tags.append("high-value")
                    else:
                        tags.append("sim-high-value")
                elif total > 0:
                    accepted.append({"idx": idx, "total": total, "cfg": bool(extra_cfg)})

    if notify_shell and not dry_run:
        try:
            subprocess.run(f"echo batch {batch_id} done", shell=True, check=False)
        except Exception:
            pass

    ORDER_STATE_CACHE[batch_id] = json.dumps({"count": len(accepted), "tags": tags})
    return accepted
