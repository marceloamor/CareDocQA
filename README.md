# 🏥 AI-Enhanced Incident Response System
### Emma AI - Take Home Assessment Submission

---

## 📋 **Quick Start for Assessment Review**

This repository contains my **Emma AI founding engineer assessment submission**. The assignment required building an AI-enhanced incident response system for social care.

### **🚀 Run the Assessment Submission**
```bash
git clone https://github.com/marceloamor/CareDocQA
cd CareDocQA
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-api-key"
./start_assessment.sh
```

**System will be available at:** http://localhost:3000

---

## 🎯 **Assignment Requirements Met**

### **Core Functionality:**
- ✅ **Process social care call transcripts**
- ✅ **Analyse transcripts against policies** 
- ✅ **Generate incident forms automatically**
- ✅ **Draft emails to appropriate personnel**
- ✅ **React frontend for input/display**
- ✅ **FastAPI backend with OpenAI integration**
- ✅ **Error handling and logging**
- ✅ **Fallback mechanisms & fact-checking**

### **Bonus Features:**
- ✅ **User feedback system for AI content editing**
- ✅ **Innovative features**: Real-time policy compliance scoring, automated escalation workflows

---

## 🌟 **Beyond the Assignment: Full System Demonstration**

I've also built a **complete healthcare document Q&A microservice system** that demonstrates broader technical capabilities relevant to Emma AI's mission.

### **🔍 Explore the Full System**
```bash
git checkout full-careDocQA-system
./start_careDocQA.sh
```

**The full system demonstrates:**
- 🏗️ **Microservice architecture** (4 independent services)
- 🌐 **API Gateway pattern** with service orchestration  
- ⚛️ **Production-ready React frontend** with healthcare-specific UI
- 🤖 **Scalable AI integration** with cost tracking
- 📊 **Health monitoring and logging** across all services
- 🔧 **Professional DevOps tooling** (startup scripts, port management, testing)

---

## 🏥 **Healthcare Domain Expertise**

Both implementations showcase understanding of:
- **Social care workflows** and incident response processes
- **Policy compliance** and safeguarding requirements  
- **Professional healthcare UI/UX** design patterns
- **Care documentation** standards and formats
- **Real-world deployment** considerations for care providers

---

## 📁 **Repository Structure**

```
CareDocQA/
├── 🎯 services/                   # Assignment submission
│   ├── incident-service/          # Policy analysis & form generation
│   ├── email-service/             # Draft email generation
│   └── api-gateway/              # FastAPI orchestration
├── ⚛️ frontend/                   # React incident response UI
├── 📄 assignment_materials/       # Provided transcript & policies
├── 🧪 start_assessment.sh         # One-command assessment startup
└── 📋 README.md                  # This file
```

---

## 💡 **Technical Highlights**

### **Assignment-Specific Innovation:**
- **Smart policy matching** using semantic similarity
- **Context-aware form generation** based on incident severity
- **Automated escalation routing** based on policy requirements
- **Real-time compliance scoring** during transcript analysis

### **Broader System Architecture:**
- **Service isolation** for independent scaling
- **Event-driven communication** between microservices
- **Centralised logging** and health monitoring
- **Production deployment patterns** (Docker-ready, load balancer compatible)

---

## 🚀 **Getting Started**

### **Option 1: Review Assignment Submission (Recommended First)**
```bash
# Clone and run the assignment submission
./start_assessment.sh
# Visit http://localhost:3000
```

### **Option 2: Explore Full System Architecture**
```bash
# Switch to full system branch
git checkout full-careDocQA-system
./start_careDocQA.sh  
# Visit http://localhost:3000
```

---

## 📞 **Contact**

For any questions about the implementation or to discuss the technical decisions, please reach out!

**This demonstrates both targeted problem-solving for specific requirements and broader technical vision for scalable healthcare AI systems.** 