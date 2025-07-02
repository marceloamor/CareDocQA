#!/usr/bin/env python3
"""
CareDocQA Frontend Testing Script
Demonstrates the complete microservice system integration
"""

import requests
import time
import json
from pathlib import Path

# API Gateway endpoint
API_BASE = "http://localhost:8000"

def test_system_health():
    """Test system health - like checking if Flask app is running"""
    print("🏥 Testing System Health...")
    try:
        response = requests.get(f"{API_BASE}/health")
        health_data = response.json()
        
        print(f"✅ System Status: {health_data['overall']['status']}")
        print(f"📊 Healthy Services: {health_data['overall']['healthy_services']}/{health_data['overall']['services_count']}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_document_upload():
    """Test document upload - like testing Flask file upload"""
    print("\n📄 Testing Document Upload...")
    
    # Use one of our sample documents
    sample_doc = Path("sample_documents/emergency_procedures.txt")
    
    if not sample_doc.exists():
        print(f"❌ Sample document not found: {sample_doc}")
        return None
    
    try:
        with open(sample_doc, 'rb') as file:
            files = {'file': (sample_doc.name, file, 'text/plain')}
            response = requests.post(f"{API_BASE}/upload", files=files)
            
            if response.status_code == 200:
                data = response.json()
                doc_id = data['document_id']
                print(f"✅ Document uploaded successfully!")
                print(f"📄 Document ID: {doc_id}")
                print(f"📁 Filename: {data['original_filename']}")
                print(f"💾 Size: {data['file_size']} bytes")
                return doc_id
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"Error: {response.text}")
                return None
                
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return None

def test_ai_question(document_id):
    """Test AI questioning - like testing Flask API endpoint"""
    print("\n🤖 Testing AI Question...")
    
    question = "What should I do if there is a fire emergency?"
    
    try:
        response = requests.post(f"{API_BASE}/ask", json={
            'document_id': document_id,
            'question': question
        })
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ AI Question processed successfully!")
            print(f"❓ Question: {question}")
            print(f"🤖 Answer: {data['answer'][:200]}...")
            print(f"🎯 Tokens used: {data['tokens_used']}")
            print(f"💰 Cost: ${data['estimated_cost_usd']:.6f}")
            print(f"🧠 Model: {data['model_used']}")
            return True
        else:
            print(f"❌ Question failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Question error: {e}")
        return False

def test_document_list():
    """Test document listing - like testing Flask GET endpoint"""
    print("\n📋 Testing Document List...")
    
    try:
        response = requests.get(f"{API_BASE}/documents")
        
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            print(f"✅ Found {len(documents)} documents:")
            
            for doc in documents:
                print(f"  📄 {doc['original_filename']} ({doc['file_size']} bytes)")
                
            return True
        else:
            print(f"❌ Document list failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Document list error: {e}")
        return False

def check_react_frontend():
    """Check if React frontend is accessible"""
    print("\n⚛️  Testing React Frontend...")
    
    try:
        response = requests.get("http://localhost:3000")
        if response.status_code == 200:
            print("✅ React frontend is running!")
            print("🌐 Access your app at: http://localhost:3000")
            return True
        else:
            print(f"❌ React frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ React frontend error: {e}")
        print("💡 Make sure to run: npm start")
        return False

def main():
    """
    Complete system test - like testing a Flask app end-to-end
    This demonstrates the full microservice architecture
    """
    print("🚀 CareDocQA Full-Stack System Test")
    print("=" * 50)
    
    # Test backend services
    if not test_system_health():
        print("\n❌ Backend services not healthy. Please start:")
        print("1. Document Service: cd services/document-service && python app.py")
        print("2. AI Service: cd services/ai-service && python app.py") 
        print("3. API Gateway: cd services/api-gateway && python app.py")
        return
    
    # Test React frontend
    frontend_ok = check_react_frontend()
    
    # Test core functionality
    document_id = test_document_upload()
    if document_id:
        test_ai_question(document_id)
    
    test_document_list()
    
    print("\n🎉 System Test Complete!")
    print("\n📋 Next Steps:")
    print("1. ✅ Backend services are running")
    if frontend_ok:
        print("2. ✅ Frontend is accessible at: http://localhost:3000")
    else:
        print("2. ❌ Start frontend: npm start")
    print("3. 🌐 Open http://localhost:3000 in your browser")
    print("4. 📄 Upload a healthcare document")
    print("5. ❓ Ask questions about the document")
    
    print("\n🏥 Healthcare Use Cases to Try:")
    print("- Upload care_plan_mrs_wilson.txt and ask: 'What medications does Mrs Wilson take?'")
    print("- Upload emergency_procedures.txt and ask: 'What should I do if someone falls?'")
    print("- Upload dementia_care_guidelines.txt and ask: 'How should I communicate with dementia patients?'")

if __name__ == "__main__":
    main() 