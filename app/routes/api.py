from flask import Blueprint, request, jsonify
from app.services.story_service import StoryService
from app.services.qr_service import QRService

api_bp = Blueprint('api', __name__)

@api_bp.route('/stories', methods=['GET'])
def get_stories():
    """Get all stories."""
    stories = StoryService.get_all_stories()
    return jsonify([story.to_dict() for story in stories])

@api_bp.route('/stories/<story_id>', methods=['GET'])
def get_story(story_id):
    """Get a specific story."""
    story = StoryService.get_story(story_id)
    if not story:
        return jsonify({'error': 'Story not found'}), 404
    
    return jsonify(story.to_dict())

@api_bp.route('/stories', methods=['POST'])
def create_story():
    """Create a new story."""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    story = StoryService.create_story(
        title=data['title'],
        description=data.get('description')
    )
    
    return jsonify(story.to_dict()), 201

@api_bp.route('/segments/<segment_id>', methods=['GET'])
def get_segment(segment_id):
    """Get a specific story segment."""
    segment = StoryService.get_segment(segment_id)
    if not segment:
        return jsonify({'error': 'Segment not found'}), 404
    
    return jsonify(segment.to_dict())

@api_bp.route('/segments', methods=['POST'])
def create_segment():
    """Create a new story segment."""
    data = request.get_json()
    
    required_fields = ['story_id', 'title', 'content', 'order']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    segment = StoryService.create_segment(
        story_id=data['story_id'],
        title=data['title'],
        content=data['content'],
        order=data['order']
    )
    
    return jsonify(segment.to_dict()), 201

@api_bp.route('/segments/<segment_id>', methods=['PUT'])
def update_segment(segment_id):
    """Update a story segment."""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    segment = StoryService.update_segment(segment_id, **data)
    if not segment:
        return jsonify({'error': 'Segment not found'}), 404
    
    return jsonify(segment.to_dict())

@api_bp.route('/segments/<segment_id>', methods=['DELETE'])
def delete_segment(segment_id):
    """Delete a story segment."""
    success = StoryService.delete_segment(segment_id)
    if not success:
        return jsonify({'error': 'Segment not found'}), 404
    
    return jsonify({'message': 'Segment deleted successfully'})

@api_bp.route('/qr/<segment_id>', methods=['GET'])
def get_qr_info(segment_id):
    """Get QR code information for a segment."""
    qr_code = QRService.get_qr_code(segment_id)
    if not qr_code:
        return jsonify({'error': 'QR code not found'}), 404
    
    return jsonify(qr_code.to_dict()) 