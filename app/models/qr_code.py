from app import db
from datetime import datetime
import uuid

class QRCode(db.Model):
    """QR Code model for story segments."""
    __tablename__ = 'qr_codes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    segment_id = db.Column(db.String(36), db.ForeignKey('story_segments.id'), nullable=False, unique=True)
    qr_url = db.Column(db.String(500), nullable=False)
    qr_image_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<QRCode {self.id}>'
    
    def to_dict(self):
        """Convert QR code to dictionary."""
        return {
            'id': self.id,
            'segment_id': self.segment_id,
            'qr_url': self.qr_url,
            'qr_image_path': self.qr_image_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active
        } 