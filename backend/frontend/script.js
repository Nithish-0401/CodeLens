const API_BASE = "http://127.0.0.1:8000";

const fileInput = document.getElementById("fileInput");
const reviewButton = document.getElementById("reviewButton");
const statusText = document.getElementById("status");
const dashboard = document.getElementById("overviewView");
const repoUrlInput = document.getElementById("repoUrl");
const filePathInput = document.getElementById("filePath");
const githubReviewButton = document.getElementById("githubReviewButton");
const githubStatusText = document.getElementById("githubStatus");

let latestReport = null;
let latestSource = "";
let toastTimer = null;

const views = {
  overview: document.getElementById("overviewView"),
  review: document.getElementById("reviewView"),
  findings: document.getElementById("findingsView"),
  settings: document.getElementById("settingsView")
};

function navigateTo(viewName) {
  if (!views[viewName]) viewName = "overview";
  Object.entries(views).forEach(([name, element]) => {
    element.classList.toggle("hidden", name !== viewName);
  });
  document.querySelectorAll(".nav-link[data-view]").forEach(button => {
    button.classList.toggle("active", button.dataset.view === viewName);
  });
  const labels = { overview: "Overview", review: "AI Code Review", findings: "Findings", settings: "Settings" };
  document.getElementById("pageCrumb").textContent = labels[viewName] || "Overview";
  document.getElementById("sidebar").classList.remove("sidebar-open");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

document.querySelectorAll("[data-view]").forEach(button => {
  button.addEventListener("click", () => {
    navigateTo(button.dataset.view);
    if (button.dataset.reviewTab === "github") setReviewTab("github");
  });
});

document.getElementById("mobileMenu").addEventListener("click", () => {
  document.getElementById("sidebar").classList.toggle("sidebar-open");
});

function setReviewTab(tab) {
  const github = tab === "github";
  document.getElementById("localTab").classList.toggle("active", !github);
  document.getElementById("githubTab").classList.toggle("active", github);
  document.getElementById("localTab").setAttribute("aria-selected", String(!github));
  document.getElementById("githubTab").setAttribute("aria-selected", String(github));
  document.getElementById("localPanel").classList.toggle("hidden", github);
  document.getElementById("githubPanel").classList.toggle("hidden", !github);
}

document.getElementById("localTab").addEventListener("click", () => setReviewTab("local"));
document.getElementById("githubTab").addEventListener("click", () => setReviewTab("github"));

fileInput.addEventListener("change", () => {
  const file = fileInput.files && fileInput.files[0];
  document.getElementById("fileNameLabel").textContent = file ? file.name : "Drop your Python file here";
  document.getElementById("dropZone").classList.toggle("has-file", Boolean(file));
  if (file) statusText.textContent = "";
});

const dropZone = document.getElementById("dropZone");
["dragenter", "dragover"].forEach(eventName => dropZone.addEventListener(eventName, event => {
  event.preventDefault();
  dropZone.classList.add("drag-over");
}));
["dragleave", "drop"].forEach(eventName => dropZone.addEventListener(eventName, event => {
  event.preventDefault();
  dropZone.classList.remove("drag-over");
}));
dropZone.addEventListener("drop", event => {
  const file = event.dataTransfer.files && event.dataTransfer.files[0];
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".py")) {
    statusText.textContent = "Only .py files are allowed.";
    return;
  }
  const transfer = new DataTransfer();
  transfer.items.add(file);
  fileInput.files = transfer.files;
  document.getElementById("fileNameLabel").textContent = file.name;
  dropZone.classList.add("has-file");
  statusText.textContent = "";
});

