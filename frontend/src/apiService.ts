import axios from 'axios';

// ==========================================
// 1. TYPING SCHEMAS & INTERFACES
// ==========================================
export type AgentId = 'direct' | 'cv' | 'audit' | 'bio' | 'voice';

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
const API_BASE = 'http://localhost:8000/api';

export const apiService = {
  async initializeSession(): Promise<string> {
    const response = await axios.get<SessionResponse>(`${API_BASE}/session`);
    localStorage.setItem('guest_token', response.data.token);
    return response.data.token;
  },

  async getChatHistory(token: string, agentId: AgentId): Promise<ChatMessage[]> {
    const response = await axios.get<ChatMessage[]>(`${API_BASE}/history/${token}/${agentId}`);
    return response.data;
  },

  async executePipeline(token: string, agentId: AgentId, text: string): Promise<ChatMessage> {
    const response = await 
    axios.post
    <ChatMessage>(`${API_BASE}/execute/${token}`, { agent_id: agentId, text: text });
    return response.data;
  }
};
