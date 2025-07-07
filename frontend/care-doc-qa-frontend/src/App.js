import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { MessageCircle, FileText, Heart, AlertTriangle, Send, Edit3, Loader, Mic } from 'lucide-react';
import './App.css';

function App() {
  // State management for incident response system
  const [message, setMessage] = useState('');                    // Current chat input
  const [messages, setMessages] = useState([]);                 // Chat history
  const [transcript, setTranscript] = useState('');             // Transcript input area
  const [isLoading, setIsLoading] = useState(false);            // Loading state
  const [systemHealth, setSystemHealth] = useState(null);       // System health
  const [totalCost, setTotalCost] = useState(0);               // AI cost tracking

  
  // Session context for follow-up questions
  const [sessionContext, setSessionContext] = useState({
    hasActiveIncident: false,
    lastAnalysis: null,
    incidentSummary: '',
    lastTranscriptTime: null,
    originalTranscript: null
  });
  
  // Ref to ensure welcome message only appears once
  const welcomeMessageAdded = useRef(false);
  
  // Ref for chat messages container to enable auto-scroll
  const chatMessagesRef = useRef(null);

  // API BASE URL
  const API_BASE = '';

  // Add message to chat interface
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

  // System health monitoring
  const checkSystemHealth = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/health`);
      setSystemHealth(response.data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ overall: { status: 'unhealthy' } });
    }
  }, [API_BASE]);

  // Initialize application state and welcome message
  useEffect(() => {
    checkSystemHealth();
    
    // Load saved cost from localStorage
    const savedCost = localStorage.getItem('totalCost');
    if (savedCost) {
      setTotalCost(parseFloat(savedCost));
    }

    // Add welcome message only once
    if (!welcomeMessageAdded.current) {
      addMessage('system', `Welcome to the AI-Enhanced Incident Response System! 

You can:
• Ask questions about social care policies
• Paste call transcripts for automatic incident analysis
• Get automated incident reports and email drafts
• Ask follow-up questions about analyzed incidents

The system has all care policies loaded and ready. After analyzing a transcript, you can ask contextual follow-up questions like "Should we also notify the family?" or "What other assessments are needed?"

Try asking: "What should I do if someone falls repeatedly?"`);
      welcomeMessageAdded.current = true;
    }
  }, [checkSystemHealth, addMessage]);

  // Auto-scroll chat to bottom when new messages arrive
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTo({
        top: chatMessagesRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  const sendChatMessage = useCallback(async () => {
    if (!message.trim()) return;

    // Add user message to chat
    addMessage('user', message);
    const currentMessage = message;
    setMessage(''); // Clear input
    setIsLoading(true);

    try {
      // Prepare request with session context if available
      const requestPayload = {
        message: currentMessage
      };

      // Include session context for follow-up questions
      if (sessionContext.hasActiveIncident && sessionContext.lastAnalysis) {
        requestPayload.session_context = {
          has_active_incident: true,
          last_analysis: sessionContext.lastAnalysis,
          incident_summary: sessionContext.incidentSummary,
          original_transcript: sessionContext.originalTranscript
        };
      }

      const response = await axios.post(`${API_BASE}/chat`, requestPayload);
      const data = response.data;
      
      if (data.type === 'transcript_analysis') {
        // Handle transcript analysis response
        addMessage('analysis', data.message, {
          analysisData: data.analysis_data,
          tokens: data.tokens_used,
          cost: data.cost,
          type: 'transcript_analysis'
        });

        // Update session context with new analysis
        setSessionContext({
          hasActiveIncident: true,
          lastAnalysis: data.analysis_data,
          incidentSummary: data.analysis_data.analysis.summary,
          lastTranscriptTime: Date.now(),
          originalTranscript: currentMessage
        });
      } else {
        // Handle policy question response (including contextual follow-ups)
        addMessage('ai', data.message, {
          tokens: data.tokens_used,
          cost: data.cost,
          type: data.type || 'policy_question'
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
  }, [message, addMessage, API_BASE, totalCost, sessionContext]);

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

      // Update session context with analysis
      setSessionContext({
        hasActiveIncident: true,
        lastAnalysis: data.analysis,
        incidentSummary: data.analysis.analysis.summary,
        lastTranscriptTime: Date.now(),
        originalTranscript: transcript
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
  }, [transcript, addMessage, API_BASE, totalCost, setSessionContext]);



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



  const clearSessionContext = useCallback(() => {
    setSessionContext({
      hasActiveIncident: false,
      lastAnalysis: null,
      incidentSummary: '',
      lastTranscriptTime: null,
      originalTranscript: null
    });
    addMessage('system', '🔄 Session context cleared. New questions will be treated as fresh inquiries.');
  }, [addMessage]);

  // MAIN RENDER
  return (
    <div className="App">
      <header className="app-header">
        <h1>AI-Enhanced Incident Response System</h1>
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
              <Mic size={16} />
              {isLoading ? 'Analyzing...' : 'Analyze Transcript'}
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
                <div>Active Session: {sessionContext.hasActiveIncident ? '🧠 Context Active' : '🔄 Fresh Session'}</div>
                <div>Going to hire Marcelo: True</div>
                <div>Cost Today: ${totalCost.toFixed(6)}</div>
              </div>
            ) : (
              <div className="status-indicator unhealthy">Checking...</div>
            )}
            
            {sessionContext.hasActiveIncident && (
              <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', borderRadius: '6px', fontSize: '0.9rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <strong>📋 Session Context:</strong><br />
                    Last incident: {sessionContext.incidentSummary}<br />
                    <em style={{ color: '#6b7280' }}>Follow-up questions will include this context</em>
                  </div>
                  <button 
                    onClick={clearSessionContext}
                    style={{ 
                      marginLeft: '0.5rem', 
                      padding: '0.25rem 0.5rem', 
                      fontSize: '0.75rem', 
                      background: '#ef4444', 
                      color: 'white', 
                      border: 'none', 
                      borderRadius: '4px', 
                      cursor: 'pointer',
                      whiteSpace: 'nowrap'
                    }}
                  >
                    Clear Context
                  </button>
                </div>
              </div>
            )}
          </div>


        </div>

        <div className="right-panel">
          {/* CHAT INTERFACE */}
          <div className="chat-section">
            <h3><MessageCircle size={20} /> Policy Chat & Analysis</h3>
            
            <div className="chat-messages" ref={chatMessagesRef}>
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
            <Loader size={24} />
            Processing request...
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
