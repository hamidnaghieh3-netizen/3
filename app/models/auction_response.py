from pydantic import BaseModel
from datetime import datetime

class Auction(BaseModel):
    id: int
    title: str
    description: str
    start_time: datetime
    end_time: datetime
    owner_id: int
