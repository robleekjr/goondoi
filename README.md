# Goondoi Wetlands

A professional web application for exploring the stories, cultural heritage, and biodiversity of the Goondoi Wetlands through an interactive, app-like interface.

## Features

### Public Features
- **Interactive Story Platform**: Explore stories through an intuitive tile-based interface
- **QR Code Integration**: Scan QR codes to access story segments and content
- **Flora & Fauna Directory**: Discover the diverse wildlife and plant life with detailed profiles
- **Compact Sidebar Navigation**: Quick access to all stories and Flora & Fauna from any page
- **Responsive Design**: Fully optimized for desktop, tablet, and mobile devices
- **Camera Integration**: Built-in QR code scanner for mobile devices
- **Professional UI**: Modern, app-like interface with smooth animations and transitions

### Admin Features
- **Secure Authentication**: Login system with protected admin routes
- **Story Management**: Create, edit, and delete stories with segments
- **Flora & Fauna Management**: Add and manage biodiversity content
- **Tile Customization**: Configure homepage tiles (title, description, image)
- **QR Code Generation**: Automatic QR code creation for story segments
- **Feedback Management**: View and manage user feedback
- **Media Upload**: Support for both images and videos

## Technology Stack

- **Backend**: Flask (Python), Gunicorn
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5, Custom CSS with CSS Variables
- **QR Codes**: jsQR library, qrcode Python library
- **File Storage**: Local storage / AWS S3 (optional)
- **Security**: Flask-WTF (CSRF protection), Werkzeug (password hashing)

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd goondoi
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables** (optional)
   ```bash
   export FLASK_ENV=development
   export SECRET_KEY=your-secret-key-here
   ```

5. **Initialize database**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

The application will be available at `http://localhost:8001`

## Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development/production/testing)
- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `AWS_ACCESS_KEY_ID`: AWS access key (for S3 storage)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `AWS_S3_BUCKET`: S3 bucket name
- `AWS_S3_REGION`: S3 region

### File Structure

```
goondoi/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── models/              # Database models
│   ├── routes/              # Route handlers
│   ├── services/            # Business logic
│   ├── static/              # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript modules
│   │   └── uploads/        # User uploads
│   └── templates/           # HTML templates
├── migrations/              # Database migrations
├── instance/               # Instance-specific files
├── requirements.txt        # Python dependencies
└── run.py                 # Application entry point
```

## Usage

### Admin Interface

Access the admin dashboard at `/admin/` (requires login):

**Admin Features:**
- Create and manage stories with multiple segments
- Add story segments with images/videos
- Generate QR codes for segments automatically
- Manage Flora & Fauna items (add, edit, delete)
- Customize Flora & Fauna tile (title, description, image, page blurb)
- View and manage user feedback
- Upload media (images and videos)

### User Interface

**Home Page (Trails):**
- Grid of story tiles with images and descriptions
- Flora & Fauna tile with customizable content
- Clean, minimal design

**Sidebar Navigation** (visible on all pages except home and admin):
- Compact vertical navigation (100px desktop, 55px mobile)
- Story tiles with images
- Flora & Fauna quick link
- Active state highlighting

**Story Pages:**
- Carousel-style segment navigation
- Images/videos with full descriptions
- QR code display for each segment
- Previous/Next navigation

**Flora & Fauna:**
- Grid of biodiversity items
- Short descriptions on tiles
- Detailed information pages with fun facts
- Conservation status badges

**Other Features:**
- QR code scanning via camera
- Feedback form
- About page
- Fixed compact footer (50-90px depending on device)

## Development

### Code Structure

The application follows a clean, modular architecture:

- **Models**: Database models in `app/models/`
  - `story.py` - Stories and segments
  - `qr_code.py` - QR code tracking
  - `feedback.py` - User feedback
  - `flora_fauna.py` - Flora & Fauna items
  - `flora_fauna_settings.py` - Tile customization
  - `user.py` - Admin authentication
- **Routes**: URL handlers in `app/routes/`
  - `main.py` - Public routes
  - `admin.py` - Admin routes (protected)
  - `api.py` - API endpoints
- **Services**: Business logic in `app/services/`
  - `story_service.py` - Story operations
  - `qr_service.py` - QR code generation
  - `flora_fauna_service.py` - Flora & Fauna operations
