from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory, redirect, url_for, flash
from app.services.story_service import StoryService
from app.models.story import Story, StorySegment
from app.models.feedback import Feedback
from app import db
import os

main_bp = Blueprint('main', __name__)

@main_bp.app_template_filter('image_url')
def image_url(image_path):
    """Convert image path to full URL, handling both local and S3 paths."""
    if not image_path:
        return None
    if image_path.startswith('http'):
        return image_path
    return url_for('static', filename=image_path)

@main_bp.route('/')
def index():
    """Home page showing available stories."""
    stories = StoryService.get_all_stories()
    return render_template('index.html', stories=stories)

@main_bp.route('/story/<story_id>')
def view_story(story_id):
    """View a specific story."""
    story = StoryService.get_story(story_id)
    if not story:
        return render_template('404.html'), 404
    
    segments = StoryService.get_story_segments(story_id)
    
    # Get current segment from query parameter or default to first segment
    current_segment_id = request.args.get('segment')
    fullscreen_requested = request.args.get('fullscreen') == 'true'
    current_segment = None
    
    if current_segment_id:
        current_segment = StoryService.get_segment(current_segment_id)
        if not current_segment or current_segment.story_id != story_id:
            current_segment = None
    
    # If fullscreen is requested and no specific segment, use the first segment
    if fullscreen_requested and not current_segment and segments:
        current_segment = segments[0]
    # If no current segment specified, use the first one
    elif not current_segment and segments:
        current_segment = segments[0]
    
    return render_template('story.html', 
                         story=story, 
                         segments=segments, 
                         current_segment=current_segment)

@main_bp.route('/story/segment/<segment_id>')
def view_segment(segment_id):
    """View a specific story segment (accessed via QR code)."""
    print(f"Attempting to view segment: {segment_id}")
    
    segment = StoryService.get_segment(segment_id)
    if not segment:
        print(f"Segment not found: {segment_id}")
        return render_template('404.html'), 404
    
    print(f"Found segment: {segment.title} for story: {segment.story_id}")
    
    story = StoryService.get_story(segment.story_id)
    if not story:
        print(f"Story not found for segment: {segment.story_id}")
        return render_template('404.html'), 404
    
    print(f"Found story: {story.title}")
    print(f"Segment content: {segment.content[:100]}...")
    
    # Redirect to full-screen story experience with current segment
    return redirect(url_for('main.view_story', story_id=story.id, segment=segment_id))

@main_bp.route('/qr/<segment_id>')
def get_qr_code(segment_id):
    """Get QR code image for a segment."""
    from app.services.qr_service import QRService
    
    try:
        qr_code = QRService.get_qr_code(segment_id)
        if not qr_code:
            print(f"QR code not found for segment {segment_id}")
            return jsonify({'error': 'QR code not found'}), 404
        
        if not qr_code.qr_image_path:
            print(f"QR code image path is None for segment {segment_id}")
            return jsonify({'error': 'QR code image path not found'}), 404
        
        # Check if file exists
        if not os.path.exists(qr_code.qr_image_path):
            print(f"QR code file does not exist: {qr_code.qr_image_path}")
            return jsonify({'error': 'QR code file not found'}), 404
        
        # Get directory and filename using absolute paths
        upload_dir = os.path.abspath(current_app.config['UPLOAD_FOLDER'])
        filename = os.path.basename(qr_code.qr_image_path)
        
        print(f"Serving QR code: {filename} from {upload_dir}")
        return send_from_directory(upload_dir, filename)
        
    except Exception as e:
        print(f"Error serving QR code for segment {segment_id}: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@main_bp.route('/camera-test')
def camera_test():
    """Camera test page for troubleshooting."""
    return render_template('camera_test.html')

@main_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback page for user comments and suggestions."""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            comments = request.form.get('comments', '').strip()
            
            # Basic validation
            if not name or not email or not comments:
                flash('Please fill in all fields.', 'error')
                return render_template('feedback.html')
            
            if len(name) > 100:
                flash('Name must be 100 characters or less.', 'error')
                return render_template('feedback.html')
            
            if len(email) > 120:
                flash('Email must be 120 characters or less.', 'error')
                return render_template('feedback.html')
            
            # Create new feedback entry
            feedback_entry = Feedback(
                name=name,
                email=email,
                comments=comments
            )
            
            db.session.add(feedback_entry)
            db.session.commit()
            
            flash('Thank you for your feedback! We appreciate your input.', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error saving feedback: {e}")
            flash('An error occurred while saving your feedback. Please try again.', 'error')
            return render_template('feedback.html')
    
    return render_template('feedback.html') 