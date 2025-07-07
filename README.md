# 🏥 CareDocQA - Healthcare Document Q&A System

## 🎯 **Project Overview**

CareDocQA is a **microservice-based healthcare AI assistant** that demonstrates enterprise-level architecture. Healthcare professionals can upload care documents and ask natural language questions powered by GPT-3.5-turbo.

### **🏗️ System Architecture**

```
Frontend (React)     ←→    API Gateway (FastAPI)    ←→    Microservices
Port 3000                     Port 8000                   Document: 5000
                                                         AI Service: 5100
```

**Key Technical Features:**
- ✅ **Microservice Architecture** - Service separation & communication
- ✅ **API Gateway Pattern** - Request orchestration & routing  
- ✅ **Full-Stack Development** - React frontend + Python backend
- ✅ **Healthcare Domain** - Real-world care document processing
- ✅ **LLM Integration** - OpenAI GPT with cost tracking
- ✅ **Database Integration** - SQLite with file management
- ✅ **Modern UI/UX** - Professional healthcare interface

---

## 🚀 **Quick Start Guide**

### **Prerequisites**
```bash
# Required software
- Python 3.11+ 
- Node.js 18+
- OpenAI API key
```

### **1. One-Command Setup & Start**

```bash
# 1. Clone and setup environment
git clone https://github.com/marceloamor/CareDocQA
cd CareDocQA
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# 2. Configure OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"

# 3. Start entire system (all 4 services automatically)
./start_careDocQA.sh
```

**That's it! The start script automatically:**
- ✅ Checks all prerequisites 
- ✅ Installs npm dependencies if needed
- ✅ Starts all 4 services in correct order
- ✅ Waits for each service to be ready
- ✅ Provides comprehensive monitoring

**Services will be running on:**
- 🏥 **React Frontend**: http://localhost:3000
- 🌐 **API Gateway**: http://localhost:8000 
- 🤖 **AI Service**: http://localhost:5100
- 📄 **Document Service**: http://localhost:5000

### **2. Alternative: Manual Service Start (Development)**

If you prefer to run services individually for development:

```bash
# Terminal 1 - Document Service
source venv/bin/activate && cd services/document-service && python app.py

# Terminal 2 - AI Service  
source venv/bin/activate && cd services/ai-service && python app.py

# Terminal 3 - API Gateway
source venv/bin/activate && cd services/api-gateway && python app.py

# Terminal 4 - React Frontend
cd frontend/care-doc-qa-frontend && npm start
```

### **3. Test Complete System**
```bash
# Run comprehensive end-to-end test
python test_frontend.py
```

---

## 🏥 **Healthcare Features & Use Cases**

### **Document Types Supported**
- **Care Plans** - Patient medication schedules, treatment plans
- **Emergency Procedures** - Fire safety, medical emergencies  
- **Guidelines** - Dementia care, safeguarding policies
- **Shift Notes** - Staff handover documentation

### **Sample Questions to Try**
```
🩺 "What medications does Mrs Wilson take?"
🚨 "What should I do if there's a fire emergency?"  
🧠 "How should I communicate with dementia patients?"
💊 "What are the side effects of this medication?"
🏥 "What is the procedure for patient handover?"
```

### **AI Cost Tracking**
- Real-time token usage monitoring
- Cost estimation per query ($0.0005 average)
- Daily spend tracking with localStorage persistence

---

## 📁 **Project Structure**

```
CareDocQA/
├── 🏥 services/               # Backend microservices
│   ├── document-service/      # File & database management
│   ├── ai-service/           # OpenAI integration  
│   └── api-gateway/          # Request orchestration
├── ⚛️ frontend/               # React application
│   └── care-doc-qa-frontend/  # Healthcare UI
├── 📄 sample_documents/       # Test healthcare documents
├── 🧪 test_frontend.py        # End-to-end system test
└── 📋 README.md              # This file
```

---

## 🔧 **Development Tips**

### **React Development Server**
```bash
# Auto-reload on file changes
npm start

# Build for production  
npm run build

# Run tests
npm test
```

### **Python Service Development**
```bash
# All services have auto-reload enabled
# Edit files and see changes immediately

# View service logs
tail -f services/*/app.log
```

### **API Testing**
```bash
# Test individual services
curl http://localhost:5000/health  # Document service
curl http://localhost:5100/health  # AI service  
curl http://localhost:8000/health  # API Gateway

# Upload document via API
curl -X POST -F "file=@sample_documents/care_plan.txt" \
     http://localhost:8000/upload
```

---

## 🎯 **Technical Highlights**

### **Microservice Benefits Demonstrated**
1. **Service Independence** - Each service can be deployed/scaled separately
2. **Technology Diversity** - FastAPI + Flask + React showcase
3. **Fault Tolerance** - Gateway handles service failures gracefully  
4. **Clear Separation** - Document storage vs AI processing vs UI

### **Full-Stack Skills Shown**
1. **Frontend** - Modern React with hooks, state management, responsive design
2. **Backend** - RESTful APIs, database integration, external service calls
3. **DevOps** - Multi-service orchestration, health monitoring, logging
4. **Domain Knowledge** - Healthcare workflows and terminology

### **Healthcare AI Application**
1. **Document Processing** - Healthcare document upload and storage
2. **Natural Language** - Questions in plain English about care procedures  
3. **Cost Management** - AI usage tracking for budget control
4. **Professional UI** - Healthcare-appropriate interface design

### **Architectural Design for RAG Extension**
The current **UUID-based document selection** architecture was deliberately chosen to facilitate future **RAG (Retrieval-Augmented Generation)** implementation:

- **Current Approach**: Users select specific documents before querying, sending only relevant content to the LLM
- **RAG Compatibility**: This mimics how RAG systems work - retrieving specific relevant documents rather than sending entire document collections
- **Scalability**: An architecture that sends all documents to the LLM would hit context window limits and be difficult to extend to RAG
- **Easy Migration Path**: The existing document selection pattern directly translates to RAG document retrieval, requiring minimal architectural changes

This design demonstrates **forward-thinking system architecture** that anticipates scaling challenges and emerging AI patterns.

---

## 🚀 **Next Steps for Production**

### **Scalability Enhancements**
- Docker containerization with docker-compose
- Load balancing with multiple service instances
- Redis for session management and caching
- PostgreSQL for production database

### **Security Improvements**  
- JWT authentication and authorization
- HTTPS with SSL certificates
- Input validation and sanitization
- API rate limiting

### **Healthcare Compliance**
- HIPAA compliance measures
- Audit logging for document access
- Data encryption at rest and in transit
- User access controls and permissions


**Key URLs:**
- 🌐 Frontend: http://localhost:3000
- 🚪 API Gateway: http://localhost:8000  
- 📄 Document Service: http://localhost:5000
- 🤖 AI Service: http://localhost:5100
- 📊 API Documentation: http://localhost:8000/docs

---

**Technical demonstration ready for production deployment and enterprise scaling.** 