from pydantic import BaseModel
from typing import Optional

class LotCreate(BaseModel):
    auction_id: int
    title: str
    description: Optional[str] = None
    starting_bid: float = 0
    estimate_low: Optional[float] = None
    estimate_high: Optional[float] = None
    reserve_price: Optional[float] = None
    image_url: Optional[str] = None
class LotUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    starting_bid: Optional[float] = None
    estimate_low: Optional[float] = None
    estimate_high: Optional[float] = None
    reserve_price: Optional[float] = None
    image_url: Optional[str] = None
