import axios from "axios";

export const api = axios.create({
  baseURL: "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

// ============================================================
// Types
// ============================================================

export interface Session {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

export interface ChatSource {
  chunk_id: string;
  title: string;
  guest: string | null;
  date: string | null;
  source_url: string | null;
  score: number;
}

export interface ChatResponse {
  provider: string;
  model: string;
  response: string;
  sources: ChatSource[];
}

export interface Message {
  id?: string;
  session_id?: string;
  role: string;
  content: string;
  created_at?: string;
  metadata?: Record<string, unknown>;
}

// ============================================================
// Agent Response
// ============================================================

export interface AgentResponse {
  response: string;
  artifact_id: string | null;
  run_id: string;
  skill: string;
  status: string;
}

// ============================================================
// Session API
// ============================================================

export const createSession = async (
  title: string = "Lenny Growth Assistant"
): Promise<Session> => {
  const response = await api.post<Session>("/sessions", {
    title,
  });

  return response.data;
};

export const getSessionMessages = async (
  sessionId: string
): Promise<Message[]> => {
  const response = await api.get<Message[]>(
    `/sessions/${sessionId}/messages`
  );

  return response.data;
};

// ============================================================
// Chat API
// ============================================================

export const sendChatMessage = async (
  sessionId: string,
  prompt: string,
  topK: number = 5
): Promise<ChatResponse> => {
  const response = await api.post<ChatResponse>("/chat", {
    session_id: sessionId,
    prompt,
    top_k: topK,
  });

  return response.data;
};

// ============================================================
// Agent API
// ============================================================

export const runAgent = async (
  sessionId: string,
  prompt: string,
  conversationHistory: Message[] = []
): Promise<AgentResponse> => {
  const response = await api.post<AgentResponse>("/agent/run", {
    session_id: sessionId,
    prompt,
    conversation_history: conversationHistory.map((message) => ({
      role: message.role,
      content: message.content,
    })),
  });

  return response.data;
};

// ============================================================
// Artifact API
// ============================================================

export interface Artifact {
  id: string;
  session_id: string;
  run_id: string | null;
  artifact_type: string;
  title: string;
  content: string;
  metadata_json?: Record<string, unknown>;
  created_at?: string;
}

export const getArtifact = async (
  artifactId: string
): Promise<Artifact> => {
  const response = await api.get<Artifact>(
    `/artifacts/${artifactId}`
  );

  return response.data;
};

export const getSessionArtifacts = async (
  sessionId: string
): Promise<Artifact[]> => {
  const response = await api.get<Artifact[]>(
    `/artifacts/sessions/${sessionId}`
  );

  return response.data;
};