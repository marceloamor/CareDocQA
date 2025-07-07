# 🏥 AI-Enhanced Incident Response System
### Emma AI - Founding Engineer Assessment Submission

---

## 📋 **Quick Start**

```bash
git clone <repository-url>
cd CareDocQA
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Add your OpenAI API key to .env file
echo "OPENAI_API_KEY=your-openai-api-key-here" > .env

# Start the complete system
./start_assessment.sh
```

**🌐 Access the system at:** http://localhost:3000

---

## 🚀 **System Overview**

This is a sophisticated **AI-Enhanced Incident Response System** built for social care organisations. It analyses call transcripts against organisational policies, generates compliance reports, creates incident documentation, and drafts appropriate notifications—all powered by **GPT-4o** for superior reasoning and analysis.

### **🎯 Core Capabilities:**
- **📞 Transcript Analysis**: Smart detection and processing of call transcripts
- **📋 Policy Compliance**: Automatic analysis against loaded care policies  
- **📝 Document Generation**: Professional incident reports and forms
- **📧 Email Drafting**: Contextual notifications to supervisors, families, and assessors
- **💬 Contextual Conversations**: Follow-up questions with session memory
- **✏️ Natural Language Editing**: Improve generated documents with feedback
- **🔄 Cross-Document Consistency**: Updates maintain coherence across all documents

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   React SPA     │───▶│   API Gateway    │───▶│ Incident Processor  │
│  (Port 3000)    │    │   (Port 8000)    │    │    (Port 5001)      │
│                 │    │                  │    │                     │
│ • Chat Interface│    │ • Request Routing│    │ • GPT-4o Integration│
│ • Session Context│   │ • Service Health │    │ • Policy Analysis   │
│ • Document Edit │    │ • CORS Handling  │    │ • Form Generation   │
│ • Auto-scroll   │    │ • Error Handling │    │ • Email Drafting    │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

### **Technology Stack:**
- **Frontend**: React 18 with modern hooks and context management
- **Backend**: FastAPI (API Gateway) + Flask (Incident Processor)  
- **AI**: OpenAI GPT-4o with structured JSON responses
- **Styling**: Custom CSS with healthcare-focused design
- **Deployment**: One-command startup with health monitoring

---

## ✨ **Key Features**

### **🧠 Intelligent Session Management**
- **Contextual Memory**: System remembers previous transcript analysis
- **Follow-up Questions**: Ask "Should we notify the family?" after incident analysis
- **Session Indicators**: Clear UI showing when context is active
- **Fresh Start**: Page refresh clears session for new scenarios

### **📋 Advanced Document Processing**
- **Smart Detection**: Automatically identifies transcripts vs policy questions
- **Structured Generation**: Clean, professional incident reports
- **Complete Email Content**: No truncation, full professional emails
- **Natural Language Editing**: "Make this more urgent" or "Add family contact details"

### **🎨 Professional UI/UX**
- **Resizable Components**: Chat and input areas resize like text editors
- **Auto-scrolling Chat**: Immediately shows AI responses
- **Loading States**: Professional spinner with appropriate messaging
- **Visual Context**: Session state clearly indicated
- **Cost Tracking**: Real-time OpenAI usage monitoring

### **🔧 Production-Ready Features**
- **Health Monitoring**: All services report status and readiness
- **Error Handling**: Graceful degradation with informative messages
- **Logging**: Comprehensive request/response logging
- **Service Discovery**: Automatic health checks and status aggregation
- **Mobile Responsive**: Works on tablets and phones

---

## 📖 **How to Use**

### **1. Basic Policy Questions**
```
Type: "What should I do if someone falls repeatedly?"
→ Get comprehensive policy guidance with references
```

### **2. Transcript Analysis**
```
Paste: "Julie: Good morning, how can I help you?
        Greg: Hi, I've fallen again this week..."
→ Get full incident analysis, forms, and email drafts
```

### **3. Follow-up Questions**
```
After transcript analysis, ask:
"Should we also notify the family?"
"What other assessments are needed?"
→ Contextual responses considering the specific incident
```

