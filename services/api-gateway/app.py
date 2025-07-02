import os
import requests
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CareDocQA API Gateway",
    description="Microservice orchestration layer for healthcare document Q&A system",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Service configuration
SERVICES = {
    'document': {
        'url': os.getenv('DOCUMENT_SERVICE_URL', 'http://localhost:5000'),
        'timeout': 30
    },
    'ai': {
        'url': os.getenv('AI_SERVICE_URL', 'http://localhost:5100'),
        'timeout': 60  # Longer timeout for AI processing
    }
}

def call_service(service_name: str, endpoint: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
    """
    Generic service caller with error handling and circuit breaker patterns
    """
    service_config = SERVICES.get(service_name)
    if not service_config:
        raise HTTPException(status_code=500, detail=f"Unknown service: {service_name}")
    
    url = f"{service_config['url']}{endpoint}"
    timeout = service_config['timeout']
    
    try:
        logger.info(f"Calling {service_name} service: {method} {url}")
        
        if method.upper() == 'GET':
            response = requests.get(url, timeout=timeout, **kwargs)
        elif method.upper() == 'POST':
            response = requests.post(url, timeout=timeout, **kwargs)
        else:
            raise HTTPException(status_code=500, detail=f"Unsupported HTTP method: {method}")
        
        # Log response for debugging
        logger.info(f"Service {service_name} responded with status {response.status_code}")
        
        if response.status_code >= 500:
            raise HTTPException(
                status_code=502, 
                detail=f"{service_name} service error: {response.status_code}"
            )
        
        return {
            'status_code': response.status_code,
            'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
            'success': 200 <= response.status_code < 300
        }
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout calling {service_name} service")
        raise HTTPException(
            status_code=504, 
            detail=f"{service_name} service timeout"
        )
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {service_name} service")
        raise HTTPException(
            status_code=503, 
            detail=f"{service_name} service unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error calling {service_name} service: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Internal error calling {service_name} service"
        )

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Aggregate health check across all microservices
    """
    health_status = {
        'api_gateway': {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
    }
    
    overall_healthy = True
    
    # Check each service health
    for service_name in SERVICES.keys():
        try:
            result = call_service(service_name, '/health', 'GET')
            health_status[f'{service_name}_service'] = result['data']
            if not result['success']:
                overall_healthy = False
        except Exception as e:
            health_status[f'{service_name}_service'] = {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            overall_healthy = False
    
    # Overall system status
    health_status['overall'] = {
        'status': 'healthy' if overall_healthy else 'degraded',
        'services_count': len(SERVICES),
        'healthy_services': sum(1 for k, v in health_status.items() 
                               if k.endswith('_service') and v.get('status') == 'healthy'),
        'timestamp': datetime.now().isoformat()
    }
    
    status_code = 200 if overall_healthy else 503
    return JSONResponse(content=health_status, status_code=status_code)

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Upload document via Document Service
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validate file type at gateway level
    if not file.filename.endswith('.txt'):
        raise HTTPException(
            status_code=400, 
            detail="Only .txt files are allowed"
        )
    
    try:
        # Prepare file for forwarding to Document Service
        files = {'file': (file.filename, await file.read(), file.content_type)}
        
        result = call_service('document', '/upload', 'POST', files=files)
        
        if result['success']:
            logger.info(f"Document uploaded successfully: {result['data'].get('document_id')}")
            return result['data']
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Upload failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload processing error: {e}")
        raise HTTPException(status_code=500, detail="Upload processing failed")

@app.post("/ask")
async def ask_question(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestrate document Q&A: validate request, then call AI Service
    This demonstrates microservice orchestration patterns
    """
    # Request validation
    document_id = request_data.get('document_id')
    question = request_data.get('question')
    
    if not document_id or not question:
        raise HTTPException(
            status_code=400,
            detail="Both 'document_id' and 'question' are required"
        )
    
    logger.info(f"Processing question for document {document_id}: {question[:50]}...")
    
    try:
        # Call AI Service (which will internally call Document Service)
        result = call_service(
            'ai', 
            '/ask', 
            'POST', 
            json={'document_id': document_id, 'question': question}
        )
        
        if result['success']:
            # Enhance response with gateway metadata
            response_data = result['data']
            response_data['processed_by'] = 'api-gateway'
            response_data['processing_time'] = datetime.now().isoformat()
            
            logger.info(f"Question processed successfully. Tokens used: {response_data.get('tokens_used', 'unknown')}")
            return response_data
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Question processing failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Question processing error: {e}")
        raise HTTPException(status_code=500, detail="Question processing failed")

@app.get("/documents")
async def list_documents() -> Dict[str, Any]:
    """
    List all documents via Document Service
    """
    try:
        result = call_service('document', '/documents', 'GET')
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Failed to list documents')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document listing error: {e}")
        raise HTTPException(status_code=500, detail="Document listing failed")

@app.get("/models")
async def list_ai_models() -> Dict[str, Any]:
    """
    Get AI model information via AI Service
    """
    try:
        result = call_service('ai', '/models', 'GET')
        
        if result['success']:
            return result['data']
        else:
            raise HTTPException(
                status_code=result['status_code'],
                detail=result['data'].get('error', 'Failed to get model info')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model info error: {e}")
        raise HTTPException(status_code=500, detail="Model info retrieval failed")

@app.get("/")
async def root() -> Dict[str, Any]:
    """
    API Gateway information and available endpoints
    """
    return {
        'service': 'CareDocQA API Gateway',
        'version': '1.0.0',
        'status': 'running',
        'architecture': 'microservices',
        'services': {
            'document_service': SERVICES['document']['url'],
            'ai_service': SERVICES['ai']['url']
        },
        'endpoints': {
            'upload': 'POST /upload - Upload healthcare documents',
            'ask': 'POST /ask - Ask questions about documents',
            'documents': 'GET /documents - List all documents',
            'models': 'GET /models - Get AI model information',
            'health': 'GET /health - System health status',
            'docs': 'GET /docs - Interactive API documentation'
        },
        'timestamp': datetime.now().isoformat()
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Global exception handler for consistent error responses
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'success': False,
            'error': exc.detail,
            'timestamp': datetime.now().isoformat(),
            'gateway': 'api-gateway'
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    # Validate service configuration
    for service_name, config in SERVICES.items():
        logger.info(f"Configured {service_name} service: {config['url']}")
    
    # Run FastAPI with uvicorn
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    ) 