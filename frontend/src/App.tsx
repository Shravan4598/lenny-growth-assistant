import React, { useState } from 'react';
import { api } from './api/client';
import { ArtifactViewer } from './components/ArtifactViewer';

function App() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<{role: string, content: string}[]>([]);
  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const sessionId = "00000000-0000-0000-0000-000000000001"; // Use a real UUID in prod

  const sendMessage = async () => {
    if (!input) return;
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    const currentInput = input;
    setInput("");
    setLoading(true);

    try {
      const res = await api.post('/agent/run', { 
        session_id: sessionId, 
        prompt: currentInput 
      });
      setMessages(prev => [...prev, { role: 'agent', content: res.data.response }]);
      if (res.data.artifact_id) setActiveArtifactId(res.data.artifact_id);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="h-screen w-screen flex bg-gray-50 p-4 gap-4 font-sans">
      {/* Left side: Chat */}
      <div className="w-1/3 flex flex-col border bg-white rounded shadow">
        <div className="p-4 bg-blue-600 text-white font-bold rounded-t">Lenny Growth Assistant</div>
        <div className="flex-1 p-4 overflow-y-auto space-y-4">
          {messages.map((m, i) => (
            <div key={i} className={`p-3 rounded max-w-[85%] ${m.role === 'user' ? 'bg-blue-100 ml-auto' : 'bg-gray-100'}`}>
              {m.content}
            </div>
          ))}
          {loading && <div className="text-gray-400 italic">Agent is thinking...</div>}
        </div>
        <div className="p-3 border-t flex gap-2">
          <input 
            value={input} 
            onChange={e => setInput(e.target.value)} 
            onKeyDown={e => e.key === 'Enter' && sendMessage()}
            className="flex-1 border p-2 rounded" 
            placeholder="Ask for a Ship 30 plan..." 
          />
          <button onClick={sendMessage} className="bg-blue-600 text-white px-4 rounded">Send</button>
        </div>
      </div>

      {/* Right side: Artifact Viewer */}
      <div className="flex-1">
        <ArtifactViewer artifactId={activeArtifactId} />
      </div>
    </div>
  );
}

export default App;