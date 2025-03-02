# Import the createApp function from the app module.
from app import createApp

# Initialize the Flask application instance using the createApp function.
appInstance = createApp()

# If this script is executed as the main program, run the Flask app in debug mode.
if __name__ == '__main__':
    appInstance.run(debug=True)
