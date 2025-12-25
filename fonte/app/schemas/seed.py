from datetime import datetime

from pydantic import BaseModel


class SeedRequest(BaseModel):
    start_date: datetime
    days: int = 10
