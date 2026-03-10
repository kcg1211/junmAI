import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const API_URL = "http://localhost:8000/query";

function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg = { role: 'user', content: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(API_URL, { query: input });
      setMessages(prev => [...prev, { role: 'bot', content: response.data.answer }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: "I'm sorry, I lost my notes on that sake. Try again?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ backgroundColor: '#fdfcf0', minHeight: '100vh', padding: '20px', fontFamily: 'Georgia, serif' }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#1a1a1a', fontSize: '2.5rem', marginBottom: '5px' }}>JunmAI</h1>
        <p style={{ color: '#666', fontStyle: 'italic' }}>Professional Sake Sommelier</p>
      </header>

      <main style={{ maxWidth: '700px', margin: '0 auto', backgroundColor: '#fff', borderRadius: '12px', boxShadow: '0 4px 15px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
        <div style={{ height: '500px', overflowY: 'auto', padding: '20px' }}>
          {messages.map((m, i) => (
            <div key={i} style={{ marginBottom: '20px', textAlign: m.role === 'user' ? 'right' : 'left' }}>
              <div style={{ 
                display: 'inline-block', 
                maxWidth: '80%', 
                padding: '12px 16px', 
                borderRadius: '15px',
                backgroundColor: m.role === 'user' ? '#2c3e50' : '#f0f2f5',
                color: m.role === 'user' ? '#fff' : '#333',
                lineHeight: '1.5'
              }}>
                {m.content}
              </div>
            </div>
          ))}
          {loading && <div style={{ color: '#aaa', fontSize: '0.9rem' }}>JunmAI is consulting the cellar...</div>}
          <div ref={scrollRef} />
        </div>

        <form onSubmit={sendMessage} style={{ display: 'flex', borderTop: '1px solid #eee', padding: '15px' }}>
          <input 
            type="text" 
            value={input} 
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about flavor profiles, rice polishing, or food pairings..." 
            style={{ flex: 1, border: '1px solid #ddd', borderRadius: '25px', padding: '10px 20px', outline: 'none' }}
          />
          <button 
            type="submit" 
            style={{ marginLeft: '10px', backgroundColor: '#2c3e50', color: '#fff', border: 'none', borderRadius: '25px', padding: '10px 25px', cursor: 'pointer' }}
            disabled={loading}
          >
            Ask
          </button>
        </form>
      </main>
    </div>
  );
}

export default App;