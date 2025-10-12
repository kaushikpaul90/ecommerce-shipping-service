
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict
import uuid

app = FastAPI(title="Shipping Service")

class Shipment(BaseModel):
    id: str
    orderId: str
    address: dict
    items: list
    status: str  # created | picked | delivered

SHIPMENTS: Dict[str, Shipment] = {}

@app.get("/health")
def health():
    return {"status": "ok", "service": "Shipping Service"}

@app.post("/shipments", response_model=Shipment)
def create_shipment(payload: dict):
    sid = str(uuid.uuid4())
    sh = Shipment(id=sid, orderId=payload.get("orderId"), address=payload.get("address"), items=payload.get("items", []), status="created")
    SHIPMENTS[sid] = sh
    return sh

@app.get("/shipments/{sid}", response_model=Shipment)
def get_shipment(sid: str):
    return SHIPMENTS[sid]
