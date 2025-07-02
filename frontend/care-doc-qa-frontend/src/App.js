import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Upload, MessageCircle, FileText, Heart, AlertTriangle, DollarSign } from 'lucide-react';
import './App.css';

// Think of this like a Flask app with multiple routes
// Each component is like a different route handler function
function App() {
  // STATE MANAGEMENT - like Python variables that trigger UI updates
  // In Flask/Dash, changing a variable and returning it updates the display
  // In React, useState() does the same thing automatically
  
  const [documents, setDocuments] = useState([]);           // Like: documents = []
  const [selectedDocument, setSelectedDocument] = useState(null);  // Like: selected_doc = None
  const [question, setQuestion] = useState('');             // Like: question = ""
  const [messages, setMessages] = useState([]);             // Like: messages = []
  const [isLoading, setIsLoading] = useState(false);        // Like: is_loading = False
  const [systemHealth, setSystemHealth] = useState(null);   // Like: health = None
  const [totalCost, setTotalCost] = useState(0);           // Like: total_cost = 0.0

  // API BASE URL - like your Flask app URL
  const API_BASE = 'http://localhost:8000';

  // LIFECYCLE HOOK - like @app.before_first_request in Flask
  // This runs when the component first loads (like app startup)
  useEffect(() => {
    loadDocuments();
    checkSystemHealth();
    
    // Load saved cost from localStorage (like session storage)
    const savedCost = localStorage.getItem('totalCost');
    if (savedCost) {
      setTotalCost(parseFloat(savedCost));
    }
  }, []); // Empty array means "run once on startup"

  // API FUNCTIONS - like Python requests.get/post functions
  
  const loadDocuments = async () => {
    // This is like: response = requests.get(f"{base_url}/documents")
    try {
      const response = await axios.get(`${API_BASE}/documents`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
      addMessage('system', 'Failed to load documents. Please check if services are running.');
    }
  };

  const checkSystemHealth = async () => {
    // Like: health_response = requests.get(f"{base_url}/health")
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ overall: { status: 'unhealthy' } });
    }
  };

  const uploadDocument = async (file) => {
    // Like: requests.post(url, files={'file': file})
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setIsLoading(true);
      const response = await axios.post(`${API_BASE}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      addMessage('system', `Document "${file.name}" uploaded successfully!`);
      loadDocuments(); // Refresh the document list
    } catch (error) {
      console.error('Upload failed:', error);
      addMessage('system', `Upload failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const askQuestion = async () => {
    if (!selectedDocument || !question.trim()) {
      addMessage('system', 'Please select a document and enter a question.');
      return;
    }

    // Add user message to chat
    addMessage('user', question);
    const currentQuestion = question;
    setQuestion(''); // Clear input
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/ask`, {
        document_id: selectedDocument.document_id,
        question: currentQuestion
      });

      const data = response.data;
      
      // Add AI response to chat
      addMessage('ai', data.answer, {
        document: data.document_filename,
        tokens: data.tokens_used,
        cost: data.estimated_cost_usd,
        model: data.model_used
      });

      // Update total cost
      const newCost = totalCost + (data.estimated_cost_usd || 0);
      setTotalCost(newCost);
      localStorage.setItem('totalCost', newCost.toString());

    } catch (error) {
      console.error('Question failed:', error);
      addMessage('system', `Question failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  // UTILITY FUNCTION 
  const addMessage = (type, content, metadata = null) => {
    const newMessage = {
      id: Date.now(),
      type, // 'user', 'ai', 'system'
      content,
      metadata,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]); 
  };

  // FILE UPLOAD COMPONENT - like a Flask form handler
  const FileUpload = () => (
    <div className="upload-section">
      <h3><FileText size={20} /> Upload Healthcare Document</h3>
      <div className="upload-area">
        <input
          type="file"
          accept=".txt"
          onChange={(e) => {
            if (e.target.files[0]) {
              uploadDocument(e.target.files[0]);
            }
          }}
          disabled={isLoading}
        />
        <p>Upload .txt files containing care plans, procedures, or guidelines</p>
      </div>
    </div>
  );

  // DOCUMENT SELECTOR - like a dropdown in Flask forms
  const DocumentSelector = () => (
    <div className="document-selector">
      <h3><FileText size={20} /> Select Document</h3>
      <select 
        value={selectedDocument?.document_id || ''} 
        onChange={(e) => {
          const doc = documents.find(d => d.document_id === e.target.value);
          setSelectedDocument(doc);
        }}
        disabled={documents.length === 0}
      >
        <option value="">Choose a document...</option>
        {documents.map(doc => (
          <option key={doc.document_id} value={doc.document_id}>
            {doc.original_filename} ({Math.round(doc.file_size / 1024)}KB)
          </option>
        ))}
      </select>
      {selectedDocument && (
        <div className="document-preview">
          <strong>Preview:</strong>
          <p>{selectedDocument.content_preview}</p>
        </div>
      )}
    </div>
  );

  // CHAT INTERFACE - like Dash Input/Output callbacks
  const ChatInterface = () => (
    <div className="chat-section">
      <h3><MessageCircle size={20} /> Ask Questions</h3>
      
      <div className="chat-messages">
        {messages.map(message => (
          <div key={message.id} className={`message message-${message.type}`}>
            <div className="message-header">
              <span className="message-type">{message.type.toUpperCase()}</span>
              <span className="message-time">{message.timestamp}</span>
            </div>
            <div className="message-content">{message.content}</div>
            {message.metadata && (
              <div className="message-metadata">
                📄 {message.metadata.document} | 
                🎯 {message.metadata.tokens} tokens | 
                💰 ${message.metadata.cost?.toFixed(6)} | 
                🤖 {message.metadata.model}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask about medications, procedures, safety protocols..."
          onKeyPress={(e) => e.key === 'Enter' && askQuestion()}
          disabled={isLoading || !selectedDocument}
        />
        <button 
          onClick={askQuestion} 
          disabled={isLoading || !selectedDocument || !question.trim()}
        >
          {isLoading ? 'Processing...' : 'Ask'}
        </button>
      </div>
    </div>
  );

  // SYSTEM STATUS - like Flask health check display
  const SystemStatus = () => (
    <div className="system-status">
      <h3><Heart size={20} /> System Status</h3>
      {systemHealth ? (
        <div className={`status-indicator ${systemHealth.overall?.status}`}>
          <div>Overall: {systemHealth.overall?.status || 'unknown'}</div>
          <div>Services: {systemHealth.overall?.healthy_services || 0}/{systemHealth.overall?.services_count || 0}</div>
          <div>Cost Today: ${totalCost.toFixed(6)}</div>
        </div>
      ) : (
        <div className="status-indicator unhealthy">Checking...</div>
      )}
    </div>
  );

  // MAIN RENDER - like Flask's render_template()
  // This is what gets displayed to the user
  return (
    <div className="App">
      <header className="app-header">
        <h1>🏥 CareDocQA - Healthcare AI Assistant</h1>
        <p>Upload care documents and ask intelligent questions powered by microservices</p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          <FileUpload />
          <DocumentSelector />
          <SystemStatus />
        </div>

        <div className="right-panel">
          <ChatInterface />
        </div>
      </div>

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">Processing...</div>
        </div>
      )}
    </div>
  );
}

export default App;
