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
