import type React from 'react';

export type AgentId = 'direct' | 'cv' | 'audit' | 'bio' | 'voice';

export interface Agent {
  id: AgentId;
  name: string;
  desc: string;
  icon: React.ComponentType<{ className?: string }>;
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