reviewButton.addEventListener("click", async () => {
  const file = fileInput.files && fileInput.files[0];
  if (!file) {
    statusText.textContent = "Please select a Python file.";
    return;
  }
  if (!file.name.toLowerCase().endsWith(".py")) {
    statusText.textContent = "Only .py files are allowed.";
    return;
  }

  const formData = new FormData();
  formData.append("file", file);
  setLoading(reviewButton, true, "Analyzing…");
  statusText.textContent = "Analyzing code with your review pipeline…";

  try {
    const response = await fetch(`${API_BASE}/upload`, { method: "POST", body: formData });
    const data = await readResponse(response);
    if (!data.report) throw new Error("The server response does not contain a review report.");
    displayReport(data.report, `Local file · ${file.name}`);
    statusText.textContent = "Code review completed successfully.";
    showToast("Review completed successfully");
    navigateTo("overview");
  } catch (error) {
    console.error(error);
    statusText.textContent = formatFetchError(error);
  } finally {
    setLoading(reviewButton, false, "Analyze Python file");
  }
});

githubReviewButton.addEventListener("click", async () => {
  const repoUrl = repoUrlInput.value.trim();
  const filePath = filePathInput.value.trim();
  if (!repoUrl || !filePath) {
    githubStatusText.textContent = "Please enter the repository URL and Python file path.";
    return;
  }
  if (!/^https:\/\/github\.com\/[^/]+\/[^/]+\/?$/.test(repoUrl)) {
    githubStatusText.textContent = "Enter a repository URL like https://github.com/owner/repository.";
    return;
  }
  if (!filePath.toLowerCase().endsWith(".py")) {
    githubStatusText.textContent = "Only Python (.py) files are supported.";
    return;
  }

  setLoading(githubReviewButton, true, "Reviewing…");
  githubStatusText.textContent = "Fetching and reviewing GitHub file…";
  try {
    const response = await fetch(`${API_BASE}/review-github`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoUrl, file_path: filePath })
    });
    const data = await readResponse(response);
    if (!data.report) throw new Error("The server response does not contain a review report.");
    displayReport(data.report, `GitHub · ${filePath}`);
    githubStatusText.textContent = "GitHub code review completed successfully.";
    showToast("GitHub review completed");
    navigateTo("overview");
  } catch (error) {
    console.error(error);
    githubStatusText.textContent = formatFetchError(error);
  } finally {
    setLoading(githubReviewButton, false, "Review GitHub file");
  }
});

async function readResponse(response) {
  let data;
  try {
    data = await response.json();
  } catch {
    throw new Error(`Server returned an unreadable response (${response.status}).`);
  }
  if (!response.ok) throw new Error(data.detail || `Server returned error: ${response.status}`);
  return data;
}

function formatFetchError(error) {
  if (error instanceof TypeError && /fetch/i.test(error.message)) {
    return "Could not connect to the API. Make sure FastAPI is running at " + API_BASE + " and CORS allows this frontend origin.";
  }
  return "Review failed: " + (error.message || "Unknown error");
}

function setLoading(button, loading, label) {
  button.disabled = loading;
  button.classList.toggle("is-loading", loading);
  button.innerHTML = loading
    ? `<span class="button-spinner" aria-hidden="true"></span>${escapeHTML(label)}`
    : `${escapeHTML(label)} <span>→</span>`;
}

function displayReport(report, sourceLabel = "Latest code review") {
  latestReport = report || {};
  latestSource = sourceLabel;
  const statistics = latestReport.statistics || {};
  const findings = Array.isArray(latestReport.findings) ? latestReport.findings : [];
  const score = numericScore(latestReport.score);
  const highCount = countSeverity(findings, ["high", "critical", "blocker"]);
  const totalCount = Number.isFinite(Number(statistics.total_findings)) ? Number(statistics.total_findings) : findings.length;

  setText("scoreMetric", score === null ? "—" : String(score));
  document.getElementById("scoreMetric").innerHTML = `${score === null ? "—" : escapeHTML(String(score))}<span>/100</span>`;
  setText("totalMetric", totalCount);
  setText("highMetric", Number.isFinite(Number(statistics.high)) ? Number(statistics.high) : highCount);
  setText("riskMetric", latestReport.risk_level || "Unknown");
  setText("navIssueCount", totalCount);
  setText("findingCount", findings.length);
  setText("overviewUpdated", "Latest review completed");
  setText("scoreFoot", score === null ? "Score unavailable" : score >= 80 ? "Good code health" : score >= 60 ? "Room to improve" : "Needs attention");
  document.getElementById("scoreProgress").style.width = `${score === null ? 0 : Math.max(0, Math.min(100, score))}%`;

  renderSeverityChart(findings);
  renderLatestReview(latestReport, sourceLabel, totalCount);
  renderFindingsSummary(latestReport, findings);
  displayFindings(findings);
  displayList("strengths", latestReport.strengths, "No strengths were included in this report.");
  displayList("improvements", latestReport.improvements, "No improvement suggestions were included in this report.");
  document.getElementById("severityFilter").value = "all";
  applySeverityFilter();
}

