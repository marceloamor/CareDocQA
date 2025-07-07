import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { MessageCircle, FileText, Heart } from 'lucide-react';
import './App.css';

// Healthcare document Q&A system with AI-powered analysis
function App() {
  // State management for application components
  const [documents, setDocuments] = useState([]);           // Available documents
  const [selectedDocument, setSelectedDocument] = useState(null);  // Currently selected document
  const [question, setQuestion] = useState('');             // User question input
  const [messages, setMessages] = useState([]);             // Chat conversation history
  const [isLoading, setIsLoading] = useState(false);        // Loading state for async operations
  const [systemHealth, setSystemHealth] = useState(null);   // System health monitoring
  const [totalCost, setTotalCost] = useState(0);           // API usage cost tracking

  // API base URL configuration
  const API_BASE = '';

  // Utility function for adding messages to chat interface
  const addMessage = useCallback((type, content, metadata = null) => {
    const newMessage = {
      id: Date.now(),
      type, // 'user', 'ai', 'system'
      content,
      metadata,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);

  // Document management functions
  
  const loadDocuments = useCallback(async () => {
    // Fetch available documents from document service
    try {
      const response = await axios.get(`${API_BASE}/documents`);
      setDocuments(response.data.documents || []);
    } catch (error) {
      console.error('Failed to load documents:', error);
      addMessage('system', 'Failed to load documents. Please check if services are running.');
    }
  }, [API_BASE, addMessage]);

  const checkSystemHealth = useCallback(async () => {
    // Monitor system health across all microservices
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ overall: { status: 'unhealthy' } });
    }
  }, [API_BASE]);

  // Component initialization and setup
  useEffect(() => {
    loadDocuments();
    checkSystemHealth();
    
    // Restore cost tracking from localStorage
    const savedCost = localStorage.getItem('totalCost');
    if (savedCost) {
      setTotalCost(parseFloat(savedCost));
    }
  }, [loadDocuments, checkSystemHealth]);

  const uploadDocument = useCallback(async (file) => {
    // Handle document upload to document service
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      setIsLoading(true);
      await axios.post(`${API_BASE}/upload`, formData, {
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
  }, [API_BASE, addMessage, loadDocuments]);

  const askQuestion = useCallback(async () => {
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
  }, [selectedDocument, question, addMessage, API_BASE, totalCost]);

  // Event handlers for user interactions
  const handleQuestionChange = useCallback((e) => {
    setQuestion(e.target.value);
  }, []);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter') {
      askQuestion();
    }
  }, [askQuestion]);

  // Main component render
  return (
    <div className="App">
      <header className="app-header">
        <h1>🏥 CareDocQA - Healthcare AI Assistant</h1>
        <p>Upload care documents and ask intelligent questions with AI-powered analysis</p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          {/* FILE UPLOAD COMPONENT */}
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

          {/* DOCUMENT SELECTOR */}
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

          {/* SYSTEM STATUS */}
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
        </div>

        <div className="right-panel">
          {/* Chat interface */}
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
                onChange={handleQuestionChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask about medications, procedures, safety protocols..."
                disabled={isLoading || !selectedDocument}
                autoComplete="off"
              />
              <button 
                onClick={askQuestion} 
                disabled={isLoading || !selectedDocument || !question.trim()}
              >
                {isLoading ? 'Processing...' : 'Ask'}
              </button>
            </div>
          </div>
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
