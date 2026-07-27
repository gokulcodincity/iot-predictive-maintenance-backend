"""Asset API endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.asset_schema import AssetCreate, AssetResponse, AssetUpdate
from app.services.asset_service import AssetService

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    asset_data: AssetCreate, db: Session = Depends(get_db)
):
    """Create a new asset.

    Returns:
        HTTP 201 with created asset
        HTTP 409 if asset_code already exists
    """
    service = AssetService(db)
    return service.create_asset(asset_data)


@router.get("", response_model=list[AssetResponse])
async def list_assets(db: Session = Depends(get_db)):
    """Get all assets.

    Returns:
        HTTP 200 with list of assets (may be empty)
    """
    service = AssetService(db)
    return service.get_all_assets()


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(asset_id: int, db: Session = Depends(get_db)):
    """Get asset by id.

    Args:
        asset_id: Asset primary key

    Returns:
        HTTP 200 with asset
        HTTP 404 if asset not found
    """
    service = AssetService(db)
    return service.get_asset(asset_id)


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int, asset_data: AssetUpdate, db: Session = Depends(get_db)
):
    """Update an asset.

    Args:
        asset_id: Asset primary key
        asset_data: Asset update data (partial update)

    Returns:
        HTTP 200 with updated asset
        HTTP 404 if asset not found
        HTTP 409 if new asset_code conflicts
    """
    service = AssetService(db)
    return service.update_asset(asset_id, asset_data)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(asset_id: int, db: Session = Depends(get_db)):
    """Delete an asset.

    Args:
        asset_id: Asset primary key

    Returns:
        HTTP 204 No Content
        HTTP 404 if asset not found
    """
    service = AssetService(db)
    service.delete_asset(asset_id)
