import requests

# URL of the scan-document endpoint
url = "http://127.0.0.1:5000/scan-document"

# Start a session to persist cookies (if already logged in)
session = requests.Session()

# Log in as the user (adjust the URL if needed)
login_url = "http://127.0.0.1:5000/login"
login_data = {"username": "testuser", "password": "yourpassword"}
login_response = session.post(login_url, json=login_data)
print("Login:", login_response.json())

# Path to the document you want to test (an image file with text)
file_path = "path/to/your/document.jpg"  # Update this path

with open(file_path, "rb") as f:
    files = {"document": f}
    response = session.post(url, files=files)
    print("Scan Document Response:", response.json())