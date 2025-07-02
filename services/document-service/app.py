import os
import uuid
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
app.config['UPLOAD_FOLDER'] = '../../data/documents'
app.config['DATABASE'] = '../../data/metadata.db'

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_database():
    """Initialize SQLite database with documents metadata table"""
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            original_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            upload_timestamp TEXT NOT NULL,
            content_preview TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def allowed_file(filename):
    """Check if uploaded file is a .txt file"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'txt'

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service monitoring"""
    try:
        # Test database connection
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.close()
        
        # Test file system access
        Path(app.config['UPLOAD_FOLDER']).exists()
        
        return jsonify({
            'status': 'healthy',
            'service': 'document-service',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'document-service',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/upload', methods=['POST'])
def upload_document():
    """Upload a .txt document and return its UUID"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        # Check if file was selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Only .txt files are allowed'
            }), 400
        
        # Generate UUID for document
        document_id = str(uuid.uuid4())
        
        # Secure the filename and save file
        original_filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}.txt")
        file.save(file_path)
        
        # Get file size and create content preview
        file_size = os.path.getsize(file_path)
        
        # Read content for preview (first 200 chars)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            content_preview = content[:200] + "..." if len(content) > 200 else content
        
        # Store metadata in database
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO documents (id, original_filename, file_size, upload_timestamp, content_preview)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            document_id,
            original_filename,
            file_size,
            datetime.now().isoformat(),
            content_preview
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'original_filename': original_filename,
            'file_size': file_size,
            'message': 'Document uploaded successfully'
        }), 201
        
    except RequestEntityTooLarge:
        return jsonify({
            'success': False,
            'error': 'File too large. Maximum size is 5MB.'
        }), 413
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@app.route('/document/<document_id>', methods=['GET'])
def get_document(document_id):
    """Retrieve document content by UUID"""
    try:
        # Validate UUID format
        try:
            uuid.UUID(document_id)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid document ID format'
            }), 400
        
        # Check if document exists in database
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT original_filename, file_size, upload_timestamp 
            FROM documents WHERE id = ?
        ''', (document_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'Document not found'
            }), 404
        
        # Read document content
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{document_id}.txt")
        
        if not os.path.exists(file_path):
            return jsonify({
                'success': False,
                'error': 'Document file not found on disk'
            }), 404
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return jsonify({
            'success': True,
            'document_id': document_id,
            'original_filename': result[0],
            'file_size': result[1],
            'upload_timestamp': result[2],
            'content': content
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve document: {str(e)}'
        }), 500

@app.route('/documents', methods=['GET'])
def list_documents():
    """List all uploaded documents (useful for debugging)"""
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, original_filename, file_size, upload_timestamp, content_preview
            FROM documents ORDER BY upload_timestamp DESC
        ''')
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                'document_id': row[0],
                'original_filename': row[1],
                'file_size': row[2],
                'upload_timestamp': row[3],
                'content_preview': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'documents': documents,
            'total_count': len(documents)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to list documents: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    
    # Run Flask development server
    app.run(host='0.0.0.0', port=5000, debug=True) 