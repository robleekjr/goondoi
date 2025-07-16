from app import db
from app.models.story import Story, StorySegment
from app.models.qr_code import QRCode
from app.services.qr_service import QRService
from flask import current_app, request
from sqlalchemy.orm import joinedload

class StoryService:
    """Service for story and segment management."""
    
    @staticmethod
    def create_story(title, description=None):
        """Create a new story."""
        story = Story(
            title=title,
            description=description
        )
        
        db.session.add(story)
        db.session.commit()
        
        return story
    
    @staticmethod
    def get_story(story_id):
        """Get a story by ID."""
        return Story.query.filter_by(id=story_id, is_active=True).first()
    
    @staticmethod
    def get_all_stories():
        """Get all active stories."""
        return Story.query.filter_by(is_active=True).order_by(Story.created_at.desc()).all()
    
    @staticmethod
    def create_segment(story_id, title, content, order, image_path=None):
        """Create a new story segment."""
        try:
            segment = StorySegment(
                story_id=story_id,
                title=title,
                content=content,
                order=order,
                image_path=image_path
            )
            
            db.session.add(segment)
            db.session.commit()
            
            print(f"Created segment {segment.id} for story {story_id}")
            
            # Generate QR code for the segment
            base_url = request.host_url.rstrip('/')
            qr_code = QRService.create_qr_for_segment(segment.id, base_url)
            
            if qr_code:
                print(f"QR code created successfully for segment {segment.id}")
            else:
                print(f"Failed to create QR code for segment {segment.id}")
            
            return segment
            
        except Exception as e:
            print(f"Error creating segment: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_segment(segment_id):
        """Get a story segment by ID, eager loading QR code."""
        return StorySegment.query.options(joinedload(StorySegment.qr_code.property)).filter_by(id=segment_id, is_active=True).first()
    
    @staticmethod
    def get_story_segments(story_id):
        """Get all segments for a story, eager loading QR codes."""
        return StorySegment.query.options(joinedload(StorySegment.qr_code.property)).filter_by(
            story_id=story_id, 
            is_active=True
        ).order_by(StorySegment.order).all()
    
    @staticmethod
    def update_segment(segment_id, **kwargs):
        """Update a story segment."""
        segment = StoryService.get_segment(segment_id)
        if segment:
            for key, value in kwargs.items():
                if hasattr(segment, key):
                    setattr(segment, key, value)
            
            db.session.commit()
            return segment
        return None
    
    @staticmethod
    def delete_segment(segment_id):
        """Delete a story segment."""
        segment = StoryService.get_segment(segment_id)
        if segment:
            try:
                # Delete associated QR code
                QRService.delete_qr_code(segment_id)
                
                # Delete segment media file if it exists
                if segment.image_path:
                    import os
                    media_path = os.path.join('app', 'static', segment.image_path)
                    if os.path.exists(media_path):
                        os.remove(media_path)
                        print(f"Deleted segment media: {media_path}")
                
                # Delete segment from database
                db.session.delete(segment)
                db.session.commit()
                
                print(f"Successfully deleted segment {segment_id} and all associated files")
                return True
                
            except Exception as e:
                print(f"Error deleting segment {segment_id}: {e}")
                db.session.rollback()
                return False
        return False
    
    @staticmethod
    def delete_story(story_id):
        """Delete a story and all its segments."""
        story = StoryService.get_story(story_id)
        if story:
            try:
                # Delete all segments and their QR codes
                for segment in story.segments:
                    # Delete QR code file and database record
                    QRService.delete_qr_code(segment.id)
                    
                    # Delete segment media file if it exists
                    if segment.image_path:
                        import os
                        media_path = os.path.join('app', 'static', segment.image_path)
                        if os.path.exists(media_path):
                            os.remove(media_path)
                            print(f"Deleted segment media: {media_path}")
                    
                    # Delete segment from database
                    db.session.delete(segment)
                
                # Delete story
                db.session.delete(story)
                db.session.commit()
                
                print(f"Successfully deleted story {story_id} and all associated files")
                return True
                
            except Exception as e:
                print(f"Error deleting story {story_id}: {e}")
                db.session.rollback()
                return False
        return False 