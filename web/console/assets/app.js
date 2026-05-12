const dictionaries = {
  en: {
    "nav.opsHealth": "Ops Health",
    "nav.runtimeState": "Runtime State",
    "nav.memoryGraph": "Memory Graph",
    "nav.graphiti": "Graphiti",
    "ops.title": "Ops Health",
    "actions.refresh": "Refresh",
    "actions.loading": "Loading",
    "actions.pause": "Pause",
    "actions.resume": "Resume",
    "metrics.connection": "Connection",
    "metrics.modules": "Modules",
    "metrics.warnings": "Warnings",
    "metrics.selection": "Selection",
    "metrics.onlineOffline": "online / offline",
    "metrics.statusWarnings": "status warnings",
    "metrics.lineDrift": "line drift",
    "drift.noLiveBrain": "No live Brain snapshot; drift check skipped.",
    "topology.title": "Status Topology",
    "topology.console": "Web Console",
    "topology.orchestrator": "Orchestrator",
    "topology.status": "Status Snapshot",
    "topology.modules": "Module Heartbeats",
    "panes.moduleHealth": "Module Health",
    "panes.runtimeConfig": "Runtime Config",
    "panes.brainSnapshot": "Brain Snapshot",
    "panes.containers": "Containers",
    "panes.warnings": "Warnings",
    "table.module": "Module",
    "table.state": "State",
    "table.type": "Type",
    "table.layers": "Layers",
    "table.stale": "Stale",
    "table.note": "Note",
    "pills.read": "read",
    "pills.empty": "empty",
    "pills.online": "online",
    "pills.degraded": "degraded",
    "pills.checking": "checking",
    "settings.title": "Settings",
    "settings.language": "Language",
    "settings.languageHint": "Applies to this browser.",
    "states.connected": "connected",
    "states.degraded": "degraded",
    "states.offline": "offline",
    "states.unauthorized": "unauthorized",
    "states.error": "error",
    "states.aligned": "aligned",
    "states.drift": "drift",
    "states.online": "online",
    "states.offlineShort": "offline",
    "empty.noData": "No data",
    "empty.noModuleHeartbeat": "No module heartbeat data.",
    "empty.noContainer": "No container data.",
    "empty.noWarnings": "No warnings.",
    "empty.never": "never",
    "last.waiting": "Waiting for status...",
    "last.fetched": "Last fetch {time} in {ms} ms",
    "auth.mode": "auth: {mode}",
    "auth.orchestrator": "orchestrator: {url}",
    "auth.secretMissing": "Orchestrator requires Bearer auth; set PARROT_ORCH_SECRET for the Web Console process.",
    "topology.healthOk": "/health ok",
    "topology.healthMissing": "/health unreachable",
    "topology.statusOk": "/status ok",
    "topology.statusDenied": "/status needs Bearer",
    "topology.statusMissing": "/status unavailable",
    "topology.moduleCount": "{count} online",
    "module.placeholder": "waiting for heartbeat",
  },
  zh: {
    "nav.opsHealth": "运行健康",
    "nav.runtimeState": "运行状态",
    "nav.memoryGraph": "记忆图谱",
    "nav.graphiti": "Graphiti",
    "ops.title": "运行健康",
    "actions.refresh": "刷新",
    "actions.loading": "加载中",
    "actions.pause": "暂停",
    "actions.resume": "继续",
    "metrics.connection": "连接",
    "metrics.modules": "模块",
    "metrics.warnings": "警告",
    "metrics.selection": "选择",
    "metrics.onlineOffline": "在线 / 离线",
    "metrics.statusWarnings": "状态警告",
    "metrics.lineDrift": "线路漂移",
    "drift.noLiveBrain": "没有实时 Brain 快照；已跳过漂移检查。",
    "topology.title": "状态拓扑",
    "topology.console": "Web 控制台",
    "topology.orchestrator": "编排器",
    "topology.status": "状态快照",
    "topology.modules": "模块心跳",
    "panes.moduleHealth": "模块健康",
    "panes.runtimeConfig": "运行配置",
    "panes.brainSnapshot": "Brain 快照",
    "panes.containers": "容器",
    "panes.warnings": "警告",
    "table.module": "模块",
    "table.state": "状态",
    "table.type": "类型",
    "table.layers": "层级",
    "table.stale": "延迟",
    "table.note": "备注",
    "pills.read": "只读",
    "pills.empty": "空",
    "pills.online": "在线",
    "pills.degraded": "降级",
    "pills.checking": "检查中",
    "settings.title": "设置",
    "settings.language": "语言",
    "settings.languageHint": "只影响当前浏览器。",
    "states.connected": "已连接",
    "states.degraded": "降级",
    "states.offline": "离线",
    "states.unauthorized": "未授权",
    "states.error": "错误",
    "states.aligned": "一致",
    "states.drift": "漂移",
    "states.online": "在线",
    "states.offlineShort": "离线",
    "empty.noData": "暂无数据",
    "empty.noModuleHeartbeat": "暂无模块心跳数据。",
    "empty.noContainer": "暂无容器数据。",
    "empty.noWarnings": "没有警告。",
    "empty.never": "从未",
    "last.waiting": "等待状态数据...",
    "last.fetched": "上次刷新 {time}，耗时 {ms} ms",
    "auth.mode": "认证：{mode}",
    "auth.orchestrator": "编排器：{url}",
    "auth.secretMissing": "编排器需要 Bearer 认证；请为 Web Console 进程设置 PARROT_ORCH_SECRET。",
    "topology.healthOk": "/health 正常",
    "topology.healthMissing": "/health 不可达",
    "topology.statusOk": "/status 正常",
    "topology.statusDenied": "/status 需要 Bearer",
    "topology.statusMissing": "/status 不可用",
    "topology.moduleCount": "{count} 个在线",
    "module.placeholder": "等待心跳",
  },
};

