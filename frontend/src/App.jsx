import { useState } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [repoPath, setRepoPath] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [indexing, setIndexing] = useState(false);
  const [asking, setAsking] = useState(false);
  const [indexed, setIndexed] = useState(false);
  const [repoId, setRepoId] = useState("");

  const [githubUrl, setGithubUrl] = useState("");
  const [connecting, setConnecting] = useState(false);
  const connectRepository = async () => {
    if (!githubUrl.trim()) return;

    setConnecting(true);

    try {
      const response = await fetch(
        `${API_URL}/repository/connect`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            github_url: githubUrl,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail ||
          "Failed to connect repository"
        );
      }

      setIndexed(true);
      setRepoId(data.repo_id);
      setMessages([
        {
          role: "assistant",
          content:
            `Repository connected successfully. ` +
            `Found ${data.files} files and ` +
            `${data.chunks} code chunks.`,
          sources: [],
        },
      ]);

    } catch (error) {

      setMessages([
        {
          role: "assistant",
          content:
            `Error: ${error.message}`,
          sources: [],
        },
      ]);

    } finally {

      setConnecting(false);
    }
  };
  const askQuestion = async () => {

  if (!question.trim()) {
    return;
  }

  if (!repoId) {
    return;
  }

  const userQuestion = question.trim();

  // Save conversation history BEFORE
  // adding the current question
  const history = messages.map(
    (message) => ({
      role: message.role,
      content: message.content
    })
  );

  // Show user's message immediately
  setMessages((prev) => [
    ...prev,
    {
      role: "user",
      content: userQuestion
    }
  ]);

  // Clear input box
  setQuestion("");

  setAsking(true);

  try {

    const response = await fetch(
      `${API_URL}/chat`,
      {
        method: "POST",

        headers: {
          "Content-Type": "application/json"
        },

        body: JSON.stringify({

          question: userQuestion,

          repo_id: repoId,

          history: history,

          limit: 5

        })
      }
    );

    const data = await response.json();

    if (!response.ok) {

      throw new Error(
        data.detail ||
        "Failed to get response"
      );

    }

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: data.answer,
        sources: data.sources || []
      }
    ]);

  } catch (error) {

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content:
          `Error: ${error.message}`,
        sources: []
      }
    ]);

  } finally {

    setAsking(false);

  }
};

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      askQuestion();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>AI Codebase Assistant</h1>
          <p>
            Ask questions about your codebase using RAG
          </p>
        </div>

        <div
          className={
            indexed
              ? "status connected"
              : "status"
          }
        >
          <span></span>
          {indexed ? "Repository Indexed" : "Not Indexed"}
        </div>
      </header>

      <main className="container">

        <section className="repository-card">

          <div>
            <h2>Connect Repository</h2>

            <p>
              Paste a public GitHub repository URL
              to analyze its codebase.
            </p>
          </div>

          <div className="repo-input">

            <input
              type="text"
              placeholder="https://github.com/user/repository"
              value={githubUrl}
              onChange={(e) =>
                setGithubUrl(e.target.value)
              }
            />

            <button
              onClick={connectRepository}
              disabled={connecting}
            >
              {connecting
                ? "Connecting..."
                : "Connect"}
            </button>

          </div>

        </section>

        <section className="chat-card">

          <div className="chat-header">
            <div>
              <h2>Codebase Chat</h2>
              <p>
                Ask anything about your repository
              </p>
            </div>
          </div>

          <div className="messages">

            {messages.length === 0 && (
              <div className="empty">
                <div className="empty-icon">
                  {"</>"}
                </div>

                <h3>
                  Start exploring your codebase
                </h3>

                <p>
                  Index a repository and ask questions
                  about its implementation.
                </p>

                <div className="suggestions">
                  <button
                    onClick={() =>
                      setQuestion(
                        "Explain the architecture of this project"
                      )
                    }
                  >
                    Explain the architecture
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "Where is the main application initialized?"
                      )
                    }
                  >
                    Find the main entry point
                  </button>

                  <button
                    onClick={() =>
                      setQuestion(
                        "Explain the most important functions"
                      )
                    }
                  >
                    Explain important functions
                  </button>
                </div>
              </div>
            )}

            {messages.map((message, index) => (
              <div
                className={`message ${message.role
                  }`}
                key={index}
              >
                <div className="message-label">
                  {message.role === "user"
                    ? "You"
                    : "AI"}
                </div>

                <div className="message-content">
                  {message.content}
                </div>

                {message.sources?.length > 0 && (
                  <div className="sources">
                    <div className="sources-title">
                      Sources
                    </div>

                    {message.sources.map(
  (source, i) => (
    <div
      className="source"
      key={i}
    >
      <div className="source-file">
        {source.file}
      </div>

      <div className="source-details">

        {source.symbol && (
          <span>
            {source.symbol}
          </span>
        )}

        {source.start_line && (
          <span>
            Lines {source.start_line}
            {"–"}
            {source.end_line}
          </span>
        )}

      </div>
    </div>
  )
)}
                  </div>
                )}
              </div>
            ))}

            {asking && (
              <div className="message assistant">
                <div className="message-label">
                  AI
                </div>

                <div className="typing">
                  Searching codebase
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
              </div>
            )}

          </div>

          <div className="input-area">
            <textarea
              placeholder="Ask about your code..."
              value={question}
              onChange={(e) =>
                setQuestion(e.target.value)
              }
              onKeyDown={handleKeyDown}
              rows="1"
            />

            <button
              className="send-button"
              onClick={askQuestion}
              disabled={
                asking || !question.trim()
              }
            >
              ➤
            </button>
          </div>

          <div className="hint">
            Press Enter to send
          </div>

        </section>

      </main>
    </div>
  );
}

export default App;