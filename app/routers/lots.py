from fastapi import APIRouter, HTTPException, UploadFile, File
from app.database import get_cursor
from app.models.lot import LotCreate, LotUpdate

import os

lots_router = APIRouter(prefix="/lots", tags=["Lots"])

# -----------------------------
# 1. CREATE LOT
# -----------------------------
@lots_router.post("/create")
def create_lot(lot: LotCreate):
    conn, cur = get_cursor()

    # Check auction exists
    cur.execute("SELECT id FROM auctions WHERE id=%s", (lot.auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    # Insert lot
    cur.execute(
        """
        INSERT INTO lots (
            auction_id, title, description, starting_bid,
            estimate_low, estimate_high, reserve_price, image_url
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        RETURNING id
        """,
        (
            lot.auction_id,
            lot.title,
            lot.description,
            lot.starting_bid,
            lot.estimate_low,
            lot.estimate_high,
            lot.reserve_price,
            lot.image_url
        )
    )

    lot_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "message": "Lot created",
        "lot_id": lot_id,
        "auction_id": lot.auction_id,
        "title": lot.title
    }

# -----------------------------
# 2. UPLOAD LOT IMAGE  ← PLACE IT HERE
# -----------------------------
UPLOAD_DIR = "app/static/lot_images"

@lots_router.post("/upload-image/{lot_id}")
def upload_lot_image(lot_id: int, file: UploadFile = File(...)):
    # Validate file type
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only JPG/PNG images allowed")

    # Ensure lot exists
    conn, cur = get_cursor()
    cur.execute("SELECT id FROM lots WHERE id=%s", (lot_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lot not found")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Update DB
    image_url = f"/static/lot_images/{file.filename}"
    cur.execute(
        "UPDATE lots SET image_url=%s WHERE id=%s",
        (image_url, lot_id)
    )
    conn.commit()
    conn.close()

    return {
        "message": "Image uploaded",
        "lot_id": lot_id,
        "image_url": image_url
    }
@lots_router.get("/auction/{auction_id}")
def list_lots_in_auction(auction_id: int):
    conn, cur = get_cursor()

    # Check auction exists
    cur.execute("SELECT id FROM auctions WHERE id=%s", (auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    # Fetch lots
    cur.execute(
        """
        SELECT id, title, description, starting_bid,
               estimate_low, estimate_high, reserve_price,
               image_url, created_at
        FROM lots
        WHERE auction_id=%s
        ORDER BY id ASC
        """,
        (auction_id,)
    )

    lots = cur.fetchall()
    conn.close()

    # Format response
    return {
        "auction_id": auction_id,
        "count": len(lots),
        "lots": [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "starting_bid": row[3],
                "estimate_low": row[4],
                "estimate_high": row[5],
                "reserve_price": row[6],
                "image_url": row[7],
                "created_at": row[8]
            }
            for row in lots
        ]
    }
@lots_router.get("/{lot_id}")
def get_lot_details(lot_id: int):
    conn, cur = get_cursor()

    # Fetch lot
    cur.execute(
        """
        SELECT id, auction_id, title, description, starting_bid,
               estimate_low, estimate_high, reserve_price,
               image_url, created_at
        FROM lots
        WHERE id=%s
        """,
        (lot_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Lot not found")

    # Format response
    return {
        "id": row[0],
        "auction_id": row[1],
        "title": row[2],
        "description": row[3],
        "starting_bid": row[4],
        "estimate_low": row[5],
        "estimate_high": row[6],
        "reserve_price": row[7],
        "image_url": row[8],
        "created_at": row[9]
    }
@lots_router.put("/edit/{lot_id}")
def edit_lot(lot_id: int, lot: LotUpdate):
    conn, cur = get_cursor()

    # Check lot exists
    cur.execute("SELECT id FROM lots WHERE id=%s", (lot_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lot not found")

    # Build dynamic update query
    fields = []
    values = []

    if lot.title is not None:
        fields.append("title=%s")
        values.append(lot.title)

    if lot.description is not None:
        fields.append("description=%s")
        values.append(lot.description)

    if lot.starting_bid is not None:
        fields.append("starting_bid=%s")
        values.append(lot.starting_bid)

    if lot.estimate_low is not None:
        fields.append("estimate_low=%s")
        values.append(lot.estimate_low)

    if lot.estimate_high is not None:
        fields.append("estimate_high=%s")
        values.append(lot.estimate_high)

    if lot.reserve_price is not None:
        fields.append("reserve_price=%s")
        values.append(lot.reserve_price)

    if lot.image_url is not None:
        fields.append("image_url=%s")
        values.append(lot.image_url)

    if not fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    # Final SQL
    sql = f"UPDATE lots SET {', '.join(fields)} WHERE id=%s"
    values.append(lot_id)

    cur.execute(sql, tuple(values))
    conn.commit()
    conn.close()

    return {
        "message": "Lot updated",
        "lot_id": lot_id,
        "updated_fields": fields
    }
@lots_router.delete("/delete/{lot_id}")
def delete_lot(lot_id: int):
    conn, cur = get_cursor()

    # Check lot exists
    cur.execute("SELECT id FROM lots WHERE id=%s", (lot_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lot not found")

    # Delete lot
    cur.execute("DELETE FROM lots WHERE id=%s", (lot_id,))
    conn.commit()
    conn.close()

    return {
        "message": "Lot deleted",
        "lot_id": lot_id
    }
UPLOAD_DIR_MULTI = "app/static/lot_images_multi"

@lots_router.post("/upload-images/{lot_id}")
def upload_multiple_images(lot_id: int, files: list[UploadFile] = File(...)):
    conn, cur = get_cursor()

    # Check lot exists
    cur.execute("SELECT id FROM lots WHERE id=%s", (lot_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lot not found")

    os.makedirs(UPLOAD_DIR_MULTI, exist_ok=True)

    saved_images = []

    for file in files:
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            raise HTTPException(status_code=400, detail="Only JPG/PNG allowed")

        file_path = os.path.join(UPLOAD_DIR_MULTI, file.filename)

        with open(file_path, "wb") as f:
            f.write(file.file.read())

        image_url = f"/static/lot_images_multi/{file.filename}"

        cur.execute(
            "INSERT INTO lot_images (lot_id, image_url) VALUES (%s, %s)",
            (lot_id, image_url)
        )

        saved_images.append(image_url)

    conn.commit()
    conn.close()

    return {
        "message": "Images uploaded",
        "lot_id": lot_id,
        "images": saved_images
    }
# 8) PLACE BID ON LOT
@lots_router.post("/bid/{lot_id}")
def place_bid(lot_id: int, amount: float, user_id: int):
    conn, cur = get_cursor()

    # Check lot exists
    cur.execute("SELECT id FROM lots WHERE id=%s", (lot_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Lot not found")

    # Get current highest bid
    cur.execute("SELECT MAX(amount) FROM bids WHERE lot_id=%s", (lot_id,))
    highest = cur.fetchone()[0] or 0

    if amount <= highest:
        raise HTTPException(status_code=400, detail="Bid must be higher than current highest")

    # Insert bid
    cur.execute(
        """
        INSERT INTO bids (lot_id, user_id, amount)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (lot_id, user_id, amount)
    )

    bid_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "message": "Bid placed",
        "bid_id": bid_id,
        "lot_id": lot_id,
        "amount": amount
    }


# 9) GET HIGHEST BID
@lots_router.get("/highest-bid/{lot_id}")
def get_highest_bid(lot_id: int):
    conn, cur = get_cursor()

    cur.execute("SELECT MAX(amount) FROM bids WHERE lot_id=%s", (lot_id,))
    highest = cur.fetchone()[0]

    conn.close()

    return {
        "lot_id": lot_id,
        "highest_bid": highest or 0
    }


# 10) BID HISTORY
@lots_router.get("/bid-history/{lot_id}")
def bid_history(lot_id: int):
    conn, cur = get_cursor()

    cur.execute(
        """
        SELECT id, user_id, amount, created_at
        FROM bids
        WHERE lot_id=%s
        ORDER BY amount DESC
        """,
        (lot_id,)
    )

    rows = cur.fetchall()
    conn.close()

    return {
        "lot_id": lot_id,
        "count": len(rows),
        "bids": [
            {
                "bid_id": r[0],
                "user_id": r[1],
                "amount": r[2],
                "created_at": r[3]
            }
            for r in rows
        ]
    }
@lots_router.post("/close/{lot_id}")
def close_lot(lot_id: int):
    conn, cur = get_cursor()

    # Check lot exists
    cur.execute("SELECT status FROM lots WHERE id=%s", (lot_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Lot not found")

    if row[0] == "closed":
        raise HTTPException(status_code=400, detail="Lot already closed")

    # Get highest bid
    cur.execute(
        """
        SELECT user_id, amount
        FROM bids
        WHERE lot_id=%s
        ORDER BY amount DESC
        LIMIT 1
        """,
        (lot_id,)
    )
    highest = cur.fetchone()

    if not highest:
        # No bids → lot passed
        cur.execute("UPDATE lots SET status='passed' WHERE id=%s", (lot_id,))
        conn.commit()
        conn.close()
        return {
            "lot_id": lot_id,
            "status": "passed",
            "message": "No bids placed. Lot marked as passed."
        }

    winner_user_id = highest[0]
    winning_amount = highest[1]

    # Mark lot as sold
    cur.execute(
        "UPDATE lots SET status='sold' WHERE id=%s",
        (lot_id,)
    )

    # Create invoice
    cur.execute(
        """
        INSERT INTO invoices (lot_id, user_id, winning_bid)
        VALUES (%s, %s, %s)
        RETURNING id
        """,
        (lot_id, winner_user_id, winning_amount)
    )

    invoice_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "message": "Lot closed and invoice generated",
        "lot_id": lot_id,
        "invoice_id": invoice_id,
        "winner_user_id": winner_user_id,
        "winning_bid": winning_amount
    }

