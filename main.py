import os
import logging
import uuid
from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
import requests
from abilities import upload_file_to_storage, url_for_uploaded_file, apply_sqlite_migrations

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='static')

# Set Flask secret key
app.config['SECRET_KEY'] = 'supersecretflaskskey'

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db = SQLAlchemy(app)

# Database Model
class UploadedFile(db.Model):
    __tablename__ = 'uploaded_files'

    id = db.Column(db.Integer, primary_key=True)
    unique_path = db.Column(db.String(50), unique=True, nullable=False)
    file_id = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def __repr__(self):
        return f'<UploadedFile {self.unique_path}>'

# Routes
@app.route("/")
def home_route():
    return render_template("home.html")

@app.route("/upload", methods=['POST'])
def upload_html_file():
    if 'html_file' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400

    file = request.files['html_file']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400

    if not file.filename.lower().endswith('.html'):
        return jsonify({"success": False, "error": "Only HTML files are allowed"}), 400

    try:
        # Generate a unique random ID for the file
        file_id = upload_file_to_storage(file)
        
        # Generate a unique URL path
        unique_path = str(uuid.uuid4())[:8]

        # Store file_id and unique_path in database
        new_uploaded_file = UploadedFile(
            unique_path=unique_path, 
            file_id=file_id
        )
        db.session.add(new_uploaded_file)
        db.session.commit()

        return jsonify({
            "success": True, 
            "url": f"/{unique_path}",
            "file_id": file_id
        }), 200

    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return jsonify({"success": False, "error": "Upload failed"}), 500

@app.route("/<path:unique_path>")
def serve_uploaded_html(unique_path):
    # Retrieve file_id from database using unique_path
    uploaded_file = UploadedFile.query.filter_by(unique_path=unique_path).first()
    
    if not uploaded_file:
        return "File not found", 404

    try:
        # Get the URL for the uploaded file
        file_url = url_for_uploaded_file(uploaded_file.file_id)

        # Download the file content
        response = requests.get(file_url)

        # Return the HTML content with the correct MIME type
        return response.text, 200, {
            'Content-Type': 'text/html', 
            'X-Content-Type-Options': 'nosniff',
            'Access-Control-Allow-Origin': '*'  # Add CORS header
        }

    except Exception as e:
        logger.error(f"Error serving HTML file: {str(e)}")
        return "Error serving file", 500

# Database Initialization
with app.app_context():
    db.create_all()
    apply_sqlite_migrations(db.engine, db.Model, 'migrations')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
