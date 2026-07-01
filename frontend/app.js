const API_BASE = "";

let currentDocId = null;

async function apiFetch(path, options = {}) {
    const res = await fetch(`${API_BASE}${path}`, {
        headers: { "Content-Type": "application/json", ...options.headers },
        ...options,
    });
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
}

function showToast(message, type = "success") {
    const existing = document.querySelector(".toast");
    if (existing) existing.remove();
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
}

function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleString();
}

function renderStats() {
    apiFetch("/api/stats").then(stats => {
        document.getElementById("stat-docs").textContent = stats.total_documents;
        document.getElementById("stat-processed").textContent = stats.processed;
        document.getElementById("stat-words").textContent = stats.total_words.toLocaleString();
        document.getElementById("stat-chars").textContent = stats.total_chars.toLocaleString();
        const pct = stats.total_documents > 0
            ? Math.round((stats.processed / stats.total_documents) * 100)
            : 0;
        document.getElementById("progress-fill").style.width = `${pct}%`;
    }).catch(() => {});
}

function renderDocumentList() {
    apiFetch("/api/documents?limit=100").then(data => {
        const list = document.getElementById("doc-list");
        if (data.documents.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="icon">📄</div>
                    <p>No documents yet. Ingest some text or upload a file to get started.</p>
                </div>
            `;
            return;
        }
        list.innerHTML = data.documents.map(d => `
            <div class="doc-item" onclick="loadDocument(${d.id})">
                <div class="doc-title">${escapeHtml(d.title || "Untitled")}</div>
                <div class="doc-meta">
                    <span>${d.content_type}</span>
                    <span>${d.word_count} words</span>
                    <span>${formatDate(d.created_at)}</span>
                    <span class="status-badge ${d.processed ? 'status-processed' : 'status-pending'}">
                        ${d.processed ? 'Processed' : 'Pending'}
                    </span>
                </div>
            </div>
        `).join("");
    }).catch(() => {});
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function renderStructuredPanel(structured) {
    const panel = document.getElementById("structured-panel");
    if (!structured || !structured.raw_json) {
        panel.innerHTML = `
            <div class="empty-state">
                <div class="icon">📊</div>
                <p>Ollama not available or document not processed yet. <br>
                <span style="font-size:0.8rem;color:#999;">Make sure Ollama is running with phi3:mini.</span></p>
            </div>
        `;
        return;
    }
    const json = typeof structured.raw_json === "string"
        ? JSON.parse(structured.raw_json)
        : structured.raw_json;
    const topics = (json.key_topics || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join("");
    const entities = (json.extracted_entities || []).map(e =>
        `<span class="entity-tag">${escapeHtml(e.type)}: ${escapeHtml(e.name)}</span>`
    ).join("");

    panel.innerHTML = `
        <div class="detail-section">
            <h3>${escapeHtml(json.title || "Untitled")}</h3>
            <p style="font-size:0.85rem;color:#555;">${escapeHtml(json.ai_summary || "")}</p>
        </div>
        <div class="detail-section">
            <h3>Key Topics</h3>
            <div>${topics || "None"}</div>
        </div>
        <div class="detail-section">
            <h3>Extracted Entities</h3>
            <div>${entities || "None"}</div>
        </div>
        <div class="detail-section" style="display:flex;gap:0.5rem;flex-wrap:wrap;">
            <span class="badge" style="background:#e3f2fd;color:#1565c0;">${escapeHtml(json.document_type || "other")}</span>
            <span class="badge" style="background:${json.sentiment === 'positive' ? '#e8f5e9' : json.sentiment === 'negative' ? '#ffebee' : '#fff3e0'};color:${json.sentiment === 'positive' ? '#2e7d32' : json.sentiment === 'negative' ? '#c62828' : '#e65100'};">${escapeHtml(json.sentiment || "neutral")}</span>
        </div>
        <div class="actions" style="margin-top:1rem;">
            <button class="btn btn-secondary" onclick="downloadStructuredJSON()">Download JSON</button>
        </div>
    `;
}

function downloadStructuredJSON() {
    if (!currentDocId) return;
    apiFetch(`/api/documents/${currentDocId}`).then(data => {
        const json = data.structured_output;
        if (!json) {
            showToast("No structured data available", "error");
            return;
        }
        const blob = new Blob([JSON.stringify(json, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `document-${currentDocId}-structured.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showToast("JSON downloaded");
    }).catch(err => {
        showToast("Download failed: " + err.message, "error");
    });
}

async function loadDocument(docId) {
    currentDocId = docId;
    try {
        const data = await apiFetch(`/api/documents/${docId}`);
        const doc = data.document;
        const detail = document.getElementById("doc-detail");
        const entitiesHtml = (data.entities || []).map(e =>
            `<span class="entity-tag" title="confidence: ${(e.confidence * 100).toFixed(0)}%">${escapeHtml(e.entity_type)}: ${escapeHtml(e.entity_value)}</span>`
        ).join("");

        const tagsHtml = (data.summary?.suggested_tags || []).map(t =>
            `<span class="tag">${escapeHtml(t)}</span>`
        ).join("");

        const classificationHtml = data.classification
            ? `<p><strong>Category:</strong> ${escapeHtml(data.classification.category)} <span class="entity-tag">${(data.classification.confidence * 100).toFixed(0)}% confident</span></p>`
            : "<p>No classification available</p>";

        detail.innerHTML = `
            <div class="detail-section">
                <h3>Summary</h3>
                <p>${escapeHtml(data.summary?.summary_text || "No summary generated")}</p>
            </div>
            <div class="detail-section">
                <h3>Classification</h3>
                ${classificationHtml}
            </div>
            <div class="detail-section">
                <h3>Entities (${(data.entities || []).length})</h3>
                <div>${entitiesHtml || "No entities found"}</div>
            </div>
            <div class="detail-section">
                <h3>Suggested Tags</h3>
                <div>${tagsHtml || "No tags generated"}</div>
            </div>
            <div class="detail-section">
                <h3>Raw Content <span style="font-weight:normal;font-size:0.8rem;color:#888;">(${doc.char_count} chars, ${doc.word_count} words)</span></h3>
                <div class="detail-text">${escapeHtml((doc.raw_text || "").slice(0, 2000))}</div>
                ${(doc.raw_text || "").length > 2000 ? '<p style="font-size:0.8rem;color:#888;margin-top:0.3rem;">Content truncated to 2000 characters</p>' : ""}
            </div>
            <div class="actions" style="margin-top:1rem;">
                <button class="btn btn-danger" onclick="deleteCurrentDoc()">Delete</button>
            </div>
        `;

        renderStructuredPanel(data.structured_output);
    } catch (err) {
        showToast("Failed to load document: " + err.message, "error");
    }
}

async function deleteCurrentDoc() {
    if (!currentDocId) return;
    if (!confirm("Delete this document?")) return;
    try {
        await apiFetch(`/api/documents/${currentDocId}`, { method: "DELETE" });
        showToast("Document deleted");
        currentDocId = null;
        document.getElementById("doc-detail").innerHTML = `
            <div class="empty-state">
                <div class="icon">📋</div>
                <p>Select a document from the list to view details.</p>
            </div>
        `;
        document.getElementById("structured-panel").innerHTML = `
            <div class="empty-state">
                <div class="icon">📊</div>
                <p>Select a processed document to view structured JSON output.</p>
            </div>
        `;
        renderDocumentList();
        renderStats();
    } catch (err) {
        showToast("Delete failed: " + err.message, "error");
    }
}

async function ingestText() {
    const text = document.getElementById("text-input").value.trim();
    const title = document.getElementById("doc-title").value.trim();
    if (!text) {
        showToast("Please enter some text", "error");
        return;
    }
    const btn = document.getElementById("btn-ingest-text");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Processing...';
    try {
        const formData = new URLSearchParams();
        formData.append("text", text);
        formData.append("title", title || "Text Input");
        const res = await fetch(`${API_BASE}/api/ingest/text`, {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData,
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        const data = await res.json();
        showToast(`Document #${data.document_id} processed! ${data.entities_found} entities found.`);
        document.getElementById("text-input").value = "";
        renderDocumentList();
        renderStats();
        loadDocument(data.document_id);
        pollStructuredOutput(data.document_id);
    } catch (err) {
        showToast("Ingestion failed: " + err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Analyze Text';
    }
}

function pollStructuredOutput(docId) {
    const startTime = Date.now();
    const maxDuration = 60000;
    const interval = setInterval(async () => {
        if (Date.now() - startTime > maxDuration) {
            clearInterval(interval);
            return;
        }
        try {
            const data = await apiFetch(`/api/documents/${docId}`);
            const so = data.structured_output;
            if (so && so.raw_json) {
                clearInterval(interval);
                if (currentDocId === docId) {
                    renderStructuredPanel(so);
                }
            }
        } catch (err) {
            clearInterval(interval);
        }
    }, 2000);
}

async function ingestFile() {
    const fileInput = document.getElementById("file-input");
    if (!fileInput.files.length) {
        showToast("Please select a file", "error");
        return;
    }
    const file = fileInput.files[0];
    const btn = document.getElementById("btn-ingest-file");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Uploading & Processing...';
    try {
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_BASE}/api/ingest/file`, {
            method: "POST",
            body: formData,
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({ detail: res.statusText }));
            throw new Error(err.detail || `HTTP ${res.status}`);
        }
        const data = await res.json();
        showToast(`File processed! ${data.entities_found} entities found.`);
        fileInput.value = "";
        renderDocumentList();
        renderStats();
        loadDocument(data.document_id);
        pollStructuredOutput(data.document_id);
    } catch (err) {
        showToast("File ingestion failed: " + err.message, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Upload & Analyze';
    }
}

function searchDocuments() {
    const q = document.getElementById("search-input").value.trim();
    if (!q) {
        renderDocumentList();
        return;
    }
    apiFetch(`/api/search?q=${encodeURIComponent(q)}`).then(data => {
        const list = document.getElementById("doc-list");
        if (data.results.length === 0) {
            list.innerHTML = `<div class="empty-state"><p>No results for "${escapeHtml(q)}"</p></div>`;
            return;
        }
        list.innerHTML = data.results.map(d => `
            <div class="doc-item" onclick="loadDocument(${d.id})">
                <div class="doc-title">${escapeHtml(d.title || "Untitled")}</div>
                <div class="doc-meta">
                    <span>${d.content_type}</span>
                    <span>${d.word_count} words</span>
                    <span>${formatDate(d.created_at)}</span>
                </div>
            </div>
        `).join("");
    }).catch(() => {});
}

document.addEventListener("DOMContentLoaded", () => {
    renderStats();
    renderDocumentList();
});
