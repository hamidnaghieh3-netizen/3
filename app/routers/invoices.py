from fastapi import APIRouter, HTTPException
from app.database import get_cursor

router = APIRouter(prefix="/invoices", tags=["Invoices"])


@router.get("/{invoice_id}")
def get_invoice(invoice_id: int):
    conn, cur = get_cursor()

    cur.execute(
        """
        SELECT id, lot_id, user_id, winning_bid, created_at
        FROM invoices
        WHERE id=%s
        """,
        (invoice_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found")

    return {
        "invoice_id": row[0],
        "lot_id": row[1],
        "user_id": row[2],
        "winning_bid": row[3],
        "created_at": row[4]
    }


@router.get("/lot/{lot_id}")
def get_invoice_by_lot(lot_id: int):
    conn, cur = get_cursor()

    cur.execute(
        """
        SELECT id, user_id, winning_bid, created_at
        FROM invoices
        WHERE lot_id=%s
        """,
        (lot_id,)
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Invoice not found for this lot")

    return {
        "invoice_id": row[0],
        "lot_id": lot_id,
        "user_id": row[1],
        "winning_bid": row[2],
        "created_at": row[3]
    }

