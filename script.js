// ═══════════════════════════════════════════
// LabelAI — script.js
// ═══════════════════════════════════════════

// ── UTILS ────────────────────────────────

function showLoading(msg = "Processing...") {
    document.getElementById("loadingMsg").textContent = msg;
    document.getElementById("loadingOverlay").classList.remove("hidden");
}
function hideLoading() {
    document.getElementById("loadingOverlay").classList.add("hidden");
}
function previewImage(input, id) {
    const el = document.getElementById(id);
    if (input.files && input.files[0]) {
        el.src = URL.createObjectURL(input.files[0]);
        el.classList.remove("hidden");
    }
}
function handleDragOver(e) {
    e.preventDefault();
    document.getElementById("uploadZone").classList.add("drag-over");
}
function handleDragLeave(e) {
    document.getElementById("uploadZone").classList.remove("drag-over");
}
function handleDrop(e, inputId) {
    e.preventDefault();
    document.getElementById("uploadZone").classList.remove("drag-over");
    const input = document.getElementById(inputId);
    input.files = e.dataTransfer.files;
    previewImage(input, "uploadPreview");
}
function setStatus(id, html, type = "") {
    const el = document.getElementById(id);
    el.innerHTML = html;
    el.className = "status-msg " + type;
    el.classList.remove("hidden");
}

// Active diagram name for AI context
let activeDiagramName = "";
let activeImagePath   = "";


// ── UPLOAD & EXTRACT ──────────────────────

async function uploadDiagram() {
    const fileInput = document.getElementById("diagramImage");
    if (!fileInput.files.length) {
        setStatus("uploadStatus", "Please select an image first.", "err"); return;
    }
    showLoading("Extracting labels...");

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);
    formData.append("diagram_name", document.getElementById("diagramName").value.trim());

    try {
        const data = await fetch("/upload_diagram", { method: "POST", body: formData })
                           .then(r => r.json());
        hideLoading();

        if (data.error) { setStatus("uploadStatus", data.error, "err"); return; }
        if (!data.keywords || Object.keys(data.keywords).length === 0) {
            setStatus("uploadStatus", data.message || "No labels detected.", "err"); return;
        }

        activeDiagramName = data.diagram_name;
        activeImagePath   = "";  // will come from saved list

        setStatus("uploadStatus",
            `✓ <b>${data.diagram_name}</b> — ${data.total_labels} label(s) extracted`, "ok");

        // Show editor with extracted data
        document.getElementById("editorTitle").textContent = data.diagram_name;
        renderEditor(data.label_config);
        document.getElementById("editorCard").classList.remove("hidden");

        // Show uploaded image as reference
        showReference(URL.createObjectURL(fileInput.files[0]));

        loadSavedDiagrams();

    } catch { hideLoading(); setStatus("uploadStatus", "Network error.", "err"); }
}


// ── REFERENCE IMAGE ───────────────────────

function showReference(src) {
    const wrap = document.getElementById("previewReference");
    const img  = document.getElementById("referenceImg");
    img.src = src;
    wrap.classList.remove("hidden");
}


// ── LABEL EDITOR ─────────────────────────

async function loadLabelEditor() {
    showLoading("Loading labels...");
    try {
        const config = await fetch("/get_label_config").then(r => r.json());
        hideLoading();
        if (!Object.keys(config).length) {
            setStatus("editorStatus", "No labels found. Upload a diagram first.", ""); return;
        }
        renderEditor(config);
        document.getElementById("editorCard").classList.remove("hidden");
        if (activeImagePath) showReference(`/uploads_serve/${activeImagePath}`);
    } catch { hideLoading(); }
}

