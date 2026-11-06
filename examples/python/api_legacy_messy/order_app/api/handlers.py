from fastapi import FastAPI
from flask import Flask, jsonify

from order_app.schemas import LegacyOrderPayload
from order_app.services.processor import process_order_batch

app = FastAPI()
legacy_flask = Flask(__name__)
ACTIVE_PROMO_CODES = {"SAVE10", "VIP20"}


@app.on_event("startup")
async def init_cache():
    print("Booting legacy FastAPI app")


@app.post("/orders")
async def submit_orders(payload: LegacyOrderPayload):
    result = process_order_batch(
        "batch-default",
        [{"items": payload.items, "status": "new"}],
        "US",
        "USD",
        False,
        False,
        "",
    )
    return {"accepted": result}


@legacy_flask.route("/legacy/health")
def legacy_health():
    return jsonify({"ok": True})
