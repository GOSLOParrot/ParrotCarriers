import { useCallback, useEffect, useMemo, useReducer, useState, type MouseEvent as ReactMouseEvent } from "react";
import ReactFlow, {
  Background,
  type Connection,
  ConnectionMode,
  Controls,
  type Edge,
  type EdgeMouseHandler,
  Handle,
  MiniMap,
  type Node,
  type NodeChange,
  type NodeMouseHandler,
  type NodeProps,
  type NodeTypes,
  Position,
  type ReactFlowInstance
} from "reactflow";
import {
  Activity,
  Bell,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  GitBranch,
  Languages,
  PanelRightOpen,
  Play,
  Plus,
  RefreshCw,
  Settings,
  ShieldCheck,
  Sparkles,
  Trash2,
  Workflow
} from "lucide-react";
import { api } from "./api";
import type { ConsoleConfig, L15Pool, Language, LiveState, Receipt, RuntimeFlow, TriggerCatalog } from "./types";

type ViewId = "memory" | "runtime";
type RuntimeAction =
  | "message_check"
  | "message_push"
  | "llm_push"
  | "scheduler_tick"
  | "calendar_test"
  | "scene_switch"
  | "roleplay_open";

type MemoryNodeData = {
  label: string;
  source?: Record<string, unknown>;
  preview?: boolean;
};

const memoryNodeTypes: NodeTypes = {
  memory: MemoryNodeCard
};

const dict = {
  en: {
    memory: "Memory Graph",
    runtime: "Runtime Flow",
    refresh: "Refresh",
    settings: "Settings",
    language: "Language",
    live: "live",
    autoRefresh: "Auto",
    auth: "auth",
    nodes: "Nodes",
    edges: "Edges",
    blackboard: "Blackboard",
    intent: "IntentWorkspace",
    l15: "L1.5 Pool",
    l15Buckets: "L1.5 Buckets",
    l15Health: "Pool Health",
    pressure: "Pressure",
    currentScene: "Scene",
    refs: "Refs",
    lastActivity: "Last activity",
    obsidianSettings: "Obsidian Settings",
    settingProfile: "Profile",
    settingLabel: "Setting label",
    obsidianUuid: "Obsidian UUID",
    settingDraft: "Draft setting",
    uuidFree: "daily / roleplay are UUID-free",
    refRequiresUuid: "ref requires an Obsidian UUID",
    registeredTriggers: "Registered triggers",
    receipt: "Records",
    receiptTimeline: "Records",
    selected: "Selection",
    createNode: "New Node",
    draftEdge: "Connect Edge",
    messageCheck: "Message Check",
    messagePush: "Message Push",
    actionGroupMessage: "Message",
    actionGroupRuntime: "Runtime",
    actionGroupMode: "Mode",
    llmPush: "LLM Push",
    schedulerTick: "Scheduler Tick",
    calendarTest: "Calendar Test",
    sceneSwitch: "Scene Switch",
    roleplayOpen: "Roleplay Open",
    dryApply: "Preview Apply",
    draft: "Preview",
    approve: "Approve",
    approveAndStart: "Approve + Start",
    reject: "Reject",
    revise: "Revise",
    cancel: "Cancel",
    resume: "Resume",
    clear: "Clear",
    focusSelection: "Focus",
    layoutGraph: "Layout",
    noPendingGate: "No pending gate.",
    noSelection: "Select an item on the canvas.",
    noReceipts: "No records yet.",
    triggerPalette: "Trigger Palette",
    operatorSafe: "operator-safe preview",
    dryRunOnly: "preview only",
    previewMode: "preview",
    executeMode: "execute",
    safeMode: "safe",
    operatorMode: "operator",
    okStatus: "ok",
    failedStatus: "failed",
    recordDetails: "JSON details",
    nodeLabel: "Node label",
    fromUuid: "from uuid",
    toUuid: "to uuid",
    connectHint: "Double-click empty canvas to create a Node. Drag between Node handles to preview an Edge.",
    selectedEdgeTools: "Edge Operations",
    retargetEdge: "Preview Retarget",
    swapEdge: "Swap",
    selectedEdgeHint: "Retarget creates a new Edge preview and record; it does not mutate or delete the existing Edge.",
    emptyGraphTitle: "No L2-B Nodes yet",
    emptyGraphBody: "This canvas will show real L2-B Nodes and Edges after L1.5 commits memory candidates. The chips below are status summaries, not graph Nodes.",
    blackboardScope: "Blackboard",
    intentScope: "Intent",
    runtimeSummary: "Intent, Plan, HITL, Blackboard, Scheduler, Nanobot, and messages.",
    memorySummary: "L1.5, L2-B, Graphiti, Refs, Evidence Board, and safe graph previews."
  },
  zh: {
    memory: "记忆图谱",
    runtime: "协作流",
    refresh: "刷新",
    settings: "设置",
    language: "语言",
    live: "实时",
    autoRefresh: "自动",
    auth: "认证",
    nodes: "Node",
    edges: "Edge",
    blackboard: "黑板",
    intent: "IntentWorkspace",
    l15: "L1.5 池",
    l15Buckets: "L1.5 池",
    l15Health: "池健康",
    pressure: "压力",
    currentScene: "场景",
    refs: "Refs",
    lastActivity: "最后活动",
    obsidianSettings: "Obsidian 设置",
    settingProfile: "Profile",
    settingLabel: "设定标签",
    obsidianUuid: "Obsidian UUID",
    settingDraft: "设定草稿",
    uuidFree: "daily / roleplay 可不填 UUID",
    refRequiresUuid: "ref 必须绑定 Obsidian UUID",
    registeredTriggers: "已注册触发器",
    receipt: "操作记录",
    receiptTimeline: "操作记录",
    selected: "选中项",
    createNode: "新建 Node",
    draftEdge: "连接 Edge",
    messageCheck: "查新消息",
    messagePush: "消息推送",
    actionGroupMessage: "消息",
    actionGroupRuntime: "运行",
    actionGroupMode: "模式",
    llmPush: "推给 LLM",
    schedulerTick: "调度器 Tick",
    calendarTest: "日程测试",
    sceneSwitch: "场景切换",
    roleplayOpen: "打开 Roleplay",
    dryApply: "预演执行",
    draft: "预览",
    approve: "批准",
    approveAndStart: "批准并启动",
    reject: "拒绝",
    revise: "修订",
    cancel: "取消",
    resume: "恢复",
    clear: "清空",
    focusSelection: "聚焦",
    layoutGraph: "整理",
    noPendingGate: "暂无待确认 gate。",
    noSelection: "在画布上选择一个项目。",
    noReceipts: "暂无操作记录。",
    triggerPalette: "触发器面板",
    operatorSafe: "operator 安全预演",
    dryRunOnly: "仅预演",
    previewMode: "预演",
    executeMode: "执行",
    safeMode: "安全",
    operatorMode: "operator",
    okStatus: "ok",
    failedStatus: "失败",
    recordDetails: "JSON 详情",
    nodeLabel: "Node 标签",
    fromUuid: "起点 UUID",
    toUuid: "终点 UUID",
    connectHint: "双击空白画布新建 Node；拖动 Node 连接点可创建 Edge 预览。",
    selectedEdgeTools: "Edge 操作",
    retargetEdge: "重定向预览",
    swapEdge: "交换端点",
    selectedEdgeHint: "重定向只生成新的 Edge 预览和操作记录，不会改写已有 Edge。",
    emptyGraphTitle: "L2-B 还没有真实 Node",
    emptyGraphBody: "这里之后显示真实 L2-B Node / Edge。下面这些是状态概览，不是可以连接的图 Node。",
    blackboardScope: "黑板",
    intentScope: "Intent",
    runtimeSummary: "Intent、Plan、HITL、黑板、Scheduler、Nanobot 和消息流。",
    memorySummary: "L1.5、L2-B、Graphiti、Refs、Evidence Board 和图上安全预演操作。"
  }
};

