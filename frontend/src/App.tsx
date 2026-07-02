import React, { useState, useEffect, useRef } from 'react';
import type { FormEvent } from 'react';
import { Bot, Code, User, Terminal, Send, Volume2, MapPin } from 'lucide-react';
import axios from 'axios';

// ==========================================
// 1. STRICT ENTERPRISE TYPES & INTERFACES
// ==========================================
export type AgentId = 'direct' | 'cv' | 'audit' | 'bio' | 'voice';

export interface Agent {
  id: AgentId;
  name: string;
  desc: string;
  icon: React.ComponentType<any>;
  color: string;
}

export interface ChatMessage {
  id?: number;
  agent_id: string;
  sender: 'user' | 'system' | 'agent';
  text: string;
  audio_url?: string | null;
  timestamp: string;
}

export interface SessionResponse {
  token: string;
}

// ==========================================
// 2. MONOLITHIC API SERVICE ENGINE
// ==========================================
const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export const apiService = {
  async initializeSession(): Promise<string> {
    const response = await axios.get<SessionResponse>(`${API_BASE}/session`);
    localStorage.setItem('guest_token', response.data.token);
    return response.data.token;
  },

  async getChatHistory(token: string, agentId: string): Promise<ChatMessage[]> {
    const response = await axios.get<ChatMessage[]>(`${API_BASE}/history/${token}/${agentId}`);
    return response.data;
  },

  async executePipeline(token: string, agentId: string, text: string): Promise<ChatMessage> {
    const response = await 
    axios.post
    <ChatMessage>(`${API_BASE}/execute/${token}`, { agent_id: agentId, text: text });
    return response.data;
  }
};

// ==========================================
// 3. MASTER SAAS DASHBOARD INTERFACE
// ==========================================
function renderTextWithInlineFormatting(text: string): React.ReactNode {
  const lines = text.split('\n');
  return lines.map((line, lineIdx) => {
    const isBullet = line.trim().startsWith('- ') || line.trim().startsWith('* ');
    const displayLine = isBullet ? line.trim().substring(2) : line;

    const inlineParts: React.ReactNode[] = [];
    const inlineRegex = /(\*\*|`)(.*?)\1/g;
    let inlineLastIndex = 0;
    let inlineMatch;

    while ((inlineMatch = inlineRegex.exec(displayLine)) !== null) {
      const inlineMatchIndex = inlineMatch.index;

      if (inlineMatchIndex > inlineLastIndex) {
        inlineParts.push(displayLine.substring(inlineLastIndex, inlineMatchIndex));
      }

      const delimiter = inlineMatch[1];
      const content = inlineMatch[2];

      if (delimiter === '**') {
        inlineParts.push(<strong key={inlineMatchIndex} className="font-semibold text-white tracking-wide">{content}</strong>);
      } else if (delimiter === '`') {
        inlineParts.push(<code key={inlineMatchIndex} className="bg-slate-900/90 text-pink-400 font-mono text-[11px] px-1.5 py-0.5 rounded border border-slate-800/80">{content}</code>);
      }

      inlineLastIndex = inlineRegex.lastIndex;
    }

    if (inlineLastIndex < displayLine.length) {
      inlineParts.push(displayLine.substring(inlineLastIndex));
    }

    if (isBullet) {
      return (
        <li key={lineIdx} className="ml-5 list-disc text-slate-300 leading-relaxed text-sm my-1">
          {inlineParts}
        </li>
      );
    }

    return (
      <p key={lineIdx} className="text-slate-300 leading-relaxed text-sm my-1.5">
        {inlineParts.length === 0 || (inlineParts.length === 1 && inlineParts[0] === '') ? '\u00A0' : inlineParts}
      </p>
    );
  });
}

