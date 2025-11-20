from app import db
from datetime import datetime

class FloraFaunaTileSettings(db.Model):
    """Settings for the Flora & Fauna tile on the homepage."""
    __tablename__ = 'flora_fauna_tile_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, default='Flora & Fauna')
    description = db.Column(db.Text, nullable=False, default='Discover the diverse wildlife and plant life of Goondoi Wetlands')
    page_blurb = db.Column(db.Text, nullable=True, default='Explore the rich biodiversity of our wetlands.')
    image_path = db.Column(db.String(256), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_settings():
        """Get the tile settings, creating default if none exist."""
        settings = FloraFaunaTileSettings.query.first()
        if not settings:
            settings = FloraFaunaTileSettings(
                title='Flora & Fauna',
                description='Discover the diverse wildlife and plant life of Goondoi Wetlands'
            )
            db.session.add(settings)
            db.session.commit()
        return settings
    
    def __repr__(self):
        return f'<FloraFaunaTileSettings {self.title}>'

