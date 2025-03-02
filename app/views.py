from flask import Blueprint, request, jsonify, session, render_template
from app import db
from app.models import User, CreditRequest
from datetime import datetime
from sqlalchemy import func

# Create the blueprint for main routes
mainBlueprint = Blueprint('main', __name__)

# -------------------------------------------------------------------
# Helper Decorators
# -------------------------------------------------------------------
def loginRequired(func):
    """
    Decorator that ensures the user is logged in before accessing the route.
    Returns a 401 response if the user session is not found.
    """
    from functools import wraps
    @wraps(func)
    def decoratedFunction(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Login required"}), 401
        return func(*args, **kwargs)
    return decoratedFunction

def adminRequired(func):
    """
    Decorator that ensures the user has admin privileges before accessing the route.
    Returns a 401 if not logged in and 403 if the user is not an admin.
    """
    from functools import wraps
    @wraps(func)
    def decoratedFunction(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Login required"}), 401
        currentUser = User.query.get(session['user_id'])
        if not currentUser or currentUser.role != 'admin':
            return jsonify({"message": "Admin access required"}), 403
        return func(*args, **kwargs)
    return decoratedFunction

# -------------------------------------------------------------------
# Authentication Endpoints
# -------------------------------------------------------------------
@mainBlueprint.route('/register', methods=['POST'])
def register():
    """
    Register a new user with username, email, and password.
    Returns a success message upon successful registration.
    """
    requestData = request.get_json()
    if not requestData:
        return jsonify({"message": "No input data provided"}), 400

    userName = requestData.get('username')
    email = requestData.get('email')
    password = requestData.get('password')

    if not userName or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400

    # Check if a user with the same username or email already exists.
    if User.query.filter((User.username == userName) | (User.email == email)).first():
        return jsonify({"message": "User already exists"}), 400

    newUser = User(username=userName, email=email)
    newUser.set_password(password)

    db.session.add(newUser)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@mainBlueprint.route('/login', methods=['POST'])
def login():
    """
    Log in a user using provided username and password.
    Establishes a session upon successful authentication.
    """
    requestData = request.get_json()
    if not requestData:
        return jsonify({"message": "No input data provided"}), 400

    userName = requestData.get('username')
    password = requestData.get('password')

    if not userName or not password:
        return jsonify({"message": "Missing required fields"}), 400

    currentUser = User.query.filter_by(username=userName).first()
    if currentUser is None or not currentUser.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    session['user_id'] = currentUser.id
    return jsonify({"message": "Login successful"}), 200

@mainBlueprint.route('/logout', methods=['POST'])
@loginRequired
def logout():
    """
    Log out the current user by removing the user_id from the session.
    """
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

@mainBlueprint.route('/profile', methods=['GET'])
@loginRequired
def profile():
    """
    Retrieve and return the profile information of the currently logged in user.
    """
    currentUser = User.query.get(session['user_id'])
    return jsonify({
        "username": currentUser.username,
        "email": currentUser.email,
        "role": currentUser.role,
        "daily_scan_count": currentUser.daily_scan_count,
        "last_scan_date": currentUser.last_scan_date.isoformat()
    })

# -------------------------------------------------------------------
# Admin Dashboard Endpoint
# -------------------------------------------------------------------
@mainBlueprint.route('/admin/dashboard', methods=['GET'])
@adminRequired
def adminDashboard():
    """
    Simple admin dashboard endpoint returning a welcome message.
    """
    return jsonify({"message": "Welcome to the admin dashboard"})

# -------------------------------------------------------------------
# Document Scanning Endpoints
# -------------------------------------------------------------------
@mainBlueprint.route('/scan', methods=['POST'])
@loginRequired
def scanDocument():
    """
    Simulate a document scan by incrementing the user's scan count.
    Resets the daily count if a new day has started.
    Returns the scan status and remaining scans.
    """
    currentUser = User.query.get(session['user_id'])
    currentDate = datetime.utcnow().date()

    # Reset scan count and extra credits if a new day has started.
    if currentUser.last_scan_date != currentDate:
        currentUser.daily_scan_count = 0
        currentUser.extra_credits = 0
        currentUser.last_scan_date = currentDate
        db.session.commit()

    allowedScans = 20 + currentUser.extra_credits  # 20 free scans + approved extra credits

    if currentUser.daily_scan_count < allowedScans:
        # Simulate scanning a document.
        currentUser.daily_scan_count += 1
        db.session.commit()
        return jsonify({
            "message": "Document scanned successfully",
            "scans_used": currentUser.daily_scan_count,
            "scans_remaining": allowedScans - currentUser.daily_scan_count
        })
    else:
        return jsonify({"message": "Daily scan limit reached. Please request additional credits."}), 403

@mainBlueprint.route('/scan-document', methods=['POST'])
@loginRequired
def scanAndMatchDocument():
    """
    Processes an uploaded document file to extract text using OCR,
    then performs AI-powered text matching using the OpenAI API.
    Updates the user's scan count and returns the OCR text and AI analysis.
    """
    currentUser = User.query.get(session['user_id'])
    currentDate = datetime.utcnow().date()

    # Reset scan count and extra credits if a new day has started.
    if currentUser.last_scan_date != currentDate:
        currentUser.daily_scan_count = 0
        currentUser.extra_credits = 0
        currentUser.last_scan_date = currentDate
        db.session.commit()

    allowedScans = 20 + currentUser.extra_credits  # 20 free scans + approved extra credits
    if currentUser.daily_scan_count >= allowedScans:
        return jsonify({"message": "Daily scan limit reached. Please request additional credits."}), 403

    # Ensure a file is provided in the request.
    if 'document' not in request.files:
        return jsonify({"message": "No document file provided."}), 400

    fileObj = request.files['document']
    if fileObj.filename == '':
        return jsonify({"message": "Empty filename provided."}), 400

    try:
        # Process the uploaded file using Pillow and pytesseract for OCR.
        from PIL import Image
        import io
        import pytesseract

        imageObj = Image.open(io.BytesIO(fileObj.read()))
        extractedText = pytesseract.image_to_string(imageObj)
    except Exception as e:
        return jsonify({"message": f"Error processing the document: {str(e)}"}), 500

    try:
        # Use OpenAI API to perform AI-powered text matching on the extracted text.
        import openai
        openai.api_key = "your_openai_api_key"  # Replace with your actual API key or load from environment

        promptText = f"Perform document matching on the following text:\n\n{extractedText}\n\nReturn a brief analysis."
        aiResponse = openai.Completion.create(
            engine="text-davinci-003",
            prompt=promptText,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        aiMatchingResult = aiResponse.choices[0].text.strip()
    except Exception as e:
        return jsonify({"message": f"Error in AI matching: {str(e)}"}), 500

    # Update the user's scan count.
    currentUser.daily_scan_count += 1
    db.session.commit()

    return jsonify({
        "message": "Document scanned and matched successfully",
        "scans_used": currentUser.daily_scan_count,
        "scans_remaining": allowedScans - currentUser.daily_scan_count,
        "extracted_text": extractedText,
        "ai_matching_result": aiMatchingResult
    })

# -------------------------------------------------------------------
# Credit Management Endpoints
# -------------------------------------------------------------------
@mainBlueprint.route('/request-credits', methods=['POST'])
@loginRequired
def requestCredits():
    """
    Allows a user to request additional scan credits.
    Validates the request and records it in the system.
    """
    requestData = request.get_json()
    additionalCredits = requestData.get("additional", 0)

    if additionalCredits <= 0:
        return jsonify({"message": "Invalid credit request. Specify a positive number."}), 400

    currentUser = User.query.get(session['user_id'])
    newCreditRequest = CreditRequest(user_id=currentUser.id, requested_credits=additionalCredits)
    db.session.add(newCreditRequest)
    db.session.commit()
    return jsonify({"message": f"Credit request submitted for additional {additionalCredits} scans."})

@mainBlueprint.route('/admin/credit-requests', methods=['GET'])
@adminRequired
def listCreditRequests():
    """
    Admin endpoint to list all pending credit requests.
    Returns a list of credit requests with their details.
    """
    creditRequests = CreditRequest.query.filter_by(status="pending").all()
    requestList = [{
        "id": req.id,
        "user_id": req.user_id,
        "requested_credits": req.requested_credits,
        "status": req.status,
        "request_date": req.request_date.isoformat()
    } for req in creditRequests]
    return jsonify({"credit_requests": requestList})

@mainBlueprint.route('/admin/approve-credit/<int:requestId>', methods=['POST'])
@adminRequired
def approveCredit(requestId):
    """
    Admin endpoint to approve a pending credit request.
    Updates the user's extra credits accordingly.
    """
    creditRequest = CreditRequest.query.get(requestId)
    if not creditRequest or creditRequest.status != "pending":
        return jsonify({"message": "Invalid or already processed request"}), 400

    currentUser = User.query.get(creditRequest.user_id)
    currentUser.extra_credits += creditRequest.requested_credits
    creditRequest.status = "approved"
    db.session.commit()
    return jsonify({"message": "Credit request approved."})

@mainBlueprint.route('/admin/reject-credit/<int:requestId>', methods=['POST'])
@adminRequired
def rejectCredit(requestId):
    """
    Admin endpoint to reject a pending credit request.
    Updates the status of the request to 'rejected'.
    """
    creditRequest = CreditRequest.query.get(requestId)
    if not creditRequest or creditRequest.status != "pending":
        return jsonify({"message": "Invalid or already processed request"}), 400

    creditRequest.status = "rejected"
    db.session.commit()
    return jsonify({"message": "Credit request rejected."})

# -------------------------------------------------------------------
# Analytics Endpoint
# -------------------------------------------------------------------
@mainBlueprint.route('/admin/analytics', methods=['GET'])
@adminRequired
def analyticsDashboard():
    """
    Admin endpoint to display an analytics dashboard.
    Aggregates key statistics such as total scans, credit requests, and user count.
    Renders the dashboard as an HTML template.
    """
    currentDate = datetime.utcnow().date()

    totalScansToday = db.session.query(func.sum(User.daily_scan_count)).scalar() or 0
    totalCreditRequests = db.session.query(func.count(CreditRequest.id)).scalar() or 0
    pendingCreditRequests = db.session.query(func.count(CreditRequest.id)).filter(CreditRequest.status == 'pending').scalar() or 0
    totalUsers = db.session.query(func.count(User.id)).scalar() or 0

    return render_template('dashboard.html',
                           total_scans_today=totalScansToday,
                           total_credit_requests=totalCreditRequests,
                           pending_credit_requests=pendingCreditRequests,
                           total_users=totalUsers)
