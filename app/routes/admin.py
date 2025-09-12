from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.story_service import StoryService
from app.services.qr_service import QRService
from app.models.feedback import Feedback
from app import db
import os
from werkzeug.utils import secure_filename
import boto3

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
def admin_dashboard():
    """Admin dashboard."""
    stories = StoryService.get_all_stories()
    # Get all segments for display in the dashboard
    segments = []
    for story in stories:
        segments.extend(StoryService.get_story_segments(story.id))
    return render_template('admin/dashboard.html', stories=stories, segments=segments)

@admin_bp.route('/stories/new', methods=['GET', 'POST'])
def create_story():
    """Create a new story."""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_position = request.form.get('image_position', 'center')
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/create_story.html')
        
        # Handle image upload
        image_path = None
        if 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                filename = secure_filename(image.filename)
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                if os.environ.get('AWS_S3_BUCKET'):
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                        region_name=os.environ.get('AWS_S3_REGION')
                    )
                    bucket = os.environ.get('AWS_S3_BUCKET')
                    s3.upload_fileobj(image, bucket, filename)
                    image_path = f"https://{bucket}.s3.{os.environ.get('AWS_S3_REGION')}.amazonaws.com/{filename}"
                else:
                    upload_dir = os.path.join('app', 'static', 'uploads', 'images')
                    os.makedirs(upload_dir, exist_ok=True)
                    image_path = f"uploads/images/{filename}"
                    full_path = os.path.join('app', 'static', image_path)
                    image.save(full_path)
        
        story = StoryService.create_story(title, description, image_path, image_position)
        flash(f'Story "{title}" created successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story.id))
    
    return render_template('admin/create_story.html')

@admin_bp.route('/stories/<story_id>/edit', methods=['GET', 'POST'])
def edit_story(story_id):
    """Edit a story and its segments."""
    story = StoryService.get_story(story_id)
    if not story:
        flash('Story not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        image_position = request.form.get('image_position', 'center')
        remove_image = request.form.get('remove_image') == 'on'
        
        if not title:
            flash('Title is required', 'error')
            return redirect(url_for('admin.edit_story', story_id=story_id))
        
        # Handle image upload/removal
        image_path = story.image_path  # Keep existing image by default
        
        if remove_image:
            # Remove existing image file if it exists
            if story.image_path:
                import os
                full_path = os.path.join('app', 'static', story.image_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
            image_path = None
        elif 'image' in request.files:
            image = request.files['image']
            if image and image.filename:
                # Remove old image if it exists
                if story.image_path:
                    import os
                    old_path = os.path.join('app', 'static', story.image_path)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                filename = secure_filename(image.filename)
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                if os.environ.get('AWS_S3_BUCKET'):
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                        region_name=os.environ.get('AWS_S3_REGION')
                    )
                    bucket = os.environ.get('AWS_S3_BUCKET')
                    s3.upload_fileobj(image, bucket, filename)
                    image_path = f"https://{bucket}.s3.{os.environ.get('AWS_S3_REGION')}.amazonaws.com/{filename}"
                else:
                    upload_dir = os.path.join('app', 'static', 'uploads', 'images')
                    os.makedirs(upload_dir, exist_ok=True)
                    image_path = f"uploads/images/{filename}"
                    full_path = os.path.join('app', 'static', image_path)
                    image.save(full_path)
        
        # Update the story
        StoryService.update_story(story_id, title=title, description=description, 
                                 image_path=image_path, image_position=image_position)
        flash('Story updated successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story_id))
    
    segments = StoryService.get_story_segments(story_id)
    return render_template('admin/edit_story.html', story=story, segments=segments)

@admin_bp.route('/stories/<story_id>/segments/new', methods=['GET', 'POST'])
def create_segment(story_id):
    """Create a new segment for a story."""
    story = StoryService.get_story(story_id)
    if not story:
        flash('Story not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        order = request.form.get('order')
        
        if not all([title, content, order]):
            flash('Title, content, and order are required', 'error')
            return render_template('admin/create_segment.html', story=story)
        
        try:
            order = int(order) if order else 0
        except ValueError:
            flash('Order must be a number', 'error')
            return render_template('admin/create_segment.html', story=story)
        
        # Handle media upload (image or video)
        media_path = None
        if 'media' in request.files:
            media = request.files['media']
            if media and media.filename:
                filename = secure_filename(media.filename)
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                if os.environ.get('AWS_S3_BUCKET'):
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                        region_name=os.environ.get('AWS_S3_REGION')
                    )
                    bucket = os.environ.get('AWS_S3_BUCKET')
                    s3.upload_fileobj(media, bucket, filename)
                    media_path = f"https://{bucket}.s3.{os.environ.get('AWS_S3_REGION')}.amazonaws.com/{filename}"
                else:
                    upload_dir = os.path.join('app', 'static', 'uploads', 'media')
                    os.makedirs(upload_dir, exist_ok=True)
                    media_path = f"uploads/media/{filename}"
                    full_path = os.path.join('app', 'static', media_path)
                    media.save(full_path)
        
        segment = StoryService.create_segment(
            story_id=story_id,
            title=title,
            content=content,
            order=order,
            media_path=media_path
        )
        
        flash(f'Segment "{title}" created successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story_id))
    
    return render_template('admin/create_segment.html', story=story)

@admin_bp.route('/segments/<segment_id>/edit', methods=['GET', 'POST'])
def edit_segment(segment_id):
    """Edit a story segment."""
    segment = StoryService.get_segment(segment_id)
    if not segment:
        flash('Segment not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    story = StoryService.get_story(segment.story_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        order = request.form.get('order')
        
        if not all([title, content, order]):
            flash('Title, content, and order are required', 'error')
            return render_template('admin/edit_segment.html', segment=segment, story=story)
        
        try:
            order = int(order) if order else 0
        except ValueError:
            flash('Order must be a number', 'error')
            return render_template('admin/edit_segment.html', segment=segment, story=story)
        
        # Handle media upload (image or video)
        media_path = segment.media_path  # Keep existing media path by default
        if 'media' in request.files:
            media = request.files['media']
            if media and media.filename:
                filename = secure_filename(media.filename)
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                if os.environ.get('AWS_S3_BUCKET'):
                    s3 = boto3.client(
                        's3',
                        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                        region_name=os.environ.get('AWS_S3_REGION')
                    )
                    bucket = os.environ.get('AWS_S3_BUCKET')
                    s3.upload_fileobj(media, bucket, filename)
                    media_path = f"https://{bucket}.s3.{os.environ.get('AWS_S3_REGION')}.amazonaws.com/{filename}"
                else:
                    upload_dir = os.path.join('app', 'static', 'uploads', 'media')
                    os.makedirs(upload_dir, exist_ok=True)
                    media_path = f"uploads/media/{filename}"
                    full_path = os.path.join('app', 'static', media_path)
                    media.save(full_path)
        
        StoryService.update_segment(
            segment_id,
            title=title,
            content=content,
            order=order,
            media_path=media_path
        )
        
        flash('Segment updated successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=segment.story_id))
    
    return render_template('admin/edit_segment.html', segment=segment, story=story)

@admin_bp.route('/story/<story_id>/delete', methods=['POST'])
def delete_story(story_id):
    """Delete a story and all its segments."""
    try:
        success = StoryService.delete_story(story_id)
        if success:
            flash('Story deleted successfully!', 'success')
        else:
            flash('Story not found or could not be deleted.', 'error')
    except Exception as e:
        flash(f'Error deleting story: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/segment/<segment_id>/delete', methods=['POST'])
def delete_segment(segment_id):
    """Delete a story segment."""
    try:
        success = StoryService.delete_segment(segment_id)
        if success:
            flash('Segment deleted successfully!', 'success')
        else:
            flash('Segment not found or could not be deleted.', 'error')
    except Exception as e:
        flash(f'Error deleting segment: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/feedback')
def view_feedback():
    """View all user feedback submissions."""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get feedback with pagination
    feedback_pagination = Feedback.query.order_by(Feedback.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get feedback statistics
    total_feedback = Feedback.query.count()
    recent_feedback = Feedback.query.filter(
        Feedback.created_at >= db.func.date('now', '-7 days')
    ).count()
    
    return render_template('admin/feedback.html', 
                         feedback_pagination=feedback_pagination,
                         total_feedback=total_feedback,
                         recent_feedback=recent_feedback)

@admin_bp.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete a feedback submission."""
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting feedback: {str(e)}', 'error')
    
    return redirect(url_for('admin.view_feedback')) 