function renderEditor(config) {
    const list = document.getElementById("labelEditorList");
    list.innerHTML = "";

    Object.entries(config).forEach(([label, cfg]) => {
        const keywords = (cfg.keywords || []).join(", ");
        const row = document.createElement("div");
        row.className = "editor-row";
        row.innerHTML = `
            <div class="editor-row-top">
                <input class="editor-label-input" value="${label}" placeholder="Label name"
                       title="Edit label name">
                <button class="btn-remove-label" onclick="removeRow(this)" title="Delete label">✕</button>
            </div>
            <div class="editor-kw-wrap">
                <span class="kw-prefix">Keywords &amp; synonyms:</span>
                <textarea class="editor-kw-input" rows="2"
                          placeholder="comma-separated synonyms, alternate names, formulas..."
                >${keywords}</textarea>
                <button class="btn-ai-kw" onclick="generateAIForRow(this)" title="AI generate">✨</button>
            </div>`;
        list.appendChild(row);
    });
}

function removeRow(btn) {
    const row   = btn.closest(".editor-row");
    const label = row.querySelector(".editor-label-input").value.trim();
    if (label) {
        fetch("/delete_label", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ label })
        }).catch(() => {});
    }
    row.remove();
}

function addNewLabel() {
    const list = document.getElementById("labelEditorList");
    const row  = document.createElement("div");
    row.className = "editor-row new-row";
    row.innerHTML = `
        <div class="editor-row-top">
            <input class="editor-label-input" value="" placeholder="New label name">
            <button class="btn-remove-label" onclick="removeRow(this)">✕</button>
        </div>
        <div class="editor-kw-wrap">
            <span class="kw-prefix">Keywords &amp; synonyms:</span>
            <textarea class="editor-kw-input" rows="2" placeholder="comma-separated..."></textarea>
            <button class="btn-ai-kw" onclick="generateAIForRow(this)" title="AI generate">✨</button>
        </div>`;
    list.appendChild(row);
    row.querySelector(".editor-label-input").focus();
}

async function saveAllEdits() {
    const rows    = document.querySelectorAll(".editor-row");
    const updates = [];
    rows.forEach(row => {
        const label = row.querySelector(".editor-label-input").value.trim();
        const kwRaw = row.querySelector(".editor-kw-input").value.trim();
        const kws   = kwRaw.split(",").map(k => k.trim()).filter(Boolean);
        if (label) updates.push({ label, keywords: kws });
    });
    if (!updates.length) return;

    showLoading("Saving...");
    try {
        const data = await fetch("/save_label_edits", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ updates })
        }).then(r => r.json());
        hideLoading();
        setStatus("editorStatus", "✓ " + data.message, "ok");
    } catch { hideLoading(); setStatus("editorStatus", "Save failed.", "err"); }
}


// ── AI KEYWORD GENERATION ─────────────────

async function generateAIForRow(btn) {
    const row      = btn.closest(".editor-row");
    const label    = row.querySelector(".editor-label-input").value.trim();
    const textarea = row.querySelector(".editor-kw-input");
    if (!label) { alert("Enter a label name first."); return; }

    const orig = btn.textContent;
    btn.textContent = "⏳"; btn.disabled = true;

    try {
        const data = await fetch("/generate_keywords_ai", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ label, diagram_name: activeDiagramName })
        }).then(r => r.json());

        if (data.keywords?.length) {
            textarea.value = data.keywords.join(", ");
            textarea.style.borderColor = "var(--green)";
            setTimeout(() => textarea.style.borderColor = "", 1500);
        }
    } catch { alert("AI generation failed."); }
    btn.textContent = orig; btn.disabled = false;
}

async function generateAllAI() {
    const rows   = document.querySelectorAll(".editor-row");
    const labels = [...rows].map(r => r.querySelector(".editor-label-input").value.trim()).filter(Boolean);
    if (!labels.length) return;

    setStatus("editorStatus", `⏳ Generating AI keywords for ${labels.length} labels...`, "");
    try {
        const data = await fetch("/generate_keywords_ai", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ labels, diagram_name: activeDiagramName })
        }).then(r => r.json());

        if (data.results) {
            rows.forEach(row => {
                const label    = row.querySelector(".editor-label-input").value.trim();
                const textarea = row.querySelector(".editor-kw-input");
                if (data.results[label]) textarea.value = data.results[label].join(", ");
            });
            setStatus("editorStatus", `✓ AI keywords generated for ${labels.length} labels.`, "ok");
        }
    } catch { setStatus("editorStatus", "AI batch failed.", "err"); }
}


