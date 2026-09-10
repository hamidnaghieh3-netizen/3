from pydantic import BaseModel
from datetime import datetime

class AuctionCreate(BaseModel):
    title: str
    description: str
    start_time: datetime
    end_time: datetime
