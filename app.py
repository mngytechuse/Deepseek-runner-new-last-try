import os
import logging
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import json
import uuid
import tempfile
import shutil
from book_generator import generate_book_content
from utils import create_docx, create_pdf, filter_content

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # Session lasts for 1 hour

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate-book', methods=['POST'])
def generate_book():
    try:
        # Get form data
        syllabus_text = request.form.get('syllabus')
        subject = request.form.get('subject')
        language = request.form.get('language', 'English')

        if not syllabus_text or not subject:
            return jsonify({"error": "Missing required fields"}), 400

        # Filter content for controversial material
        filtered_syllabus = filter_content(syllabus_text)
        
        # Create a unique ID for this book generation
        book_id = str(uuid.uuid4())
        
        # Store the book information in the session
        session['book_data'] = {
            'id': book_id,
            'syllabus': filtered_syllabus,
            'subject': subject,
            'language': language,
            'status': 'processing'
        }
        
        # Redirect to loading page
        return redirect(url_for('loading', book_id=book_id))
    
    except Exception as e:
        logging.error(f"Error in generate_book: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/loading/<book_id>')
def loading(book_id):
    book_data = session.get('book_data', {})
    
    if book_data.get('id') != book_id:
        return redirect(url_for('index'))
    
    return render_template('loading.html', book_id=book_id)

@app.route('/process-book/<book_id>', methods=['POST'])
def process_book(book_id):
    try:
        book_data = session.get('book_data', {})
        
        if book_data.get('id') != book_id:
            return jsonify({"error": "Invalid book ID"}), 400
        
        # Generate book content
        book_content = generate_book_content(
            book_data['syllabus'],
            book_data['subject'],
            book_data['language']
        )
        
        # Store the generated content
        temp_dir = tempfile.mkdtemp()
        
        # Create DOCX file
        docx_path = os.path.join(temp_dir, f"{book_data['subject']}_book.docx")
        create_docx(book_content, docx_path, book_data['subject'])
        
        # Create PDF file
        pdf_path = os.path.join(temp_dir, f"{book_data['subject']}_book.pdf")
        create_pdf(book_content, pdf_path, book_data['subject'])
        
        # Update session with file paths
        book_data['docx_path'] = docx_path
        book_data['pdf_path'] = pdf_path
        book_data['temp_dir'] = temp_dir
        book_data['status'] = 'completed'
        session['book_data'] = book_data
        
        return jsonify({
            "status": "success",
            "message": "Book generation completed",
            "book_id": book_id
        })
    
    except Exception as e:
        logging.error(f"Error in process_book: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status/<book_id>')
def status(book_id):
    book_data = session.get('book_data', {})
    
    if book_data.get('id') != book_id:
        return jsonify({"status": "error", "message": "Invalid book ID"}), 400
    
    return jsonify({
        "status": book_data.get('status', 'unknown'),
        "subject": book_data.get('subject', ''),
        "language": book_data.get('language', '')
    })

@app.route('/download/<book_id>/<file_type>')
def download(book_id, file_type):
    book_data = session.get('book_data', {})
    
    if book_data.get('id') != book_id or book_data.get('status') != 'completed':
        logging.error(f"Download request for invalid book or incomplete book: {book_id}, status: {book_data.get('status')}")
        return redirect(url_for('index'))
    
    try:
        download_filename = f"{book_data.get('subject', 'Educational')}_book"
        
        if file_type == 'docx':
            path = book_data.get('docx_path')
            if not path or not os.path.exists(path):
                logging.error(f"DOCX file not found at path: {path}")
                return jsonify({"error": "DOCX file not found"}), 404
                
            logging.info(f"Sending DOCX file from: {path}")
            
            # Use standard send_file with proper mimetype and download_name
            return send_file(
                path,
                as_attachment=True,
                download_name=f"{download_filename}.docx",
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                max_age=0  # Don't cache
            )
            
        elif file_type == 'pdf':
            path = book_data.get('pdf_path')
            if not path or not os.path.exists(path):
                logging.error(f"PDF file not found at path: {path}")
                return jsonify({"error": "PDF file not found"}), 404
                
            logging.info(f"Sending PDF file from: {path}")
            
            # Use standard send_file with proper mimetype and download_name
            return send_file(
                path,
                as_attachment=True,
                download_name=f"{download_filename}.pdf",
                mimetype='application/pdf',
                max_age=0  # Don't cache
            )
            
        else:
            logging.warning(f"Invalid file type requested: {file_type}")
            return redirect(url_for('index'))
    
    except Exception as e:
        logging.error(f"Error in download: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/reset')
def reset():
    if 'book_data' in session:
        # Clean up temporary files
        temp_dir = session['book_data'].get('temp_dir')
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        
        # Clear session
        session.pop('book_data', None)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
