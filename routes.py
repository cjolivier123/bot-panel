import logging
import os
import uuid
import requests
from flask import render_template, request, jsonify
from flask import current_app as app
from abilities import upload_file_to_storage, url_for_uploaded_file
from models import db, UploadedFile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_routes(app):
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
            import requests
            response = requests.get(file_url)

            # Return the HTML content with the correct MIME type
            return response.text, 200, {
                'Content-Type': 'text/html', 
                'X-Content-Type-Options': 'nosniff'
            }

        except Exception as e:
            logger.error(f"Error serving HTML file: {str(e)}")
            return "Error serving file", 500