// ── SAVED DIAGRAMS ────────────────────────

async function loadSavedDiagrams() {
    try {
        const list = await fetch("/get_diagrams").then(r => r.json());
        renderSaved(list);
        document.getElementById("db-label").textContent =
            list.length ? `${list.length} saved` : "No diagrams";
    } catch {
        document.getElementById("savedList").innerHTML =
            `<p class="empty-msg">Could not load.</p>`;
    }
}

function renderSaved(list) {
    const c = document.getElementById("savedList");
    if (!list.length) { c.innerHTML = `<p class="empty-msg">No diagrams saved yet.</p>`; return; }

    c.innerHTML = list.map(d => `
        <div class="saved-item" id="saved-${d.id}">
            <div class="saved-thumb-wrap">
                ${d.image_path
                    ? `<img class="saved-thumb" src="/uploads_serve/${d.image_path}" alt="">`
                    : `<div class="saved-thumb-placeholder">🖼</div>`}
            </div>
            <div class="saved-info">
                <div class="saved-name">${d.name}</div>
                <div class="saved-meta">${d.label_count} labels · ${d.saved_at}</div>
                <div class="saved-labels">
                    ${d.raw_labels.slice(0,5).map(l => `<span class="tag-sm">${l}</span>`).join("")}
                    ${d.raw_labels.length > 5 ? `<span class="tag-sm muted">+${d.raw_labels.length-5}</span>` : ""}
                </div>
            </div>
            <div class="saved-actions">
                <button class="btn-act btn-load"
                        onclick="loadDiagram('${d.id}','${d.name}','${encodeURIComponent(d.image_path||'')}')">
                    Open
                </button>
                <button class="btn-act btn-delete" onclick="deleteDiagram('${d.id}','${d.name}')">
                    🗑
                </button>
            </div>
        </div>`).join("");
}

async function loadDiagram(id, name, encodedPath) {
    showLoading(`Loading '${name}'...`);
    try {
        const data = await fetch("/activate_diagram", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ diagram_id: id })
        }).then(r => r.json());
        hideLoading();

        activeDiagramName = name;
        activeImagePath   = decodeURIComponent(encodedPath || "");

        document.getElementById("editorTitle").textContent = name;
        renderEditor(data.label_config || {});
        document.getElementById("editorCard").classList.remove("hidden");

        if (activeImagePath)
            showReference(`/uploads_serve/${activeImagePath}`);

        document.getElementById("editorCard")
                .scrollIntoView({ behavior: "smooth" });

        // Highlight active
        document.querySelectorAll(".saved-item").forEach(el => el.classList.remove("active-diagram"));
        document.getElementById(`saved-${id}`)?.classList.add("active-diagram");

    } catch { hideLoading(); alert("Failed to load diagram."); }
}

async function deleteDiagram(id, name) {
    if (!confirm(`Delete '${name}'? This cannot be undone.`)) return;
    showLoading("Deleting...");
    try {
        await fetch("/delete_diagram", {
            method: "POST", headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ diagram_id: id })
        });
        hideLoading();
        document.getElementById(`saved-${id}`)?.remove();
        const c = document.getElementById("savedList");
        if (!c.querySelector(".saved-item"))
            c.innerHTML = `<p class="empty-msg">No diagrams saved yet.</p>`;
        document.getElementById("db-label").textContent =
            `${document.querySelectorAll(".saved-item").length} saved`;
    } catch { hideLoading(); alert("Delete failed."); }
}

// Load on start
loadSavedDiagrams();