type ConsoleCopy = typeof dict.en;

function receiptReducer(state: Receipt[], receipt: Receipt | null): Receipt[] {
  if (!receipt) return [];
  return [receipt, ...state].slice(0, 14);
}

export function App() {
  const [view, setView] = useState<ViewId>("memory");
  const [language, setLanguage] = useState<Language>(() => (localStorage.getItem("parrot.console.lang") as Language) || "zh");
  const [config, setConfig] = useState<ConsoleConfig>({});
  const [liveState, setLiveState] = useState<LiveState>({});
  const [l15Pool, setL15Pool] = useState<L15Pool>({});
  const [runtimeFlow, setRuntimeFlow] = useState<RuntimeFlow>({});
  const [triggerCatalog, setTriggerCatalog] = useState<TriggerCatalog>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [receipts, pushReceipt] = useReducer(receiptReducer, []);
  const t = dict[language];
  const refreshIntervalS = Math.max(3, Math.round(Number(config.refresh_interval_s ?? 5)));

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextConfig, nextLive, nextPool, nextFlow, nextTriggerCatalog] = await Promise.all([
        api.config(),
        api.liveState(),
        api.l15Pool(),
        api.runtimeFlow(),
        api.triggerCatalog()
      ]);
      setConfig(nextConfig);
      setLiveState(nextLive);
      setL15Pool(nextPool);
      setRuntimeFlow(nextFlow);
      setTriggerCatalog(nextTriggerCatalog);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const timer = window.setInterval(() => void load(), refreshIntervalS * 1000);
    return () => window.clearInterval(timer);
  }, [load, refreshIntervalS]);

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
            <Languages size={16} /> {language === "zh" ? "EN" : "\u4e2d\u6587"}
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
            <span className={loading ? "live-pill loading" : "live-pill"}>
              <Sparkles size={15} /> {t.live} / {t.autoRefresh} {refreshIntervalS}s
            </span>
            {error ? <span className="error-pill">{error}</span> : null}
            <button className="button" onClick={() => void load()}><RefreshCw size={16} /> {t.refresh}</button>
            <button className="button ghost"><Settings size={16} /> {t.settings}</button>
          </div>
        </header>

        {view === "memory" ? (
          <MemoryGraphWorkspace liveState={liveState} l15Pool={l15Pool} pushReceipt={pushReceipt} t={t} />
        ) : (
          <RuntimeFlowWorkspace flow={runtimeFlow} triggerCatalog={triggerCatalog} pushReceipt={pushReceipt} t={t} />
        )}
      </main>

      <ReceiptRail receipts={receipts} t={t} />
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
  t: ConsoleCopy;
}) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [previewNodes, setPreviewNodes] = useState<Array<Record<string, unknown>>>([]);
  const [previewEdges, setPreviewEdges] = useState<Edge[]>([]);
  const [edgeFrom, setEdgeFrom] = useState("");
  const [edgeTo, setEdgeTo] = useState("");
  const [nodeLabel, setNodeLabel] = useState("Web Test Node");
  const [manualPositions, setManualPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance<MemoryNodeData> | null>(null);

  const l2bNodes = liveState.l2b?.nodes ?? [];
  const l2bEdges = liveState.l2b?.edges ?? [];
  const selectedNodeId = selected?.selection_type === "node" ? String(selected.uuid || selected.id || "") : "";
  const selectedEdgeId = selected?.selection_type === "edge" ? String(selected.id || "") : "";
  const graphNodes = useMemo<Node[]>(() => {
    const real = l2bNodes.length
      ? l2bNodes.map((row, index) => memoryNode(row, index))
      : [];
    const previews = previewNodes.map((row, index) => ({
      id: String(row.uuid),
      position: { x: 260 + (index % 4) * 170, y: 230 + Math.floor(index / 4) * 96 },
      type: "memory",
      data: { label: String(row.label), source: row, preview: true },
      className: "preview-node",
      connectable: true
    }));
    return [...real, ...previews].map((node) => ({
      ...node,
      draggable: true,
      position: manualPositions[node.id] ?? node.position,
      selected: node.id === selectedNodeId
    }));
  }, [l2bNodes, manualPositions, previewNodes, selectedNodeId]);
  const draftableNodeIds = useMemo(
    () => new Set(graphNodes.filter((node) => isDraftableMemoryNodeId(node.id)).map((node) => node.id)),
    [graphNodes]
  );

  const graphEdges = useMemo<Edge[]>(() => {
    const persisted: Edge[] = [];
    l2bEdges.forEach((row, index) => {
      const source = edgeEndpoint(row, "source");
      const target = edgeEndpoint(row, "target");
      if (!source || !target) return;
      persisted.push({
        id: `edge-${index}-${source}-${target}`,
        source,
        target,
        label: String(row.kind || ""),
        className: row.cross_compartment ? "cross-edge" : "",
        reconnectable: true,
        data: { source: row }
      });
    });
    return [...persisted, ...previewEdges].map((edge) => ({
      ...edge,
      selected: edge.id === selectedEdgeId
    }));
  }, [l2bEdges, previewEdges, selectedEdgeId]);

  const onNodeClick: NodeMouseHandler = (_, node) => {
    const source = (node.data as { source?: Record<string, unknown> }).source ?? {};
    setSelected({ selection_type: "node", ...source });
    const uuid = String(source.uuid || node.id);
    if (!draftableNodeIds.has(uuid)) return;
    if (!edgeFrom) setEdgeFrom(uuid);
    else if (!edgeTo && edgeFrom !== uuid) setEdgeTo(uuid);
  };

  const onEdgeClick: EdgeMouseHandler = (_, edge) => {
    const source = (edge.data as { source?: Record<string, unknown> } | undefined)?.source ?? {};
    setSelected({ selection_type: "edge", id: edge.id, source: edge.source, target: edge.target, ...source });
    setEdgeFrom(edge.source);
    setEdgeTo(edge.target);
  };

  const stagePreviewNode = (uuid: string, label: string, position?: { x: number; y: number }) => {
    const nodeSource = { uuid, label, kind: "object", preview: true };
    setPreviewNodes((rows) => [...rows, nodeSource]);
    if (position) {
      setManualPositions((current) => ({ ...current, [uuid]: position }));
    }
    setSelected({ selection_type: "node", ...nodeSource });
    setEdgeFrom((currentFrom) => {
      if (!currentFrom) return uuid;
      setEdgeTo((currentTo) => currentTo || (currentFrom !== uuid ? uuid : currentTo));
      return currentFrom;
    });
  };

  const draftNode = async (position?: { x: number; y: number }, origin = "toolbar") => {
    const label = nodeLabel.trim();
    if (!label) {
      pushReceipt(localReceipt("l2b.node.draft", false, { error: "missing_label" }));
      return;
    }
    try {
      const receipt = await api.l2bNodeDraft({
        label,
        kind: "object",
        description: `Created from React Memory Graph Workspace (${origin}).`,
        dry_run: true,
        operator_mode: false
      });
      if (receipt.success !== false) {
        stagePreviewNode(makeDraftId("node"), label, position);
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.node.draft", exc));
    }
  };

  const onPaneClick = (event: ReactMouseEvent) => {
    if (event.detail === 1) {
      setSelected(null);
      return;
    }
    if (event.detail !== 2) return;
    if (!flowInstance) {
      pushReceipt(localReceipt("l2b.node.draft", false, { error: "flow_instance_not_ready" }));
      return;
    }
    const position = flowInstance.screenToFlowPosition({
      x: event.clientX,
      y: event.clientY
    });
    void draftNode(position, "canvas_double_click");
  };

  const draftEdgeBetween = async (
    from: string,
    to: string,
    reason: string,
    meta: Record<string, unknown> = {}
  ) => {
    const source = from.trim();
    const target = to.trim();
    if (!source || !target || source === target) {
      pushReceipt(localReceipt("l2b.edge.draft", false, {
        error: source === target ? "self_edge_not_allowed" : "missing_endpoint",
        from_uuid: source,
        to_uuid: target,
        reason,
        ...meta
      }));
      return;
    }
    try {
      const receipt = await api.l2bEdgeDraft({
        from_uuid: source,
        to_uuid: target,
        kind: "associated_with",
        dry_run: true,
        operator_mode: false
      });
      if (receipt.success !== false && draftableNodeIds.has(source) && draftableNodeIds.has(target)) {
        setPreviewEdges((rows) => [
          ...rows,
          {
            id: `${makeDraftId("edge")}:${source}:${target}`,
            source,
            target,
            label: "associated_with",
            className: reason === "edge_retarget" || reason === "edge_reconnect" ? "preview-edge retarget-edge" : "preview-edge",
            animated: true,
            reconnectable: true,
            type: "smoothstep",
            style: { strokeWidth: 3 },
            data: { source: { kind: "associated_with", reason, preview: true, ...meta } }
          }
        ]);
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.edge.draft", exc, { from_uuid: source, to_uuid: target }));
    }
  };

  const onConnect = (connection: Connection) => {
    const source = connection.source || "";
    const target = connection.target || "";
    setEdgeFrom(source);
    setEdgeTo(target);
    if (!draftableNodeIds.has(source) || !draftableNodeIds.has(target)) {
      pushReceipt(localReceipt("l2b.edge.draft", false, {
        error: "non_l2b_canvas_endpoint",
        from_uuid: source,
        to_uuid: target
      }));
      return;
    }
    void draftEdgeBetween(source, target, "canvas_connect");
  };

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setManualPositions((current) => {
      let next = current;
      changes.forEach((change) => {
        if (change.type !== "position" || !change.position) return;
        if (next === current) next = { ...current };
        next[change.id] = change.position;
      });
      return next;
    });
  }, []);

  const onReconnect = (oldEdge: Edge, connection: Connection) => {
    const source = connection.source || oldEdge.source;
    const target = connection.target || oldEdge.target;
    setEdgeFrom(source);
    setEdgeTo(target);
    setSelected({
      selection_type: "edge",
      id: oldEdge.id,
      source,
      target,
      previous_source: oldEdge.source,
      previous_target: oldEdge.target,
      retarget_preview: true
    });
    if (!draftableNodeIds.has(source) || !draftableNodeIds.has(target)) {
      pushReceipt(localReceipt("l2b.edge.draft", false, {
        error: "non_l2b_reconnect_endpoint",
        from_uuid: source,
        to_uuid: target,
        previous_source: oldEdge.source,
        previous_target: oldEdge.target
      }));
      return;
    }
    void draftEdgeBetween(source, target, "edge_reconnect", {
      selected_edge_id: oldEdge.id,
      previous_source: oldEdge.source,
      previous_target: oldEdge.target
    });
  };

  const draftSelectedEdgeRetarget = () => {
    const hasSelectedEdge = isSelectedEdge(selected);
    void draftEdgeBetween(edgeFrom, edgeTo, "edge_retarget", {
      selected_edge_id: hasSelectedEdge ? String(selected.id || "") : "",
      previous_source: hasSelectedEdge ? String(selected.source || "") : edgeFrom,
      previous_target: hasSelectedEdge ? String(selected.target || "") : edgeTo,
      staged_endpoint_draft: !hasSelectedEdge
    });
  };

  const swapSelectedEdgeEndpoints = () => {
    const nextFrom = edgeTo;
    const nextTo = edgeFrom;
    setEdgeFrom(nextFrom);
    setEdgeTo(nextTo);
    if (isSelectedEdge(selected)) {
      setSelected({
        ...selected,
        source: nextFrom,
        target: nextTo,
        swapped_preview: true
      });
    }
  };

  const clearPreview = () => {
    setPreviewNodes([]);
    setPreviewEdges([]);
    setEdgeFrom("");
    setEdgeTo("");
    setSelected(null);
  };
  const focusSelection = () => {
    if (!flowInstance) return;
    const selectedId = selectedNodeId || selectedEdgeId;
    if (!selectedId) {
      flowInstance.fitView({ padding: 0.2, duration: 220 });
      return;
    }
    if (selectedNodeId) {
      flowInstance.fitView({ nodes: [{ id: selectedNodeId }], padding: 0.7, duration: 220, maxZoom: 1.25 });
      return;
    }
    const edge = graphEdges.find((candidate) => candidate.id === selectedEdgeId);
    if (edge) {
      flowInstance.fitView({
        nodes: [{ id: edge.source }, { id: edge.target }],
        padding: 0.45,
        duration: 220,
        maxZoom: 1.1
      });
    }
  };
  const layoutGraph = () => {
    const nodes = graphNodes.filter((node) => !node.hidden);
    if (!nodes.length) return;
    const radius = Math.max(190, Math.min(520, nodes.length * 54));
    const center = { x: 420, y: 300 };
    setManualPositions((current) => {
      const next = { ...current };
      nodes.forEach((node, index) => {
        const angle = (-Math.PI / 2) + (Math.PI * 2 * index) / Math.max(1, nodes.length);
        next[node.id] = {
          x: center.x + Math.cos(angle) * radius,
          y: center.y + Math.sin(angle) * radius
        };
      });
      return next;
    });
    window.setTimeout(() => flowInstance?.fitView({ padding: 0.2, duration: 220 }), 0);
  };
  const poolHealth = l15Pool.health ?? {};
  const buckets = l15Pool.buckets ?? [];
  const maxBucketCount = Math.max(1, ...buckets.map((bucket) => Number(bucket.node_count ?? 0)));

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
          <span className="toolbar-hint"><GitBranch size={15} /> {t.connectHint}</span>
          <input value={nodeLabel} onChange={(event) => setNodeLabel(event.target.value)} placeholder={t.nodeLabel} />
          <button className="button primary" onClick={() => void draftNode()}><Plus size={16} /> {t.createNode}</button>
          <input value={edgeFrom} onChange={(event) => setEdgeFrom(event.target.value)} placeholder={t.fromUuid} />
          <input value={edgeTo} onChange={(event) => setEdgeTo(event.target.value)} placeholder={t.toUuid} />
          <button className="button" onClick={() => void draftEdgeBetween(edgeFrom, edgeTo, "toolbar")}><GitBranch size={16} /> {t.draftEdge}</button>
          <button className="button ghost" onClick={focusSelection}><CircleDot size={16} /> {t.focusSelection}</button>
          <button className="button ghost" onClick={layoutGraph}><Workflow size={16} /> {t.layoutGraph}</button>
          <button className="button ghost" onClick={clearPreview}><Trash2 size={16} /> {t.clear}</button>
        </div>
        <ReactFlow
          nodes={graphNodes}
          edges={graphEdges}
          nodeTypes={memoryNodeTypes}
          connectionMode={ConnectionMode.Loose}
          connectionRadius={28}
          onConnect={onConnect}
          onEdgeClick={onEdgeClick}
          onReconnect={onReconnect}
          onNodesChange={onNodesChange}
          onNodeClick={onNodeClick}
          onPaneClick={onPaneClick}
          onInit={(instance) => setFlowInstance(instance)}
          edgesUpdatable
          elevateEdgesOnSelect
          elevateNodesOnSelect
          nodesDraggable
          reconnectRadius={18}
          zoomOnDoubleClick={false}
          fitView
        >
          <MiniMap pannable zoomable />
          <Controls />
          <Background />
        </ReactFlow>
        {!l2bNodes.length && !previewNodes.length ? <EmptyL2BHint liveState={liveState} t={t} /> : null}
      </div>

      <aside className="drawer">
        <h2><PanelRightOpen size={18} /> {t.selected}</h2>
        {selected ? <JsonBlock value={selected} /> : <p className="muted">{t.noSelection}</p>}
        {edgeFrom && edgeTo ? (
          <SelectedEdgeTools
            selected={isSelectedEdge(selected) ? selected : { source: edgeFrom, target: edgeTo }}
            edgeFrom={edgeFrom}
            edgeTo={edgeTo}
            onRetarget={draftSelectedEdgeRetarget}
            onSwap={swapSelectedEdgeEndpoints}
            t={t}
          />
        ) : null}
        <h2>{t.l15Buckets}</h2>
        <L15HealthPanel health={poolHealth} t={t} />
        <ObsidianDraftCard pushReceipt={pushReceipt} t={t} />
        <div className="bucket-board">
          {buckets.map((bucket) => (
            <BucketCard key={String(bucket.kind)} bucket={bucket} maxNodeCount={maxBucketCount} pushReceipt={pushReceipt} t={t} />
          ))}
        </div>
      </aside>
    </section>
  );
}

