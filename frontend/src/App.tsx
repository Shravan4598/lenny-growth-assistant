import React, { useEffect, useRef, useState } from "react";
import {
  createSession,
  getSessionMessages,
  sendChatMessage,
  type ChatSource,
  type Message,
} from "./api/client";
import { ArtifactViewer } from "./components/ArtifactViewer";

interface UIMessage {
  role: "user" | "assistant";
  content: string;
  sources?: ChatSource[];
}

function App() {
  // ==========================================================
  // State
  // ==========================================================

  const [sessionId, setSessionId] = useState<string | null>(null);

  const [messages, setMessages] = useState<UIMessage[]>([]);

  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const [initializing, setInitializing] = useState(true);

  const [error, setError] = useState<string | null>(null);

  const [activeArtifactId, setActiveArtifactId] = useState<string | null>(
    null
  );

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // ==========================================================
  // Auto-scroll
  // ==========================================================

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  // ==========================================================
  // Initialize session
  // ==========================================================

  useEffect(() => {
    initializeSession();
  }, []);

  const initializeSession = async () => {
    try {
      setInitializing(true);
      setError(null);

      // ------------------------------------------------------
      // Try to reuse existing session
      // ------------------------------------------------------

      const storedSessionId = localStorage.getItem(
        "lenny_session_id"
      );

      if (storedSessionId) {
        try {
          const existingMessages = await getSessionMessages(
            storedSessionId
          );

          setSessionId(storedSessionId);

          setMessages(
            existingMessages
              .filter(
                (message) =>
                  message.role === "user" ||
                  message.role === "assistant"
              )
              .map((message) => ({
                role:
                  message.role === "user"
                    ? "user"
                    : "assistant",
                content: message.content,
              }))
          );

          return;
        } catch (existingSessionError) {
          console.warn(
            "Stored session could not be loaded. Creating a new session.",
            existingSessionError
          );

          localStorage.removeItem(
            "lenny_session_id"
          );
        }
      }

      // ------------------------------------------------------
      // Create new session
      // ------------------------------------------------------

      const session = await createSession(
        "Lenny Growth Assistant"
      );

      setSessionId(session.id);

      localStorage.setItem(
        "lenny_session_id",
        session.id
      );

      setMessages([]);
    } catch (err) {
      console.error(
        "Failed to initialize chat session:",
        err
      );

      setError(
        "Unable to connect to the backend. Make sure Docker services are running."
      );
    } finally {
      setInitializing(false);
    }
  };

  // ==========================================================
  // Send message
  // ==========================================================

  const sendMessage = async () => {
    const currentInput = input.trim();

    if (!currentInput || loading || !sessionId) {
      return;
    }

    // --------------------------------------------------------
    // Clear error
    // --------------------------------------------------------

    setError(null);

    // --------------------------------------------------------
    // Optimistically display user message
    // --------------------------------------------------------

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: currentInput,
      },
    ]);

    setInput("");

    setLoading(true);

    try {
      // ------------------------------------------------------
      // Call backend
      // ------------------------------------------------------

      const result = await sendChatMessage(
        sessionId,
        currentInput,
        5
      );

      // ------------------------------------------------------
      // Display assistant response
      // ------------------------------------------------------

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: result.response,
          sources: result.sources,
        },
      ]);
    } catch (err) {
      console.error("Chat request failed:", err);

      setError(
        "Something went wrong while generating the response."
      );

      // Remove optimistic user message if request failed.
      setMessages((previous) => {
        const copy = [...previous];

        if (
          copy.length > 0 &&
          copy[copy.length - 1].role === "user" &&
          copy[copy.length - 1].content === currentInput
        ) {
          copy.pop();
        }

        return copy;
      });

      setInput(currentInput);
    } finally {
      setLoading(false);
    }
  };

  // ==========================================================
  // Handle Enter
  // ==========================================================

  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void sendMessage();
    }
  };

  // ==========================================================
  // New conversation
  // ==========================================================

  const startNewConversation = async () => {
    if (loading) {
      return;
    }

    try {
      setError(null);

      const session = await createSession(
        "Lenny Growth Assistant"
      );

      setSessionId(session.id);

      localStorage.setItem(
        "lenny_session_id",
        session.id
      );

      setMessages([]);

      setActiveArtifactId(null);
    } catch (err) {
      console.error(
        "Failed to create new session:",
        err
      );

      setError(
        "Unable to create a new conversation."
      );
    }
  };

  // ==========================================================
  // Loading screen
  // ==========================================================

  if (initializing) {
    return (
      <div className="h-screen w-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="text-xl font-semibold text-gray-800">
            Lenny Growth Assistant
          </div>

          <div className="mt-2 text-gray-500">
            Connecting to the backend...
          </div>
        </div>
      </div>
    );
  }

  // ==========================================================
  // Main UI
  // ==========================================================

  return (
    <div className="h-screen w-screen flex bg-gray-50 p-4 gap-4 font-sans">

      {/* ======================================================
          LEFT: CHAT
          ====================================================== */}

      <div className="w-1/2 flex flex-col border bg-white rounded-lg shadow-sm overflow-hidden">

        {/* Header */}

        <div className="p-4 bg-blue-600 text-white flex items-center justify-between">

          <div>
            <div className="font-bold text-lg">
              Lenny Growth Assistant
            </div>

            <div className="text-xs text-blue-100 mt-1">
              Transcript-grounded product & growth assistant
            </div>
          </div>

          <button
            onClick={startNewConversation}
            className="text-sm bg-white text-blue-600 px-3 py-2 rounded-md font-medium hover:bg-blue-50 transition"
          >
            New Chat
          </button>
        </div>

        {/* Session indicator */}

        {sessionId && (
          <div className="px-4 py-2 bg-gray-50 border-b text-xs text-gray-400">
            Session: {sessionId}
          </div>
        )}

        {/* Error */}

        {error && (
          <div className="mx-4 mt-3 p-3 rounded-md bg-red-50 border border-red-200 text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Messages */}

        <div className="flex-1 p-4 overflow-y-auto space-y-5">

          {messages.length === 0 && !loading && (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">

                <div className="text-4xl mb-4">
                  🎙️
                </div>

                <h2 className="text-xl font-semibold text-gray-800">
                  Ask Lenny anything
                </h2>

                <p className="text-gray-500 mt-2">
                  Ask questions about product, growth,
                  startups, leadership, and insights from
                  Lenny's Podcast and Newsletter.
                </p>

              </div>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.role === "user"
                  ? "justify-end"
                  : "justify-start"
              }`}
            >

              <div
                className={`max-w-[85%] rounded-xl px-4 py-3 ${
                  message.role === "user"
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >

                <div className="whitespace-pre-wrap leading-relaxed">
                  {message.content}
                </div>

                {/* Sources */}

                {message.role === "assistant" &&
                  message.sources &&
                  message.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-gray-200">

                      <div className="text-xs font-semibold text-gray-500 mb-2">
                        Sources
                      </div>

                      <div className="space-y-2">

                        {message.sources.map(
                          (source, sourceIndex) => (
                            <div
                              key={`${source.chunk_id}-${sourceIndex}`}
                              className="text-xs bg-white rounded-md p-2 border"
                            >

                              <div className="font-medium text-gray-700">
                                {source.title}
                              </div>

                              {source.guest && (
                                <div className="text-gray-500 mt-1">
                                  Guest: {source.guest}
                                </div>
                              )}

                              <div className="flex items-center justify-between mt-1">

                                {source.date && (
                                  <span className="text-gray-400">
                                    {source.date}
                                  </span>
                                )}

                                <span className="text-gray-400">
                                  Score:{" "}
                                  {source.score.toFixed(3)}
                                </span>

                              </div>

                              {source.source_url && (
                                <a
                                  href={source.source_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="inline-block mt-2 text-blue-600 hover:underline"
                                >
                                  View source
                                </a>
                              )}

                            </div>
                          )
                        )}

                      </div>
                    </div>
                  )}

              </div>

            </div>
          ))}

          {/* Loading */}

          {loading && (
            <div className="flex justify-start">

              <div className="bg-gray-100 rounded-xl px-4 py-3 text-gray-500">
                <span className="animate-pulse">
                  Lenny is thinking...
                </span>
              </div>

            </div>
          )}

          <div ref={messagesEndRef} />

        </div>

        {/* Input */}

        <div className="p-3 border-t bg-white">

          <div className="flex gap-2">

            <input
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={handleKeyDown}
              disabled={loading || !sessionId}
              className="flex-1 border border-gray-300 p-3 rounded-lg outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
              placeholder={
                sessionId
                  ? "Ask about product, growth, PMF..."
                  : "Connecting..."
              }
            />

            <button
              onClick={() => void sendMessage()}
              disabled={
                loading ||
                !input.trim() ||
                !sessionId
              }
              className="bg-blue-600 text-white px-5 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
            >
              {loading ? "..." : "Send"}
            </button>

          </div>

          <div className="text-xs text-gray-400 mt-2 text-center">
            Powered by Lenny's Podcast & Newsletter knowledge
          </div>

        </div>

      </div>

      {/* ======================================================
          RIGHT: ARTIFACT VIEWER
          ====================================================== */}

      <div className="flex-1 min-w-0">
        <ArtifactViewer
          artifactId={activeArtifactId}
        />
      </div>

    </div>
  );
}

export default App;