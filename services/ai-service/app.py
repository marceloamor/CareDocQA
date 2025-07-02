import os
import requests
import json
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['DOCUMENT_SERVICE_URL'] = os.getenv('DOCUMENT_SERVICE_URL', 'http://localhost:5000')
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['OPENAI_API_BASE'] = 'https://api.openai.com/v1'

# Healthcare-specific system prompt
HEALTHCARE_SYSTEM_PROMPT = """You are a helpful AI assistant for healthcare and social care professionals. 
You provide accurate, concise answers based on the care documentation provided to you.

Guidelines:
- Answer questions directly and professionally
- If information is not in the document, clearly state this
- Focus on care-relevant details like medications, procedures, and safety guidelines
- Use clear, professional language suitable for care workers
- Highlight any critical safety information

Base your responses strictly on the provided document content."""

def fetch_document_content(document_id):
    """Fetch document content from Document Service"""
    try:
        url = f"{app.config['DOCUMENT_SERVICE_URL']}/document/{document_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return {
                    'content': data.get('content'),
                    'filename': data.get('original_filename'),
                    'success': True
                }
        
        return {
            'success': False,
            'error': f"Failed to fetch document: {response.status_code}"
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Document service unavailable: {str(e)}"
        }

def generate_ai_response(question, document_content, document_filename):
    """Generate AI response using direct OpenAI API calls"""
    try:
        # Create user prompt with document context
        user_prompt = f"""Document: {document_filename}

Content:
{document_content}

Question: {question}

Please answer the question based on the document content above."""

        # Prepare OpenAI API request
        headers = {
            'Authorization': f'Bearer {app.config["OPENAI_API_KEY"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',  # Most cost-effective model
            'messages': [
                {'role': 'system', 'content': HEALTHCARE_SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            'max_tokens': 500,  # Limit tokens to control costs
            'temperature': 0.3,  # Lower temperature for focused responses
        }
        
        # Make direct HTTP request to OpenAI API
        response = requests.post(
            f'{app.config["OPENAI_API_BASE"]}/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            ai_answer = data['choices'][0]['message']['content'].strip()
            tokens_used = data['usage']['total_tokens']
            
            return {
                'success': True,
                'answer': ai_answer,
                'model_used': 'gpt-3.5-turbo',
                'tokens_used': tokens_used,
                'estimated_cost': tokens_used * 0.0015 / 1000  # Approximate cost calculation
            }
        else:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {'error': response.text}
            return {
                'success': False,
                'error': f"OpenAI API error ({response.status_code}): {error_data.get('error', {}).get('message', 'Unknown error')}"
            }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': f"Failed to connect to OpenAI API: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"AI processing failed: {str(e)}"
        }

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for service monitoring"""
    try:
        # Test environment configuration
        if not app.config['OPENAI_API_KEY']:
            raise Exception("OpenAI API key not configured")
        
        # Test Document Service connectivity
        doc_health_url = f"{app.config['DOCUMENT_SERVICE_URL']}/health"
        doc_response = requests.get(doc_health_url, timeout=5)
        
        if doc_response.status_code != 200:
            raise Exception("Document service unhealthy")
        
        return jsonify({
            'status': 'healthy',
            'service': 'ai-service',
            'document_service': 'connected',
            'openai_configured': bool(app.config['OPENAI_API_KEY']),
            'api_method': 'direct_http',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'ai-service',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/ask', methods=['POST'])
def ask_question():
    """Process questions about documents using AI"""
    try:
        # Validate request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        document_id = data.get('document_id')
        question = data.get('question')
        
        if not document_id or not question:
            return jsonify({
                'success': False,
                'error': 'Both document_id and question are required'
            }), 400
        
        # Fetch document content from Document Service
        doc_result = fetch_document_content(document_id)
        
        if not doc_result['success']:
            return jsonify({
                'success': False,
                'error': doc_result['error']
            }), 404
        
        # Generate AI response
        ai_result = generate_ai_response(
            question, 
            doc_result['content'], 
            doc_result['filename']
        )
        
        if not ai_result['success']:
            return jsonify({
                'success': False,
                'error': ai_result['error']
            }), 500
        
        # Return successful response
        return jsonify({
            'success': True,
            'answer': ai_result['answer'],
            'document_id': document_id,
            'document_filename': doc_result['filename'],
            'model_used': ai_result['model_used'],
            'tokens_used': ai_result['tokens_used'],
            'estimated_cost_usd': ai_result.get('estimated_cost', 0),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Request processing failed: {str(e)}'
        }), 500

@app.route('/models', methods=['GET'])
def list_models():
    """List available AI models and their cost information"""
    return jsonify({
        'success': True,
        'models': [
            {
                'name': 'gpt-3.5-turbo',
                'description': 'Fast, cost-effective model for Q&A',
                'cost_per_1k_tokens': 0.0015,
                'current_default': True
            }
        ],
        'cost_optimization': {
            'max_tokens': 500,
            'temperature': 0.3,
            'strategy': 'Focused responses to minimize token usage'
        },
        'api_method': 'direct_http'
    }), 200

if __name__ == '__main__':
    # Validate environment setup
    if not os.getenv('OPENAI_API_KEY'):
        print("WARNING: OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
    
    # Run Flask development server
    app.run(host='0.0.0.0', port=5100, debug=True) 