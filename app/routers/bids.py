from fastapi import APIRouter, Depends, HTTPException
from app.auth_dependency import get_current_user
from app.database import get_cursor
from datetime import datetime, timezone
router = APIRouter(prefix="/bids", tags=["Bids"])

bids_router = APIRouter(prefix="/bids", tags=["Bids"])

@bids_router.post("/create")
def place_bid(auction_id: int, amount: float, user_id: int = Depends(get_current_user)):
    conn, cur = get_cursor()

    # 1. Check auction exists
    cur.execute("SELECT id, end_time FROM auctions WHERE id=%s", (auction_id,))
    auction = cur.fetchone()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    auction_id_db, end_time = auction

    # 2. Check auction is still open
    cur.execute("SELECT NOW()")
    now = cur.fetchone()[0]
    end_time = end_time.replace(tzinfo=timezone.utc)

    if now > end_time:
        raise HTTPException(status_code=400, detail="Auction has ended")

    # 3. Get current highest bid
    cur.execute(
        "SELECT amount FROM bids WHERE auction_id=%s ORDER BY amount DESC LIMIT 1",
        (auction_id,)
    )
    highest = cur.fetchone()
    highest_amount = highest[0] if highest else 0

    # 4. Validate bid amount
    if amount <= highest_amount:
        raise HTTPException(
            status_code=400,
            detail=f"Bid must be higher than current highest ({highest_amount})"
        )

    # 5. Insert bid
    cur.execute(
        "INSERT INTO bids (auction_id, user_id, amount) VALUES (%s, %s, %s) RETURNING id",
        (auction_id, user_id, amount)
    )
    bid_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "message": "Bid placed",
        "bid_id": bid_id,
        "auction_id": auction_id,
        "user_id": user_id,
        "amount": amount
    }
@router.get("/user/{user_id}")
def get_user_bids(user_id: int):
    conn, cur = get_cursor()

    cur.execute(
        """
        SELECT lot_id, amount, created_at
        FROM bids
        WHERE user_id=%s
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return {
        "user_id": user_id,
        "count": len(rows),
        "bids": [
            {"lot_id": r[0], "amount": r[1], "created_at": r[2]}
            for r in rows
        ]
    }


