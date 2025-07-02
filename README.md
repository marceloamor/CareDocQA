# 🏥 CareDocQA — Document-Aware AI Assistant for Care Providers

A microservice-based web application that enables healthcare and social care professionals to upload care documentation and ask natural language questions about their contents, powered by large language models.

## 🎯 Project Purpose

This project serves as a technical demonstration for a **Founding Engineer role at Emma AI**, showcasing:

- **Microservice architecture design** using FastAPI and Flask
- **LLM integration** via LangChain and OpenAI
- **Full-stack development** with React/TypeScript frontend
- **Containerised deployment** using Docker Compose
- **Production-ready patterns** with proper service separation and API design

The system addresses a real problem in healthcare: enabling care workers to quickly extract information from documentation through conversational AI.

---

## 🧱 Architecture Overview

```
[React Frontend (3000)]
         │
         ▼
[API Gateway - FastAPI (8000)]
    ├──> [Document Service - Flask (5000)]
    └──> [AI Service - LangChain + OpenAI (5100)]
```

### Core Components

| Service | Technology | Purpose | Port |
|---------|------------|---------|------|
| **Frontend** | React + TypeScript | File upload UI and chat interface | 3000 |
| **API Gateway** | FastAPI | Request routing, validation, orchestration | 8000 |
| **Document Service** | Flask | Text file processing and storage | 5000 |
| **AI Service** | LangChain + OpenAI | Question answering via LLM | 5100 |

---

## 🔧 Technology Stack

- **Backend**: Python (FastAPI, Flask, LangChain)
- **Frontend**: React, TypeScript, Axios
- **LLM**: OpenAI GPT (via LangChain)
- **Storage**: Local filesystem + SQLite for metadata
- **Container Orchestration**: Docker Compose
- **Development**: Shared Python virtual environment

---

## 📂 Project Structure

```
CareDocQA/
├── .env                     # Environment variables and API keys
├── requirements.txt         # Python dependencies
├── venv/                   # Shared virtual environment
├── data/
│   ├── documents/          # Uploaded files stored by UUID
│   └── metadata.db         # SQLite database for document metadata
├── sample_documents/       # Healthcare sample files for testing
├── services/
│   ├── document-service/   # Flask service for file processing
│   ├── ai-service/         # LangChain + OpenAI service
│   └── api-gateway/        # FastAPI orchestration layer
├── frontend/               # React application
├── docker-compose.yml      # Container orchestration
└── README.md
```

---

## 🚀 Development Plan

### Development Order
1. **Document Service** (Flask) → File upload and storage
2. **AI Service** (LangChain) → Question answering functionality  
3. **API Gateway** (FastAPI) → Service orchestration
4. **Frontend** (React) → User interface
5. **Dockerisation** → Container deployment

### Development Approach
- **Local development first** for faster iteration and debugging
- **Dockerise after MVP completion** once all services integrate successfully
- **HTTP-based service communication** to mirror production patterns

---

## 📋 MVP Scope & Design Decisions

### ✅ MVP Features
- **Text file upload only** (.txt files, 1-5KB)
- **Single document Q&A** with no conversation history
- **Basic error handling** with friendly user messages
- **Local storage** with UUID-based document identification
- **Simple chat interface** (no message persistence across sessions)

### 🔄 Future Enhancements

| Feature | MVP Decision | Future Implementation |
|---------|--------------|----------------------|
| **File Types** | .txt only | PDF support with chunking strategies |
| **Large Documents** | Small files (<5KB) | Text chunking with overlap, vector embeddings |
| **Conversation History** | Session-based only | Persistent chat history with context management |
| **Storage** | Local filesystem + SQLite | Cloud storage (S3) + PostgreSQL |
| **Caching** | None | Redis for frequently asked questions |
| **Concurrency** | Single user | Message queues + worker pools |
| **Security** | Basic validation | Healthcare compliance, data encryption |
| **Observability** | Basic logging | Comprehensive monitoring and health checks |

---

## 🔌 API Design

### Document Service (Flask - Port 5000)
```
POST /upload        # Upload .txt file, return document UUID
GET  /document/{id} # Retrieve document content by UUID
GET  /health        # Health check endpoint
```

### AI Service (LangChain - Port 5100)
```
POST /ask          # Answer questions about documents
GET  /health       # Health check endpoint
```

### API Gateway (FastAPI - Port 8000)
```
POST /upload       # Proxy to document service
POST /ask          # Orchestrate document retrieval + AI query
GET  /health       # Aggregate health status
```

### Request/Response Format
```json
// Question Request
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "question": "What medication does Mrs Wilson take?"
}

// Question Response
{
  "success": true,
  "answer": "Mrs Wilson takes Levodopa/Carbidopa 100/25mg three times daily...",
  "document_title": "care_plan_mrs_wilson.txt"
}
```

---

## 🏗️ Implementation Details

### Document Storage Strategy
- **Files**: Stored in `data/documents/` with UUID filenames
- **Metadata**: SQLite database tracking upload timestamp, original filename, file size
- **Rationale**: Simple for MVP, clear migration path to cloud storage + PostgreSQL

### LangChain Integration
- **Document Loaders**: `TextLoader` for .txt files
- **QA Chain**: `load_qa_chain` with healthcare-specific system prompt
- **Retrieval**: Full document context (no chunking for MVP)
- **Prompt**: "You are a helpful assistant to care providers working in hospitals and care facilities..."

### Service Communication
- **HTTP requests** between services using container names
- **Graceful error handling** with user-friendly messages
- **Stateless design** for horizontal scalability

---

## 🔐 Configuration

### Environment Variables (.env)
```
OPENAI_API_KEY=your-openai-api-key-here
DOCUMENT_SERVICE_URL=http://localhost:5000
AI_SERVICE_URL=http://localhost:5100
```

### Healthcare Context
Sample documents include:
- Care plans (medication, mobility, nutrition)
- Shift notes and care logs
- Emergency procedures
- Safeguarding policies
- Dementia care guidelines

---

## 🧪 Testing Strategy

### Sample Questions for Demo
- "What medication does Mrs Wilson take?"
- "What should I do if there's a fire?"
- "How often should medication be administered?"
- "What are the signs of swallowing difficulties?"

### Development Testing
- Unit tests for document processing logic
- Integration tests for service communication
- Manual testing with healthcare sample documents

---

## 📈 Scalability Considerations

### Current Architecture Benefits
- **Microservice separation** enables independent scaling
- **Stateless services** support horizontal scaling
- **Clear service boundaries** facilitate team development
- **HTTP-based communication** enables language-agnostic services

### Production Migration Path
1. **Database**: SQLite → PostgreSQL/MongoDB
2. **Storage**: Local files → AWS S3/Google Cloud Storage  
3. **Orchestration**: Docker Compose → Kubernetes
4. **Monitoring**: Basic logging → Prometheus + Grafana
5. **Security**: Basic validation → OAuth, encryption, audit trails

---

## 🎯 Technical Demonstration Value

This project showcases:

| Skill Area | Demonstration |
|------------|---------------|
| **System Design** | Microservice architecture with clear separation of concerns |
| **Backend Development** | Multiple Python frameworks (FastAPI, Flask) with proper API design |
| **AI Integration** | LangChain orchestration and OpenAI integration |
| **Frontend Skills** | React/TypeScript with modern development practices |
| **DevOps** | Docker containerisation and service orchestration |
| **Healthcare Domain** | Understanding of care documentation and workflow needs |

---

*This project demonstrates production-ready thinking whilst maintaining MVP simplicity, showing the architectural foundation needed for a healthcare AI startup like Emma AI.* 