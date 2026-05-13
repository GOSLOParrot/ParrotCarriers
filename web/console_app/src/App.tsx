import { useCallback, useEffect, useMemo, useReducer, useState } from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  type NodeMouseHandler
} from "reactflow";
import {
  Activity,
  Bell,
  CheckCircle2,
  CircleDot,
  GitBranch,
  Languages,
  PanelRightOpen,
  Play,
  Plus,
  RefreshCw,
  Settings,
  Sparkles,
  Trash2
} from "lucide-react";
import { api } from "./api";
import type { ConsoleConfig, L15Pool, Language, LiveState, Receipt, RuntimeFlow } from "./types";

type ViewId = "memory" | "runtime";

const dict = {
  en: {
    memory: "Memory Graph",
    runtime: "Runtime Flow",
    refresh: "Refresh",
    settings: "Settings",
    language: "Language",
    live: "live",
    auth: "auth",
    nodes: "Nodes",
    edges: "Edges",
    blackboard: "Blackboard",
    intent: "IntentWorkspace",
    l15: "L1.5 Pool",
    receipt: "Receipts",
    selected: "Selection",
    createNode: "Draft Node",
    draftEdge: "Draft Edge",
    messageCheck: "Message Check",
    messagePush: "Message Push",
    llmPush: "LLM Push",
    dryApply: "Dry Apply",
    draft: "Draft",
    clear: "Clear",
    noSelection: "Select an item on the canvas.",
    runtimeSummary: "Intent, Plan, HITL, Blackboard, Scheduler, Nanobot, and messages.",
    memorySummary: "L1.5, L2-B, Graphiti, Refs, Evidence Board, and dry-run graph operations."
  },
  zh: {
    memory: "记忆图谱",
    runtime: "协作流",
    refresh: "刷新",
    settings: "设置",
    language: "语言",
    live: "实时",
    auth: "认证",
    nodes: "节点",
    edges: "边",
    blackboard: "黑板",
    intent: "IntentWorkspace",
    l15: "L1.5 池",
    receipt: "回执",
    selected: "选中",
    createNode: "节点草稿",
    draftEdge: "边草稿",
    messageCheck: "查新消息",
    messagePush: "消息推送",
    llmPush: "推给 LLM",
    dryApply: "干跑执行",
    draft: "草稿",
    clear: "清空",
    noSelection: "在画布上选择一个项目。",
    runtimeSummary: "Intent、Plan、HITL、黑板、Scheduler、Nanobot 和消息流。",
    memorySummary: "L1.5、L2-B、Graphiti、Refs、Evidence Board 和图上干跑操作。"
  }
};

function receiptReducer(state: Receipt[], receipt: Receipt | null): Receipt[] {
  if (!receipt) return [];
  return [receipt, ...state].slice(0, 10);
}

export function App() {
  const [view, setView] = useState<ViewId>("memory");
  const [language, setLanguage] = useState<Language>(() => (localStorage.getItem("parrot.console.lang") as Language) || "zh");
  const [config, setConfig] = useState<ConsoleConfig>({});
  const [liveState, setLiveState] = useState<LiveState>({});
  const [l15Pool, setL15Pool] = useState<L15Pool>({});
  const [runtimeFlow, setRuntimeFlow] = useState<RuntimeFlow>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [receipts, pushReceipt] = useReducer(receiptReducer, []);
  const t = dict[language];

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextConfig, nextLive, nextPool, nextFlow] = await Promise.all([
        api.config(),
        api.liveState(),
        api.l15Pool(),
        api.runtimeFlow()
      ]);
      setConfig(nextConfig);
      setLiveState(nextLive);
      setL15Pool(nextPool);
      setRuntimeFlow(nextFlow);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
    const timer = window.setInterval(() => void load(), 5000);
    return () => window.clearInterval(timer);
  }, [load]);

  const setLang = (next: Language) => {
    localStorage.setItem("parrot.console.lang", next);
    setLanguage(next);
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">P</div>
          <div>
            <strong>Parrot Console</strong>
            <small>React Web lane</small>
          </div>
        </div>
        <button className={view === "memory" ? "nav active" : "nav"} onClick={() => setView("memory")}>
          <GitBranch size={18} /> {t.memory}
        </button>
        <button className={view === "runtime" ? "nav active" : "nav"} onClick={() => setView("runtime")}>
          <Activity size={18} /> {t.runtime}
        </button>
        <div className="sidebar-footer">
          <span><CircleDot size={14} /> {t.auth}: {config.orchestrator_auth_mode || "..."}</span>
          <button className="nav small" onClick={() => setLang(language === "zh" ? "en" : "zh")}>
            <Languages size={16} /> {language === "zh" ? "EN" : "中文"}
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">{view === "memory" ? t.memory : t.runtime}</span>
            <h1>{view === "memory" ? t.memory : t.runtime}</h1>
            <p>{view === "memory" ? t.memorySummary : t.runtimeSummary}</p>
          </div>
          <div className="topbar-actions">
            <span className={loading ? "live-pill loading" : "live-pill"}><Sparkles size={15} /> {t.live}</span>
            {error ? <span className="error-pill">{error}</span> : null}
            <button className="button" onClick={() => void load()}><RefreshCw size={16} /> {t.refresh}</button>
            <button className="button ghost"><Settings size={16} /> {t.settings}</button>
          </div>
        </header>

        {view === "memory" ? (
          <MemoryGraphWorkspace liveState={liveState} l15Pool={l15Pool} pushReceipt={pushReceipt} t={t} />
        ) : (
          <RuntimeFlowWorkspace flow={runtimeFlow} pushReceipt={pushReceipt} t={t} />
        )}
      </main>

      <ReceiptRail receipts={receipts} title={t.receipt} />
    </div>
  );
}

