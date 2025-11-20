from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.services.story_service import StoryService
from app.services.qr_service import QRService
from app.services.flora_fauna_service import FloraFaunaService
from app.models.feedback import Feedback
from app.models.user import User
from app.models.flora_fauna_settings import FloraFaunaTileSettings
from app import db
import os
import time
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
try:
    import boto3
except ImportError:
    boto3 = None

admin_bp = Blueprint('admin', __name__)

def get_s3_url(bucket, key, region=None):
    """Get S3 URL for an object, using actual bucket region."""
    if not region:
        # Get actual bucket region
        try:
            if boto3:
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                )
                location = s3_client.get_bucket_location(Bucket=bucket)
                region = location.get('LocationConstraint')
                # None means us-east-1
                if region is None:
                    region = 'us-east-1'
            else:
                region = os.environ.get('AWS_S3_REGION', 'us-east-1')
        except Exception as e:
            # Fallback to environment variable
            region = os.environ.get('AWS_S3_REGION', 'us-east-1')
    
    # For us-east-1, the URL format is different (no region in URL)
    if region == 'us-east-1':
        return f"https://{bucket}.s3.amazonaws.com/{key}"
    else:
        return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"

# Authentication Routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f'LOGIN ATTEMPT - username: {username}, password length: {len(password) if password else 0}')
        
        user = User.query.filter_by(username=username, is_active=True).first()
        
        if user:
            logger.warning(f'USER FOUND: {user.username}')
            password_valid = user.check_password(password)
            logger.warning(f'PASSWORD VALID: {password_valid}')
            
            if password_valid:
                # Update last login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Log the user in
                login_user(user, remember=remember)
                flash('Welcome back! You have been logged in successfully.', 'success')
                
                # Redirect to the next page or dashboard
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('admin.admin_dashboard'))
        else:
            logger.warning(f'USER NOT FOUND for username: {username}')
        
        flash('Invalid username or password. Please try again.', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    """Log out the current user."""
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/')
@login_required
def admin_dashboard():
    """Admin dashboard."""
    stories = StoryService.get_all_stories()
    # Get all segments for display in the dashboard
    segments = []
    for story in stories:
        segments.extend(StoryService.get_story_segments(story.id))
    
    # Get Flora and Fauna data
    flora_fauna_items = FloraFaunaService.get_all_items()
    
    return render_template('admin/dashboard.html', stories=stories, segments=segments, flora_fauna_items=flora_fauna_items)

@admin_bp.route('/stories/new', methods=['GET', 'POST'])
@login_required
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
                if not os.environ.get('AWS_S3_BUCKET') or not boto3:
                    flash('S3 configuration is required for image uploads', 'error')
                    return render_template('admin/create_story.html')
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_S3_REGION', 'us-east-1')
                )
                bucket = os.environ.get('AWS_S3_BUCKET')
                s3.upload_fileobj(image, bucket, filename, ExtraArgs={'ContentType': image.content_type})
                image_path = get_s3_url(bucket, filename)
        
        story = StoryService.create_story(title, description, image_path, image_position)
        flash(f'Story "{title}" created successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story.id))
    
    return render_template('admin/create_story.html')

@admin_bp.route('/stories/<story_id>/edit', methods=['GET', 'POST'])
@login_required
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
                if not os.environ.get('AWS_S3_BUCKET') or not boto3:
                    flash('S3 configuration is required for image uploads', 'error')
                    return render_template('admin/create_story.html')
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_S3_REGION', 'us-east-1')
                )
                bucket = os.environ.get('AWS_S3_BUCKET')
                s3.upload_fileobj(image, bucket, filename, ExtraArgs={'ContentType': image.content_type})
                image_path = get_s3_url(bucket, filename)
        
        # Update the story
        StoryService.update_story(story_id, title=title, description=description, 
                                 image_path=image_path, image_position=image_position)
        flash('Story updated successfully!', 'success')
        return redirect(url_for('admin.edit_story', story_id=story_id))
    
    segments = StoryService.get_story_segments(story_id)
    return render_template('admin/edit_story.html', story=story, segments=segments)

@admin_bp.route('/stories/<story_id>/segments/new', methods=['GET', 'POST'])
@login_required
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
                if not os.environ.get('AWS_S3_BUCKET') or not boto3:
                    flash('S3 configuration is required for media uploads', 'error')
                    return redirect(url_for('admin.create_segment', story_id=story_id))
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_S3_REGION', 'us-east-1')
                )
                bucket = os.environ.get('AWS_S3_BUCKET')
                s3.upload_fileobj(media, bucket, filename, ExtraArgs={'ContentType': media.content_type})
                media_path = get_s3_url(bucket, filename)
        
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
@login_required
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
                if not os.environ.get('AWS_S3_BUCKET') or not boto3:
                    flash('S3 configuration is required for media uploads', 'error')
                    return redirect(url_for('admin.create_segment', story_id=story_id))
                
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_S3_REGION', 'us-east-1')
                )
                bucket = os.environ.get('AWS_S3_BUCKET')
                s3.upload_fileobj(media, bucket, filename, ExtraArgs={'ContentType': media.content_type})
                media_path = get_s3_url(bucket, filename)
        
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
@login_required
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
@login_required
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
@login_required
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
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_feedback = Feedback.query.filter(
        Feedback.created_at >= seven_days_ago
    ).count()
    
    return render_template('admin/feedback.html', 
                         feedback_pagination=feedback_pagination,
                         total_feedback=total_feedback,
                         recent_feedback=recent_feedback)

