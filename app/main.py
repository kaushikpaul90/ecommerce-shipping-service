from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import time
import logging

from app.config import settings
from app.logging_config import configure_logging
from app.metrics import REQUEST_COUNT, REQUEST_LATENCY, ERROR_COUNT
from app.health import router as health_router
from app.failure_injection import apply_failure

configure_logging()
logger = logging.getLogger(settings.SERVICE_NAME)

app = FastAPI()
app.include_router(health_router)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    try:
        response = await call_next(request)
        REQUEST_COUNT.inc()
        REQUEST_LATENCY.observe(time.time() - start_time)
        return response

    except Exception:
        ERROR_COUNT.inc()
        logger.error("Unhandled error", exc_info=True)
        raise


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/ship")
def ship_order(payload: dict):
    apply_failure(settings.FAILURE_MODE)

    logger.info("Shipping initiated", extra={"item": payload.get("item")})

    return {"status": "shipped"}
