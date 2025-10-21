from app import db
from datetime import datetime
import uuid

class FloraFaunaItem(db.Model):
    """Flora and Fauna item model (e.g., specific bird, tree, insect)."""
    __tablename__ = 'flora_fauna_items'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.String(200), nullable=True)  # For tiles/preview
    description = db.Column(db.Text, nullable=False)  # Full description
    image_path = db.Column(db.String(256), nullable=True)
    conservation_status = db.Column(db.String(50), nullable=True)  # e.g., "Least Concern", "Endangered"
    fun_facts = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<FloraFaunaItem {self.name}>'
    
    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'short_description': self.short_description,
            'description': self.description,
            'image_path': self.image_path,
            'conservation_status': self.conservation_status,
            'fun_facts': self.fun_facts,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        }
