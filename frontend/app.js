/* ═══════════════ app.js — CareerCompass Chat Logic ═══════════════ */

const API_BASE = "http://localhost:8000";

// ── State ────────────────────────────────────────────────────────────────────
const state = {
  sessionId: localStorage.getItem("cc_session_id") || null,
  isStreaming: false,
  messageCount: 0,
};

// ── DOM References ────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const messageInput    = $("messageInput");
const sendBtn         = $("sendBtn");
const messagesList    = $("messagesList");
const welcomeState    = $("welcomeState");
const messagesContainer = $("messagesContainer");
const charCount       = $("charCount");
const modelDot        = $("modelDot");
const modelStatus     = $("modelStatus");
const headerSub       = $("headerSub");
const nlpBadge        = $("nlpBadge");
const nlpTags         = $("nlpTags");
const sidebarToggle   = $("sidebarToggle");
const sidebar         = document.querySelector(".sidebar");
const mobileMenuBtn   = $("mobileMenuBtn");
const newChatBtn      = $("newChatBtn");
const clearChatBtn    = $("clearChatBtn");

// ── Health Check ──────────────────────────────────────────────────────────────
async function checkHealth() {
  try {
    const res = await fetch(`${API_BASE}/health`);
    const data = await res.json();
    if (data.ollama === "connected") {
      modelDot.className = "model-dot online";
      modelStatus.textContent = "Online · Ready";
    } else {
      modelDot.className = "model-dot offline";
      modelStatus.textContent = "Ollama offline";
    }
  } catch {
    modelDot.className = "model-dot offline";
    modelStatus.textContent = "Server not reachable";
  }
}

// ── Markdown Renderer (basic) ─────────────────────────────────────────────────
function renderMarkdown(text) {
  return text
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) =>
      `<pre><code class="lang-${lang}">${escapeHtml(code.trim())}</code></pre>`)
    // Inline code
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Bold
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    // Italic
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm,  '<h2>$1</h2>')
    .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
    // Blockquote
    .replace(/^> (.+)$/gm, '<blockquote>$1</blockquote>')
    // Horizontal rule
    .replace(/^---+$/gm, '<hr style="border:none;border-top:1px solid var(--border);margin:12px 0"/>')
    // Unordered list
    .replace(/^[\s]*[-*] (.+)$/gm, '<li>$1</li>')
    .replace(/(<li>.*<\/li>\n?)+/g, (m) => `<ul>${m}</ul>`)
    // Ordered list
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Paragraphs
    .replace(/\n\n+/g, '</p><p>')
    .replace(/^(?!<[hup]|<li|<pre|<blockquote|<hr)(.+)$/gm, (m) =>
      m.startsWith('<') ? m : `<p>${m}</p>`)
    // Line breaks within paragraphs
    .replace(/([^>])\n([^<])/g, '$1<br>$2');
}