const state = {
  paused: false,
  refreshMs: 15000,
  timer: null,
  language: initialLanguage(),
  config: null,
  lastEnvelope: null,
  lastHealth: null,
};

const $ = (id) => document.getElementById(id);

function initialLanguage() {
  const queryLang = new URLSearchParams(window.location.search).get("lang");
  if (queryLang === "zh" || queryLang === "en") {
    localStorage.setItem("parrot.console.language", queryLang);
    return queryLang;
  }
  const stored = localStorage.getItem("parrot.console.language");
  if (stored === "zh" || stored === "en") return stored;
  return navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
}

const t = (key, params = {}) => {
  const dictionary = dictionaries[state.language] || dictionaries.en;
  const template = dictionary[key] || dictionaries.en[key] || key;
  return Object.entries(params).reduce(
    (out, [name, value]) => out.replaceAll(`{${name}}`, String(value)),
    template,
  );
};

const formatTime = (epochSeconds) => {
  if (!epochSeconds) return t("empty.never");
  return new Date(epochSeconds * 1000).toLocaleTimeString();
};

const text = (value, fallback = "-") => {
  if (value === null || value === undefined || value === "") return fallback;
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
};

function applyLanguage() {
  document.documentElement.lang = state.language === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.dataset.i18n);
  });
  $("languageSelect").value = state.language;
  $("pauseButton").textContent = state.paused ? t("actions.resume") : t("actions.pause");
  $("moduleDetail").textContent = t("metrics.onlineOffline");
  $("warningDetail").textContent = t("metrics.statusWarnings");
  if (!state.lastEnvelope) {
    $("lastFetch").textContent = t("last.waiting");
    $("driftDetail").textContent = t("metrics.lineDrift");
  }
  if (state.config) {
    renderConfig(state.config);
  }
  if (!state.lastEnvelope) return;
  renderHealth(state.lastHealth);
  renderEnvelope(state.lastEnvelope, 0, false);
}

async function loadConfig() {
  const response = await fetch("/api/console/config");
  const config = await response.json();
  state.config = config;
  state.refreshMs = Math.max(5, Number(config.refresh_interval_s || 15)) * 1000;
  renderConfig(config);
}

function renderConfig(config) {
  $("authMode").textContent = t("auth.mode", { mode: config.orchestrator_auth_mode });
  $("orchUrl").textContent = t("auth.orchestrator", { url: config.orchestrator_base_url });
}

async function loadStatus() {
  const started = Date.now();
  setLoading(true);
  try {
    const [healthResponse, statusResponse] = await Promise.all([
      fetch("/api/orchestrator/health"),
      fetch("/api/orchestrator/status"),
    ]);
    const health = await healthResponse.json();
    const envelope = await statusResponse.json();
    renderHealth(health);
    renderEnvelope(envelope, Date.now() - started);
  } catch (error) {
    renderHealth(null);
    renderEnvelope({
      ok: false,
      state: "error",
      upstream: {},
      detail: { message: error instanceof Error ? error.message : String(error) },
      summary: {},
      status: null,
    });
  } finally {
    setLoading(false);
  }
}

function setLoading(isLoading) {
  $("refreshButton").disabled = isLoading;
  $("refreshButton").textContent = isLoading ? t("actions.loading") : t("actions.refresh");
}

