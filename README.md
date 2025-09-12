# Goondoi Wetlands

A professional web application for exploring the stories and cultural heritage of the Goondoi Wetlands through an interactive, app-like interface.

## Features

- **Interactive Story Platform**: Explore stories through an intuitive tile-based interface
- **QR Code Integration**: Scan QR codes to access story segments and content
- **Admin Dashboard**: Manage stories, segments, and user feedback
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Camera Integration**: Built-in QR code scanner for mobile devices
- **Professional UI**: Modern, app-like interface with smooth animations

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Styling**: Bootstrap 5, Custom CSS
- **QR Codes**: jsQR library, qrcode Python library
- **File Storage**: Local storage / AWS S3 (optional)

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

Access the admin dashboard at `/admin/` to:
- Create and manage stories
- Add story segments with media
- Generate QR codes for segments
- View user feedback
- Manage content

### User Interface

- **Home Page**: Three main tiles (Trails, Culture, Radiant Life College)
- **Story Navigation**: Click tiles to explore content
- **QR Code Scanning**: Use camera to scan QR codes and access segments
- **Feedback System**: Submit feedback through the footer

## Development

### Code Structure

The application follows a clean, modular architecture:

- **Models**: Database models in `app/models/`
- **Routes**: URL handlers in `app/routes/`
- **Services**: Business logic in `app/services/`
- **Static Assets**: Organized by type in `app/static/`
- **Templates**: Jinja2 templates in `app/templates/`

### JavaScript Modules

- `app.js`: Main application logic and UI management
- `qr-scanner.js`: QR code scanning functionality

### CSS Architecture

- CSS custom properties for consistent theming
- Mobile-first responsive design
- Component-based styling
- Smooth animations and transitions

## Deployment

### Production Setup

1. **Set up environment variables** in `.env` file:
   ```bash
   DATABASE_URL=postgresql://username:password@host:port/database
   AWS_S3_BUCKET=your-bucket-name
   AWS_ACCESS_KEY_ID=your-access-key
   AWS_SECRET_ACCESS_KEY=your-secret-key
   AWS_S3_REGION=your-region
   SECRET_KEY=your-secret-key
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run database migrations**:
   ```bash
   flask db upgrade
   ```

4. **Start the application**:
   ```bash
   # Option 1: Use the startup script (recommended)
   ./start_app.sh
   
   # Option 2: Manual start with environment variables
   export $(cat .env | xargs) && gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

5. **Set up web server** (e.g., Gunicorn)
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 run:app
   ```

### Docker Deployment

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please contact the development team or create an issue in the repository.