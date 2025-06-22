import datetime
from sqlmodel import SQLModel, Field


class Transfer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tx_hash: str
    frm: str
    to: str
    value: str  # store as str to avoid overflow
    block_number: int
    timestamp: datetime.datetime
