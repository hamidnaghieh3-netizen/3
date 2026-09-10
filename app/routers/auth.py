from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from app.models.user import UserCreate, UserLogin
from app.database import get_cursor
from app.auth_utils import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate):
    conn, cur = get_cursor()

    # Check if user exists
    cur.execute("SELECT id FROM users WHERE email=%s", (user.email,))
    existing = cur.fetchone()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user.password)

    cur.execute(
        "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s) RETURNING id",
        (user.email, hashed, "bidder")
    )
    user_id = cur.fetchone()[0]
    conn.commit()
    conn.close()

    return {"message": "User registered", "user_id": user_id}


@router.post("/login", response_class=PlainTextResponse)
def login(user: UserLogin):
    conn, cur = get_cursor()

    cur.execute("SELECT id, password_hash FROM users WHERE email=%s", (user.email,))
    db_user = cur.fetchone()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    user_id, password_hash = db_user

    if not verify_password(user.password, password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": str(user_id)})

    conn.close()

    # ⭐ FIX: return raw token with NO quotes, NO JSON
    return token

