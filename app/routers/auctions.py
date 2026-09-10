from fastapi import APIRouter, Depends, HTTPException
from app.models.auction import AuctionCreate
from app.auth_dependency import get_current_user
from app.database import get_cursor
from app.models.auction_response import Auction

router = APIRouter(prefix="/auctions", tags=["Auctions"])

@router.get("/", response_model=list[Auction])

def list_auctions():
    conn, cur = get_cursor()
    cur.execute("SELECT id, title, description, start_time, end_time, owner_id FROM auctions")
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "start_time": r[3],
            "end_time": r[4],
            "owner_id": r[5]
        }
        for r in rows
    ]

@router.get("/my", response_model=list[Auction])

def my_auction(user_id: int = Depends(get_current_user)):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT id, title, description, start_time, end_time, owner_id FROM auctions WHERE owner_id=%s",
        (user_id,)
    )
    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": r[0],
            "title": r[1],
            "description": r[2],
            "start_time": r[3],
            "end_time": r[4],
            "owner_id": r[5]
        }
        for r in rows
    ]

@router.get("/{auction_id}", response_model=Auction)

def get_auction(auction_id: int):
    conn, cur = get_cursor()
    cur.execute(
        "SELECT id, title, description, start_time, end_time, owner_id FROM auctions WHERE id=%s",
        (auction_id,)
    )
    auction = cur.fetchone()
    conn.close()

    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    return {
        "id": auction[0],
        "title": auction[1],
        "description": auction[2],
        "start_time": auction[3],
        "end_time": auction[4],
        "owner_id": auction[5]
    }

@router.post("/create")
def create_auction(auction: AuctionCreate, user_id: int = Depends(get_current_user)):
    conn, cur = get_cursor()

    cur.execute(
        "INSERT INTO auctions (title, description, start_time, end_time, owner_id) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING id",
        (auction.title, auction.description, auction.start_time, auction.end_time, user_id)
    )
    auction_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {
        "message": "Auction created",
        "auction_id": auction_id,
        "data": auction,
        "owner_id": user_id
    }
@router.put("/schedule/{auction_id}")
def schedule_auction(auction_id: int, start_time: str, end_time: str):
    conn, cur = get_cursor()

    cur.execute("SELECT id FROM auctions WHERE id=%s", (auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    cur.execute(
        """
        UPDATE auctions
        SET start_time=%s, end_time=%s, status='scheduled'
        WHERE id=%s
        """,
        (start_time, end_time, auction_id)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Auction scheduled",
        "auction_id": auction_id,
        "start_time": start_time,
        "end_time": end_time
    }
@router.put("/schedule/{auction_id}")
def schedule_auction(auction_id: int, start_time: str, end_time: str):
    conn, cur = get_cursor()

    cur.execute("SELECT id FROM auctions WHERE id=%s", (auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    cur.execute(
        """
        UPDATE auctions
        SET start_time=%s, end_time=%s, status='scheduled'
        WHERE id=%s
        """,
        (start_time, end_time, auction_id)
    )

    conn.commit()
    conn.close()

    return {
        "message": "Auction scheduled",
        "auction_id": auction_id,
        "start_time": start_time,
        "end_time": end_time
    }


@router.post("/start/{auction_id}")
def start_auction(auction_id: int):
    conn, cur = get_cursor()

    cur.execute("SELECT id FROM auctions WHERE id=%s", (auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    cur.execute(
        "UPDATE auctions SET status='live' WHERE id=%s",
        (auction_id,)
    )

    conn.commit()
    conn.close()

    return {"message": "Auction started", "auction_id": auction_id}


@router.post("/end/{auction_id}")
def end_auction(auction_id: int):
    conn, cur = get_cursor()

    cur.execute("SELECT id FROM auctions WHERE id=%s", (auction_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Auction not found")

    cur.execute(
        "UPDATE auctions SET status='ended' WHERE id=%s",
        (auction_id,)
    )

    conn.commit()
    conn.close()

    return {"message": "Auction ended", "auction_id": auction_id}









