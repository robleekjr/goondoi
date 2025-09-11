from datetime import datetime
from app import db

class Feedback(db.Model):
    """Feedback model for storing user feedback."""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    comments = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Feedback {self.id}: {self.name} ({self.email})>'
    
    def to_dict(self):
        """Convert feedback to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'comments': self.comments,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
