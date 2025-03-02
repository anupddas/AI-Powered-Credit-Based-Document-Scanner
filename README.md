# AI Powered Credit Based Document Scanner

AI Powered Credit Based Document Scanner is a self-contained Python/SQL system that uses OCR and AI-powered text matching (via OpenAI) to scan and process documents. It features daily free scans with a credit-based system for extra usage, secure user authentication, role-based access, and an analytics dashboard for monitoring usage.

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Running the Application](#running-the-application)
  - [API Endpoints](#api-endpoints)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Document Scanning:** Upload documents and extract text using OCR (pytesseract).
- **AI-Powered Matching:** Use OpenAI API to perform text matching and analysis.
- **Credit System:** 20 free daily scans per user with the ability to request additional credits.
- **User Authentication:** Secure registration, login, and session management.
- **Role Management:** Separate endpoints for regular users and admins.
- **Analytics Dashboard:** View system statistics such as scan counts and credit requests.

## Requirements
- Python 3.8+
- Flask
- SQLAlchemy
- Flask-SQLAlchemy
- PostgreSQL/MySQL/SQLite (as preferred)
- pytesseract and Pillow
- OpenAI Python client
- python-dotenv
- Requests (for testing purposes)

## Installation
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/ai-powered-credit-based-document-scanner.git
   cd ai-powered-credit-based-document-scanner

2. **Create and Activate Virtual Environment:**
  On macOS/Linux:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
  
  On Windows:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    
3. **Install Dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Set Up Environment Variables: Create a .env file in the project root and add:**

    ```dotenv
    SECRET_KEY=your_secret_key
    DATABASE_URL=sqlite:///app.db   # Or your preferred database URI
    OPENAI_API_KEY=your_openai_api_key

5. **Initialize the Database:** The database is automatically created when you run the application for the first time.

## Usage
### Running the Application
1. **Start the Flask Server:**
    ```bash
    python run.py

The server will run in debug mode at http://127.0.0.1:5000.

### API Endpoints
#### User Registration:
POST /register
Payload:

    
    {
        "username": "testuser",
        "email": "test@example.com",
        "password": "yourpassword"
    }
    
#### User Login:
POST /login
Payload:

    
    {
        "username": "testuser",
        "password": "yourpassword"
    }

#### View Profile:
GET /profile (Requires login)
#### Document Scan (Basic Credit Check):
POST /scan (Simulates a scan; increments scan count)

#### Document Scan with AI Matching:
POST /scan-document
#### Form Data:
Upload file with key document.
#### Request Additional Credits:
POST /request-credits
Payload:

    
    {
        "additional": 5
    }
    
#### Admin Endpoints:
  View pending credit requests: GET /admin/credit-requests
  Approve a credit request: POST /admin/approve-credit/<request_id>
  Reject a credit request: POST /admin/reject-credit/<request_id>
  Analytics Dashboard: GET /admin/analytics (Returns an HTML dashboard)
  
### Project Structure
    ```bash
    ai-powered-credit-based-document-scanner/
    ├── app/
    │   ├── __init__.py         # Flask app initialization and blueprint registration
    │   ├── config.py           # Application configuration
    │   ├── models.py           # Database models (User, CreditRequest, etc.)
    │   ├── views.py            # API endpoints and route definitions
    │   ├── services/           # Business logic for scanning and AI matching
    │   └── utils/              # Utility functions
    ├── app/templates/
    │   └── dashboard.html      # Admin analytics dashboard HTML template
    ├── requirements.txt        # Python package dependencies
    ├── run.py                  # Application runner script
    └── README.md               # Project documentation (this file)

### Testing
  Use PowerShell for testing API endpoints.
  For file uploads, you can also use a Python script with the requests library.
  
### Deployment
  Consider containerizing the application using Docker.
  Use a production WSGI server (e.g., Gunicorn) for deployment.
  Secure sensitive data and switch to HTTPS in production environments.
  Set up CI/CD pipelines for automated testing and deployment.

### Contributing
  Contributions are welcome! Please fork the repository and submit a pull request with your improvements or bug fixes. For major changes, please open an issue first to discuss your ideas.

## License
