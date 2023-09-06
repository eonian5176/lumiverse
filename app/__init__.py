from flask import Flask

app = Flask(__name__)
app.secret_key = 'some_secret_key'  # In a real app, use a secure and unique key

# Import routes after the app instance is created
from app import routes