function MemoryGraphWorkspace({
  liveState,
  l15Pool,
  pushReceipt,
  t
}: {
  liveState: LiveState;
  l15Pool: L15Pool;
  pushReceipt: (receipt: Receipt | null) => void;
  t: typeof dict.en;
}) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [previewNodes, setPreviewNodes] = useState<Array<Record<string, unknown>>>([]);
  const [edgeFrom, setEdgeFrom] = useState("");
  const [edgeTo, setEdgeTo] = useState("");
  const [nodeLabel, setNodeLabel] = useState("Web Test Node");

  const l2bNodes = liveState.l2b?.nodes ?? [];
  const l2bEdges = liveState.l2b?.edges ?? [];
  const graphNodes = useMemo<Node[]>(() => {
    const real = l2bNodes.length
      ? l2bNodes.map((row, index) => memoryNode(row, index))
      : memoryPlaceholderNodes(liveState);
    const previews = previewNodes.map((row, index) => ({
      id: String(row.uuid),
      position: { x: 260 + index * 80, y: 260 },
      data: { label: String(row.label), source: row },
      className: "preview-node"
    }));
    return [...real, ...previews];
  }, [l2bNodes, liveState, previewNodes]);

  const graphEdges = useMemo<Edge[]>(() => {
    const persisted = l2bEdges.map((row, index) => ({
      id: `edge-${index}-${String(row.source)}-${String(row.target)}`,
      source: String(row.source),
      target: String(row.target),
      label: String(row.kind || ""),
      className: row.cross_compartment ? "cross-edge" : ""
    }));
    return persisted;
  }, [l2bEdges]);

  const onNodeClick: NodeMouseHandler = (_, node) => {
    const source = (node.data as { source?: Record<string, unknown> }).source ?? {};
    setSelected(source);
    const uuid = String(source.uuid || node.id);
    if (!edgeFrom) setEdgeFrom(uuid);
    else if (!edgeTo && edgeFrom !== uuid) setEdgeTo(uuid);
  };

  const draftNode = async () => {
    const receipt = await api.l2bNodeDraft({
      label: nodeLabel,
      kind: "object",
      description: "Created from React Memory Graph Workspace.",
      dry_run: true,
      operator_mode: false
    });
    const uuid = "draft:" + Date.now();
    setPreviewNodes((rows) => [...rows, { uuid, label: nodeLabel, kind: "object" }]);
    pushReceipt(receipt);
  };

  const draftEdge = async () => {
    const receipt = await api.l2bEdgeDraft({
      from_uuid: edgeFrom,
      to_uuid: edgeTo,
      kind: "associated_with",
      dry_run: true,
      operator_mode: false
    });
    pushReceipt(receipt);
  };

  return (
    <section className="workspace memory-layout">
      <div className="metric-row">
        <Metric label={t.nodes} value={String(liveState.l2b?.node_count ?? 0)} />
        <Metric label={t.edges} value={String(liveState.l2b?.edge_count ?? 0)} />
        <Metric label={t.blackboard} value={`${liveState.blackboard?.present_count ?? 0}/${liveState.blackboard?.declared_count ?? 0}`} />
        <Metric label={t.intent} value={String(liveState.intent_workspace?.ref_count ?? 0)} />
      </div>

      <div className="canvas-panel">
        <div className="canvas-toolbar">
          <input value={nodeLabel} onChange={(event) => setNodeLabel(event.target.value)} />
          <button className="button primary" onClick={() => void draftNode()}><Plus size={16} /> {t.createNode}</button>
          <input value={edgeFrom} onChange={(event) => setEdgeFrom(event.target.value)} placeholder="from uuid" />
          <input value={edgeTo} onChange={(event) => setEdgeTo(event.target.value)} placeholder="to uuid" />
          <button className="button" onClick={() => void draftEdge()}><GitBranch size={16} /> {t.draftEdge}</button>
          <button className="button ghost" onClick={() => { setPreviewNodes([]); setEdgeFrom(""); setEdgeTo(""); }}><Trash2 size={16} /> {t.clear}</button>
        </div>
        <ReactFlow nodes={graphNodes} edges={graphEdges} onNodeClick={onNodeClick} fitView>
          <MiniMap pannable zoomable />
          <Controls />
          <Background />
        </ReactFlow>
      </div>

      <aside className="drawer">
        <h2><PanelRightOpen size={18} /> {t.selected}</h2>
        {selected ? <JsonBlock value={selected} /> : <p className="muted">{t.noSelection}</p>}
        <h2>{t.l15}</h2>
        <div className="bucket-board">
          {(l15Pool.buckets ?? []).map((bucket) => (
            <BucketCard key={String(bucket.kind)} bucket={bucket} pushReceipt={pushReceipt} />
          ))}
        </div>
      </aside>
    </section>
  );
}