@admin_bp.route('/feedback/<feedback_id>/delete', methods=['POST'])
@login_required
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

# Flora and Fauna Admin Routes
@admin_bp.route('/flora-fauna/item/create', methods=['GET', 'POST'])
@login_required
def create_flora_fauna_item():
    """Create a new flora/fauna item."""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            short_description = request.form.get('short_description')
            description = request.form.get('description')
            conservation_status = request.form.get('conservation_status')
            fun_facts = request.form.get('fun_facts')
            
            if not name or not description:
                flash('Name and description are required!', 'error')
                return render_template('admin/create_flora_fauna_item.html')
            
            # Handle image/video upload
            image_path = None
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = int(time.time())
                    filename = f"{timestamp}_{filename}"
                    
                    # Determine if it's a video or image
                    is_video = filename.lower().endswith(('.mp4', '.mov', '.avi', '.webm', '.mkv'))
                    folder = 'media' if is_video else 'images'
                    image_path = f"uploads/{folder}/{filename}"
                    
                    # Save file locally
                    file_path = os.path.join(current_app.static_folder, image_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
            
            item = FloraFaunaService.create_item(
                name=name,
                short_description=short_description,
                description=description,
                image_path=image_path,
                conservation_status=conservation_status,
                fun_facts=fun_facts
            )
            flash(f'Item "{name}" created successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
            
        except Exception as e:
            flash(f'Error creating item: {str(e)}', 'error')
    
    return render_template('admin/create_flora_fauna_item.html')

@admin_bp.route('/flora-fauna/item/<item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_flora_fauna_item(item_id):
    """Edit a flora/fauna item."""
    item = FloraFaunaService.get_item_by_id(item_id)
    if not item:
        flash('Item not found!', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            short_description = request.form.get('short_description')
            description = request.form.get('description')
            conservation_status = request.form.get('conservation_status')
            fun_facts = request.form.get('fun_facts')
            
            if not name or not description:
                flash('Name and description are required!', 'error')
                return render_template('admin/edit_flora_fauna_item.html', item=item)
            
            # Handle image/video upload
            image_path = item.image_path  # Keep existing image/video
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = int(time.time())
                    filename = f"{timestamp}_{filename}"
                    
                    # Determine if it's a video or image
                    is_video = filename.lower().endswith(('.mp4', '.mov', '.avi', '.webm', '.mkv'))
                    folder = 'media' if is_video else 'images'
                    image_path = f"uploads/{folder}/{filename}"
                    
                    # Save file locally
                    file_path = os.path.join(current_app.static_folder, image_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
            
            FloraFaunaService.update_item(
                item_id,
                name=name,
                short_description=short_description,
                description=description,
                image_path=image_path,
                conservation_status=conservation_status,
                fun_facts=fun_facts
            )
            flash(f'Item "{name}" updated successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
            
        except Exception as e:
            flash(f'Error updating item: {str(e)}', 'error')
    
    return render_template('admin/edit_flora_fauna_item.html', item=item)

@admin_bp.route('/flora-fauna/item/<item_id>/delete', methods=['POST'])
@login_required
def delete_flora_fauna_item(item_id):
    """Delete a flora/fauna item."""
    try:
        item = FloraFaunaService.get_item_by_id(item_id)
        if not item:
            flash('Item not found!', 'error')
            return redirect(url_for('admin.admin_dashboard'))
        
        FloraFaunaService.delete_item(item_id)
        flash(f'Item "{item.name}" deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting item: {str(e)}', 'error')
    
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/flora-fauna/tile/edit', methods=['GET', 'POST'])
@login_required
def edit_flora_fauna_tile():
    """Edit the Flora & Fauna tile settings."""
    settings = FloraFaunaTileSettings.get_settings()
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            description = request.form.get('description')
            page_blurb = request.form.get('page_blurb')
            
            if not title or not description:
                flash('Title and description are required!', 'error')
                return render_template('admin/edit_flora_fauna_tile.html', settings=settings)
            
            # Update settings
            settings.title = title
            settings.description = description
            settings.page_blurb = page_blurb
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    timestamp = int(time.time())
                    filename = f"{timestamp}_{filename}"
                    image_path = f"uploads/images/{filename}"
                    
                    # Save file locally
                    file_path = os.path.join(current_app.static_folder, image_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    file.save(file_path)
                    
                    settings.image_path = image_path
            
            settings.updated_at = datetime.utcnow()
            db.session.commit()
            
            flash('Flora & Fauna tile updated successfully!', 'success')
            return redirect(url_for('admin.admin_dashboard'))
            
        except Exception as e:
            flash(f'Error updating tile: {str(e)}', 'error')
    
    return render_template('admin/edit_flora_fauna_tile.html', settings=settings) 