function RuntimeFlowWorkspace({
  flow,
  triggerCatalog,
  pushReceipt,
  t
}: {
  flow: RuntimeFlow;
  triggerCatalog: TriggerCatalog;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
}) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const catalogGroups = useMemo(() => groupTriggerCatalog(triggerCatalog.triggers ?? []), [triggerCatalog]);

  const nodes = useMemo<Node[]>(() => {
    const lanes = flow.lanes ?? [];
    const laneIndex = new Map(lanes.map((lane, index) => [lane.id, index]));
    const laneRows = new Map<string, number>();
    return (flow.nodes ?? []).map((row, index) => {
      const lane = String(row.lane || "runtime");
      const rowIndex = laneRows.get(lane) ?? 0;
      laneRows.set(lane, rowIndex + 1);
      const x = (laneIndex.get(lane) ?? 0) * 250;
      const y = 40 + rowIndex * 92;
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
    label: String(row.kind || ""),
    data: { source: row }
  })), [flow]);

  const onNodeClick: NodeMouseHandler = (_, node) => {
    setSelected((node.data as { source?: Record<string, unknown> }).source ?? {});
  };

  const runAction = async (action: RuntimeAction) => {
    try {
      if (action === "message_check") {
        pushReceipt(await api.messageCheck());
        return;
      }
      if (action === "message_push") {
        pushReceipt(await api.messagePush());
        return;
      }
      if (action === "llm_push") {
        pushReceipt(await api.triggerDraft({
          trigger_name: "intent_event_boundary",
          event: {
            type: "intent_boundary",
            kind: "web_llm_context_push",
            summary: "React Runtime Flow dry-run context push."
          }
        }));
        return;
      }
      if (action === "scheduler_tick") {
        pushReceipt(await api.triggerDraft({
          trigger_name: "intent_event_boundary",
          event: {
            type: "intent_boundary",
            kind: "scheduler_tick",
            actor: "web_console",
            summary: "Synthetic Scheduler tick boundary from Runtime Flow."
          }
        }));
        return;
      }
      if (action === "calendar_test") {
        pushReceipt(await api.triggerDraft({
          trigger_name: "calendar",
          event: {
            type: "calendar_result",
            result: JSON.stringify([
              {
                id: "react_calendar_event",
                summary: "React Runtime Flow calendar test",
                start: { dateTime: "2026-05-14T10:00:00+08:00" }
              }
            ])
          }
        }));
        return;
      }
      if (action === "scene_switch") {
        pushReceipt(await api.triggerDraft({
          trigger_name: "scene_switch",
          event: {
            kind: "scene_switch",
            old_scene_type: "previous",
            new_scene_type: "desktop_webcam",
            source: "react_runtime_flow"
          }
        }));
        return;
      }
      if (action === "roleplay_open") {
        pushReceipt(await api.triggerDraft({
          trigger_name: "roleplay_mode",
          event: {
            kind: "roleplay_mode",
            action: "open",
            source: "react_runtime_flow"
          }
        }));
        return;
      }
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.action", exc, { runtime_action: action }));
    }
  };

  const draftGate = async (gate: Record<string, unknown>, decision: string, apply = false) => {
    const body = {
      gate_id: gate.gate_id,
      decision,
      dry_run: true,
      operator_mode: false
    };
    try {
      pushReceipt(apply ? await api.hitlApply(body) : await api.hitlDraft(body));
    } catch (exc) {
      pushReceipt(errorReceipt(apply ? "hitl.apply" : "hitl.draft", exc, { gate_id: gate.gate_id, decision }));
    }
  };

  return (
    <section className="workspace runtime-layout">
      <div className="metric-row">
        <Metric label="Sequence" value={String(flow.sequence ?? 0)} />
        <Metric label="Events" value={String(flow.events?.length ?? 0)} />
        <Metric label="HITL" value={String(flow.pending_human_gates?.length ?? 0)} />
        <Metric label="Nodes" value={String(flow.nodes?.length ?? 0)} />
      </div>

      <div className="action-palette">
        <div className="palette-title">
          <strong><Workflow size={17} /> {t.triggerPalette}</strong>
          <span><ShieldCheck size={14} /> {t.operatorSafe}</span>
        </div>
        <div className="action-groups">
          {runtimeActionGroups(t).map((group) => (
            <section className="action-group" key={group.label}>
              <span>{group.label}</span>
              <div>
                {group.actions.map((item) => (
                  <button className="action-tile" key={item.action} onClick={() => void runAction(item.action)}>
                    {item.icon}
                    <strong>{item.label}</strong>
                    <small>{t.dryRunOnly}</small>
                  </button>
                ))}
              </div>
            </section>
          ))}
        </div>
        <div className="trigger-catalog">
          <strong>{t.registeredTriggers}</strong>
          <div>
            {catalogGroups.map((group) => (
              <span className="trigger-chip" key={group.kind}>
                {group.kind}: {group.names.join(", ")}
              </span>
            ))}
          </div>
        </div>
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
              <small>{String(gate.gate_id)} / {String(gate.plan_state || gate.state || "pending")}</small>
              <div className="button-row">
                {gateActions(gate).map((action) => (
                  <button className="button small" key={action} onClick={() => void draftGate(gate, action)}>
                    {hitlActionLabel(action, t)}
                  </button>
                ))}
                {gateActions(gate).length ? (
                  <button
                    className="button small primary"
                    onClick={() => void draftGate(gate, preferredGateAction(gate), true)}
                  >
                    {t.dryApply}: {hitlActionLabel(preferredGateAction(gate), t)}
                  </button>
                ) : null}
              </div>
            </div>
          ))
        ) : <p className="muted">{t.noPendingGate}</p>}
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