function RuntimeFlowWorkspace({
  flow,
  pushReceipt,
  t
}: {
  flow: RuntimeFlow;
  pushReceipt: (receipt: Receipt | null) => void;
  t: typeof dict.en;
}) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);

  const nodes = useMemo<Node[]>(() => {
    const lanes = flow.lanes ?? [];
    const laneIndex = new Map(lanes.map((lane, index) => [lane.id, index]));
    return (flow.nodes ?? []).map((row, index) => {
      const lane = String(row.lane || "runtime");
      const x = (laneIndex.get(lane) ?? 0) * 250;
      const y = 40 + (index % 8) * 92;
      return {
        id: String(row.id || `${lane}:${index}`),
        position: { x, y },
        data: {
          label: String(row.label || row.entity_id || row.id),
          source: row
        },
        className: `runtime-node status-${String(row.status || "unknown").replace(/[^a-z0-9_-]/gi, "_")}`
      };
    });
  }, [flow]);

  const edges = useMemo<Edge[]>(() => (flow.edges ?? []).map((row, index) => ({
    id: String(row.id || `runtime-edge-${index}`),
    source: String(row.source),
    target: String(row.target),
    label: String(row.kind || "")
  })), [flow]);

  const onNodeClick: NodeMouseHandler = (_, node) => {
    setSelected((node.data as { source?: Record<string, unknown> }).source ?? {});
  };

  const runAction = async (action: "message_check" | "message_push" | "llm_push") => {
    if (action === "message_check") pushReceipt(await api.messageCheck());
    if (action === "message_push") pushReceipt(await api.messagePush());
    if (action === "llm_push") {
      pushReceipt(await api.triggerDraft({
        trigger_name: "intent_event_boundary",
        event: {
          type: "intent_boundary",
          kind: "web_llm_context_push",
          summary: "React Runtime Flow dry-run context push."
        }
      }));
    }
  };

  const draftGate = async (gate: Record<string, unknown>, decision: string, apply = false) => {
    const body = {
      gate_id: gate.gate_id,
      decision,
      dry_run: true,
      operator_mode: false
    };
    pushReceipt(apply ? await api.hitlApply(body) : await api.hitlDraft(body));
  };

  return (
    <section className="workspace runtime-layout">
      <div className="metric-row">
        <Metric label="Sequence" value={String(flow.sequence ?? 0)} />
        <Metric label="Events" value={String(flow.events?.length ?? 0)} />
        <Metric label="HITL" value={String(flow.pending_human_gates?.length ?? 0)} />
        <Metric label="Nodes" value={String(flow.nodes?.length ?? 0)} />
      </div>

      <div className="runtime-actions">
        <button className="button" onClick={() => void runAction("message_check")}><Bell size={16} /> {t.messageCheck}</button>
        <button className="button" onClick={() => void runAction("message_push")}><Play size={16} /> {t.messagePush}</button>
        <button className="button" onClick={() => void runAction("llm_push")}><Sparkles size={16} /> {t.llmPush}</button>
      </div>

      <div className="canvas-panel runtime-canvas">
        <ReactFlow nodes={nodes} edges={edges} onNodeClick={onNodeClick} fitView>
          <Controls />
          <Background />
        </ReactFlow>
      </div>

      <aside className="drawer">
        <h2><CheckCircle2 size={18} /> Human Gates</h2>
        {(flow.pending_human_gates ?? []).length ? (
          (flow.pending_human_gates ?? []).map((gate) => (
            <div className="gate-card" key={String(gate.gate_id)}>
              <strong>{String(gate.summary || gate.gate_id)}</strong>
              <small>{String(gate.gate_id)}</small>
              <div className="button-row">
                <button className="button small" onClick={() => void draftGate(gate, "approve")}>{t.draft}</button>
                <button className="button small primary" onClick={() => void draftGate(gate, "approve_and_start", true)}>{t.dryApply}</button>
              </div>
            </div>
          ))
        ) : <p className="muted">No pending gate.</p>}
        <h2>{t.selected}</h2>
        {selected ? <JsonBlock value={selected} /> : <p className="muted">{t.noSelection}</p>}
      </aside>

      <div className="event-tape">
        {(flow.events ?? []).slice().reverse().slice(0, 18).map((event, index) => (
          <div className="event-chip" key={`${String(event.span_id)}-${index}`}>
            <span>{String(event.entity_kind)}</span>
            <strong>{String(event.op)}</strong>
            <small>{String(event.summary)}</small>
          </div>
        ))}
      </div>
    </section>
  );
}

