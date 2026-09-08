from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.item import ItemRead


class OutfitBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    occasion: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class OutfitCreate(OutfitBase):
    item_ids: list[str] = Field(default_factory=list)


class OutfitUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    occasion: str | None = Field(default=None, max_length=120)
    notes: str | None = None
    item_ids: list[str] | None = None


class OutfitRead(OutfitBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    items: list[ItemRead]


class OutfitSuggestRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=500)


class OutfitSuggestion(BaseModel):
    items: list[ItemRead]
    rationale: str
