# backend/live_bidding.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List
from app.db import get_db
from sqlalchemy.orm import Session
from app.models import Bid


router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/auctions/{auction_id}")
async def websocket_auction(
    websocket: WebSocket,
    auction_id: int,
    db: Session = Depends(get_db),
):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            # -------------------------
            # 1. BID LOGIC (correct)
            # -------------------------
            if data.get("type") == "bid":
                amount = data.get("amount")
                user_id = data.get("user_id")

                # Insert bid into DB
                new_bid = Bid(
                    auction_id=auction_id,
                    user_id=user_id,
                    amount=amount,
                )
                db.add(new_bid)
                db.commit()
                db.refresh(new_bid)

                # Broadcast bid to all clients
                await manager.broadcast({
                    "event": "bid",
                    "auction_id": auction_id,
                    "amount": new_bid.amount,
                    "user_id": new_bid.user_id,
                    "bid_id": new_bid.id,
                })

            # -------------------------
            # 2. AUCTIONEER CONTROL LOGIC (unchanged)
            # -------------------------
            elif data.get("type") in {"start", "pause", "resume", "end"}:
                await manager.broadcast({
                    "event": data["type"],
                    "auction_id": auction_id,
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)

