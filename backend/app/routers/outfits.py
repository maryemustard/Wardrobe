from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_db
from app.models.item import Item
from app.models.outfit import Outfit
from app.schemas.outfit import OutfitCreate, OutfitRead, OutfitUpdate
from app.security import require_auth

router = APIRouter(
    prefix="/api/outfits",
    tags=["outfits"],
    dependencies=[Depends(require_auth)],
)


def _items_for(db: Session, item_ids: list[str]) -> list[Item]:
    if not item_ids:
        return []
    found = db.execute(select(Item).where(Item.id.in_(item_ids))).scalars().all()
    by_id = {it.id: it for it in found}
    # keep the caller's order, drop ids that don't exist
    return [by_id[i] for i in item_ids if i in by_id]


@router.get("", response_model=list[OutfitRead])
def list_outfits(db: Session = Depends(get_db)) -> list[Outfit]:
    stmt = select(Outfit).order_by(Outfit.created_at.desc())
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=OutfitRead, status_code=status.HTTP_201_CREATED)
def create_outfit(payload: OutfitCreate, db: Session = Depends(get_db)) -> Outfit:
    data = payload.model_dump(exclude={"item_ids"})
    outfit = Outfit(**data)
    outfit.items = _items_for(db, payload.item_ids)
    db.add(outfit)
    db.commit()
    db.refresh(outfit)
    return outfit


@router.get("/{outfit_id}", response_model=OutfitRead)
def get_outfit(outfit_id: str, db: Session = Depends(get_db)) -> Outfit:
    outfit = db.get(Outfit, outfit_id)
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")
    return outfit


@router.patch("/{outfit_id}", response_model=OutfitRead)
def update_outfit(
    outfit_id: str, payload: OutfitUpdate, db: Session = Depends(get_db)
) -> Outfit:
    outfit = db.get(Outfit, outfit_id)
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")

    fields = payload.model_dump(exclude_unset=True)
    item_ids = fields.pop("item_ids", None)
    for field, value in fields.items():
        setattr(outfit, field, value)
    if item_ids is not None:
        outfit.items = _items_for(db, item_ids)

    db.commit()
    db.refresh(outfit)
    return outfit


@router.delete("/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_outfit(outfit_id: str, db: Session = Depends(get_db)) -> None:
    outfit = db.get(Outfit, outfit_id)
    if outfit is None:
        raise HTTPException(status_code=404, detail="Outfit not found")
    db.delete(outfit)
    db.commit()
