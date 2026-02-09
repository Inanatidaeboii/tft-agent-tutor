import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles, Zap, Trophy, Star } from 'lucide-react';
import './index.css';

function getSessionId() {
  let sessionId = localStorage.getItem("chat_session_id");

  if (!sessionId) {
    sessionId = crypto.randomUUID(); 
    localStorage.setItem("chat_session_id", sessionId);
  }

  return sessionId;
}
function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      text: 'Welcome, Tactician! I\'m your TFT AI Coach. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputText.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      text: inputText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentMessage = inputText;
    const session_id = getSessionId();
    setInputText('');
    setIsTyping(true);

    try {
      // Call the REST API
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: currentMessage,
          session_id: session_id,
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Create assistant message from API response
      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: data.response,
        tool_used: data.tool_used,
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    } catch (error) {
      console.error('Error calling chat API:', error);
      
      // Show error message to user
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        text: 'Sorry, I encountered an error connecting to the chat service. Please make sure the server is running on localhost:8000.',
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, errorMessage]);
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const quickActions = [
    { icon: Trophy, label: 'Meta Comps', color: 'yellow' },
    { icon: Sparkles, label: 'Item Guide', color: 'blue' },
    { icon: Zap, label: 'Synergies', color: 'yellow' }
  ];

  return (
    <div className="app-container">
      {/* Hexagon pattern background */}
      <div className="hexagon-background">
        <svg width="100%" height="100%">
          <defs>
            <pattern id="hexagons" x="0" y="0" width="50" height="43.4" patternUnits="userSpaceOnUse">
              <polygon points="24.8,22 37.3,29.2 37.3,43.7 24.8,50.9 12.3,43.7 12.3,29.2" fill="none" stroke="white" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#hexagons)"/>
        </svg>
      </div>

      {/* Floating particles */}
      <div className="particle particle-1"></div>
      <div className="particle particle-2"></div>
      <div className="particle particle-3"></div>
      <div className="particle particle-4"></div>

      <div className="chat-container">
        
        {/* Header with TFT styling */}
        <div className="chat-header">
          {/* Subtle glow effect */}
          <div className="header-glow"></div>
          
          <div className="header-content">
            <div className="header-left">
              {/* Hexagon avatar */}
              <div className="avatar-container">
                <div className="avatar-glow"></div>
                <svg className="avatar-hexagon" viewBox="0 0 100 100">
                  <defs>
                    <linearGradient id="hexGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#fbbf24" />
                      <stop offset="100%" stopColor="#f59e0b" />
                    </linearGradient>
                  </defs>
                  <polygon points="50,5 90,30 90,70 50,95 10,70 10,30" fill="url(#hexGrad)" stroke="#fef3c7" strokeWidth="2"/>
                  <text x="50" y="60" fontSize="32" fill="#1e293b" fontWeight="bold" textAnchor="middle">AI</text>
                </svg>
              </div>
              
              <div className="header-info">
                <h1 className="header-title">
                  TFT Coach AI
                  <Star className="header-star" />
                </h1>
                <p className="header-subtitle">Your Challenger-level Strategy Partner</p>
              </div>
            </div>
            
            <div className="header-right">
              <div className="status-badge">
                <div className="status-dot"></div>
                <span className="status-text">ONLINE</span>
              </div>
              <span className="status-message">Ready to carry</span>
            </div>
          </div>
        </div>

        {/* Quick Actions with TFT styling */}
        {/* <div className="quick-actions">
          {quickActions.map((action, idx) => (
            <button key={idx} className="action-button">
              <div className="action-button-glow"></div>
              <action.icon className={`action-icon ${action.color === 'yellow' ? 'text-yellow' : 'text-blue'}`} />
              <span className="action-label">{action.label}</span>
            </button>
          ))}
        </div> */}

        {/* Messages Area */}
        <div className="messages-area">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`message-wrapper ${message.type === 'user' ? 'message-user' : 'message-assistant'}`}
            >
              <div className="message-content">
                {message.type === 'assistant' && (
                  <div className="assistant-header">
                    <svg className="assistant-avatar" viewBox="0 0 100 100">
                      <polygon points="50,10 85,30 85,70 50,90 15,70 15,30" fill="#fbbf24" stroke="#f59e0b" strokeWidth="3"/>
                      <text x="50" y="62" fontSize="28" fill="#1e293b" fontWeight="bold" textAnchor="middle">AI</text>
                    </svg>
                    <span className="assistant-label">TFT Coach</span>
                  </div>
                )}
                
                <div className="message-bubble-wrapper">
                  {/* Glow effect for messages */}
                  <div className={`message-glow ${message.type === 'user' ? 'glow-blue' : 'glow-yellow'}`}></div>
                  
                  <div className={`message-bubble ${message.type === 'user' ? 'bubble-user' : 'bubble-assistant'}`}>
                    <p className="message-text">{message.text}</p>
                    {message.type === 'assistant' && message.tool_used && (
                      <div className="tool-badge">
                        <Zap className="tool-icon" />
                        <span className="tool-text">Tool: {message.tool_used}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                <span className={`message-time ${message.type === 'user' ? 'time-right time-blue' : 'time-left time-gray'}`}>
                  {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="message-wrapper message-assistant">
              <div className="message-content">
                <div className="assistant-header">
                  <svg className="assistant-avatar" viewBox="0 0 100 100">
                    <polygon points="50,10 85,30 85,70 50,90 15,70 15,30" fill="#fbbf24" stroke="#f59e0b" strokeWidth="3"/>
                    <text x="50" y="62" fontSize="28" fill="#1e293b" fontWeight="bold" textAnchor="middle">AI</text>
                  </svg>
                  <span className="assistant-label">TFT Coach</span>
                </div>
                
                <div className="message-bubble-wrapper">
                  <div className="message-glow glow-yellow"></div>
                  <div className="message-bubble bubble-assistant">
                    <div className="typing-indicator">
                      <div className="typing-dot typing-dot-1"></div>
                      <div className="typing-dot typing-dot-2"></div>
                      <div className="typing-dot typing-dot-3"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-wrapper">
            <div className="input-container">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about comps, items, or strategy..."
                className="input-field"
                rows="2"
              />
              {/* Decorative corner accent */}
              <div className="input-accent">
                <div className="accent-dot accent-yellow"></div>
                <div className="accent-dot accent-blue"></div>
              </div>
            </div>
            
            <button
              onClick={handleSend}
              disabled={!inputText.trim()}
              className="send-button"
            >
              <div className="send-button-glow"></div>
              <Send className="send-icon" />
            </button>
          </div>
          
          <div className="input-footer">
            Press <kbd className="kbd-key">Enter</kbd> to send • 
            <span className="gg-text">GG WP!</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;