import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { MessageCircle, FileText, Heart, AlertTriangle, Send, Edit3 } from 'lucide-react';
import './App.css';

// Think of this like a Flask app with multiple routes
// Each component is like a different route handler function
function App() {
  // STATE MANAGEMENT for incident response system
  const [message, setMessage] = useState('');                    // Current chat input
  const [messages, setMessages] = useState([]);                 // Chat history
  const [transcript, setTranscript] = useState('');             // Transcript input area
  const [isLoading, setIsLoading] = useState(false);            // Loading state
  const [systemHealth, setSystemHealth] = useState(null);       // System health
  const [totalCost, setTotalCost] = useState(0);               // AI cost tracking
  const [editingDocument, setEditingDocument] = useState(null); // Document being edited
  const [editFeedback, setEditFeedback] = useState('');         // User feedback for edits

  // API BASE URL
  const API_BASE = '';

  // UTILITY FUNCTION - Add message to chat (STABLE)
  const addMessage = useCallback((type, content, metadata = null) => {
    const newMessage = {
      id: Date.now(),
      type, // 'user', 'ai', 'system', 'analysis'
      content,
      metadata,
      timestamp: new Date().toLocaleTimeString()
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);

  // API FUNCTIONS

  const checkSystemHealth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ overall: { status: 'unhealthy' } });
    }
  }, [API_BASE]);

  // LIFECYCLE HOOK - runs when component loads
  useEffect(() => {
    checkSystemHealth();
    
    // Load saved cost from localStorage
    const savedCost = localStorage.getItem('totalCost');
    if (savedCost) {
      setTotalCost(parseFloat(savedCost));
    }

    // Add welcome message
    addMessage('system', `Welcome to the AI-Enhanced Incident Response System! 

You can:
• Ask questions about social care policies
• Paste call transcripts for automatic incident analysis
• Get automated incident reports and email drafts

The system has all care policies loaded and ready. Try asking: "What should I do if someone falls repeatedly?"`);
  }, [checkSystemHealth, addMessage]);

  const sendChatMessage = useCallback(async () => {
    if (!message.trim()) return;

    // Add user message to chat
    addMessage('user', message);
    const currentMessage = message;
    setMessage(''); // Clear input
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: currentMessage
      });

      const data = response.data;
      
      if (data.type === 'transcript_analysis') {
        // Handle transcript analysis response
        addMessage('analysis', data.message, {
          analysisData: data.analysis_data,
          tokens: data.tokens_used,
          cost: data.cost,
          type: 'transcript_analysis'
        });
      } else {
        // Handle policy question response
        addMessage('ai', data.message, {
          tokens: data.tokens_used,
          cost: data.cost,
          type: 'policy_question'
        });
      }

      // Update total cost
      const newCost = totalCost + (data.cost || 0);
      setTotalCost(newCost);
      localStorage.setItem('totalCost', newCost.toString());

    } catch (error) {
      console.error('Chat failed:', error);
      addMessage('system', `Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [message, addMessage, API_BASE, totalCost]);

  const analyzeTranscript = useCallback(async () => {
    if (!transcript.trim()) {
      addMessage('system', 'Please enter a call transcript to analyze.');
      return;
    }

    addMessage('user', `📄 Analyzing call transcript (${transcript.length} characters)`);
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/analyze`, {
        transcript: transcript
      });

      const data = response.data;
      
      // Format structured analysis response
      const analysisMessage = formatAnalysisResponse(data.analysis);
      
      addMessage('analysis', analysisMessage, {
        analysisData: data.analysis,
        tokens: data.tokens_used,
        cost: data.cost,
        type: 'direct_analysis'
      });

      // Update total cost
      const newCost = totalCost + (data.cost || 0);
      setTotalCost(newCost);
      localStorage.setItem('totalCost', newCost.toString());

    } catch (error) {
      console.error('Analysis failed:', error);
      addMessage('system', `Analysis failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [transcript, addMessage, API_BASE, totalCost]);

  const updateDocument = useCallback(async (documentType, currentContent, allDocuments) => {
    if (!editFeedback.trim()) {
      addMessage('system', 'Please provide feedback for how to improve the document.');
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE}/update`, {
        feedback: editFeedback,
        document_type: documentType,
        current_content: currentContent,
        all_documents: allDocuments
      });

      const data = response.data;
      
      if (data.updates.requires_cross_updates) {
        addMessage('ai', `✅ Updated ${documentType} and related documents:

**Primary Update:**
${data.updates.updated_document}

**Related Changes:**
${data.updates.cross_updates.map(update => 
  `• ${update.document_type}: ${update.reason}`
).join('\n')}

**Explanation:** ${data.updates.explanation}`, {
        tokens: data.tokens_used,
        cost: data.cost,
        type: 'document_update'
      });
      } else {
        addMessage('ai', `✅ Updated ${documentType}:

${data.updates.updated_document}

**Explanation:** ${data.updates.explanation}`, {
          tokens: data.tokens_used,
          cost: data.cost,
          type: 'document_update'
        });
      }

      // Update total cost
      const newCost = totalCost + (data.cost || 0);
      setTotalCost(newCost);
      localStorage.setItem('totalCost', newCost.toString());

      // Clear editing state
      setEditingDocument(null);
      setEditFeedback('');

    } catch (error) {
      console.error('Update failed:', error);
      addMessage('system', `Update failed: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  }, [editFeedback, addMessage, API_BASE, totalCost]);

  // FORMAT ANALYSIS RESPONSE
  const formatAnalysisResponse = (analysis) => {
    let response = `📋 **INCIDENT ANALYSIS**

**Summary:** ${analysis.analysis.summary}

**🚨 TRIGGERED POLICIES:**
`;
    
    analysis.analysis.triggered_policies.forEach(policy => {
      response += `• **${policy.section}**: ${policy.reason}\n`;
    });
    
    response += `\n**📝 REQUIRED ACTIONS:**\n`;
    analysis.analysis.required_actions.forEach(action => {
      response += `• ${action}\n`;
    });
    
    response += `\n**📋 INCIDENT REPORT:**\n`;
    Object.entries(analysis.incident_report).forEach(([field, value]) => {
      response += `• **${field}**: ${value}\n`;
    });
    
    response += `\n**📧 EMAILS TO SEND:**\n`;
    analysis.emails.forEach(email => {
      response += `\n**To: ${email.recipient_type.toUpperCase()}**\n`;
      response += `Subject: ${email.subject}\n`;
      response += `Urgency: ${email.urgency.toUpperCase()}\n`;
      if (email.cc && email.cc.length > 0) {
        response += `CC: ${email.cc.join(', ')}\n`;
      }
      response += `\n${email.body}\n\n---\n`;
    });
    
    return response;
  };

  // EVENT HANDLERS
  const handleMessageChange = useCallback((e) => {
    setMessage(e.target.value);
  }, []);

  const handleTranscriptChange = useCallback((e) => {
    setTranscript(e.target.value);
  }, []);

  const handleKeyPress = useCallback((e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendChatMessage();
    }
  }, [sendChatMessage]);

  const handleEditDocument = useCallback((documentType, content, allDocs) => {
    setEditingDocument({ type: documentType, content, allDocuments: allDocs });
  }, []);

  // MAIN RENDER
  return (
    <div className="App">
      <header className="app-header">
        <h1>🚨 AI-Enhanced Incident Response System</h1>
        <p>Social Care Incident Analysis • Policy Compliance • Automated Documentation</p>
      </header>

      <div className="app-content">
        <div className="left-panel">
          {/* TRANSCRIPT INPUT */}
          <div className="transcript-section">
            <h3><FileText size={20} /> Call Transcript</h3>
            <textarea
              value={transcript}
              onChange={handleTranscriptChange}
              placeholder="Paste call transcript here for automatic incident analysis...

Example:
Julie Peaterson: 'Good morning, how can I help you?'
Greg Jones: 'Hi, I've fallen again...'
..."
              className="transcript-input"
              rows="8"
              disabled={isLoading}
            />
            <button 
              onClick={analyzeTranscript}
              disabled={isLoading || !transcript.trim()}
              className="analyze-button"
            >
              <AlertTriangle size={16} />
              {isLoading ? 'Analyzing...' : 'Analyze Incident'}
            </button>
            <p className="transcript-info">
              The system will analyze transcripts against all policies and generate required documents automatically.
            </p>
          </div>

          {/* SYSTEM STATUS */}
          <div className="system-status">
            <h3><Heart size={20} /> System Status</h3>
            {systemHealth ? (
              <div className={`status-indicator ${systemHealth.overall?.status}`}>
                <div>Overall: {systemHealth.overall?.status || 'unknown'}</div>
                <div>Incident Processor: {systemHealth.incident_processor?.status || 'unknown'}</div>
                <div>Policies Loaded: {systemHealth.incident_processor?.policies_loaded ? '✅' : '❌'}</div>
                <div>Cost Today: ${totalCost.toFixed(6)}</div>
              </div>
            ) : (
              <div className="status-indicator unhealthy">Checking...</div>
            )}
          </div>

          {/* EDIT DOCUMENT SECTION */}
          {editingDocument && (
            <div className="edit-section">
              <h3><Edit3 size={20} /> Edit Document</h3>
              <p>Editing: <strong>{editingDocument.type}</strong></p>
              <textarea
                value={editFeedback}
                onChange={(e) => setEditFeedback(e.target.value)}
                placeholder="How should this document be improved? (e.g., 'Make it more urgent', 'Add more detail about confusion')"
                className="edit-feedback"
                rows="3"
              />
              <div className="edit-buttons">
                <button 
                  onClick={() => updateDocument(editingDocument.type, editingDocument.content, editingDocument.allDocuments)}
                  disabled={isLoading || !editFeedback.trim()}
                  className="update-button"
                >
                  Update Document
                </button>
                <button 
                  onClick={() => setEditingDocument(null)}
                  className="cancel-button"
                >
                  Cancel
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="right-panel">
          {/* CHAT INTERFACE */}
          <div className="chat-section">
            <h3><MessageCircle size={20} /> Policy Chat & Analysis</h3>
            
            <div className="chat-messages">
              {messages.map(message => (
                <div key={message.id} className={`message message-${message.type}`}>
                  <div className="message-header">
                    <span className="message-type">{message.type.toUpperCase()}</span>
                    <span className="message-time">{message.timestamp}</span>
                  </div>
                  <div 
                    className="message-content"
                    style={{ whiteSpace: 'pre-wrap' }}
                  >
                    {message.content}
                  </div>
                  {message.metadata && (
                    <div className="message-metadata">
                      {message.metadata.type === 'transcript_analysis' && (
                        <button 
                          onClick={() => handleEditDocument('incident_report', 
                            JSON.stringify(message.metadata.analysisData.incident_report, null, 2),
                            message.metadata.analysisData
                          )}
                          className="edit-doc-button"
                        >
                          <Edit3 size={12} /> Edit Documents
                        </button>
                      )}
                      <span>
                        🎯 {message.metadata.tokens} tokens | 
                        💰 ${message.metadata.cost?.toFixed(6)}
                      </span>
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="chat-input">
              <textarea
                value={message}
                onChange={handleMessageChange}
                onKeyPress={handleKeyPress}
                placeholder="Ask about policies or paste a transcript for analysis..."
                className="message-input"
                rows="3"
                disabled={isLoading}
                autoComplete="off"
              />
              <button 
                onClick={sendChatMessage} 
                disabled={isLoading || !message.trim()}
                className="send-button"
              >
                <Send size={16} />
                {isLoading ? 'Processing...' : 'Send'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="loading-overlay">
          <div className="loading-spinner">
            <AlertTriangle size={24} />
            Processing incident analysis...
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