function BucketCard({ bucket, pushReceipt }: { bucket: Record<string, unknown>; pushReceipt: (receipt: Receipt | null) => void }) {
  const kind = String(bucket.kind || "");
  const op = async (operation: string) => {
    pushReceipt(await api.l15BucketDraft({ kind, op: operation, dry_run: true, operator_mode: false }));
  };
  return (
    <article className="bucket-card">
      <strong>{kind}</strong>
      <small>{String(bucket.status || bucket.lifecycle || "ok")}</small>
      <div className="button-row">
        <button className="button small" onClick={() => void op("freeze")}>freeze</button>
        <button className="button small" onClick={() => void op("unfreeze")}>unfreeze</button>
        <button className="button small danger" onClick={() => void op("clear")}>clear</button>
      </div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

function ReceiptRail({ receipts, title }: { receipts: Receipt[]; title: string }) {
  return (
    <aside className="receipt-rail">
      <h2>{title}</h2>
      {receipts.length ? receipts.map((receipt, index) => (
        <div className={receipt.success === false ? "receipt bad" : "receipt"} key={`${receipt.receipt_id || index}`}>
          <strong>{receipt.action || "receipt"}</strong>
          <small>{receipt.dry_run ? "dry-run" : "execute"} / {receipt.operator_mode ? "operator" : "safe"}</small>
          <JsonBlock value={receipt.data ?? receipt} />
        </div>
      )) : <p className="muted">No receipts yet.</p>}
    </aside>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre className="json-block">{JSON.stringify(value, null, 2)}</pre>;
}

function memoryNode(row: Record<string, unknown>, index: number): Node {
  const angle = (Math.PI * 2 * index) / Math.max(1, 12);
  const radius = 220;
  return {
    id: String(row.uuid),
    position: { x: 360 + Math.cos(angle) * radius, y: 280 + Math.sin(angle) * radius },
    data: {
      label: String(row.label || row.uuid),
      source: row
    },
    className: `memory-node kind-${String(row.kind || "node")}`
  };
}

function memoryPlaceholderNodes(liveState: LiveState): Node[] {
  const rows = [
    { id: "placeholder:blackboard", label: `Blackboard ${liveState.blackboard?.present_count ?? 0}` },
    { id: "placeholder:intent", label: `Intent ${liveState.intent_workspace?.ref_count ?? 0}` },
    { id: "placeholder:refs", label: `Refs ${liveState.refs?.refs?.length ?? 0}` },
    { id: "placeholder:l2b", label: `L2-B ${liveState.l2b?.node_count ?? 0}` }
  ];
  return rows.map((row, index) => ({
    id: row.id,
    position: { x: 180 + index * 210, y: 260 },
    data: { label: row.label, source: row },
    className: "placeholder-node"
  }));
}
