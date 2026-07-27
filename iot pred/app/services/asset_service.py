"""Asset service for asset management operations."""

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, ResourceNotFoundException
from app.models.asset import Asset
from app.repositories.asset_repository import AssetRepository
from app.schemas.asset_schema import AssetCreate, AssetUpdate


class AssetService:
    """Service for asset management operations."""

    def __init__(self, db: Session):
        """Initialize asset service with database session."""
        self.db = db
        self.asset_repository = AssetRepository(db)

    def create_asset(self, asset_data: AssetCreate) -> Asset:
        """Create a new asset.

        Args:
            asset_data: Asset creation data

        Returns:
            Created Asset object

        Raises:
            ConflictException: If asset_code already exists
        """
        # Business Rule 1: Check if asset_code already exists
        existing_asset = self.asset_repository.get_by_asset_code(
            asset_data.asset_code
        )
        if existing_asset:
            raise ConflictException(
                f"Asset code {asset_data.asset_code} already exists"
            )

        # Create asset ORM object
        asset = Asset(
            asset_code=asset_data.asset_code,
            asset_name=asset_data.asset_name,
            asset_type=asset_data.asset_type,
            location=asset_data.location,
            status=asset_data.status,
            manufacturer=asset_data.manufacturer,
            model_number=asset_data.model_number,
            installation_date=asset_data.installation_date,
        )

        # Save to database
        return self.asset_repository.create(asset)

    def get_asset(self, asset_id: int) -> Asset:
        """Get asset by id.

        Args:
            asset_id: Asset primary key

        Returns:
            Asset object

        Raises:
            ResourceNotFoundException: If asset not found
        """
        asset = self.asset_repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException(f"Asset with id {asset_id} not found")
        return asset

    def get_all_assets(self):
        """Get all assets.

        Returns:
            List of Asset objects (may be empty)
        """
        return self.asset_repository.get_all()

    def update_asset(self, asset_id: int, asset_data: AssetUpdate) -> Asset:
        """Update an existing asset.

        Args:
            asset_id: Asset primary key
            asset_data: Asset update data (only provided fields will be updated)

        Returns:
            Updated Asset object

        Raises:
            ResourceNotFoundException: If asset not found
        """
        # Business Rule 2: Verify asset exists before update
        asset = self.asset_repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException(f"Asset with id {asset_id} not found")

        # Business Rule 3: Check if new asset_code would conflict (if being updated)
        if asset_data.asset_code and asset_data.asset_code != asset.asset_code:
            existing_asset = self.asset_repository.get_by_asset_code(
                asset_data.asset_code
            )
            if existing_asset:
                raise ConflictException(
                    f"Asset code {asset_data.asset_code} already exists"
                )

        # Update only provided fields
        if asset_data.asset_code is not None:
            asset.asset_code = asset_data.asset_code
        if asset_data.asset_name is not None:
            asset.asset_name = asset_data.asset_name
        if asset_data.asset_type is not None:
            asset.asset_type = asset_data.asset_type
        if asset_data.location is not None:
            asset.location = asset_data.location
        if asset_data.status is not None:
            asset.status = asset_data.status
        if asset_data.manufacturer is not None:
            asset.manufacturer = asset_data.manufacturer
        if asset_data.model_number is not None:
            asset.model_number = asset_data.model_number
        if asset_data.installation_date is not None:
            asset.installation_date = asset_data.installation_date

        # Save to database
        return self.asset_repository.update(asset)

    def delete_asset(self, asset_id: int) -> None:
        """Delete an asset.

        Args:
            asset_id: Asset primary key

        Raises:
            ResourceNotFoundException: If asset not found
        """
        # Business Rule 4: Verify asset exists before delete
        asset = self.asset_repository.get_by_id(asset_id)
        if not asset:
            raise ResourceNotFoundException(f"Asset with id {asset_id} not found")

        # Delete from database
        self.asset_repository.delete(asset_id)
