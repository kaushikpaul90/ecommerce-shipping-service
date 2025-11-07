# shipping_service/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import httpx

app = FastAPI(title="Shipping Service")

# DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://localhost:8000")
DATABASE_SERVICE_URL = os.getenv("DATABASE_SERVICE_URL", "http://192.168.105.2:30000")
# If true, shipping will be simulated synchronously and status toggled to 'shipped' or 'failed'
PROCESS_SHIPPING_SYNC = os.getenv("PROCESS_SHIPPING_SYNC", "true").lower() != "false"

HTTPX_TIMEOUT = httpx.Timeout(30.0, connect=10.0)

class ShipmentIn(BaseModel):
    id: str
    order_id: str
    address: dict
    items: list
    status: str  # e.g. "created", "shipped", "failed"

class ShipmentOut(ShipmentIn):
    pass

async def db_request(method: str, path: str, json: Optional[dict] = None):
    url = f"{DATABASE_SERVICE_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as client:
            resp = await client.request(method, url, json=json)
    except httpx.ConnectTimeout:
        raise HTTPException(504, detail=f"Timeout connecting to database service at {url}")
    except httpx.ReadTimeout:
        raise HTTPException(504, detail=f"Timeout reading response from database service at {url}")
    except httpx.NetworkError as e:
        raise HTTPException(502, detail=f"Network error contacting database service at {url}: {e}")

    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise HTTPException(status_code=resp.status_code, detail=detail)

    return resp.json() if resp.content else {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Shipping Service"}

# Create shipment: persist to DB and optionally simulate shipping
@app.post("/shipments", response_model=ShipmentOut, status_code=201)
async def create_shipment(payload: ShipmentIn):
    # Persist to DB (idempotent behavior is handled by DB if id exists)
    await db_request("POST", "/shipments", json=payload.dict())

    # Optionally simulate shipping processing immediately
    if PROCESS_SHIPPING_SYNC:
        # Simple rule: if order_id contains "fail" or any other condition you choose, fail.
        # For realistic behaviour, replace this simulation with gateway API calls.
        should_fail = False
        # Example: if the address country is "FAIL" we simulate a failure (useful for tests)
        try:
            country = payload.address.get("country", "").upper()
            if country == "FAIL":
                should_fail = True
        except Exception:
            pass

        if should_fail:
            # Update DB to mark shipment failed
            payload_dict = payload.dict()
            payload_dict["status"] = "failed"
            await db_request("PUT", f"/shipments/{payload.id}", json=payload_dict)
            # Return HTTP error so caller (Order) can take compensating actions
            raise HTTPException(502, detail="Shipping provider reported failure for shipment")

        # Otherwise mark as shipped
        payload_dict = payload.dict()
        payload_dict["status"] = "shipped"
        await db_request("PUT", f"/shipments/{payload.id}", json=payload_dict)
        return payload_dict

    # If not simulating, return created record as-is (status stays as provided)
    return payload.dict()

# Proxy / wrapper endpoints that use the DB service underlying endpoints
@app.get("/shipments/{sid}", response_model=ShipmentOut)
async def get_shipment(sid: str):
    r = await db_request("GET", f"/shipments/{sid}")
    return r

@app.get("/shipments", response_model=List[ShipmentOut])
async def list_shipments():
    r = await db_request("GET", "/shipments")
    return r

@app.put("/shipments/{sid}", response_model=ShipmentOut)
async def update_shipment(sid: str, payload: ShipmentIn):
    await db_request("PUT", f"/shipments/{sid}", json=payload.dict())
    return payload.dict()

@app.delete("/shipments/{sid}", status_code=204)
async def delete_shipment(sid: str):
    await db_request("DELETE", f"/shipments/{sid}")
    return
