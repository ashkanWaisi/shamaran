from datetime import datetime

from pydantic import BaseModel


class MemoryRecord(BaseModel):
    id: int
    category: str
    content: str
    project: str | None
    created_at: datetime
    updated_at: datetime
