import { useState, useRef, useEffect } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

function parseRepoName(url) {
  const cleaned = url.trim().replace(/\.git$/, "").replace(/\/$/, "");
  const match = cleaned.match(/github\.com\/([^/]+)\/([^/]+)/i);
  return match ? `${match[1]}/${match[2]}` : cleaned;
}

function dedupeSources(sources = []) {
  const seen = new Map();
  sources.forEach((s) => {
    const key = `${s.file}-${s.start_line}-${s.end_line}-${s.symbol}`;
    if (!seen.has(key)) seen.set(key, s);
  });
  return Array.from(seen.values());
}

function fileTail(path, segments = 2) {
  const parts = path.split("/");
  if (parts.length <= segments) return path;
  return `.../${parts.slice(-segments).join("/")}`;
}

function renderInline(line, keyPrefix) {
  const parts = line.split(/(\*\*[^*]+\*\*|`[^`]+`)/g).filter(Boolean);
  return parts.map((part, idx) => {
    const key = `${keyPrefix}-${idx}`;
    if (part.startsWith("**") && part.endsWith("**")) {
      return <strong key={key}>{part.slice(2, -2)}</strong>;
    }
    if (part.startsWith("`") && part.endsWith("`")) {
      return <code key={key}>{part.slice(1, -1)}</code>;
    }
    return <span key={key}>{part}</span>;
  });
}

function MessageBody({ text }) {
  const lines = text.split("\n");
  return (
    <>
      {lines.map((line, i) =>
        line.trim() === "" ? (
          <div key={i} className="line-break" />
        ) : (
          <p key={i} className="line">
            {renderInline(line, i)}
          </p>
        )
      )}
    </>
  );
}

function Logomark() {
  return (
    <svg
      className="logomark"
      width="22"
      height="22"
      viewBox="0 0 22 22"
      fill="none"
      aria-hidden="true"
    >
      <rect x="1" y="4" width="14" height="2.4" rx="1.2" fill="#4B5361" />
      <rect x="1" y="9.8" width="20" height="2.4" rx="1.2" fill="#E3A857" />
      <rect x="1" y="15.6" width="10" height="2.4" rx="1.2" fill="#4B5361" />
    </svg>
  );
}

function App() {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [asking, setAsking] = useState(false);
  const [repoId, setRepoId] = useState("");
  const [repoInfo, setRepoInfo] = useState(null);

  const [githubUrl, setGithubUrl] = useState("");
  const [connecting, setConnecting] = useState(false);
  const [connectError, setConnectError] = useState("");

  const textareaRef = useRef(null);
  const threadEndRef = useRef(null);

  useEffect(() => {
    threadEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, asking]);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [question]);

  const connectRepository = async () => {
    if (!githubUrl.trim() || connecting) return;

    setConnecting(true);
    setConnectError("");

    try {
      const response = await fetch(`${API_URL}/repository/connect`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ github_url: githubUrl }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to connect repository");
      }

      setRepoId(data.repo_id);
      setRepoInfo({
        name: parseRepoName(githubUrl),
        files: data.files,
        chunks: data.chunks,
      });
      setMessages([]);
    } catch (error) {
      setConnectError(error.message);
    } finally {
      setConnecting(false);
    }
  };

  const disconnectRepository = () => {
    setRepoId("");
    setRepoInfo(null);
    setMessages([]);
    setGithubUrl("");
    setConnectError("");
  };

  const askQuestion = async () => {
    if (!question.trim() || !repoId || asking) return;

    const userQuestion = question.trim();

    const history = messages.map((message) => ({
      role: message.role,
      content: message.content,
    }));

    setMessages((prev) => [...prev, { role: "user", content: userQuestion }]);
    setQuestion("");
    setAsking(true);

    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: userQuestion,
          repo_id: repoId,
          history,
          limit: 5,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to get response");
      }

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer,
          sources: dedupeSources(data.sources),
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${error.message}`, sources: [], isError: true },
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

  const suggestions = [
    "Explain the architecture of this project",
    "Where is the main application initialized?",
    "Explain the most important functions",
  ];

  return (
    <div className="shell">
      <aside className="rail">
        <div className="brand">
          <Logomark />
          <div>
            <div className="brand-name">Codebase Assistant</div>
            <div className="brand-tag">Ask questions, get cited answers</div>
          </div>
        </div>

        {!repoInfo ? (
          <div className="connect-panel">
            <h2>Connect a repository</h2>
            <p>Paste a public GitHub repository URL to index its codebase.</p>

            <input
              type="text"
              placeholder="https://github.com/user/repository"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && connectRepository()}
            />

            <button
              className="primary-button"
              onClick={connectRepository}
              disabled={connecting || !githubUrl.trim()}
            >
              {connecting ? "Indexing repository…" : "Connect repository"}
            </button>

            {connectError && <div className="field-error">{connectError}</div>}
          </div>
        ) : (
          <div className="repo-panel">
            <div className="repo-panel-head">
              <span className="status-dot" />
              <span className="repo-name" title={repoInfo.name}>
                {repoInfo.name}
              </span>
            </div>

            <dl className="repo-stats">
              <div>
                <dt>Files indexed</dt>
                <dd>{repoInfo.files}</dd>
              </div>
              <div>
                <dt>Code chunks</dt>
                <dd>{repoInfo.chunks}</dd>
              </div>
            </dl>

            <button className="ghost-button" onClick={disconnectRepository}>
              Connect a different repository
            </button>
          </div>
        )}

        <div className="rail-footer">
          Answers are generated from indexed source only — verify anything
          load-bearing against the file itself.
        </div>
      </aside>

      <main className="main">
        <div className="thread">
          {messages.length === 0 && (
            <div className="empty">
              <div className="empty-mark">{"{ }"}</div>
              <h3>
                {repoInfo ? "Ask your first question" : "No repository connected"}
              </h3>
              <p>
                {repoInfo
                  ? "Try one of these, or ask anything about the codebase."
                  : "Connect a repository from the left panel to start exploring it."}
              </p>

              {repoInfo && (
                <div className="suggestions">
                  {suggestions.map((s) => (
                    <button key={s} onClick={() => setQuestion(s)}>
                      {s}
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          {messages.map((message, index) => (
            <div
              className={`message ${message.role}${message.isError ? " error" : ""}`}
              key={index}
            >
              <div className="message-label">
                {message.role === "user" ? "You" : "Assistant"}
              </div>

              <div className="message-content">
                <MessageBody text={message.content} />
              </div>

              {message.sources?.length > 0 && (
                <div className="cited">
                  <div className="cited-title">Cited passages</div>

                  {message.sources.map((source, i) => (
                    <div className="cite-row" key={i}>
                      <span className="cite-file" title={source.file}>
                        {fileTail(source.file)}
                      </span>
                      {source.symbol && (
                        <span className="cite-symbol">{source.symbol}</span>
                      )}
                      {source.start_line && (
                        <span className="cite-lines">
                          L{source.start_line}
                          {source.end_line ? `–${source.end_line}` : ""}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {asking && (
            <div className="message assistant">
              <div className="message-label">Assistant</div>
              <div className="typing">
                Searching codebase<span>.</span>
                <span>.</span>
                <span>.</span>
              </div>
            </div>
          )}

          <div ref={threadEndRef} />
        </div>

        <div className="composer">
          <textarea
            ref={textareaRef}
            placeholder={
              repoInfo ? "Ask about your code…" : "Connect a repository to begin"
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={!repoInfo}
            rows="1"
          />

          <button
            className="send-button"
            onClick={askQuestion}
            disabled={asking || !question.trim() || !repoInfo}
            aria-label="Send question"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path
                d="M1.5 8h11M8 2.5 13.5 8 8 13.5"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </button>
        </div>
        <div className="hint">Enter to send · Shift + Enter for a new line</div>
      </main>
    </div>
  );
}

export default App;