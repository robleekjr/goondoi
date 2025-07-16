from app import db
from datetime import datetime
import uuid
from app.models.qr_code import QRCode

class Story(db.Model):
    """Story model representing a complete story."""
    __tablename__ = 'stories'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationship to story segments
    segments = db.relationship('StorySegment', backref='story', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Story {self.title}>'
    
    def to_dict(self):
        """Convert story to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'segment_count': self.segments.count()
        }

class StorySegment(db.Model):
    """Story segment model representing individual parts of a story."""
    __tablename__ = 'story_segments'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = db.Column(db.String(36), db.ForeignKey('stories.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    order = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(256), nullable=True)  # Path to uploaded image
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # QR code relationship
    qr_code = db.relationship('QRCode', backref='segment', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<StorySegment {self.title}>'
    
    def to_dict(self):
        """Convert segment to dictionary."""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'title': self.title,
            'content': self.content,
            'order': self.order,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'qr_code_url': self.qr_code.qr_url if self.qr_code else None
        } 