# Goondoi Dreamtime Bush Trail 


A Flask web application that creates an interactive story experience where users scan QR codes to reveal different parts of a narrative.

## Features

- QR code generation for story segments
- Interactive story progression

## Project Structure

```
qr_story/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── story.py             # Story and segment models
│   │   └── qr_code.py           # QR code model
│   ├── routes/                   # Route handlers
│   │   ├── __init__.py
│   │   ├── main.py              # Main routes
endpoints
│   │   └── admin.py             # Admin routes
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── qr_service.py        # QR code generation
│   │   └── story_service.py     # Story management
│   ├── static/                   # Static files
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── templates/                # HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── story.html
│   │   └── admin/
│   ├── utils/                    # Utility functions
│   │   ├── __init__.py
│   │   └── helpers.py
│   └── config.py                 # Configuration
├── migrations/                   # Database migrations
├── tests/                        # Test files
├── requirements.txt              # Python dependencies
├── config.py                     # Application config
├── run.py                        # Application entry point
```

## Setup Instructions

Tested on Python version 3.9.10


1. **Clone and navigate to the project:**
   ```bash
   cd qr_story
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:** (Not required for localhosting)
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database:**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. **Run the application:**
   ```bash
   python run.py
   ```

7. **Access the application:**
   - Main app: http://localhost:8001
   - Admin panel: http://localhost:8001/admin

## Development

- **Adding new story segments:** Use the admin panel
- **Database changes:** Create new migrations with `flask db migrate`


## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request 
