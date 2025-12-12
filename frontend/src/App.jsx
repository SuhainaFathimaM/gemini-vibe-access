import { useState } from "react";
import axios from "axios";
import "./App.css";

export default function App() {
  const [file, setFile] = useState(null);
  const [url, setUrl] = useState("");
  const [loadingStage, setLoadingStage] = useState(""); // "", "extract", "ai", "tts"
  const [result, setResult] = useState(null);
  const [mode, setMode] = useState("default"); // default | dyslexia | highcontrast

  const handleUpload = async () => {
    if (!file && !url.trim()) {
      alert("Please upload a file or enter a URL");
      return;
    }

    setResult(null);
    setLoadingStage("extract");

    try {
      const formData = new FormData();
      if (file) formData.append("file", file);
      if (!file && url) formData.append("url", url);

      // ping backend
      setLoadingStage("ai");
      const res = await axios.post("http://127.0.0.1:5000/process", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
        timeout: 120000,
      });

      setResult(res.data || null);
      setLoadingStage("");
    } catch (err) {
      console.error("Processing error:", err);
      alert("Error processing content. Check backend (see console).");
      setLoadingStage("");
    }
  };

  const onDownloadZip = () => {
    if (!result?.zip_url) return;
    window.open(result.zip_url, "_blank");
  };

  return (
    <div className={`container ${mode === "dyslexia" ? "dyslexia" : ""} ${mode === "highcontrast" ? "highcontrast" : ""}`}>
      <header className="header" role="banner">
        <h1>Gemini Vibe Access ⚡</h1>
        <p>AI-powered accessibility: Simplify • Listen • Visualize</p>

        <div className="modes">
          <label>
            <input type="radio" name="mode" checked={mode === "default"} onChange={() => setMode("default")} /> Default
          </label>
          <label>
            <input type="radio" name="mode" checked={mode === "dyslexia"} onChange={() => setMode("dyslexia")} /> Dyslexia Mode
          </label>
          <label>
            <input type="radio" name="mode" checked={mode === "highcontrast"} onChange={() => setMode("highcontrast")} /> High Contrast
          </label>
        </div>
      </header>

      <main>
        <section className="input-section" aria-label="Upload or URL">
          <div className="card" aria-hidden={loadingStage ? "true" : "false"}>
            <h3>Option 1: Upload PDF / TXT</h3>
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={(e) => {
                setFile(e.target.files[0]);
                setUrl("");
              }}
            />
          </div>

          <div className="card">
            <h3>Option 2: Website URL</h3>
            <input
              type="text"
              placeholder="https://en.wikipedia.org/wiki/Law"
              value={url}
              onChange={(e) => {
                setUrl(e.target.value);
                setFile(null);
              }}
            />
          </div>
        </section>

        <button
          className="process-btn"
          onClick={handleUpload}
          disabled={!!loadingStage}
          aria-busy={!!loadingStage}
        >
          {loadingStage ? (
            <>
              <span className="dot" />{" "}
              {loadingStage === "extract" ? "Extracting content..." : loadingStage === "ai" ? "Processing with Gemini..." : "Working..."}
            </>
          ) : (
            "✨ Make Accessible"
          )}
        </button>

        {result && (
          <section className="results-section" aria-live="polite">
            <div className="result-card">
              <h2>📖 Simplified Text</h2>
              <div className="simplified-text" tabIndex={0}>
                {result.simplified_text || "No simplified text returned."}
              </div>
            </div>

            <div className="result-card">
              <h2>🔊 Audio Output</h2>
              {result.audio_url ? (
                <audio controls className="audio-player" src={result.audio_url}></audio>
              ) : (
                <div>No audio generated.</div>
              )}
            </div>

            {result.keywords && result.keywords.length > 0 && (
              <div className="result-card">
                <h2>🤟 Sign Language Key Concepts</h2>
                <p style={{ color: "#666", marginBottom: 12 }}>Click any card to view the sign language video.</p>
                <div className="keywords-grid">
                  {result.keywords.map((w, i) => (
                    <a
                      key={i}
                      className="sign-card"
                      href={`https://www.signasl.org/sign/${encodeURIComponent(w)}`}
                      target="_blank"
                      rel="noreferrer"
                    >
                      <div className="sign-icon">👐</div>
                      <div className="sign-word">{w}</div>
                      <div className="sign-cta">Watch ↗</div>
                    </a>
                  ))}
                </div>
              </div>
            )}

            <div style={{ display: "flex", gap: 12 }}>
              {result.zip_url && (
                <button className="download-btn" onClick={onDownloadZip}>
                  📦 Download Accessibility Pack (ZIP)
                </button>
              )}
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
