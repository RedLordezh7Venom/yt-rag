import { useEffect, useState, useRef } from 'react';
import './App.css';

const BACKEND_URL = 'http://127.0.0.1:8000'; // Change if backend runs elsewhere

function App() {
  const [videoUrl, setVideoUrl] = useState('');
  const [chat, setChat] = useState([]); // {role: 'user'|'bot', text: string}
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat]);

  // On mount, get YouTube URL from background
  useEffect(() => {
    chrome.runtime.sendMessage({ type: 'GET_VIDEO_URL' }, (res) => {
      if (res?.url) {
        setVideoUrl(res.url);
        // Call backend to process video
        fetch(`${BACKEND_URL}/process_video`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: res.url })
        });
      }
    });
  }, []);

  const sendQuestion = async (e) => {
    e.preventDefault();
    if (!input.trim() || !videoUrl) return;
    setChat([...chat, { role: 'user', text: input }]);
    setLoading(true);
    try {
      const resp = await fetch(`${BACKEND_URL}/ask_question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: videoUrl, question: input })
      });
      const data = await resp.json();
      setChat((c) => [...c, { role: 'bot', text: data.answer || data.detail || 'No answer.' }]);
    } catch (err) {
      setChat((c) => [...c, { role: 'bot', text: 'Error contacting backend.' }]);
    }
    setInput('');
    setLoading(false);
  };

  return (
    <div className="panel-container">
      <h2>YouTube RAG Chatbot</h2>
      <div className="video-url">Video: <span>{videoUrl || 'Detecting...'}</span></div>
      <div className="chat-box">
        {chat.map((msg, i) => (
          <div key={i} className={msg.role === 'user' ? 'chat-user' : 'chat-bot'}>
            <b>{msg.role === 'user' ? 'You' : 'Bot'}:</b> {msg.text}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>
      <form className="chat-input" onSubmit={sendQuestion}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask a question about this video..."
          disabled={loading || !videoUrl}
        />
        <button type="submit" disabled={loading || !videoUrl || !input.trim()}>
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
}

export default App;
