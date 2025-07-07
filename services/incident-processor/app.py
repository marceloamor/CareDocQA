import os
import json
import csv
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# Load environment variables from root directory
load_dotenv('../../.env')

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')
app.config['OPENAI_API_BASE'] = 'https://api.openai.com/v1'

# Load policy and form template on startup
POLICIES_PATH = '../../assignment_materials/Policies and Procedures Dev Task.txt'
FORM_TEMPLATE_PATH = '../../assignment_materials/Incident Report Form Dev Task - Sheet1.csv'

class IncidentProcessor:
    def __init__(self):
        self.policies_content = self._load_policies()
        self.form_template = self._load_form_template()
        
    def _load_policies(self) -> str:
        """Load the policies document into memory"""
        try:
            policies_path = os.path.join(os.path.dirname(__file__), POLICIES_PATH)
            with open(policies_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            app.logger.error(f"Policies file not found at {policies_path}")
            return ""
    
    def _load_form_template(self) -> List[Dict[str, str]]:
        """Load the incident report form template"""
        try:
            template_path = os.path.join(os.path.dirname(__file__), FORM_TEMPLATE_PATH)
            with open(template_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except FileNotFoundError:
            app.logger.error(f"Form template not found at {template_path}")
            return []
    
    def _call_openai(self, messages: List[Dict], max_tokens: int = 2000) -> Dict:
        """Make a call to OpenAI API"""
        try:
            headers = {
                'Authorization': f'Bearer {app.config["OPENAI_API_KEY"]}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'gpt-3.5-turbo',
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': 0.3,
            }
            
            response = requests.post(
                f'{app.config["OPENAI_API_BASE"]}/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'content': data['choices'][0]['message']['content'].strip(),
                    'tokens_used': data['usage']['total_tokens'],
                    'cost': data['usage']['total_tokens'] * 0.0015 / 1000
                }
            else:
                return {
                    'success': False,
                    'error': f"OpenAI API error: {response.status_code}"
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f"OpenAI API call failed: {str(e)}"
            }
    
    def analyze_transcript(self, transcript: str) -> Dict:
        """Analyze transcript against policies and generate required documents"""
        
        # Build comprehensive prompt for analysis
        analysis_prompt = f"""You are an AI assistant for social care incident response. 

POLICIES AND PROCEDURES:
{self.policies_content}

INCIDENT TRANSCRIPT:
{transcript}

INCIDENT REPORT FORM FIELDS:
{', '.join([field['Field'] for field in self.form_template])}

Please analyze this transcript and provide a structured response in the following JSON format:

{{
    "analysis": {{
        "summary": "Brief summary of what happened",
        "triggered_policies": [
            {{
                "section": "Section name and number",
                "reason": "Why this section is triggered",
                "requirements": ["List of required actions from this section"]
            }}
        ],
        "severity": "low|medium|high|critical",
        "required_actions": ["Overall list of all required actions"]
    }},
    "incident_report": {{
        "Date and Time of Incident": "2024-01-15T10:30:00",
        "Service User Name": "Name from transcript",
        "Location of Incident": "Location mentioned",
        "Type of Incident": "Type (fall, medical, etc)",
        "Description of the Incident": "Detailed description",
        "Immediate Actions Taken": "Actions taken during call",
        "Was First Aid Administered?": true/false,
        "Were Emergency Services Contacted?": true/false,
        "Who Was Notified?": "List of people notified",
        "Witnesses": "Any witnesses mentioned",
        "Agreed Next Steps": "Next steps planned",
        "Risk Assessment Needed": true/false,
        "If Yes, Which Risk Assessment": "Type if needed"
    }},
    "emails": [
        {{
            "recipient_type": "supervisor|risk_assessor|family",
            "subject": "Email subject line",
            "body": "Professional email content",
            "urgency": "low|medium|high|critical",
            "cc": ["List of CC recipients"]
        }}
    ]
}}

Ensure all responses are based strictly on the policies provided and the incident details in the transcript."""

        messages = [
            {"role": "system", "content": "You are a professional social care incident analysis AI. Provide accurate, policy-compliant responses in valid JSON format."},
            {"role": "user", "content": analysis_prompt}
        ]
        
        result = self._call_openai(messages, max_tokens=3000)
        
        if not result['success']:
            return {
                'success': False,
                'error': result['error']
            }
        
        try:
            # Parse the JSON response
            analysis_data = json.loads(result['content'])
            
            return {
                'success': True,
                'analysis': analysis_data,
                'tokens_used': result['tokens_used'],
                'cost': result['cost']
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Failed to parse AI response as JSON: {str(e)}",
                'raw_response': result['content']
            }
    
    def answer_policy_question(self, question: str) -> Dict:
        """Answer general questions about policies"""
        
        policy_prompt = f"""You are an AI assistant for social care policies and procedures.

POLICIES AND PROCEDURES:
{self.policies_content}

USER QUESTION: {question}

Please provide a helpful, accurate answer based on the policies above. Include specific section references where relevant."""

        messages = [
            {"role": "system", "content": "You are a knowledgeable social care policy advisor. Provide clear, accurate answers with policy references."},
            {"role": "user", "content": policy_prompt}
        ]
        
        result = self._call_openai(messages, max_tokens=1000)
        
        if not result['success']:
            return {
                'success': False,
                'error': result['error']
            }
        
        return {
            'success': True,
            'answer': result['content'],
            'tokens_used': result['tokens_used'],
            'cost': result['cost']
        }
    
    def update_document(self, feedback: str, document_type: str, current_content: str, all_documents: Dict) -> Dict:
        """Update a document based on user feedback and check for cross-document impacts"""
        
        update_prompt = f"""You are helping update incident response documents based on user feedback.

CURRENT {document_type.upper()}:
{current_content}

ALL CURRENT DOCUMENTS:
{json.dumps(all_documents, indent=2)}

USER FEEDBACK: {feedback}

Please:
1. Update the specified document based on the feedback
2. Analyze if this change requires updates to other documents for consistency
3. If yes, provide those updates too

Respond in JSON format:
{{
    "updated_document": "The updated {document_type} content",
    "requires_cross_updates": true/false,
    "cross_updates": [
        {{
            "document_type": "document name",
            "updated_content": "new content",
            "reason": "why this update is needed"
        }}
    ],
    "explanation": "Brief explanation of changes made"
}}"""

        messages = [
            {"role": "system", "content": "You are an AI assistant helping maintain consistency across incident response documents."},
            {"role": "user", "content": update_prompt}
        ]
        
        result = self._call_openai(messages, max_tokens=2000)
        
        if not result['success']:
            return {
                'success': False,
                'error': result['error']
            }
        
        try:
            update_data = json.loads(result['content'])
            
            return {
                'success': True,
                'updates': update_data,
                'tokens_used': result['tokens_used'],
                'cost': result['cost']
            }
            
        except json.JSONDecodeError as e:
            return {
                'success': False,
                'error': f"Failed to parse update response: {str(e)}",
                'raw_response': result['content']
            }

# Initialize the processor
processor = IncidentProcessor()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test OpenAI API key configuration
        if not app.config['OPENAI_API_KEY']:
            raise Exception("OpenAI API key not configured")
        
        # Test that policies and form template loaded
        if not processor.policies_content:
            raise Exception("Policies not loaded")
        
        if not processor.form_template:
            raise Exception("Form template not loaded")
        
        return jsonify({
            'status': 'healthy',
            'service': 'incident-processor',
            'policies_loaded': bool(processor.policies_content),
            'form_template_loaded': bool(processor.form_template),
            'openai_configured': bool(app.config['OPENAI_API_KEY']),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'service': 'incident-processor',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_incident():
    """Analyze a transcript for incident response"""
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data:
            return jsonify({
                'success': False,
                'error': 'Transcript is required'
            }), 400
        
        transcript = data['transcript']
        
        if not transcript.strip():
            return jsonify({
                'success': False,
                'error': 'Transcript cannot be empty'
            }), 400
        
        # Analyze the transcript
        result = processor.analyze_transcript(transcript)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500

@app.route('/chat', methods=['POST'])
def chat_about_policies():
    """Answer questions about policies"""
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                'success': False,
                'error': 'Question is required'
            }), 400
        
        question = data['question']
        
        if not question.strip():
            return jsonify({
                'success': False,
                'error': 'Question cannot be empty'
            }), 400
        
        # Answer the policy question
        result = processor.answer_policy_question(question)
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Chat error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Chat failed: {str(e)}'
        }), 500

@app.route('/update', methods=['POST'])
def update_documents():
    """Update documents based on user feedback"""
    try:
        data = request.get_json()
        
        required_fields = ['feedback', 'document_type', 'current_content', 'all_documents']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'{field} is required'
                }), 400
        
        result = processor.update_document(
            data['feedback'],
            data['document_type'], 
            data['current_content'],
            data['all_documents']
        )
        
        if not result['success']:
            return jsonify(result), 500
        
        return jsonify(result), 200
        
    except Exception as e:
        app.logger.error(f"Update error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Update failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🧠 Starting Incident Processor Service...")
    print(f"📋 Policies loaded: {'✅' if processor.policies_content else '❌'}")
    print(f"📝 Form template loaded: {'✅' if processor.form_template else '❌'}")
    print("🚀 Service running on http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True) 