function renderHealth(health) {
  state.lastHealth = health;
  const ok = Boolean(health?.ok);
  setNodeState("nodeOrchestrator", ok ? "good" : "bad");
  setEdgeState("edgeHealth", ok ? "good" : "bad");
  $("orchestratorHealthText").textContent = ok
    ? t("topology.healthOk")
    : t("topology.healthMissing");
}

function renderEnvelope(envelope, durationMs = 0, remember = true) {
  if (remember) state.lastEnvelope = envelope;
  const status = envelope.status || {};
  const summary = envelope.summary || {};
  const upstream = envelope.upstream || {};
  const stateLabel = envelope.state || "unknown";
  const fetchedAt = upstream.fetched_at || Date.now() / 1000;
  let detailText = envelope.detail?.message || envelope.detail?.error;
  if (envelope.state === "unauthorized" && upstream.auth_mode === "dev-open") {
    detailText = t("auth.secretMissing");
  }

  $("connectionState").textContent = t(`states.${stateLabel}`) || stateLabel;
  if (envelope.state === "unauthorized" && upstream.auth_mode === "dev-open") {
    $("connectionDetail").textContent = detailText;
  } else {
    $("connectionDetail").textContent = upstream.status_code
      ? `${upstream.status_code} from ${upstream.auth_mode || "unknown"}${
          detailText ? `; ${detailText}` : ""
        }`
      : text(detailText, "no upstream response");
  }
  $("lastFetch").textContent = t("last.fetched", {
    time: formatTime(fetchedAt),
    ms: durationMs,
  });

  $("moduleCount").textContent = `${summary.online_processes ?? 0} / ${
    summary.offline_processes ?? 0
  }`;
  $("warningCount").textContent = String(summary.warning_count ?? 0);
  $("driftState").textContent = summary.selection_drift
    ? t("states.drift")
    : t("states.aligned");
  const driftSummary = status.selection_drift?.summary || "";
  $("driftDetail").textContent = driftSummary.startsWith("No live Brain snapshot")
    ? t("drift.noLiveBrain")
    : driftSummary || t("metrics.lineDrift");

  const processes = Array.isArray(status.processes) ? status.processes : [];
  renderModules(processes);
  renderKv("runtimeConfig", status.runtime_config || {});
  renderKv("brainSnapshot", status.brain_runtime_snapshot || {});
  renderContainers(status.containers);
  renderWarnings(Array.isArray(status.warnings) ? status.warnings : []);
  renderTopology(envelope, summary);

  setPill("moduleTableState", modulePillState(summary));
  setPill("brainState", Object.keys(status.brain_runtime_snapshot || {}).length ? "good" : "");
  setPill("containerState", summary.containers_unavailable ? "warn" : "good");
  setPill("warningState", (summary.warning_count || 0) > 0 ? "warn" : "good");
}

function renderTopology(envelope, summary) {
  const statusState =
    envelope.state === "connected"
      ? "good"
      : envelope.state === "degraded" || envelope.state === "unauthorized"
        ? "warn"
        : "bad";
  setNodeState("nodeConsole", "good");
  setNodeState("nodeStatus", statusState);
  setNodeState("nodeModules", (summary.online_processes || 0) > 0 ? "good" : "warn");
  setEdgeState("edgeStatus", statusState);
  setEdgeState("edgeModules", statusState === "good" ? "good" : "warn");
  $("statusAuthText").textContent =
    envelope.state === "unauthorized"
      ? t("topology.statusDenied")
      : envelope.ok
        ? t("topology.statusOk")
        : t("topology.statusMissing");
  $("moduleTopologyText").textContent = t("topology.moduleCount", {
    count: summary.online_processes || 0,
  });
  setPill("topologyState", statusState);
}

function setNodeState(id, statusClass) {
  const dot = $(id).querySelector(".node-dot");
  dot.className = `node-dot ${statusClass || ""}`.trim();
}

function setEdgeState(id, statusClass) {
  $(id).className = `topology-edge ${statusClass || ""}`.trim();
}

function modulePillState(summary) {
  if ((summary.offline_processes || 0) > 0) return "bad";
  if ((summary.online_processes || 0) > 0) return "good";
  return "";
}

function setPill(id, statusClass) {
  const el = $(id);
  el.className = `pill ${statusClass || ""}`.trim();
  const labels = {
    moduleTableState:
      statusClass === "bad"
        ? t("pills.degraded")
        : statusClass === "good"
          ? t("pills.online")
          : t("pills.empty"),
    topologyState:
      statusClass === "bad"
        ? t("pills.degraded")
        : statusClass === "good"
          ? t("states.connected")
          : statusClass === "warn"
            ? t("states.degraded")
            : t("pills.checking"),
  };
  if (labels[id]) {
    el.textContent = labels[id];
  }
}

