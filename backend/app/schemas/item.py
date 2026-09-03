from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Category = Literal["top", "bottom", "dress", "outerwear", "shoes", "accessory"]
Season = Literal["spring", "summer", "fall", "winter", "all"]


class ItemBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    category: Category
    color: str | None = Field(default=None, max_length=60)
    brand: str | None = Field(default=None, max_length=120)
    size: str | None = Field(default=None, max_length=40)
    season: Season | None = None
    material: str | None = Field(default=None, max_length=120)
    purchase_date: date | None = None
    price: float | None = Field(default=None, ge=0)
    notes: str | None = None
    image_url: str | None = None
    image_public_id: str | None = Field(default=None, max_length=200)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: Category | None = None
    color: str | None = Field(default=None, max_length=60)
    brand: str | None = Field(default=None, max_length=120)
    size: str | None = Field(default=None, max_length=40)
    season: Season | None = None
    material: str | None = Field(default=None, max_length=120)
    purchase_date: date | None = None
    price: float | None = Field(default=None, ge=0)
    notes: str | None = None
    image_url: str | None = None
    image_public_id: str | None = Field(default=None, max_length=200)
    is_archived: bool | None = None


class ItemRead(ItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    is_archived: bool
    created_at: datetime
    updated_at: datetime