### **4. Document Editing**
```
Click "Edit Documents" on any analysis
Provide feedback: "Make the email more urgent"
→ AI updates documents maintaining consistency
```

---

## 🎯 **Assignment Requirements Fulfilled**

| Requirement | Implementation | Status |
|-------------|----------------|--------|
| **Backend (Python/FastAPI)** | API Gateway + Incident Processor | ✅ |
| **Receive transcript data** | Smart input detection via chat/upload | ✅ |
| **Analyze against policies** | GPT-4o policy analysis with triggers | ✅ |
| **Generate incident forms** | Structured 13-field incident reports | ✅ |
| **Draft emails** | Professional emails to all stakeholders | ✅ |
| **Extensive OpenAI usage** | GPT-4o for all AI operations | ✅ |
| **Fallback mechanisms** | Error handling with graceful degradation | ✅ |
| **React frontend** | Modern SPA with professional UI | ✅ |
| **Input/paste call data** | Multiple input methods with auto-detection | ✅ |
| **Display forms and emails** | Clean, formatted document display | ✅ |
| **Clear comments** | Professional code documentation | ✅ |
| **Error handling & logging** | Comprehensive error management | ✅ |
| **Bonus: User feedback** | Natural language document editing | ✅ |
| **Bonus: Cross-document consistency** | Maintains coherence across updates | ✅ |

---

## 📁 **Project Structure**

```
CareDocQA/
├── 🧠 services/
│   ├── api-gateway/           # FastAPI service orchestration
│   └── incident-processor/    # Flask AI analysis service
├── ⚛️ frontend/
│   └── care-doc-qa-frontend/  # React application
├── 📄 assignment_materials/   # Policies, transcript, form template
├── 🔧 venv/                  # Python virtual environment
├── 📊 logs/                  # Service logs (auto-generated)
├── ⚙️ .env                   # Environment configuration
├── 📋 requirements.txt       # Python dependencies
├── 🚀 start_assessment.sh    # One-command startup script
└── 🧹 kill_ports.sh         # Cleanup script
```

---

## 🌟 **Alternative Demonstration**

This repository also contains a **complete healthcare document Q&A system** on a separate branch that demonstrates broader microservice architecture capabilities.

### **🔍 Explore the Full System**
```bash
git checkout full-careDocQA-system
./start_careDocQA.sh
```

**The full system demonstrates:**
- 🏗️ **4-service microservice architecture**
- 🗄️ **Document storage and retrieval**
- 🔍 **Semantic search across healthcare documents**
- 📊 **Advanced monitoring and analytics**
- 🐳 **Docker containerisation readiness**

---

## 🔧 **Development**

### **Prerequisites**
- Python 3.8+
- Node.js 18+
- OpenAI API key

### **Service Ports**
- **React Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **Incident Processor**: http://localhost:5001
- **API Documentation**: http://localhost:8000/docs

### **Logs & Debugging**
```bash
# Check service logs
tail -f logs/api-gateway.log
tail -f logs/incident-processor.log
tail -f logs/react-frontend.log

# Stop all services
./kill_ports.sh
```

---

## 💡 **Technical Highlights**

### **Advanced AI Integration**
- **GPT-4o Model**: Latest OpenAI model for superior reasoning
- **Structured Responses**: Reliable JSON output with markdown handling
- **Cost Optimization**: Precise token tracking and cost calculation
- **Context Management**: Session-aware conversations

### **Professional Frontend**
- **Modern React**: Hooks, refs, and proper state management
- **Responsive Design**: Works across devices and screen sizes
- **User Experience**: Auto-scroll, resize handles, loading states
- **Healthcare UI**: Professional design patterns for care environments

### **Robust Backend**
- **Service Orchestration**: Clean separation of concerns
- **Health Monitoring**: Comprehensive system status tracking
- **Error Resilience**: Graceful failure handling
- **Scalable Architecture**: Ready for production deployment

---

## 📞 **Questions or Feedback**

This system demonstrates both **specific problem-solving** for the assignment requirements and **broader technical capabilities** for building production-grade healthcare AI systems.

**Ready for your Emma AI founding engineer interview!** 🚀 