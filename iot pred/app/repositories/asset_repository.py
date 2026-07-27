"""Asset repository for database operations."""

from sqlalchemy.orm import Session

from app.models.asset import Asset


class AssetRepository:
    """Repository for asset database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create(self, asset: Asset) -> Asset:
        """Create a new asset.

        Args:
            asset: Asset ORM object with values set

        Returns:
            Created Asset object with id and timestamps populated
        """
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_by_id(self, asset_id: int):
        """Get asset by primary key.

        Args:
            asset_id: Asset primary key

        Returns:
            Asset object or None if not found
        """
        return self.db.query(Asset).filter(Asset.id == asset_id).first()

    def get_by_asset_code(self, asset_code: str):
        """Get asset by unique business identifier.

        Args:
            asset_code: Unique asset code (e.g., 'PUMP-001')

        Returns:
            Asset object or None if not found
        """
        return self.db.query(Asset).filter(Asset.asset_code == asset_code).first()

    def get_all(self):
        """Get all assets.

        Returns:
            List of all Asset objects (may be empty)
        """
        return self.db.query(Asset).all()

    def update(self, asset: Asset) -> Asset:
        """Update an existing asset.

        Args:
            asset: Asset ORM object with updated values

        Returns:
            Updated Asset object
        """
        self.db.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def delete(self, asset_id: int) -> bool:
        """Delete an asset by id.

        Args:
            asset_id: Asset primary key to delete

        Returns:
            True if asset was deleted, False if not found
        """
        asset = self.get_by_id(asset_id)
        if asset:
            self.db.delete(asset)
            self.db.commit()
            return True
        return False