function gateActions(gate: Record<string, unknown>): string[] {
  const raw = Array.isArray(gate.options)
    ? gate.options
    : Array.isArray(gate.valid_actions_for_state)
      ? gate.valid_actions_for_state
      : [];
  return raw.map((action) => String(action)).filter(Boolean);
}

function preferredGateAction(gate: Record<string, unknown>): string {
  const actions = gateActions(gate);
  return actions.includes("approve_and_start") ? "approve_and_start" : actions[0] || "approve";
}

function hitlActionLabel(action: string, t: ConsoleCopy): string {
  switch (action) {
    case "approve":
      return t.approve;
    case "approve_and_start":
      return t.approveAndStart;
    case "reject":
      return t.reject;
    case "revise":
      return t.revise;
    case "cancel":
      return t.cancel;
    case "resume":
      return t.resume;
    default:
      return action;
  }
}

function runtimeActionGroups(t: ConsoleCopy): Array<{
  label: string;
  actions: Array<{ action: RuntimeAction; label: string; icon: JSX.Element }>;
}> {
  return [
    {
      label: t.actionGroupMessage,
      actions: [
        { action: "message_check", label: t.messageCheck, icon: <Bell size={17} /> },
        { action: "message_push", label: t.messagePush, icon: <Play size={17} /> }
      ]
    },
    {
      label: t.actionGroupRuntime,
      actions: [
        { action: "llm_push", label: t.llmPush, icon: <Sparkles size={17} /> },
        { action: "scheduler_tick", label: t.schedulerTick, icon: <Activity size={17} /> },
        { action: "calendar_test", label: t.calendarTest, icon: <CalendarDays size={17} /> }
      ]
    },
    {
      label: t.actionGroupMode,
      actions: [
        { action: "scene_switch", label: t.sceneSwitch, icon: <GitBranch size={17} /> },
        { action: "roleplay_open", label: t.roleplayOpen, icon: <CircleDot size={17} /> }
      ]
    }
  ];
}

