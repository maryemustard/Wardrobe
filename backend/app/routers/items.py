from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.item import Item
from app.schemas.item import ItemCreate, ItemRead, ItemUpdate
from app.security import require_auth

router = APIRouter(
    prefix="/api/items",
    tags=["items"],
    dependencies=[Depends(require_auth)],
)


@router.get("", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    category: str | None = None,
    season: str | None = None,
    brand: str | None = None,
    q: str | None = None,
    archived: bool = False,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> list[Item]:
    stmt = select(Item).where(Item.is_archived == archived)
    if category:
        stmt = stmt.where(Item.category == category)
    if season:
        stmt = stmt.where(Item.season == season)
    if brand:
        stmt = stmt.where(Item.brand == brand)
    if q:
        stmt = stmt.where(Item.name.ilike(f"%{q}%"))
    stmt = stmt.order_by(Item.created_at.desc()).limit(limit).offset(offset)
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> Item:
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model=ItemRead)
def get_item(item_id: str, db: Session = Depends(get_db)) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=ItemRead)
def update_item(item_id: str, payload: ItemUpdate, db: Session = Depends(get_db)) -> Item:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: str, db: Session = Depends(get_db)) -> None:
    item = db.get(Item, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
