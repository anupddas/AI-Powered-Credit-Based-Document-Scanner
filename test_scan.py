import requests

# Define the URL for the scan-document endpoint.
scanDocumentUrl = "http://127.0.0.1:5000/scan-document"

# Create a session instance to persist cookies (maintains login session).
sessionInstance = requests.Session()

# Define the login endpoint URL.
loginUrl = "http://127.0.0.1:5000/login"

# Prepare the login payload with username and password.
loginData = {"username": "testuser", "password": "yourpassword"}

# Send a POST request to the login endpoint with the JSON payload.
loginResponse = sessionInstance.post(loginUrl, json=loginData)

# Output the JSON response from the login attempt.
print("Login:", loginResponse.json())

# Specify the file path for the document to be tested (an image file containing text).
filePath = "path/to/your/document.jpg"  # Update this path accordingly.

# Open the file in binary mode and send it as a file upload to the scan-document endpoint.
with open(filePath, "rb") as fileObject:
    files = {"document": fileObject}
    scanResponse = sessionInstance.post(scanDocumentUrl, files=files)
    
    # Output the JSON response from the scan-document endpoint.
    print("Scan Document Response:", scanResponse.json())