function groupTriggerCatalog(triggers: Array<Record<string, unknown>>): Array<{ kind: string; names: string[] }> {
  const groups = new Map<string, string[]>();
  triggers.forEach((trigger) => {
    const names = groupsForTrigger(trigger);
    names.forEach((kind) => {
      const rows = groups.get(kind) ?? [];
      rows.push(String(trigger.name || trigger.class || "trigger"));
      groups.set(kind, rows);
    });
  });
  return Array.from(groups.entries()).map(([kind, names]) => ({ kind, names }));
}

function groupsForTrigger(trigger: Record<string, unknown>): string[] {
  const raw = trigger.kinds;
  if (!Array.isArray(raw) || raw.length === 0) return ["unknown"];
  return raw.map((kind) => String(kind));
}

function isSelectedEdge(selected: Record<string, unknown> | null): selected is Record<string, unknown> {
  return selected?.selection_type === "edge";
}

function EmptyL2BHint({ liveState, t }: { liveState: LiveState; t: ConsoleCopy }) {
  const rows = [
    { label: t.blackboardScope, value: `${liveState.blackboard?.present_count ?? 0}/${liveState.blackboard?.declared_count ?? 0}` },
    { label: t.intentScope, value: String(liveState.intent_workspace?.ref_count ?? 0) },
    { label: "Refs", value: String(liveState.refs?.refs?.length ?? 0) },
    { label: "L2-B", value: `${liveState.l2b?.node_count ?? 0}/${liveState.l2b?.edge_count ?? 0}` }
  ];
  return (
    <div className="empty-graph-hint">
      <div>
        <strong>{t.emptyGraphTitle}</strong>
        <p>{t.emptyGraphBody}</p>
      </div>
      <div className="empty-scope-row">
        {rows.map((row) => (
          <span className="empty-scope-chip" key={row.label}>
            <i />
            {row.label} {row.value}
          </span>
        ))}
      </div>
    </div>
  );
}

