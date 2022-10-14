from datetime import datetime

from sqlmodel import Field, SQLModel


class Price(SQLModel, table=True):
    id: int | None = Field(primary_key=True)
    symbol: str
    price: float
    extracted_time: datetime