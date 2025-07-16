from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.services.story_service import StoryService
from app.services.qr_service import QRService
import os
from werkzeug.utils import secure_filename

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
        
        if not title:
            flash('Title is required', 'error')
            return render_template('admin/create_story.html')
        
        story = StoryService.create_story(title, description)
        flash(f'Story "{title}" created successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story.id))
    
    return render_template('admin/create_story.html')

@admin_bp.route('/stories/<story_id>/edit')
def edit_story(story_id):
    """Edit a story and its segments."""
    story = StoryService.get_story(story_id)
    if not story:
        flash('Story not found', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
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
                # Ensure the upload directory exists
                upload_dir = os.path.join('app', 'static', 'uploads', 'media')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Secure the filename and save the media
                filename = secure_filename(media.filename)
                # Add timestamp to avoid filename conflicts
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                
                media_path = os.path.join('uploads', 'media', filename)
                full_path = os.path.join('app', 'static', media_path)
                media.save(full_path)
        
        segment = StoryService.create_segment(
            story_id=story_id,
            title=title,
            content=content,
            order=order,
            image_path=media_path
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
        media_path = segment.image_path  # Keep existing media path by default
        if 'media' in request.files:
            media = request.files['media']
            if media and media.filename:
                # Ensure the upload directory exists
                upload_dir = os.path.join('app', 'static', 'uploads', 'media')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Secure the filename and save the media
                filename = secure_filename(media.filename)
                # Add timestamp to avoid filename conflicts
                import time
                timestamp = int(time.time())
                filename = f"{timestamp}_{filename}"
                
                media_path = os.path.join('uploads', 'media', filename)
                full_path = os.path.join('app', 'static', media_path)
                media.save(full_path)
        
        StoryService.update_segment(
            segment_id,
            title=title,
            content=content,
            order=order,
            image_path=media_path
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