function escapeHtml(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── NLP Badge ─────────────────────────────────────────────────────────────────
function showNlpBadge(analysis) {
  const tags = [];
  if (analysis.intent)  tags.push(`Intent: ${analysis.intent.replace('_', ' ')}`);
  if (analysis.domain)  tags.push(`Domain: ${analysis.domain.replace('_', ' ')}`);
  if (analysis.skills?.length) tags.push(`Skills: ${analysis.skills.slice(0,3).join(', ')}`);

  if (tags.length === 0) { nlpBadge.style.display = "none"; return; }

  nlpTags.innerHTML = tags.map(t => `<span class="nlp-tag">${t}</span>`).join("");
  nlpBadge.style.display = "flex";

  setTimeout(() => { nlpBadge.style.display = "none"; }, 6000);
}

// ── Message Rendering ─────────────────────────────────────────────────────────
function hideWelcome() {
  if (welcomeState.style.display !== "none") {
    welcomeState.style.display = "none";
  }
}

function appendMessage(role, content = "", streaming = false) {
  hideWelcome();

  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  const avatar = document.createElement("div");
  avatar.className = `avatar ${role === "user" ? "user-avatar" : "bot"}`;
  avatar.textContent = role === "user" ? "U" : "CC";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble";

  if (streaming) {
    // Show typing indicator first
    bubble.innerHTML = `<div class="typing-indicator">
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    </div>`;
  } else {
    bubble.innerHTML = role === "user"
      ? `<p>${escapeHtml(content)}</p>`
      : renderMarkdown(content);
  }

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesList.appendChild(row);

  scrollToBottom();
  state.messageCount++;
  headerSub.textContent = `${state.messageCount} message${state.messageCount > 1 ? 's' : ''} in this session`;

  return bubble;
}

function renderMatchCard(matchData) {
  hideWelcome();

  const row = document.createElement("div");
  row.className = "message-row bot";

  const avatar = document.createElement("div");
  avatar.className = "avatar bot";
  avatar.textContent = "CC";

  const bubble = document.createElement("div");
  bubble.className = "message-bubble match-card";

  const overlappingHtml = matchData.overlapping_skills.map(s => `<span class="skill-tag overlap">${s}</span>`).join("");
  const missingHtml = matchData.missing_skills.map(s => `<span class="skill-tag missing">${s}</span>`).join("");

  bubble.innerHTML = `
    <div class="match-card-header">
      <div class="match-score-circle">
        <svg viewBox="0 0 36 36" class="circular-chart gold">
          <path class="circle-bg"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path class="circle"
            stroke-dasharray="${matchData.match_score}, 100"
            d="M18 2.0845
              a 15.9155 15.9155 0 0 1 0 31.831
              a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <text x="18" y="20.35" class="percentage">${matchData.match_score}%</text>
        </svg>
      </div>
      <div class="match-title">
        <h3>TF-IDF Resume Match</h3>
        <p>Target Role: <strong>${matchData.domain}</strong></p>
      </div>
    </div>
    <div class="match-details">
      <div class="match-section">
        <h4>Overlapping Skills (Extracted)</h4>
        <div class="skills-container">${overlappingHtml || "<em>None detected</em>"}</div>
      </div>
      <div class="match-section">
        <h4>Missing Skills (Gap Analysis)</h4>
        <div class="skills-container">${missingHtml || "<em>None detected</em>"}</div>
      </div>
    </div>
  `;

  row.appendChild(avatar);
  row.appendChild(bubble);
  messagesList.appendChild(row);
  scrollToBottom();
}

function scrollToBottom() {
  messagesContainer.scrollTo({ top: messagesContainer.scrollHeight, behavior: "smooth" });
}

// ── Send Message ──────────────────────────────────────────────────────────────
async function sendMessage(text) {
  if (!text.trim() || state.isStreaming) return;

  const userText = text.trim();
  messageInput.value = "";
  messageInput.style.height = "auto";
  charCount.textContent = "0 / 2000";
  sendBtn.disabled = true;
  state.isStreaming = true;

  // Append resume text silently to the backend payload if present
  let finalMessageText = userText;
  if (uploadedResumeText) {
    finalMessageText += `\n\n--- ATTACHED RESUME ---\n${uploadedResumeText}\n-----------------------\n`;
  }

  // Render user message (without the wall of resume text)
  appendMessage("user", userText);

  // Bot bubble with typing indicator
  const botBubble = appendMessage("bot", "", true);
  let rawTokens = "";

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        message: finalMessageText,
        session_id: state.sessionId,
      }),
    });

    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop(); // keep incomplete

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;

        try {
          const chunk = JSON.parse(jsonStr);

          if (chunk.type === "meta") {
            state.sessionId = chunk.session_id;
            localStorage.setItem("cc_session_id", chunk.session_id);
            if (chunk.nlp) showNlpBadge(chunk.nlp);
            if (chunk.match_data) renderMatchCard(chunk.match_data);

          } else if (chunk.type === "token") {
            rawTokens += chunk.content;
            // Update bubble with rendered markdown on each token
            botBubble.innerHTML = renderMarkdown(rawTokens);
            scrollToBottom();

          } else if (chunk.type === "done") {
            // Final render
            botBubble.innerHTML = renderMarkdown(rawTokens);
            scrollToBottom();
          }
        } catch { /* skip malformed JSON */ }
      }
    }
  } catch (err) {
    botBubble.innerHTML = `<p style="color:#ef4444">⚠️ Error: ${err.message}. Is the backend running?</p>`;
  }

  state.isStreaming = false;
  sendBtn.disabled = !messageInput.value.trim();
}