function parseMessageText(text: string): React.ReactNode {
  if (!text) return null;

  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    const matchIndex = match.index;
    
    if (matchIndex > lastIndex) {
      const prevText = text.substring(lastIndex, matchIndex);
      parts.push(renderTextWithInlineFormatting(prevText));
    }

    const language = match[1] || 'code';
    const codeContent = match[2].trim();

    parts.push(
      <div key={`code-${matchIndex}`} className="my-3 rounded-lg overflow-hidden border border-slate-800 bg-[#0d111a] font-mono text-xs shadow-xl">
        <div className="bg-[#151c2c] px-4 py-2 border-b border-slate-800 text-slate-400 text-[10px] font-bold tracking-wider flex justify-between items-center uppercase">
          <span className="flex items-center space-x-1.5">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>{language}</span>
          </span>
          <span className="text-[9px] text-slate-500 font-mono">COMPILED_OUTPUT</span>
        </div>
        <pre className="p-4 overflow-x-auto text-emerald-400/90 leading-relaxed font-mono">
          <code>{codeContent}</code>
        </pre>
      </div>
    );

    lastIndex = codeBlockRegex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(renderTextWithInlineFormatting(text.substring(lastIndex)));
  }

  return <div className="space-y-1">{parts}</div>;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<AgentId>('audit');
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>('');
  const [token, setToken] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const agents: Agent[] = [
    { id: 'direct', name: 'Chat Live With Me', desc: 'Routes straight to my phone', icon: User, color: 'text-emerald-400' },
    { id: 'cv', name: 'CV & Project Analyst', desc: 'RAG business intelligence bot', icon: Bot, color: 'text-blue-400' },
    { id: 'audit', name: 'Code Auditor Bot', desc: 'Automated technical recruiter', icon: Code, color: 'text-amber-400' },
    { id: 'bio', name: 'Identity & Location Envoy', desc: 'Geographic & bio verification', icon: MapPin, color: 'text-purple-400' },
    { id: 'voice', name: 'Live Voice Ambassador', desc: 'ElevenLabs vocal stream agent', icon: Volume2, color: 'text-pink-400' },
  ];

  // Initialize Handshake Session
  useEffect(() => {
    const startSession = async () => {
      try {
        let existingToken = localStorage.getItem('guest_token');
        if (!existingToken) {
          existingToken = await apiService.initializeSession();
        }
        setToken(existingToken);
      } catch (err) {
        console.error("Session initialization failed. Ensure your Django engine is running.", err);
      }
    };
    startSession();
  }, []);

  // Long-Polling Synchronization loop
  useEffect(() => {
    if (!token) return;

    const fetchHistory = async () => {
      try {
        const data = await apiService.getChatHistory(token, activeTab);
        setMessages(data);
      } catch (err) {
        console.error("Error polling sequence logs:", err);
      }
    };

    fetchHistory();
    const interval = setInterval(fetchHistory, 5000); 
    return () => clearInterval(interval);
  }, [token, activeTab]);

  // Keep workspace container pinned to base text
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isProcessing]);

  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !token || isProcessing) return;

    const userText = input;
    setInput('');
    setIsProcessing(true);

    // Optimistic UI local bubble update
    setMessages(prev => [...prev, { agent_id: activeTab, sender: 'user', text: userText, timestamp: 'Syncing...' }]);

    try {
      await apiService.executePipeline(token, activeTab, userText);
    } catch (err) {
      console.error("Pipeline failure execution error:", err);
      setMessages(prev => [...prev, { agent_id: activeTab, sender: 'system', text: '⚠️ Execution error. Check API server logging configurations.', timestamp: '' }]);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-[#0b0f19] text-gray-100 font-sans overflow-hidden">
      {/* SaaS Layout Top Header Panel */}
      <header className="h-14 border-b border-gray-800 bg-[#111827] flex items-center justify-between px-6">
        <div className="flex items-center space-x-3">
          <Terminal className="text-blue-500 h-6 w-6" />
          <span className="font-bold tracking-wider text-sm uppercase text-gray-200">CoreAI Command Console v1.0</span>
        </div>
        <div className="flex items-center space-x-4 text-xs">
          <div className="flex items-center space-x-2 bg-[#1f2937] px-3 py-1.5 rounded-md border border-gray-700">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span className="text-gray-400 font-mono">NODE_CLUSTER: CORE_COMPILED</span>
          </div>
          <span className="text-gray-500 font-mono hidden md:inline truncate max-w-[180px]">ID: {token || 'Assigning...'}</span>
        </div>
      </header>

      {/* Main SaaS Working Grid Layout */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Agent Side Bar Console */}
        <aside className="w-80 border-r border-gray-800 bg-[#111827] flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <h2 className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-3">AI Cluster Orchestration</h2>
            <div className="bg-[#1f2937] p-3 rounded-lg border border-gray-700 flex items-center space-x-3">
              <div className="p-2 bg-blue-500/10 rounded-md">
                <User className="h-5 w-5 text-blue-400" />
              </div>
              <div>
                <h3 className="text-sm font-medium">Your Name</h3>
                <p className="text-xs text-emerald-400 font-mono">STATUS: OPEN_TO_HIRE</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-2 space-y-1 overflow-y-auto">
            {agents.map((agent) => {
              const IconComponent = agent.icon;
              return (
                <button
                  key={agent.id}
                  onClick={() => setActiveTab(agent.id)}
                  className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-all text-left ${
                    activeTab === agent.id 
                      ? 'bg-blue-600/10 border border-blue-500/30 text-white' 
                      : 'hover:bg-[#1f2937]/50 text-gray-400 border border-transparent'
                  }`}
                >
                  <IconComponent className={`h-5 w-5 ${agent.color}`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{agent.name}</p>
                    <p className="text-xs text-gray-500 truncate">{agent.desc}</p>
                  </div>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Right Output Active Terminal Panel */}
        <main className="flex-1 flex flex-col bg-[#0f172a]">
          <div className="px-6 py-3 border-b border-gray-800 bg-[#111827]/60 flex items-center justify-between text-xs text-gray-400">
            <div className="flex items-center space-x-2">
              <span className="text-gray-500">Target Worker Thread:</span>
              <span className="font-mono text-blue-400 bg-blue-500/5 px-2 py-0.5 rounded border border-blue-500/10">
                crewai.service.{activeTab}_node
              </span>
            </div>
          </div>

          {/* Dynamic Message Streams */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 font-sans">
            {messages.length === 0 && (
              <div className="flex-1 flex flex-col items-center justify-center p-8 max-w-xl mx-auto text-center h-full">
                <div className="p-4 rounded-full bg-blue-500/5 border border-slate-800/80 mb-6 animate-pulse">
                  <Terminal className="h-8 w-8 text-blue-400" />
                </div>
                <h2 className="text-lg font-semibold tracking-tight text-white mb-2">
                  Active SaaS Node: <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 font-mono text-sm">{activeTab}_cluster_thread</span>
                </h2>
                <p className="text-xs text-slate-400 leading-relaxed mb-6 max-w-sm">
                  This terminal interface provides low-latency communication with {agents.find(a => a.id === activeTab)?.name}. Select standard parameters or issue a natural language instruction to execute your pipeline.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 w-full max-w-md text-left">
                  <div className="bg-[#111827]/60 border border-slate-800/80 rounded-lg p-3 hover:border-slate-700/80 transition-colors cursor-pointer" onClick={() => setInput("Audit my smart contract or security patterns.")}>
                    <span className="text-[9px] font-mono uppercase tracking-wider text-blue-400 block mb-1">PROMPT SUGGESTION</span>
                    <span className="text-xs text-slate-300 font-medium leading-normal block">"Audit my smart contract or security patterns."</span>
                  </div>
                  <div className="bg-[#111827]/60 border border-slate-800/80 rounded-lg p-3 hover:border-slate-700/80 transition-colors cursor-pointer" onClick={() => setInput("Analyze my career history and match standard RAG indexes.")}>
                    <span className="text-[9px] font-mono uppercase tracking-wider text-purple-400 block mb-1">PROMPT SUGGESTION</span>
                    <span className="text-xs text-slate-300 font-medium leading-normal block">"Analyze my career history and match standard RAG indexes."</span>
                  </div>
                </div>
              </div>
            )}
            
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-2xl rounded-xl px-5 py-4 border shadow-sm transition-all ${
                  msg.sender === 'user' 
                    ? 'bg-blue-600/10 border-blue-500/20 text-blue-100 hover:border-blue-500/30' 
                    : 'bg-[#111827]/80 border-slate-800/80 text-gray-300 hover:border-slate-700/60'
                }`}>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-500 mb-2 flex items-center justify-between">
                    <span className="flex items-center space-x-1">
                      <span className={`h-1.5 w-1.5 rounded-full ${msg.sender === 'user' ? 'bg-blue-400' : 'bg-amber-400'}`}></span>
                      <span>{msg.sender === 'user' ? 'CLIENT_USER' : `AGENT_${activeTab.toUpperCase()}_OUT`}</span>
                    </span>
                  </div>
                  <div className="space-y-1.5 text-sm font-sans tracking-wide">
                    {parseMessageText(msg.text)}
                  </div>
                  
                  {/* Streaming Audio Playback Overlay if ElevenLabs audio_url is attached */}
                  {msg.audio_url && (
                    <div className="mt-3 pt-2 border-t border-gray-800 flex items-center space-x-2">
                      <audio controls className="h-8 max-w-full accent-pink-500">
                        <source src={msg.audio_url} type="audio/mpeg" />
                      </audio>
                    </div>
                  )}
                  
                  <span className="block text-[10px] text-gray-500 text-right mt-1.5">{msg.timestamp}</span>
                </div>
              </div>
            ))}

            {isProcessing && (
              <div className="flex justify-start">
                <div className="bg-[#111827] border border-gray-800 rounded-lg px-4 py-3 shadow-sm text-gray-300 flex items-center space-x-2">
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce"></span>
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.2s]"></span>
                  <span className="h-2 w-2 rounded-full bg-blue-500 animate-bounce [animation-delay:0.4s]"></span>
                  <span className="text-xs text-gray-500 italic ml-2">Pipeline execution processing...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Footer Input Console Form */}
          <footer className="p-4 border-t border-gray-800 bg-[#111827]/40">
            <form onSubmit={handleSendMessage} className="flex items-center space-x-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={`Send prompt query to [${activeTab}] cluster node...`}
                disabled={isProcessing}
                className="flex-1 bg-[#111827] border border-gray-800 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-200 placeholder-gray-500 disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!input.trim() || isProcessing}
                className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-lg flex items-center justify-center transition-colors disabled:opacity-50"
              >
                <Send className="h-5 w-5" />
              </button>
            </form>
          </footer>
        </main>
      </div>
    </div>
  );
}