function L15HealthPanel({ health, t }: { health: Record<string, unknown>; t: ConsoleCopy }) {
  const totalNodes = Number(health.total_nodes ?? 0);
  const refsTotal = Number(health.refs_total ?? 0);
  const pressure = String(health.capacity_pressure || "ok");
  const scene = String(health.current_scene || "-");
  return (
    <div className="l15-health">
      <strong className="l15-health-title">{t.l15Health}</strong>
      <div>
        <span>{t.nodes}</span>
        <strong>{totalNodes}</strong>
      </div>
      <div>
        <span>{t.refs}</span>
        <strong>{refsTotal}</strong>
      </div>
      <div>
        <span>{t.pressure}</span>
        <strong>{pressure}</strong>
      </div>
      <div>
        <span>{t.currentScene}</span>
        <strong>{scene}</strong>
      </div>
    </div>
  );
}

function ObsidianDraftCard({
  pushReceipt,
  t
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
}) {
  const [profile, setProfile] = useState("daily");
  const [label, setLabel] = useState("Web setting node");
  const [obsidianUuid, setObsidianUuid] = useState("");
  const refMissingUuid = profile === "ref" && !obsidianUuid.trim();
  const draft = async () => {
    if (refMissingUuid) {
      pushReceipt(localReceipt("l15.obsidian_node.draft", false, {
        error: "ref_profile_requires_obsidian_uuid",
        profile,
        label
      }));
      return;
    }
    try {
      pushReceipt(await api.l15ObsidianNodeDraft({
        profile,
        label: label.trim(),
        obsidian_uuid: obsidianUuid.trim(),
        description: `Drafted from React Memory Graph Workspace (${profile}).`,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l15.obsidian_node.draft", exc, { profile, label }));
    }
  };
  return (
    <article className="obsidian-card">
      <div className="obsidian-card-head">
        <strong>{t.obsidianSettings}</strong>
        <small className={refMissingUuid ? "warn-text" : ""}>{profile === "ref" ? t.refRequiresUuid : t.uuidFree}</small>
      </div>
      <label>
        <span>{t.settingProfile}</span>
        <select value={profile} onChange={(event) => setProfile(event.target.value)}>
          <option value="daily">daily</option>
          <option value="roleplay">roleplay</option>
          <option value="ref">ref</option>
        </select>
      </label>
      <label>
        <span>{t.settingLabel}</span>
        <input value={label} onChange={(event) => setLabel(event.target.value)} placeholder={t.settingLabel} />
      </label>
      <label>
        <span>{t.obsidianUuid}</span>
        <input value={obsidianUuid} onChange={(event) => setObsidianUuid(event.target.value)} placeholder={profile === "ref" ? "required for ref" : "optional"} />
      </label>
      <button className={refMissingUuid ? "button danger" : "button primary"} onClick={() => void draft()}>{t.settingDraft}</button>
    </article>
  );
}

function SelectedEdgeTools({
  selected,
  edgeFrom,
  edgeTo,
  onRetarget,
  onSwap,
  t
}: {
  selected: Record<string, unknown>;
  edgeFrom: string;
  edgeTo: string;
  onRetarget: () => void;
  onSwap: () => void;
  t: ConsoleCopy;
}) {
  const previousSource = String(selected.previous_source || selected.source || "");
  const previousTarget = String(selected.previous_target || selected.target || "");
  return (
    <article className="edge-tools">
      <div className="edge-tools-head">
        <strong><GitBranch size={16} /> {t.selectedEdgeTools}</strong>
        <small>{t.selectedEdgeHint}</small>
      </div>
      <div className="edge-endpoint-grid">
        <span>{t.fromUuid}</span>
        <strong>{edgeFrom || "-"}</strong>
        <span>{t.toUuid}</span>
        <strong>{edgeTo || "-"}</strong>
      </div>
      <small>{`${previousSource} -> ${previousTarget}`}</small>
      <div className="button-row">
        <button className="button small" onClick={onRetarget}>{t.retargetEdge}</button>
        <button className="button small ghost" onClick={onSwap}>{t.swapEdge}</button>
      </div>
    </article>
  );
}

function BucketCard({
  bucket,
  maxNodeCount,
  pushReceipt,
  t
}: {
  bucket: Record<string, unknown>;
  maxNodeCount: number;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
}) {
  const kind = String(bucket.kind || "");
  const nodeCount = Number(bucket.node_count ?? 0);
  const frozen = Boolean(bucket.frozen);
  const ratio = Math.max(0.04, Math.min(1, nodeCount / Math.max(1, maxNodeCount)));
  const lastActivity = Math.max(Number(bucket.last_modified_at ?? 0), Number(bucket.created_at ?? 0));
  const op = async (operation: string) => {
    try {
      pushReceipt(await api.l15BucketDraft({ kind, op: operation, dry_run: true, operator_mode: false }));
    } catch (exc) {
      pushReceipt(errorReceipt("l15.bucket.draft", exc, { kind, op: operation }));
    }
  };
  return (
    <article className={frozen ? "bucket-card frozen" : "bucket-card"}>
      <div>
        <strong>{kind}</strong>
        <small>{nodeCount} nodes / {frozen ? "frozen" : "open"}</small>
      </div>
      <div className="bucket-meter" aria-label={`${kind} capacity`}>
        <span style={{ width: `${ratio * 100}%` }} />
      </div>
      <small>{t.lastActivity}: {formatRelativeTime(lastActivity)}</small>
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

function ReceiptRail({ receipts, t }: { receipts: Receipt[]; t: ConsoleCopy }) {
  return (
    <aside className="receipt-rail">
      <h2>{t.receiptTimeline}</h2>
      {receipts.length ? receipts.map((receipt, index) => {
        const id = receiptId(receipt, index);
        const data = receipt.data ?? {};
        const summary = receiptSummary(data);
        return (
          <div className={receipt.success === false ? "receipt bad" : "receipt"} key={id}>
            <div className="receipt-head">
              <strong>{receipt.action || "receipt"}</strong>
              <span className={receipt.success === false ? "status-chip bad" : "status-chip"}>
                {receipt.success === false ? t.failedStatus : t.okStatus}
              </span>
            </div>
            <small>
              {receipt.dry_run ? t.previewMode : t.executeMode} / {receipt.operator_mode ? t.operatorMode : t.safeMode} / {id}
            </small>
            {summary ? <p className="receipt-summary">{summary}</p> : null}
            <details className="record-details">
              <summary>{t.recordDetails}</summary>
              <JsonBlock value={data} />
            </details>
          </div>
        );
      }) : <p className="muted">{t.noReceipts}</p>}
    </aside>
  );
}

function JsonBlock({ value }: { value: unknown }) {
  return <pre className="json-block">{JSON.stringify(value, null, 2)}</pre>;
}

function MemoryNodeCard({ data, selected, isConnectable }: NodeProps<MemoryNodeData>) {
  const nodeKind = String(data.source?.kind || (data.preview ? "preview" : "node"));
  const compactId = String(data.source?.uuid || "").slice(0, 18);
  const handlePositions = [
    { id: "top", position: Position.Top },
    { id: "right", position: Position.Right },
    { id: "bottom", position: Position.Bottom },
    { id: "left", position: Position.Left }
  ];

  return (
    <div className={selected ? "memory-node-card selected" : "memory-node-card"}>
      {handlePositions.map((handle) => (
        <Handle
          key={handle.id}
          id={handle.id}
          type="source"
          position={handle.position}
          isConnectable={isConnectable}
        />
      ))}
      <div className="memory-node-title">{data.label}</div>
      <div className="memory-node-meta">
        <span>{nodeKind}</span>
        {compactId ? <span>{compactId}</span> : null}
      </div>
    </div>
  );
}

function memoryNode(row: Record<string, unknown>, index: number): Node {
  const angle = (Math.PI * 2 * index) / Math.max(1, 12);
  const radius = 220;
  return {
    id: String(row.uuid),
    position: { x: 360 + Math.cos(angle) * radius, y: 280 + Math.sin(angle) * radius },
    type: "memory",
    data: {
      label: String(row.label || row.uuid),
      source: row
    },
    className: `memory-node kind-${String(row.kind || "node")}`,
    connectable: true
  };
}

function isDraftableMemoryNodeId(id: string): boolean {
  return Boolean(id) && !id.startsWith("placeholder:");
}

function makeDraftId(kind: string): string {
  return `draft:${kind}:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
}

function edgeEndpoint(row: Record<string, unknown>, side: "source" | "target"): string {
  const fallback = side === "source" ? row.from_uuid : row.to_uuid;
  return String(row[side] ?? fallback ?? "");
}

function formatRelativeTime(epochSeconds: number): string {
  if (!epochSeconds) return "-";
  const deltaSeconds = Math.max(0, Math.round(Date.now() / 1000 - epochSeconds));
  if (deltaSeconds < 60) return `${deltaSeconds}s ago`;
  const minutes = Math.round(deltaSeconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 48) return `${hours}h ago`;
  return `${Math.round(hours / 24)}d ago`;
}

function localReceipt(action: string, success: boolean, data: Record<string, unknown>): Receipt {
  return {
    receipt_id: `local_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    action,
    success,
    dry_run: true,
    operator_mode: false,
    data
  };
}

function errorReceipt(action: string, exc: unknown, data: Record<string, unknown> = {}): Receipt {
  return localReceipt(action, false, {
    ...data,
    error: exc instanceof Error ? exc.message : String(exc)
  });
}

function receiptId(receipt: Receipt, index: number): string {
  const nested = receipt.receipt;
  return String(receipt.receipt_id || nested?.receipt_id || `${receipt.action || "receipt"}-${index}`);
}

function receiptSummary(data: Record<string, unknown>): string {
  const error = data.error;
  if (error) return String(error);
  const matched = data.matched_triggers;
  if (Array.isArray(matched) && matched.length) return `matched: ${matched.map(String).join(", ")}`;
  const skipped = data.publish_skipped_reason || data.apply_skipped_reason || data.dispatch_skipped_reason;
  if (skipped) return String(skipped);
  const event = data.event;
  if (event && typeof event === "object") {
    const row = event as Record<string, unknown>;
    return String(row.kind || row.type || "");
  }
  return "";
}
