# 🏥 CareDocQA - Healthcare Document Q&A System

## 🎯 **Project Overview**

CareDocQA is a **microservice-based healthcare AI assistant** that demonstrates enterprise-level architecture for a technical interview. Healthcare professionals can upload care documents and ask natural language questions powered by GPT-3.5-turbo.

### **🏗️ Architecture - Perfect for Emma AI Interview**

```
Frontend (React)     ←→    API Gateway (FastAPI)    ←→    Microservices
Port 3000                     Port 8000                   Document: 5000
                                                         AI Service: 5100
```

**Key Interview Points:**
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
- Python 3.8+ 
- Node.js 18+
- OpenAI API key
```

### **1. Backend Services Setup**

```bash
# 1. Clone and setup Python environment
cd CareDocQA
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements-document-service.txt
pip install -r requirements-ai-service.txt  
pip install -r requirements-api-gateway.txt

# 2. Configure OpenAI API key
export OPENAI_API_KEY="your-openai-api-key-here"
```

### **2. Start Backend Services (3 Terminal Windows)**

**Terminal 1 - Document Service:**
```bash
source venv/bin/activate
cd services/document-service  
python app.py
# ✅ Running on http://localhost:5000
```

**Terminal 2 - AI Service:**
```bash
source venv/bin/activate
cd services/ai-service
python app.py  
# ✅ Running on http://localhost:5100
```

**Terminal 3 - API Gateway:**
```bash  
source venv/bin/activate
cd services/api-gateway
python app.py
# ✅ Running on http://localhost:8000
```

### **3. Start React Frontend**

**Terminal 4 - React App:**
```bash
cd frontend/care-doc-qa-frontend
npm install  # Only needed first time
npm start
# ✅ Running on http://localhost:3000
```

### **4. Test Complete System**
```bash
# Run comprehensive test
python test_frontend.py
```

---

## 🧠 **React for Python Developers - Complete Guide**

### **Core Concept Mappings**

| **Python/Flask Concept** | **React Equivalent** | **Example** |
|--------------------------|---------------------|-------------|
| `app.py` | `App.js` | Main application file |
| `@app.route()` | Component functions | Route handlers → Components |
| `render_template()` | `return <JSX>` | HTML templating |
| `request.form['name']` | `useState()` | Form data management |
| `requests.get/post()` | `axios.get/post()` | API calls |
| Jinja2 `{{ variable }}` | JSX `{variable}` | Variable interpolation |
| Flask sessions | `localStorage` | Client-side storage |

### **State Management = Python Variables with Auto-Updates**

```python
# Python/Flask - Manual updates
user_input = ""
documents = []
messages = []

def update_page():
    return render_template('index.html', 
                         input=user_input, 
                         docs=documents, 
                         msgs=messages)

# React - Automatic updates
const [userInput, setUserInput] = useState("");     // user_input = ""
const [documents, setDocuments] = useState([]);     // documents = []  
const [messages, setMessages] = useState([]);       // messages = []

// When you call setUserInput("new value"), UI automatically re-renders!
```

### **React Components = Python Functions**

```python
# Python function returning HTML
def render_upload_form(disabled=False):
    return f'''
    <div class="upload-section">
        <h3>Upload Document</h3>
        <input type="file" {'disabled' if disabled else ''}>
    </div>
    '''

# React component (same concept!)
const FileUpload = ({ disabled = false }) => (
    <div className="upload-section">
        <h3>Upload Document</h3>
        <input type="file" disabled={disabled} />
    </div>
);
```

### **useEffect = Flask Startup Functions**

```python  
# Flask - Run on app startup
@app.before_first_request
def startup():
    load_documents()
    check_health()
    setup_logging()

# React - Run when component loads
useEffect(() => {
    loadDocuments();
    checkHealth();
    setupLogging();
}, []); // Empty array = run once on startup
```

### **API Calls = Python requests**

```python
# Python requests
import requests

response = requests.post('http://localhost:8000/upload', 
                        files={'file': file})
data = response.json()

# React axios (identical concept!)
import axios from 'axios';

const response = await axios.post('/upload', formData);
const data = response.data;
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

## 🎯 **Interview Talking Points**

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

---

## 📞 **Support & Questions**

This project demonstrates enterprise-level microservice architecture with healthcare domain expertise, perfect for technical interviews in the AI/healthcare space.

**Key URLs:**
- 🌐 Frontend: http://localhost:3000
- 🚪 API Gateway: http://localhost:8000  
- 📄 Document Service: http://localhost:5000
- 🤖 AI Service: http://localhost:5100
- 📊 API Documentation: http://localhost:8000/docs

---

**Happy coding! 🚀 Perfect for Emma AI interview! 🏥** 