// ── Event Listeners ───────────────────────────────────────────────────────────

// ── File Upload Logic ──
let uploadedResumeText = "";
const resumeUpload = $("resumeUpload");
const resumeBadge = $("resumeBadge");
const resumeName = $("resumeName");
const resumeClear = $("resumeClear");

if (resumeUpload) {
  resumeUpload.addEventListener("change", async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    resumeName.textContent = file.name + " (extracting...)";
    resumeBadge.style.display = "flex";
    sendBtn.disabled = true;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/extract_resume`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error("Failed to extract PDF");
      
      const data = await res.json();
      uploadedResumeText = data.text;
      resumeName.textContent = file.name;
      sendBtn.disabled = false;
    } catch (err) {
      alert("Error parsing PDF: " + err.message);
      uploadedResumeText = "";
      resumeBadge.style.display = "none";
      resumeUpload.value = "";
    }
  });
}

if (resumeClear) {
  resumeClear.addEventListener("click", () => {
    uploadedResumeText = "";
    resumeBadge.style.display = "none";
    resumeUpload.value = "";
  });
}

// Input handling — auto-resize and char count
messageInput.addEventListener("input", () => {
  const len = messageInput.value.length;
  charCount.textContent = `${len} / 2000`;
  sendBtn.disabled = (len === 0 && !uploadedResumeText) || state.isStreaming;

  // Auto-resize
  messageInput.style.height = "auto";
  messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + "px";
});

// Send on Enter (Shift+Enter for newline)
messageInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    if (!sendBtn.disabled) sendMessage(messageInput.value);
  }
});

// Send button
sendBtn.addEventListener("click", () => {
  if (messageInput.value.trim() || uploadedResumeText) {
    sendMessage(messageInput.value || "Please review my attached resume.");
  }
});

// Quick action buttons (sidebar)
document.querySelectorAll(".quick-action-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const prompt = btn.dataset.prompt;
    if (prompt) sendMessage(prompt);
    // Close sidebar on mobile
    if (window.innerWidth <= 768) sidebar.classList.remove("mobile-open");
  });
});

// Welcome chips
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const prompt = chip.dataset.prompt;
    if (prompt) sendMessage(prompt);
  });
});

// Sidebar toggle (desktop)
sidebarToggle.addEventListener("click", () => {
  sidebar.classList.toggle("collapsed");
});

// Mobile menu toggle
mobileMenuBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  sidebar.classList.toggle("mobile-open");
});

// Close mobile sidebar if clicked outside (on the chat main)
document.querySelector(".chat-main").addEventListener("click", () => {
  if (window.innerWidth <= 768 && sidebar.classList.contains("mobile-open")) {
    sidebar.classList.remove("mobile-open");
  }
});

// New chat
newChatBtn.addEventListener("click", () => {
  state.sessionId = null;
  localStorage.removeItem("cc_session_id");
  state.messageCount = 0;
  messagesList.innerHTML = "";
  welcomeState.style.display = "flex";
  headerSub.textContent = "Ask me anything about your career";
  nlpBadge.style.display = "none";
});

// Clear chat
clearChatBtn.addEventListener("click", async () => {
  if (state.sessionId) {
    try {
      await fetch(`${API_BASE}/history/${state.sessionId}`, { method: "DELETE" });
    } catch { /* ignore */ }
  }

  state.sessionId = null;
  localStorage.removeItem("cc_session_id");
  state.messageCount = 0;
  messagesList.innerHTML = "";
  welcomeState.style.display = "flex";
  headerSub.textContent = "Ask me anything about your career";
  nlpBadge.style.display = "none";
});

// ── Init ──────────────────────────────────────────────────────────────────────
checkHealth();
setInterval(checkHealth, 30000); // Re-check every 30s
messageInput.focus();