function renderModules(processes) {
  renderModuleMap(processes);
  const rows = $("moduleRows");
  rows.innerHTML = "";
  if (!processes.length) {
    rows.innerHTML = `<tr><td class="empty" colspan="6">${t("empty.noModuleHeartbeat")}</td></tr>`;
    return;
  }

  rows.innerHTML = processes
    .map((item) => {
      const stale = typeof item.stale_seconds === "number" ? `${item.stale_seconds.toFixed(1)}s` : "-";
      const dot = item.online ? "good" : "bad";
      const note = item.warning || "";
      return `<tr>
        <td>${escapeHtml(text(item.module_id))}</td>
        <td><span class="state-dot ${dot}"></span>${
          item.online ? t("states.online") : t("states.offlineShort")
        }</td>
        <td>${escapeHtml(text(item.module_type))}</td>
        <td>${escapeHtml(text(item.layers))}</td>
        <td>${escapeHtml(stale)}</td>
        <td>${escapeHtml(note)}</td>
      </tr>`;
    })
    .join("");
}

function renderModuleMap(processes) {
  const map = $("moduleMap");
  const items = processes.length
    ? processes
    : [
        { module_id: "brain", module_type: "Brain", online: false },
        { module_id: "scheduler", module_type: "Scheduler", online: false },
        { module_id: "nanobot-worker", module_type: "Nanobot", online: false },
        { module_id: "graphiti", module_type: "Memory", online: false },
        { module_id: "unity-app", module_type: "Unity", online: false },
        { module_id: "a10", module_type: "Vision/ECS", online: false },
      ];
  map.innerHTML = items
    .map((item) => {
      const dot = item.online ? "good" : processes.length ? "bad" : "";
      const placeholder = processes.length ? "" : " placeholder";
      const note = processes.length
        ? item.online
          ? t("states.online")
          : t("states.offlineShort")
        : t("module.placeholder");
      return `<div class="module-card${placeholder}">
        <span class="state-dot ${dot}"></span>
        <strong>${escapeHtml(text(item.module_id))}</strong>
        <small>${escapeHtml(text(item.module_type))} · ${escapeHtml(note)}</small>
      </div>`;
    })
    .join("");
}

function renderKv(id, value) {
  const list = $(id);
  const entries = Object.entries(value || {});
  if (!entries.length) {
    list.innerHTML = `<dt class="empty">${t("pills.empty")}</dt><dd class="empty">${t("empty.noData")}</dd>`;
    return;
  }
  list.innerHTML = entries
    .map(([key, val]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(text(val))}</dd>`)
    .join("");
}

function renderContainers(containers) {
  const el = $("containers");
  if (!containers) {
    el.textContent = t("empty.noContainer");
    return;
  }
  if (Array.isArray(containers) && !containers.length) {
    el.textContent = t("empty.noContainer");
    return;
  }
  el.textContent = JSON.stringify(containers, null, 2);
}

function renderWarnings(warnings) {
  const list = $("warnings");
  if (!warnings.length) {
    list.innerHTML = `<li class="empty">${t("empty.noWarnings")}</li>`;
    return;
  }
  list.innerHTML = warnings.map((warning) => `<li>${escapeHtml(text(warning))}</li>`).join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function schedule() {
  window.clearInterval(state.timer);
  state.timer = window.setInterval(() => {
    if (!state.paused) {
      loadStatus();
    }
  }, state.refreshMs);
}

function openSettings() {
  const dialog = $("settingsDialog");
  if (typeof dialog.showModal === "function") {
    dialog.showModal();
  } else {
    dialog.setAttribute("open", "");
  }
}

$("refreshButton").addEventListener("click", loadStatus);
$("pauseButton").addEventListener("click", () => {
  state.paused = !state.paused;
  $("pauseButton").textContent = state.paused ? t("actions.resume") : t("actions.pause");
});
$("settingsButton").addEventListener("click", openSettings);
$("languageSelect").addEventListener("change", (event) => {
  state.language = event.target.value;
  localStorage.setItem("parrot.console.language", state.language);
  applyLanguage();
});

async function init() {
  applyLanguage();
  await loadConfig();
  await loadStatus();
  schedule();
}

init().catch((error) => {
  renderEnvelope({
    ok: false,
    state: "error",
    upstream: {},
    detail: { message: error instanceof Error ? error.message : String(error) },
    summary: {},
    status: null,
  });
});