- **Static Assets**: Organized by type in `app/static/`
- **Templates**: Jinja2 templates in `app/templates/`

### Database Schema

**Tables:**
- `stories` - Story content and metadata
- `story_segments` - Individual story segments
- `qr_codes` - QR code images and URLs
- `feedback` - User feedback submissions
- `flora_fauna_items` - Flora & Fauna profiles
- `flora_fauna_tile_settings` - Homepage tile configuration
- `users` - Admin user accounts

### JavaScript Modules

- `app.js`: Flash message management and initialization

### CSS Architecture

- CSS custom properties for consistent theming
- Mobile-first responsive design with extensive media queries
- Component-based styling with reusable classes
- Smooth animations and transitions
- Compact sidebar navigation (100px → 55px responsive)
- Fixed footer with responsive heights (50px → 90px)

## Deployment

### Production Setup

1. **Set up environment variables** in `.env` file:
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database
   AWS_S3_BUCKET=your-bucket-name
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_S3_REGION=your-region
   SECRET_KEY=your-secret-key-here
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Create database tables**:
   ```bash
   # The application will auto-create tables in development mode
   # For production, you may need to create them manually:
   python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
   ```

4. **Create admin user** (if not exists):
   ```bash
   python -c "
   from app import create_app, db
   from app.models.user import User
   import uuid
   
   app = create_app('production')
   app.app_context().push()
   
   # Check if admin exists
   admin = User.query.filter_by(username='admin').first()
   if not admin:
       admin = User(id=str(uuid.uuid4()), username='admin', email='admin@example.com')
       admin.set_password('admin')  # CHANGE THIS!
       db.session.add(admin)
       db.session.commit()
       print('Admin user created. Please change password!')
   else:
       print('Admin user already exists')
   "
   ```

5. **Start the application**:
   ```bash
   # Option 1: Use the startup script (recommended)
   chmod +x start_app.sh
   ./start_app.sh
   
   # Option 2: Manual start with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 --timeout 120 run:app
   ```


## Security

### Admin Access
- Admin section is protected by Flask-Login authentication
- All admin routes require valid login session
- Passwords are hashed using Werkzeug's secure password hashing
- CSRF protection enabled on all forms

### Best Practices
1. **Change default admin password immediately** after first deployment
2. Use strong passwords for admin accounts
3. Keep SECRET_KEY environment variable secure and unique
4. Regularly update dependencies for security patches
5. Use HTTPS in production
6. Restrict database access to localhost when possible

### Database Security
- Database files are excluded from git (.gitignore)
- Instance folder with sensitive data is git-ignored
- Use environment variables for database credentials
- Never commit `.env` files

## API Routes

### Public Routes
- `GET /` - Homepage (trails grid)
- `GET /story/<story_id>` - View story with segments
- `GET /flora-fauna` - Flora & Fauna listing
- `GET /flora-fauna/<item_id>` - Flora & Fauna item detail
- `GET /feedback` - Feedback form
- `GET /about` - About page
- `GET /qr/<segment_id>` - Get QR code image

### Admin Routes (Login Required)
- `GET /admin/` - Admin dashboard
- `GET/POST /admin/login` - Login page
- `GET /admin/logout` - Logout
- `GET/POST /admin/stories/new` - Create story
- `GET/POST /admin/stories/<id>/edit` - Edit story
- `POST /admin/story/<id>/delete` - Delete story
- `GET/POST /admin/stories/<id>/segments/new` - Create segment
- `GET/POST /admin/segments/<id>/edit` - Edit segment
- `POST /admin/segment/<id>/delete` - Delete segment
- `GET/POST /admin/flora-fauna/item/create` - Create Flora & Fauna item
- `GET/POST /admin/flora-fauna/item/<id>/edit` - Edit item
- `POST /admin/flora-fauna/item/<id>/delete` - Delete item
- `GET/POST /admin/flora-fauna/tile/edit` - Edit tile settings
- `GET /admin/feedback` - View feedback
- `POST /admin/feedback/<id>/delete` - Delete feedback

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/YourFeature`)
3. Make your changes
4. Run tests and verify all routes work
5. Clean up debug code and unused imports
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.