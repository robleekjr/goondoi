import qrcode
import os
from app import db
from app.models.qr_code import QRCode
from flask import current_app, request

class QRService:
    """Service for QR code generation and management."""
    
    @staticmethod
    def generate_qr_code(data, filename=None):
        """Generate a QR code image from data."""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.ERROR_CORRECT_L,
                box_size=current_app.config['QR_CODE_SIZE'],
                border=current_app.config['QR_CODE_BORDER']
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            if filename:
                upload_path = current_app.config['UPLOAD_FOLDER']
                # Ensure upload directory exists
                os.makedirs(upload_path, exist_ok=True)
                file_path = os.path.join(upload_path, filename)
                img.save(file_path)
                return file_path
            
            return img
        except Exception as e:
            print(f"Error generating QR code: {e}")
            return None
    
    @staticmethod
    def create_qr_for_segment(segment_id, base_url=None):
        """Create QR code for a story segment."""
        try:
            if base_url is None:
                base_url = request.host_url.rstrip('/')
            
            # Get segment and story information for filename
            from app.models.story import StorySegment
            segment = StorySegment.query.get(segment_id)
            if not segment:
                print(f"Segment {segment_id} not found")
                return None
            
            story = segment.story
            if not story:
                print(f"Story not found for segment {segment_id}")
                return None
            
            # Generate the URL for the segment
            segment_url = f"{base_url}/story/segment/{segment_id}"
            
            # Create descriptive filename with story title and segment number
            story_title_safe = "".join(c for c in story.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            story_title_safe = story_title_safe.replace(' ', '_')
            filename = f"qr_{story_title_safe}_segment_{segment.order}_{segment_id}.png"
            
            qr_path = QRService.generate_qr_code(segment_url, filename)
            
            if qr_path is None:
                print(f"Failed to generate QR code for segment {segment_id}")
                return None
            
            # Check if QR code already exists
            existing_qr = QRCode.query.filter_by(segment_id=segment_id).first()
            if existing_qr:
                # Update existing QR code
                existing_qr.qr_url = segment_url
                existing_qr.qr_image_path = qr_path
                db.session.commit()
                print(f"Updated QR code for segment {segment_id}")
                return existing_qr
            
            # Create new QR code record
            qr_code = QRCode(
                segment_id=segment_id,
                qr_url=segment_url,
                qr_image_path=qr_path
            )
            
            db.session.add(qr_code)
            db.session.commit()
            print(f"Created QR code for segment {segment_id}")
            return qr_code
            
        except Exception as e:
            print(f"Error creating QR code for segment {segment_id}: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_qr_code(segment_id):
        """Get QR code for a segment."""
        return QRCode.query.filter_by(segment_id=segment_id, is_active=True).first()
    
    @staticmethod
    def delete_qr_code(segment_id):
        """Delete QR code for a segment."""
        qr_code = QRService.get_qr_code(segment_id)
        if qr_code:
            # Delete the image file
            if qr_code.qr_image_path and os.path.exists(qr_code.qr_image_path):
                os.remove(qr_code.qr_image_path)
            
            # Delete from database
            db.session.delete(qr_code)
            db.session.commit() 