function numericScore(value) {
  const parsed = Number(value);
  return value !== null && value !== "" && Number.isFinite(parsed) ? Math.max(0, Math.min(100, Math.round(parsed))) : null;
}
function setText(id, value) {
  document.getElementById(id).textContent = value === null || value === undefined ? "" : String(value);
}
function countSeverity(findings, severities) {
  return findings.filter(item => severities.includes(String(item.severity || "").toLowerCase())).length;
}
function normalizedSeverity(value) {
  const severity = String(value || "other").toLowerCase();
  if (severity.includes("critical") || severity.includes("blocker")) return "critical";
  if (severity.includes("high")) return "high";
  if (severity.includes("medium") || severity.includes("moderate")) return "medium";
  if (severity.includes("low") || severity.includes("info")) return "low";
  return "low";
}
function displayFindings(findings) {
  const container = document.getElementById("findings");
  container.replaceChildren();
  if (!findings || findings.length === 0) {
    container.innerHTML = '<div class="empty-state"><div class="empty-icon success-empty">✓</div><h3>No findings reported</h3><p>Your review did not return any findings.</p></div>';
    return;
  }
  findings.forEach((finding, index) => {
    const severity = normalizedSeverity(finding.severity);
    const article = document.createElement("article");
    article.className = "finding-item";
    article.dataset.severity = severity;

    const head = document.createElement("div");
    head.className = "finding-head";
    const left = document.createElement("div");
    left.className = "finding-title-group";
    const badge = document.createElement("span");
    badge.className = `severity-badge ${severity}`;
    badge.textContent = finding.severity || "Other";
    const title = document.createElement("h3");
    title.textContent = finding.title || finding.category || `Finding ${index + 1}`;
    left.append(badge, title);
    const line = document.createElement("span");
    line.className = "line-badge";
    line.textContent = `Line ${finding.line ?? "N/A"}`;
    head.append(left, line);

    const explanation = document.createElement("p");
    explanation.className = "finding-explanation";
    explanation.textContent = finding.explanation || "No explanation was provided.";
    const meta = document.createElement("div");
    meta.className = "finding-meta";
    const category = document.createElement("span");
    category.innerHTML = '<span class="meta-key">Category</span> ';
    const categoryValue = document.createElement("strong");
    categoryValue.textContent = finding.category || "Uncategorized";
    category.append(categoryValue);
    meta.append(category);
    if (finding.confidence !== undefined && finding.confidence !== null && finding.confidence !== "") {
      const confidence = document.createElement("span");
      confidence.innerHTML = '<span class="meta-key">Confidence</span> ';
      const confidenceValue = document.createElement("strong");
      confidenceValue.textContent = String(finding.confidence);
      confidence.append(confidenceValue);
      meta.append(confidence);
    }
    const suggestion = document.createElement("div");
    suggestion.className = "suggestion-box";
    const suggestionTitle = document.createElement("strong");
    suggestionTitle.textContent = "Suggested improvement";
    const suggestionText = document.createElement("p");
    suggestionText.textContent = finding.suggestion || "No suggestion provided.";
    suggestion.append(suggestionTitle, suggestionText);
    article.append(head, explanation, meta, suggestion);
    container.append(article);
  });
}
function applySeverityFilter() {
  const filter = document.getElementById("severityFilter").value;
  const items = [...document.querySelectorAll(".finding-item")];
  let visible = 0;
  items.forEach(item => {
    const show = filter === "all" || item.dataset.severity === filter;
    item.classList.toggle("hidden", !show);
    if (show) visible++;
  });
  const count = document.getElementById("findingCount");
  if (count) count.textContent = String(visible);
}
document.getElementById("severityFilter").addEventListener("change", applySeverityFilter);

