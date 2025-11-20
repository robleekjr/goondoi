from app.models.flora_fauna import FloraFaunaItem
from app import db
from datetime import datetime
import os
import uuid

class FloraFaunaService:
    """Service class for managing Flora and Fauna data."""
    
    @staticmethod
    def get_all_items():
        """Get all active flora/fauna items."""
        return FloraFaunaItem.query.filter_by(is_active=True).order_by(FloraFaunaItem.name).all()
    
    @staticmethod
    def get_item_by_id(item_id):
        """Get a specific item by ID."""
        return FloraFaunaItem.query.filter_by(id=item_id, is_active=True).first()
    
    @staticmethod
    def create_item(name, description, image_path=None, short_description=None, conservation_status=None, fun_facts=None):
        """Create a new flora/fauna item."""
        item = FloraFaunaItem(
            name=name,
            short_description=short_description,
            description=description,
            image_path=image_path,
            conservation_status=conservation_status,
            fun_facts=fun_facts
        )
        db.session.add(item)
        db.session.commit()
        return item
    
    @staticmethod
    def update_item(item_id, **kwargs):
        """Update an existing item."""
        item = FloraFaunaItem.query.get(item_id)
        if not item:
            return None
        
        for key, value in kwargs.items():
            if hasattr(item, key):
                setattr(item, key, value)
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        return item
    
    @staticmethod
    def delete_item(item_id):
        """Delete an item (soft delete)."""
        item = FloraFaunaItem.query.get(item_id)
        if not item:
            return False
        
        item.is_active = False
        item.updated_at = datetime.utcnow()
        db.session.commit()
        return True
    
    @staticmethod
    def get_recent_items(limit=6):
        """Get recently added items for homepage display."""
        return FloraFaunaItem.query.filter_by(is_active=True).order_by(FloraFaunaItem.created_at.desc()).limit(limit).all()
