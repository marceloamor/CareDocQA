import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Incident Response API Gateway",
    description="AI-Enhanced Social Care Incident Response System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service configuration
INCIDENT_PROCESSOR_URL = os.getenv('INCIDENT_PROCESSOR_URL', 'http://localhost:5001')
SERVICE_TIMEOUT = 60  # Longer timeout for AI processing

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    session_context: Optional[Dict[str, Any]] = None

class TranscriptAnalysisRequest(BaseModel):
    transcript: str

class DocumentUpdateRequest(BaseModel):
    feedback: str
    document_type: str
    current_content: str
    all_documents: Dict[str, Any]

def call_incident_processor(endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
    """
    Call the incident processor service with error handling
    """
    url = f"{INCIDENT_PROCESSOR_URL}{endpoint}"
    
    try:
        logger.info(f"Calling incident processor: {method} {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=SERVICE_TIMEOUT, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, timeout=SERVICE_TIMEOUT, **kwargs)
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported HTTP method: {method}")
        
        logger.info(f"Incident processor responded with status {response.status_code}")
        
        if response.status_code >= 500:
            raise HTTPException(
                status_code=502, 
                detail=f"Incident processor error: {response.status_code}"
            )
        
        return {
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'success': 200 <= response.status_code < 300
        }
        
    except requests.exceptions.Timeout:
        logger.error("Timeout calling incident processor service")
        raise HTTPException(
            status_code=504, 
            detail="Incident processor service timeout"
        )
    except requests.exceptions.ConnectionError:
        logger.error("Connection error to incident processor service")
        raise HTTPException(
            status_code=503, 
            detail="Incident processor service unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling incident processor: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Internal error calling incident processor"
        )

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    System health check including incident processor service
    """
    health_status = {
        'api_gateway': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    overall_healthy = True
    
    # Check incident processor health
    try:
        result = call_incident_processor('/health', 'GET')
        health_status['incident_processor'] = result['data']
        if not result['success']:
            overall_healthy = False
    except Exception as e:
        health_status['incident_processor'] = {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        overall_healthy = False
    
    # Overall system status
    health_status['overall'] = {
        'status': 'healthy' if overall_healthy else 'degraded',
        'system': 'incident_response',
        'timestamp': datetime.now().isoformat()
    }
    
    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)

@app.post("/chat")
async def chat_about_policies(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat endpoint for policy questions and general interaction
    """
    logger.info(f"Processing chat message: {request.message[:50]}...")
    
    try:
        # Determine if this is a transcript or a question
        message = request.message.strip()
        
        # Simple heuristic: if message is very long or contains specific keywords, treat as transcript
        is_transcript = (
            len(message) > 500 or  # Long message likely to be transcript
            any(keyword in message.lower() for keyword in [
                'transcript', 'telephone call', 'greg jones', 'julie peaterson',
                'fallen again', 'on the floor', 'living room'
            ])
        )
        
        if is_transcript:
            # Process as transcript analysis
            result = call_incident_processor(
                '/analyze',
                'POST',
                json={'transcript': message}
            )
            
            if result['success']:
                # Format response for chat interface
                analysis_data = result['data']['analysis']
                
                chat_response = f"""📋 **INCIDENT ANALYSIS**

**Summary:** {analysis_data['analysis']['summary']}

**🚨 TRIGGERED POLICIES:**
"""
                
                for policy in analysis_data['analysis']['triggered_policies']:
                    chat_response += f"• **{policy['section']}**: {policy['reason']}\n"
                
                chat_response += f"""
**📝 REQUIRED ACTIONS:**
"""
                for action in analysis_data['analysis']['required_actions']:
                    chat_response += f"• {action}\n"
                
                chat_response += f"""
**📋 INCIDENT REPORT GENERATED:**
```json
{analysis_data['incident_report']}
```

**📧 EMAILS GENERATED:**
"""
                
                for email in analysis_data['emails']:
                    chat_response += f"""
**To: {email['recipient_type'].title()}**
Subject: {email['subject']}
Urgency: {email['urgency'].upper()}
{email['body'][:200]}...
---
"""
                
                return {
                    'success': True,
                    'message': chat_response,
                    'type': 'transcript_analysis',
                    'analysis_data': analysis_data,
                    'tokens_used': result['data'].get('tokens_used', 0),
                    'cost': result['data'].get('cost', 0)
                }
            else:
                raise HTTPException(
                    status_code=result['status_code'],
                    detail=result['data'].get('error', 'Transcript analysis failed')
                )
        
        else:
            # Process as policy question (potentially with context)
            request_data = {'question': message}
            
            # Include session context for follow-up questions
            if request.session_context and request.session_context.get('has_active_incident'):
                request_data['session_context'] = request.session_context
                
            result = call_incident_processor(
                '/chat',
                'POST',
                json=request_data
            )
            
            if result['success']:
                response_type = 'contextual_followup' if request.session_context else 'policy_question'
                return {
                    'success': True,
                    'message': result['data']['answer'],
                    'type': response_type,
                    'tokens_used': result['data'].get('tokens_used', 0),
                    'cost': result['data'].get('cost', 0)
                }
            else:
                raise HTTPException(
                    status_code=result['status_code'],
                    detail=result['data'].get('error', 'Policy question failed')
                )
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")

@app.post("/analyze")
async def analyze_transcript(request: TranscriptAnalysisRequest) -> Dict[str, Any]:
    """
    Direct transcript analysis endpoint
    """
    logger.info(f"Processing transcript analysis: {len(request.transcript)} characters")
    
    try:
        result = call_incident_processor(
            '/analyze',
            'POST',
            json={'transcript': request.transcript}
        )
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Transcript analysis failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcript analysis error: {e}")
        raise HTTPException(status_code=500, detail="Transcript analysis failed")

@app.post("/update")
async def update_documents(request: DocumentUpdateRequest) -> Dict[str, Any]:
    """
    Update generated documents based on user feedback
    """
    logger.info(f"Processing document update: {request.document_type}")
    
    try:
        result = call_incident_processor(
            '/update',
            'POST',
            json={
                'feedback': request.feedback,
                'document_type': request.document_type,
                'current_content': request.current_content,
                'all_documents': request.all_documents
            }
        )
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Document update failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document update error: {e}")
        raise HTTPException(status_code=500, detail="Document update failed")

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    API Gateway information endpoint
    """
    return {
        'service': 'Incident Response API Gateway',
        'description': 'AI-Enhanced Social Care Incident Response System',
        'version': '1.0.0',
        'endpoints': {
            '/health': 'System health check',
            '/chat': 'Chat about policies or analyze transcripts',
            '/analyze': 'Direct transcript analysis',
            '/update': 'Update generated documents',
            '/docs': 'API documentation'
        },
        'features': [
            'Policy-driven incident analysis',
            'Automated form generation',
            'Email drafting for required notifications',
            'Natural language policy Q&A',
            'Document editing with cross-document consistency'
        ],
        'timestamp': datetime.now().isoformat()
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom HTTP exception handler with structured error responses
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': exc.detail,
            'status_code': exc.status_code,
            'timestamp': datetime.now().isoformat()
        }
    )

if __name__ == '__main__':
    import uvicorn
    print("🌐 Starting Incident Response API Gateway...")
    print("🚀 Gateway running on http://localhost:8000")
    print("📚 API docs available at http://localhost:8000/docs")
    
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info') 