function displayList(id, values, emptyMessage) {
  const list = document.getElementById(id);
  list.replaceChildren();
  const items = Array.isArray(values) ? values : [];
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = emptyMessage;
    li.className = "empty-list-item";
    list.append(li);
    return;
  }
  items.forEach(value => {
    const li = document.createElement("li");
    li.textContent = String(value);
    list.append(li);
  });
}
function renderSeverityChart(findings) {
  const chart = document.getElementById("severityChart");
  const counts = {
    critical: findings.filter(f => normalizedSeverity(f.severity) === "critical").length,
    high: findings.filter(f => normalizedSeverity(f.severity) === "high").length,
    medium: findings.filter(f => normalizedSeverity(f.severity) === "medium").length,
    low: findings.filter(f => normalizedSeverity(f.severity) === "low").length
  };
  const total = findings.length;
  if (!total) {
    chart.innerHTML = '<div class="empty-chart"><span class="empty-chart-icon">▥</span><strong>No findings to chart</strong><p>There were no findings in the latest report.</p></div>';
    return;
  }
  const rows = [
    ["Critical", counts.critical, "critical"],
    ["High", counts.high, "high"],
    ["Medium", counts.medium, "medium"],
    ["Low / Other", counts.low, "low"]
  ];
  chart.innerHTML = "";
  const bars = document.createElement("div");
  bars.className = "severity-bars";
  rows.forEach(([label, count, cls]) => {
    const row = document.createElement("div");
    row.className = "severity-row";
    const labelEl = document.createElement("span");
    labelEl.className = "severity-row-label";
    labelEl.textContent = label;
    const track = document.createElement("div");
    track.className = "bar-track";
    const fill = document.createElement("div");
    fill.className = `bar-fill ${cls}`;
    fill.style.width = `${total ? count / total * 100 : 0}%`;
    track.append(fill);
    const number = document.createElement("strong");
    number.textContent = String(count);
    row.append(labelEl, track, number);
    bars.append(row);
  });
  const totalLabel = document.createElement("div");
  totalLabel.className = "chart-total";
  totalLabel.innerHTML = `<strong>${total}</strong><span>total ${total === 1 ? "finding" : "findings"}</span>`;
  chart.append(totalLabel, bars);
}
function renderLatestReview(report, source, total) {
  const container = document.getElementById("latestReview");
  container.replaceChildren();
  const summary = document.createElement("p");
  summary.className = "latest-summary";
  summary.textContent = report.summary || "Review finished. Open findings to inspect the results.";
  const sourceEl = document.createElement("div");
  sourceEl.className = "latest-source";
  sourceEl.innerHTML = '<span class="source-dot"></span>';
  sourceEl.append(document.createTextNode(source));
  const foot = document.createElement("div");
  foot.className = "latest-foot";
  const issueLabel = document.createElement("span");
  issueLabel.textContent = `${total} ${total === 1 ? "finding" : "findings"}`;
  const viewButton = document.createElement("button");
  viewButton.className = "text-button";
  viewButton.type = "button";
  viewButton.textContent = "Inspect report →";
  viewButton.addEventListener("click", () => navigateTo("findings"));
  foot.append(issueLabel, viewButton);
  container.append(sourceEl, summary, foot);
}
function renderFindingsSummary(report, findings) {
  const container = document.getElementById("findingsSummary");
  container.replaceChildren();
  const icon = document.createElement("div");
  icon.className = "findings-summary-icon";
  icon.textContent = "◉";
  const body = document.createElement("div");
  const title = document.createElement("strong");
  title.textContent = latestSource;
  const description = document.createElement("p");
  description.textContent = report.summary || `${findings.length} findings returned by the latest review.`;
  body.append(title, description);
  container.append(icon, body);
}
function showToast(message) {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("show"), 2800);
}
function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, character => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[character]);
}
