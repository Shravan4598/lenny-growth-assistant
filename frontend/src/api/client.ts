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