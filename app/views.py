from flask import Blueprint, request, jsonify, session, render_template
from app import db
from app.models import User
from datetime import datetime
from app.models import User, CreditRequest
from sqlalchemy import func

main = Blueprint('main', __name__)

# Helper decorator to ensure user is logged in
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Login required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Helper decorator to ensure admin access
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"message": "Login required"}), 401
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({"message": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated_function

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400
    
    # Check if user exists
    if User.query.filter((User.username == username) | (User.email == email)).first():
        return jsonify({"message": "User already exists"}), 400
    
    new_user = User(username=username, email=email)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({"message": "Missing required fields"}), 400
    
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401
    
    session['user_id'] = user.id
    return jsonify({"message": "Login successful"}), 200

@main.route('/logout', methods=['POST'])
@login_required
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

# Example of a protected route for logged in users
@main.route('/profile', methods=['GET'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return jsonify({
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "daily_scan_count": user.daily_scan_count,
        "last_scan_date": user.last_scan_date.isoformat()
    })

# protected route for admin users only
@main.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    return jsonify({"message": "Welcome to the admin dashboard"})

@main.route('/scan', methods=['POST'])
@login_required
def scan_document():
    user = User.query.get(session['user_id'])
    today = datetime.utcnow().date()
    
    # Reset scan count and extra credits if a new day has started.
    if user.last_scan_date != today:
        user.daily_scan_count = 0
        user.extra_credits = 0
        user.last_scan_date = today
        db.session.commit()
    
    allowed_scans = 20 + user.extra_credits  # 20 free scans + approved extra credits
    
    if user.daily_scan_count < allowed_scans:
        # Simulate scanning a document.
        user.daily_scan_count += 1
        db.session.commit()
        return jsonify({
            "message": "Document scanned successfully",
            "scans_used": user.daily_scan_count,
            "scans_remaining": allowed_scans - user.daily_scan_count
        })
    else:
        return jsonify({"message": "Daily scan limit reached. Please request additional credits."}), 403

@main.route('/request-credits', methods=['POST'])
@login_required
def request_credits():
    data = request.get_json()
    additional = data.get("additional", 0)
    
    if additional <= 0:
        return jsonify({"message": "Invalid credit request. Specify a positive number."}), 400
    
    user = User.query.get(session['user_id'])
    # Create a new credit request record
    credit_request = CreditRequest(user_id=user.id, requested_credits=additional)
    db.session.add(credit_request)
    db.session.commit()
    return jsonify({"message": f"Credit request submitted for additional {additional} scans."})


@main.route('/admin/credit-requests', methods=['GET'])
@admin_required
def list_credit_requests():
    requests = CreditRequest.query.filter_by(status="pending").all()
    req_list = [{
        "id": req.id,
        "user_id": req.user_id,
        "requested_credits": req.requested_credits,
        "status": req.status,
        "request_date": req.request_date.isoformat()
    } for req in requests]
    return jsonify({"credit_requests": req_list})


@main.route('/admin/approve-credit/<int:request_id>', methods=['POST'])
@admin_required
def approve_credit(request_id):
    credit_request = CreditRequest.query.get(request_id)
    if not credit_request or credit_request.status != "pending":
        return jsonify({"message": "Invalid or already processed request"}), 400
    
    user = User.query.get(credit_request.user_id)
    # Update the user's extra credits with the requested amount
    user.extra_credits += credit_request.requested_credits
    credit_request.status = "approved"
    db.session.commit()
    return jsonify({"message": "Credit request approved."})


@main.route('/admin/reject-credit/<int:request_id>', methods=['POST'])
@admin_required
def reject_credit(request_id):
    credit_request = CreditRequest.query.get(request_id)
    if not credit_request or credit_request.status != "pending":
        return jsonify({"message": "Invalid or already processed request"}), 400
    
    credit_request.status = "rejected"
    db.session.commit()
    return jsonify({"message": "Credit request rejected."})

@main.route('/scan-document', methods=['POST'])
@login_required
def scan_and_match_document():
    # Retrieve the current user
    user = User.query.get(session['user_id'])
    today = datetime.utcnow().date()

    # Reset daily scan count and extra credits if a new day has started.
    if user.last_scan_date != today:
        user.daily_scan_count = 0
        user.extra_credits = 0
        user.last_scan_date = today
        db.session.commit()

    allowed_scans = 20 + user.extra_credits  # 20 free scans + approved extra credits
    if user.daily_scan_count >= allowed_scans:
        return jsonify({"message": "Daily scan limit reached. Please request additional credits."}), 403

    # Check if a file is provided in the request
    if 'document' not in request.files:
        return jsonify({"message": "No document file provided."}), 400

    file = request.files['document']
    if file.filename == '':
        return jsonify({"message": "Empty filename provided."}), 400

    try:
        # Process the uploaded file using Pillow and pytesseract
        from PIL import Image
        import io
        import pytesseract

        image = Image.open(io.BytesIO(file.read()))
        extracted_text = pytesseract.image_to_string(image)
    except Exception as e:
        return jsonify({"message": f"Error processing the document: {str(e)}"}), 500

    # Use OpenAI API for AI-powered text matching
    try:
        import openai
        # Ensure you have your OpenAI API key set as an environment variable or directly here
        openai.api_key = "your_openai_api_key"  # Replace with your actual API key or load from env

        prompt = f"Perform document matching on the following text:\n\n{extracted_text}\n\nReturn a brief analysis."
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )
        ai_result = response.choices[0].text.strip()
    except Exception as e:
        return jsonify({"message": f"Error in AI matching: {str(e)}"}), 500

    # Update user's scan count
    user.daily_scan_count += 1
    db.session.commit()

    return jsonify({
        "message": "Document scanned and matched successfully",
        "scans_used": user.daily_scan_count,
        "scans_remaining": allowed_scans - user.daily_scan_count,
        "extracted_text": extracted_text,
        "ai_matching_result": ai_result
    })

@main.route('/admin/analytics', methods=['GET'])
@admin_required
def analytics_dashboard():
    today = datetime.utcnow().date()
    
    # Aggregate statistics
    total_scans_today = db.session.query(func.sum(User.daily_scan_count)).scalar() or 0
    total_credit_requests = db.session.query(func.count(CreditRequest.id)).scalar() or 0
    pending_credit_requests = db.session.query(func.count(CreditRequest.id)).filter(CreditRequest.status=='pending').scalar() or 0
    total_users = db.session.query(func.count(User.id)).scalar() or 0

    return render_template('dashboard.html',
                           total_scans_today=total_scans_today,
                           total_credit_requests=total_credit_requests,
                           pending_credit_requests=pending_credit_requests,
                           total_users=total_users)