import { Fragment, useCallback, useEffect, useMemo, useReducer, useRef, useState, type MouseEvent as ReactMouseEvent, type ReactNode } from "react";
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
  Camera,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  Database,
  FileText,
  Filter,
  GitBranch,
  Languages,
  Layers,
  Link2,
  PanelRightOpen,
  Pencil,
  Play,
  Plus,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Tags,
  Trash2,
  UploadCloud,
  Workflow
} from "lucide-react";
import { api } from "./api";
import type {
  ConsoleConfig,
  L15Pool,
  Language,
  LiveKitConfig,
  LiveKitToken,
  LiveState,
  Receipt,
  RuntimeFlow,
  TriggerCatalog,
  VisionEvidenceStatus,
  VisionEvidenceTimeline
} from "./types";

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

type EdgeHandlePair = {
  sourceHandle?: string;
  targetHandle?: string;
};

type GraphitiPreviewPayload = {
  hits?: Array<Record<string, unknown>>;
  nodes?: Array<Record<string, unknown>>;
  edges?: Array<Record<string, unknown>>;
  partition?: string;
  query?: string;
};

type SourceBoardId = "graphiti" | "obsidian" | "calendar" | "refs" | "manual";
type MemoryToolId = "node" | "edge" | "filter" | "tags" | "subgraph" | "state" | "pool" | "settings";

type HandleSide = "top" | "right" | "bottom" | "left";

type NodePositionMap = Map<string, { x: number; y: number }>;
type LiveKitEventStatus = "idle" | "good" | "warn" | "bad";

type LiveKitEventRow = {
  at: string;
  label: string;
  detail: string;
  status: LiveKitEventStatus;
};

type LiveKitClientModule = {
  Room: new (options?: Record<string, unknown>) => any;
  RoomEvent?: Record<string, string>;
  Track?: any;
};

const EDGE_KIND_OPTIONS = [
  "associated_with",
  "reminds_of",
  "co_occurred",
  "spatial_context",
  "part_of_episode",
  "has_photo",
  "captured_via",
  "candidate_subject"
];

const NODE_KIND_OPTIONS = ["object", "surface", "zone", "person", "event", "photo"];
const GRAPH_IMPORT_DESTINATIONS = [
  "workspace_only",
  "index_pointer",
  "isolated_compartment",
  "promote_to_main_graph",
  "connect_by_rule"
];
const GRAPH_TRANSFORM_OPTIONS = [
  "wrap_selection",
  "aggregate_subgraphs",
  "compare_subgraphs",
  "draft_cross_links",
  "promote_to_main_graph",
  "split_subgraph",
  "tombstone_stale_cluster",
  "send_context_to_llm"
];

const memoryNodeTypes: NodeTypes = {
  memory: MemoryNodeCard
};

const LIVEKIT_CLIENT_URLS = [
  "https://cdn.jsdelivr.net/npm/livekit-client@2.18.10/dist/livekit-client.esm.mjs",
  "https://unpkg.com/livekit-client@2.18.10/dist/livekit-client.esm.mjs"
];

let liveKitClientPromise: Promise<LiveKitClientModule> | null = null;

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
    updateNode: "Update Node",
    deleteNode: "Delete Node",
    draftEdge: "Connect Edge",
    updateEdge: "Update Edge",
    deleteEdge: "Delete Edge",
    tools: "Tools",
    closeTools: "Close Tools",
    filters: "Filters",
    tags: "Tags",
    subgraph: "Subgraph",
    stateView: "State colors",
    pool: "Pool",
    nodeKind: "Node kind",
    edgeKind: "Edge kind",
    edgeStrength: "Edge strength",
    edgeMeta: "Edge meta JSON",
    selectedNode: "Node details",
    selectedEdge: "Edge details",
    useAsEndpoints: "Use endpoints",
    addTagDraft: "Tag preview",
    createSubgraph: "New subgraph",
    importDestination: "Import destination",
    graphPolicy: "Graph policy",
    previewPolicy: "Preview policy",
    graphTransform: "Graph transform",
    previewTransform: "Preview transform",
    graphHealth: "Graph health",
    refreshHealth: "Refresh health",
    overlayDraft: "Overlay preview",
    statusColors: "Status color overlay",
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
    connectHint: "Double-click to add; drag handles to connect.",
    selectedEdgeTools: "Edge Operations",
    retargetEdge: "Preview Retarget",
    swapEdge: "Swap",
    selectedEdgeHint: "Retarget creates a new Edge preview and record; it does not mutate or delete the existing Edge.",
    emptyGraphTitle: "No L2-B Nodes yet",
    emptyGraphBody: "This canvas will show real L2-B Nodes and Edges after L1.5 commits memory candidates. The chips below are status summaries, not graph Nodes.",
    blackboardScope: "Blackboard",
    intentScope: "Intent",
    runtimeSummary: "Intent, Plan, HITL, Blackboard, Scheduler, Nanobot, and messages.",
    memorySummary: "L1.5, L2-B, Graphiti, Refs, Evidence Board, and safe graph previews.",
    evidenceConsole: "Time / Evidence",
    evidenceSamples: "Samples",
    evidenceAssets: "Assets",
    frameCache: "Frame cache",
    liveKitSampler: "LiveKit sampler",
    fresh: "fresh",
    stale: "stale",
    evidenceAutoRefresh: "Auto",
    requestEvidence: "Request Evidence",
    stageEvidenceHint: "Stage Hint",
    cacheFrameTest: "Cache Frame",
    bboxTest: "BBox Test",
    focusTest: "Focus Test",
    noEvidence: "No evidence samples yet.",
    sourceBoard: "Source Board",
    graphiti: "Graphiti",
    graphitiQuery: "Natural-language search",
    partition: "Partition",
    limit: "Limit",
    searchGraphiti: "Search",
    previewOnCanvas: "Preview on canvas",
    exportSubgraphDraft: "Export Draft",
    applyExportDryRun: "Preview Apply",
    selectedHits: "Selected hits",
    selectAll: "Select all",
    selectedOf: "selected",
    resultGraph: "Result graph",
    noHits: "No hits yet.",
    writeThroughL15: "writes through L1.5",
    sourceBoardHint: "Sources become previews or L1.5 observations before L2-B.",
    liveKitBridge: "LiveKit / Brain Bridge",
    liveKitRoom: "Room",
    liveKitIdentity: "Identity",
    mintToken: "Mint token",
    connectRoom: "Connect",
    disconnectRoom: "Disconnect",
    enableMic: "Mic on",
    disableMic: "Mic off",
    shareScreen: "Share screen",
    stopShare: "Stop share",
    checkSamples: "Check samples",
    liveKitEvents: "Events",
    liveKitTranscripts: "Transcript",
    liveKitBridgeHint: "Use screen share when there is no camera. Brain must be running in the same room.",
    googleCalendar: "Google Calendar",
    calendarFetch: "Fetch Preview",
    calendarFetchExecute: "Dispatch Fetch",
    calendarPreview: "Calendar Preview",
    calendarPayload: "Google/Nanobot JSON",
    calendarImportExecute: "Import to L1.5",
    calendarResults: "Result History",
    calendarResultEmpty: "No recent calendar_result rows.",
    calendarResultUnavailable: "Result ledger unavailable. Start Redis, Scheduler, and Nanobot to see real calendar_result rows.",
    manualNode: "Manual Node",
    manualNodeHint: "Use the canvas toolbar for direct Node and Edge drafts.",
    roleplayModeHint: "RolePlay is a mode/profile; it can contain many source packs.",
    obsidianVaultPath: "Vault path",
    scanVault: "Scan vault",
    readyNotes: "Ready notes",
    invalidNotes: "Invalid notes",
    useNote: "Use note",
    importDraft: "Import Preview",
    selectedNotes: "Selected notes",
    selectVisibleNotes: "Select visible",
    clearSelection: "Clear selection",
    vaultStatus: "Vault status",
    readyCount: "Ready",
    normalizedPreview: "Normalized preview",
    observationPreview: "Observation preview",
    calendarMapping: "Mapping preview",
    calendarTarget: "Target",
    calendarPolicy: "Policy"
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
    tools: "工具",
    closeTools: "收起工具",
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
    connectHint: "双击新建；拖动连接点连 Edge。",
    selectedEdgeTools: "Edge 操作",
    retargetEdge: "重定向预览",
    swapEdge: "交换端点",
    selectedEdgeHint: "重定向只生成新的 Edge 预览和操作记录，不会改写已有 Edge。",
    emptyGraphTitle: "L2-B 还没有真实 Node",
    emptyGraphBody: "这里之后显示真实 L2-B Node / Edge。下面这些是状态概览，不是可以连接的图 Node。",
    blackboardScope: "黑板",
    intentScope: "Intent",
    runtimeSummary: "Intent、Plan、HITL、黑板、Scheduler、Nanobot 和消息流。",
    memorySummary: "L1.5、L2-B、Graphiti、Refs、Evidence Board 和图上安全预演操作。",
    evidenceConsole: "时间 / Evidence",
    evidenceSamples: "样本",
    evidenceAssets: "资产",
    frameCache: "帧缓存",
    liveKitSampler: "LiveKit sampler",
    fresh: "fresh",
    stale: "stale",
    evidenceAutoRefresh: "自动",
    requestEvidence: "请求 Evidence",
    stageEvidenceHint: "暂存提示",
    cacheFrameTest: "缓存测试帧",
    bboxTest: "BBox 测试",
    focusTest: "Focus 测试",
    noEvidence: "暂无 evidence 样本。",
    sourceBoard: "Source Board",
    graphiti: "Graphiti",
    graphitiQuery: "自然语言检索",
    partition: "分区",
    limit: "数量",
    searchGraphiti: "搜索",
    previewOnCanvas: "画布预览",
    exportSubgraphDraft: "导出草稿",
    applyExportDryRun: "预演执行",
    selectedHits: "选中结果",
    selectAll: "全选",
    selectedOf: "已选",
    resultGraph: "结果子图",
    noHits: "暂无结果。",
    writeThroughL15: "通过 L1.5 写入",
    sourceBoardHint: "来源数据先变成预览或 L1.5 Observation，再进入 L2-B。",
    liveKitBridge: "LiveKit / Brain 连接",
    liveKitRoom: "房间",
    liveKitIdentity: "身份",
    mintToken: "生成 Token",
    connectRoom: "连接",
    disconnectRoom: "断开",
    enableMic: "打开麦克风",
    disableMic: "关闭麦克风",
    shareScreen: "屏幕共享",
    stopShare: "停止共享",
    checkSamples: "检查采样",
    liveKitEvents: "事件",
    liveKitTranscripts: "转写",
    liveKitBridgeHint: "没有摄像头时用屏幕共享。Brain 必须在同一个房间运行。",
    googleCalendar: "Google 日程",
    calendarFetch: "请求获取",
    calendarFetchExecute: "真实请求",
    calendarPreview: "日程预览",
    calendarPayload: "Google/Nanobot JSON",
    calendarImportExecute: "导入 L1.5",
    calendarResults: "结果记录",
    calendarResultEmpty: "暂无 calendar_result 记录。",
    calendarResultUnavailable: "结果记录不可用：需要 Redis、Scheduler 和 Nanobot 运行后才会出现 calendar_result。",
    manualNode: "手动 Node",
    manualNodeHint: "直接 Node / Edge 草稿放在画布工具栏里操作。",
    roleplayModeHint: "RolePlay 是模式/Profile，可以包含很多来源包。",
    obsidianVaultPath: "Vault 路径",
    scanVault: "扫描 Vault",
    readyNotes: "可导入 Notes",
    invalidNotes: "无效 Notes",
    useNote: "使用 Note",
    importDraft: "导入预演",
    selectedNotes: "已选 Notes",
    selectVisibleNotes: "选择可见项",
    clearSelection: "清空选择",
    vaultStatus: "Vault 状态",
    readyCount: "可导入",
    normalizedPreview: "标准化预览",
    observationPreview: "Observation 预览",
    calendarMapping: "映射预览",
    calendarTarget: "目标",
    calendarPolicy: "策略"
  }
};

type ConsoleCopy = typeof dict.en;

const zhRuntimeCopy: Partial<ConsoleCopy> = {
  updateNode: "更新 Node",
  deleteNode: "删除 Node",
  updateEdge: "更新 Edge",
  deleteEdge: "删除 Edge",
  filters: "过滤",
  tags: "Tag",
  subgraph: "子图",
  stateView: "状态颜色",
  pool: "Pool",
  nodeKind: "Node 类型",
  edgeKind: "Edge 类型",
  edgeStrength: "Edge 强度",
  edgeMeta: "Edge meta JSON",
  selectedNode: "Node 详情",
  selectedEdge: "Edge 详情",
  useAsEndpoints: "使用端点",
  addTagDraft: "Tag 预演",
  createSubgraph: "新建子图",
  statusColors: "状态颜色开关"
};

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
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [recordsOpen, setRecordsOpen] = useState(false);
  const memorySequenceRef = useRef(0);
  const runtimeSequenceRef = useRef(0);
  const t = { ...dict.en, ...dict[language], ...(language === "zh" ? zhRuntimeCopy : {}) };
  const configuredRefreshIntervalS = Math.max(3, Math.round(Number(config.refresh_interval_s ?? 5)));
  const refreshIntervalS = view === "memory" ? Math.min(configuredRefreshIntervalS, 5) : configuredRefreshIntervalS;

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextConfig, memoryChanges, nextPool, flowChanges, nextTriggerCatalog] = await Promise.all([
        api.config(),
        api.memoryLiveChanges(memorySequenceRef.current),
        api.l15Pool(),
        api.runtimeFlowChanges(runtimeSequenceRef.current),
        api.triggerCatalog()
      ]);
      setConfig(nextConfig);
      if (typeof memoryChanges.sequence === "number") {
        memorySequenceRef.current = memoryChanges.sequence;
      }
      if (memoryChanges.changed && memoryChanges.snapshot) {
        setLiveState(memoryChanges.snapshot);
      }
      setL15Pool(nextPool);
      if (typeof flowChanges.sequence === "number") {
        runtimeSequenceRef.current = flowChanges.sequence;
      }
      if (flowChanges.changed && flowChanges.snapshot) {
        setRuntimeFlow(flowChanges.snapshot);
      }
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
    <div className={`app-shell${sidebarOpen ? "" : " sidebar-collapsed"}${recordsOpen ? "" : " records-collapsed"}`}>
      <aside className={sidebarOpen ? "sidebar" : "sidebar collapsed"}>
        <button className="sidebar-toggle" onClick={() => setSidebarOpen((open) => !open)} title={sidebarOpen ? "Collapse" : "Expand"}>
          <PanelRightOpen size={17} />
        </button>
        <div className="brand">
          <div className="brand-mark">P</div>
          {sidebarOpen ? (
            <div>
              <strong>Parrot Console</strong>
              <small>React Web lane</small>
            </div>
          ) : null}
        </div>
        <button className={view === "memory" ? "nav active" : "nav"} onClick={() => setView("memory")} title={t.memory}>
          <GitBranch size={18} /> {sidebarOpen ? t.memory : null}
        </button>
        <button className={view === "runtime" ? "nav active" : "nav"} onClick={() => setView("runtime")} title={t.runtime}>
          <Activity size={18} /> {sidebarOpen ? t.runtime : null}
        </button>
        <div className="sidebar-footer">
          {sidebarOpen ? <span><CircleDot size={14} /> {t.auth}: {config.orchestrator_auth_mode || "..."}</span> : null}
          <button className="nav small" onClick={() => setLang(language === "zh" ? "en" : "zh")} title={t.language}>
            <Languages size={16} /> {language === "zh" ? "EN" : "\u4e2d\u6587"}
          </button>
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <span className="eyebrow">{view === "memory" ? t.memory : t.runtime}</span>
            <h1>{view === "memory" ? t.memory : t.runtime}</h1>
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

      <ReceiptRail receipts={receipts} t={t} open={recordsOpen} onToggle={() => setRecordsOpen((open) => !open)} />
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
  const [nodeKind, setNodeKind] = useState("object");
  const [edgeKind, setEdgeKind] = useState("associated_with");
  const [edgeStrength, setEdgeStrength] = useState("0.5");
  const [edgeMetaText, setEdgeMetaText] = useState("{}");
  const [tagText, setTagText] = useState("");
  const [filterKind, setFilterKind] = useState("all");
  const [subgraphLabel, setSubgraphLabel] = useState("Work subgraph");
  const [graphDestination, setGraphDestination] = useState("isolated_compartment");
  const [graphTransformKind, setGraphTransformKind] = useState("wrap_selection");
  const [graphHealth, setGraphHealth] = useState<Record<string, unknown> | null>(null);
  const [stateColors, setStateColors] = useState(true);
  const [manualPositions, setManualPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance<MemoryNodeData> | null>(null);
  const [activeTool, setActiveTool] = useState<MemoryToolId | null>("node");

  const l2bNodes = liveState.l2b?.nodes ?? [];
  const l2bEdges = liveState.l2b?.edges ?? [];
  const selectedNodeId = selected?.selection_type === "node" ? String(selected.uuid || selected.id || "") : "";
  const selectedEdgeId = selected?.selection_type === "edge" ? String(selected.id || "") : "";
  const selectedNodeRefs = useMemo(
    () => relatedRefsForNode(liveState, selectedNodeId, selected),
    [liveState, selected, selectedNodeId]
  );
  const graphNodes = useMemo<Node[]>(() => {
    const real = l2bNodes.length
      ? l2bNodes.map((row, index) => memoryNode(row, index, stateColors))
      : [];
    const previews = previewNodes.map((row, index) => ({
      id: String(row.uuid),
      position: { x: 260 + (index % 4) * 170, y: 230 + Math.floor(index / 4) * 96 },
      type: "memory",
      data: { label: String(row.label), source: row, preview: true },
      className: `preview-node${row.kind === "subgraph" ? " subgraph-node" : ""}`,
      connectable: row.draftable !== false
    }));
    return [...real, ...previews].filter((node) => {
      if (filterKind === "all") return true;
      const source = (node.data as MemoryNodeData | undefined)?.source;
      return String(source?.kind || "node") === filterKind;
    }).map((node) => ({
      ...node,
      draggable: true,
      position: manualPositions[node.id] ?? node.position,
      selected: node.id === selectedNodeId
    }));
  }, [filterKind, l2bNodes, manualPositions, previewNodes, selectedNodeId, stateColors]);
  const draftableNodeIds = useMemo(
    () => new Set(graphNodes
      .filter((node) => {
        const source = (node.data as MemoryNodeData | undefined)?.source;
        return isDraftableMemoryNodeId(node.id) && node.connectable !== false && source?.draftable !== false;
      })
      .map((node) => node.id)),
    [graphNodes]
  );
  const nodePositions = useMemo<NodePositionMap>(
    () => new Map(graphNodes.map((node) => [node.id, node.position])),
    [graphNodes]
  );
  const visibleNodeIds = useMemo(
    () => new Set(graphNodes.map((node) => node.id)),
    [graphNodes]
  );

  const graphEdges = useMemo<Edge[]>(() => {
    const persisted: Edge[] = [];
    l2bEdges.forEach((row, index) => {
      const source = edgeEndpoint(row, "source");
      const target = edgeEndpoint(row, "target");
      if (!source || !target) return;
      if (!visibleNodeIds.has(source) || !visibleNodeIds.has(target)) return;
      const handles = inferEdgeHandles(source, target, nodePositions);
      persisted.push({
        id: `edge-${index}-${source}-${target}`,
        source,
        target,
        sourceHandle: handles.sourceHandle,
        targetHandle: handles.targetHandle,
        label: String(row.kind || ""),
        className: row.cross_compartment ? "cross-edge" : "",
        reconnectable: true,
        data: { source: row }
      });
    });
    return [...persisted, ...previewEdges]
      .filter((edge) => visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target))
      .map((edge) => ({
        ...edge,
        ...(edge.sourceHandle && edge.targetHandle ? {} : inferEdgeHandles(edge.source, edge.target, nodePositions)),
        selected: edge.id === selectedEdgeId
      }));
  }, [l2bEdges, nodePositions, previewEdges, selectedEdgeId, visibleNodeIds]);

  useEffect(() => {
    if (!selected) return;
    if (selectedNodeId && !visibleNodeIds.has(selectedNodeId)) {
      setSelected(null);
      return;
    }
    if (selectedEdgeId && !graphEdges.some((edge) => edge.id === selectedEdgeId)) {
      setSelected(null);
    }
  }, [graphEdges, selected, selectedEdgeId, selectedNodeId, visibleNodeIds]);

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
    setSelected({
      ...source,
      selection_type: "edge",
      id: edge.id,
      source: edge.source,
      target: edge.target,
      source_handle: formatHandleSide(edge.sourceHandle),
      target_handle: formatHandleSide(edge.targetHandle)
    });
    setEdgeFrom(edge.source);
    setEdgeTo(edge.target);
  };

  const stagePreviewNode = (uuid: string, label: string, position?: { x: number; y: number }) => {
    const nodeSource = { uuid, label, kind: nodeKind, preview: true, confirmation: "confirmed", salience: "active", tags: [] };
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

  const stageGraphitiPreview = (preview: GraphitiPreviewPayload) => {
    const sourceRows = (preview.nodes?.length ? preview.nodes : preview.hits ?? []).slice(0, 18);
    const nodes = sourceRows.map((row, index) => ({
      uuid: graphitiPreviewNodeId(row, index),
      label: graphitiHitLabel(row, index),
      kind: String(row.kind || "graphiti_fact"),
      preview: true,
      draftable: false,
      source_tool: "graphiti_subgraph_preview",
      partition: String(row.partition || preview.partition || "arknights_test"),
      graphiti_uuid: String(row.uuid || row.graphiti_uuid || ""),
      source_url: String(row.source_url || ""),
      source_description: String(row.source_description || ""),
      summary: String(row.summary || row.text || "")
    }));
    const nodeIds = new Set(nodes.map((node) => node.uuid));
    const graphitiEdges = (preview.edges ?? [])
      .filter((edge) => nodeIds.has(String(edge.source || "")) && nodeIds.has(String(edge.target || "")))
      .slice(0, 24)
      .map((edge, index): Edge => ({
        id: String(edge.id || `graphiti-preview-edge:${index}`),
        source: String(edge.source || ""),
        target: String(edge.target || ""),
        label: String(edge.label || edge.kind || "fact"),
        className: "preview-edge graphiti-preview-edge",
        animated: true,
        reconnectable: false,
        type: "smoothstep",
        style: { strokeWidth: 2.5 },
        data: {
          source: {
            ...edge,
            source_tool: "graphiti_subgraph_preview",
            preview: true,
            draftable: false
          }
        }
      }));
    setPreviewNodes((current) => [
      ...current.filter((row) => row.source_tool !== "graphiti_subgraph_preview"),
      ...nodes
    ]);
    setPreviewEdges((current) => [
      ...current.filter((edge) => {
        const source = (edge.data as { source?: Record<string, unknown> } | undefined)?.source;
        return source?.source_tool !== "graphiti_subgraph_preview";
      }),
      ...graphitiEdges
    ]);
    if (nodes.length) {
      pushReceipt(localReceipt("graphiti.subgraph.preview", true, {
        count: nodes.length,
        edge_count: graphitiEdges.length,
        partition: preview.partition || "arknights_test",
        query: preview.query || "",
        canvas_preview: true,
        note: "Graphiti preview nodes are read-only until exported through L1.5."
      }));
    }
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
        kind: nodeKind,
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

  const edgeMetaPayload = (reason: string, extra: Record<string, unknown> = {}) => ({
    ...parseJsonObject(edgeMetaText),
    reason,
    ...extra
  });

  const draftEdgeBetween = async (
    from: string,
    to: string,
    reason: string,
    meta: Record<string, unknown> = {},
    handles: EdgeHandlePair = {}
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
        kind: edgeKind,
        strength: Number(edgeStrength) || 0.5,
        meta: edgeMetaPayload(reason, meta),
        dry_run: true,
        operator_mode: false
      });
      if (receipt.success !== false && draftableNodeIds.has(source) && draftableNodeIds.has(target)) {
        const resolvedHandles = completeEdgeHandles(source, target, nodePositions, handles);
        setPreviewEdges((rows) => [
          ...rows,
          {
            id: `${makeDraftId("edge")}:${source}:${target}`,
            source,
            target,
            sourceHandle: resolvedHandles.sourceHandle,
            targetHandle: resolvedHandles.targetHandle,
            label: edgeKind,
            className: reason === "edge_retarget" || reason === "edge_reconnect" ? "preview-edge retarget-edge" : "preview-edge",
            animated: true,
            reconnectable: true,
            type: "smoothstep",
            style: { strokeWidth: 3 },
            data: {
              source: {
                kind: edgeKind,
                strength: Number(edgeStrength) || 0.5,
                reason,
                preview: true,
                ...meta,
                source_handle: resolvedHandles.sourceHandle,
                target_handle: resolvedHandles.targetHandle
              }
            }
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
    void draftEdgeBetween(source, target, "canvas_connect", {}, {
      sourceHandle: connection.sourceHandle || undefined,
      targetHandle: connection.targetHandle || undefined
    });
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
      source_handle: formatHandleSide(connection.sourceHandle) || formatHandleSide(oldEdge.sourceHandle),
      target_handle: formatHandleSide(connection.targetHandle) || formatHandleSide(oldEdge.targetHandle),
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
    }, {
      sourceHandle: connection.sourceHandle || oldEdge.sourceHandle || undefined,
      targetHandle: connection.targetHandle || oldEdge.targetHandle || undefined
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

  const updateSelectedEdgeDraft = async () => {
    const source = edgeFrom.trim();
    const target = edgeTo.trim();
    if (!source || !target) {
      pushReceipt(localReceipt("l2b.edge.update", false, { error: "missing_endpoint" }));
      return;
    }
    try {
      pushReceipt(await api.l2bEdgeUpdate({
        from_uuid: source,
        to_uuid: target,
        kind: edgeKind,
        strength: Number(edgeStrength) || 0.5,
        meta: edgeMetaPayload("edge_update"),
        match_kind: isSelectedEdge(selected) ? String(selected.kind || "") : "",
        match_source: isSelectedEdge(selected) ? String(selected.edge_source || selected.source_tool || "") : "",
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.edge.update", exc, { from_uuid: source, to_uuid: target }));
    }
  };

  const deleteSelectedEdgeDraft = async () => {
    const source = edgeFrom.trim();
    const target = edgeTo.trim();
    if (!source || !target) {
      pushReceipt(localReceipt("l2b.edge.delete", false, { error: "missing_endpoint" }));
      return;
    }
    if (selectedEdgeId && previewEdges.some((edge) => edge.id === selectedEdgeId)) {
      setPreviewEdges((rows) => rows.filter((edge) => edge.id !== selectedEdgeId));
    }
    try {
      pushReceipt(await api.l2bEdgeDelete({
        from_uuid: source,
        to_uuid: target,
        match_kind: isSelectedEdge(selected) ? String(selected.kind || "") : "",
        match_source: isSelectedEdge(selected) ? String(selected.edge_source || selected.source_tool || "") : "",
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.edge.delete", exc, { from_uuid: source, to_uuid: target }));
    }
  };

  const deleteSelectedNodeDraft = async () => {
    const uuid = selectedNodeId;
    if (!uuid) {
      pushReceipt(localReceipt("l2b.node.delete", false, { error: "missing_node_uuid" }));
      return;
    }
    if (previewNodes.some((row) => String(row.uuid) === uuid)) {
      setPreviewNodes((rows) => rows.filter((row) => String(row.uuid) !== uuid));
      setPreviewEdges((rows) => rows.filter((edge) => edge.source !== uuid && edge.target !== uuid));
      setSelected(null);
    }
    try {
      pushReceipt(await api.l2bNodeDelete({ node_uuid: uuid, dry_run: true, operator_mode: false }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.node.delete", exc, { node_uuid: uuid }));
    }
  };

  const policyNodeSelection = () => uniqueStrings([
    selectedNodeId,
    edgeFrom,
    edgeTo
  ]).filter((id) => visibleNodeIds.has(id)).slice(0, 24);

  const selectedRefIds = () => selectedNodeRefs
    .map((row) => row.ref_id || row.id)
    .filter(Boolean)
    .slice(0, 24);

  const draftImportPolicy = async () => {
    const node_uuids = policyNodeSelection();
    try {
      pushReceipt(await api.l2bGraphImportDraft({
        destination: graphDestination,
        source_kind: "memory_canvas",
        source_id: selectedNodeId || selectedEdgeId || "current_view",
        workspace_id: "memory_graph",
        subgraph_label: subgraphLabel,
        node_uuids,
        ref_ids: selectedRefIds(),
        proposed_edges: edgeFrom && edgeTo && edgeFrom !== edgeTo
          ? [{ source: edgeFrom, target: edgeTo, kind: edgeKind, strength: Number(edgeStrength) || 0.5 }]
          : [],
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.graph_policy.import_draft", exc, { destination: graphDestination }));
    }
  };

  const createSubgraphPreview = async () => {
    const label = subgraphLabel.trim() || "Work subgraph";
    const uuid = makeDraftId("subgraph");
    const nodeSelection = policyNodeSelection();
    const nodeSource = {
      uuid,
      label,
      kind: "subgraph",
      preview: true,
      draftable: false,
      description: "Visual grouping box. Backend overlay persistence is a later operator-gated route.",
      tags: ["subgraph", "view"]
    };
    try {
      const receipt = await api.l2bSubgraphDraft({
        subgraph_id: uuid,
        label,
        node_uuids: nodeSelection,
        ref_ids: selectedRefIds(),
        source_kind: "memory_canvas",
        dry_run: true,
        operator_mode: false
      });
      if (receipt.success !== false) {
        setPreviewNodes((rows) => [...rows, nodeSource]);
        setManualPositions((current) => ({ ...current, [uuid]: { x: 220, y: 180 } }));
        setSelected({ selection_type: "node", ...nodeSource });
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.subgraph.draft", exc, { label }));
    }
  };

  const draftGraphTransform = async () => {
    try {
      pushReceipt(await api.l2bTransformDraft({
        transform_kind: graphTransformKind,
        node_uuids: policyNodeSelection(),
        subgraph_ids: selectedNodeId && String(selected?.kind || "") === "subgraph" ? [selectedNodeId] : [],
        label: subgraphLabel,
        proposed_edges: edgeFrom && edgeTo && edgeFrom !== edgeTo
          ? [{ source: edgeFrom, target: edgeTo, kind: edgeKind, strength: Number(edgeStrength) || 0.5 }]
          : [],
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.transform.draft", exc, { transform_kind: graphTransformKind }));
    }
  };

  const refreshGraphHealth = async () => {
    try {
      const health = await api.l2bGraphHealth();
      setGraphHealth(health);
      pushReceipt(localReceipt("l2b.analysis.health", true, { health }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.analysis.health", exc));
    }
  };

  const draftTagForSelection = () => {
    if (!selected) {
      pushReceipt(localReceipt("l2b.tag.draft", false, { error: "no_selection" }));
      return;
    }
    pushReceipt(localReceipt("l2b.tag.draft", true, {
      target: selectedNodeId || selectedEdgeId,
      selection_type: String(selected.selection_type || ""),
      tags: parseTags(tagText),
      note: "UI-only draft until Node/Edge tag mutation policy is promoted."
    }));
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
      <div className="metric-row compact">
        <Metric label={t.nodes} value={String(liveState.l2b?.node_count ?? 0)} />
        <Metric label={t.edges} value={String(liveState.l2b?.edge_count ?? 0)} />
        <Metric label={t.blackboard} value={`${liveState.blackboard?.present_count ?? 0}/${liveState.blackboard?.declared_count ?? 0}`} />
        <Metric label={t.intent} value={String(liveState.intent_workspace?.ref_count ?? 0)} />
      </div>

      <div className="canvas-panel">
        <div className="canvas-toolbar icon-toolbar">
          <IconToolButton active={activeTool === "node"} label={t.createNode} onClick={() => setActiveTool(activeTool === "node" ? null : "node")}><Plus size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "edge"} label={t.draftEdge} onClick={() => setActiveTool(activeTool === "edge" ? null : "edge")}><GitBranch size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "subgraph"} label={t.subgraph} onClick={() => setActiveTool(activeTool === "subgraph" ? null : "subgraph")}><Layers size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "filter"} label={t.filters} onClick={() => setActiveTool(activeTool === "filter" ? null : "filter")}><Filter size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "tags"} label={t.tags} onClick={() => setActiveTool(activeTool === "tags" ? null : "tags")}><Tags size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "state"} label={t.stateView} onClick={() => setActiveTool(activeTool === "state" ? null : "state")}><Activity size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "pool"} label={t.l15} onClick={() => setActiveTool(activeTool === "pool" ? null : "pool")}><Database size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "settings"} label={t.settings} onClick={() => setActiveTool(activeTool === "settings" ? null : "settings")}><Settings size={18} /></IconToolButton>
          <span className="tool-divider" />
          <IconToolButton label={t.focusSelection} onClick={focusSelection}><CircleDot size={18} /></IconToolButton>
          <IconToolButton label={t.layoutGraph} onClick={layoutGraph}><Workflow size={18} /></IconToolButton>
          <IconToolButton label={t.clear} danger onClick={clearPreview}><Trash2 size={18} /></IconToolButton>
        </div>

        {activeTool ? (
          <div className="tool-dock">
            <MemoryToolPanel
              activeTool={activeTool}
              liveState={liveState}
              t={t}
              nodeLabel={nodeLabel}
              setNodeLabel={setNodeLabel}
              nodeKind={nodeKind}
              setNodeKind={setNodeKind}
              edgeFrom={edgeFrom}
              setEdgeFrom={setEdgeFrom}
              edgeTo={edgeTo}
              setEdgeTo={setEdgeTo}
              edgeKind={edgeKind}
              setEdgeKind={setEdgeKind}
              edgeStrength={edgeStrength}
              setEdgeStrength={setEdgeStrength}
              edgeMetaText={edgeMetaText}
              setEdgeMetaText={setEdgeMetaText}
              tagText={tagText}
              setTagText={setTagText}
              filterKind={filterKind}
              setFilterKind={setFilterKind}
              stateColors={stateColors}
              setStateColors={setStateColors}
              subgraphLabel={subgraphLabel}
              setSubgraphLabel={setSubgraphLabel}
              graphDestination={graphDestination}
              setGraphDestination={setGraphDestination}
              graphTransformKind={graphTransformKind}
              setGraphTransformKind={setGraphTransformKind}
              graphHealth={graphHealth}
              onDraftNode={() => void draftNode()}
              onDraftEdge={() => void draftEdgeBetween(edgeFrom, edgeTo, "toolbar")}
              onUpdateEdge={() => void updateSelectedEdgeDraft()}
              onDeleteEdge={() => void deleteSelectedEdgeDraft()}
              onDraftImportPolicy={() => void draftImportPolicy()}
              onCreateSubgraph={() => void createSubgraphPreview()}
              onDraftTransform={() => void draftGraphTransform()}
              onRefreshHealth={() => void refreshGraphHealth()}
              onDraftTag={draftTagForSelection}
              poolHealth={poolHealth}
              buckets={buckets}
              maxBucketCount={maxBucketCount}
              pushReceipt={pushReceipt}
              onGraphitiPreview={stageGraphitiPreview}
            />
          </div>
        ) : null}

        {selected ? (
          <SelectionInspector
            selected={selected}
            selectedNodeId={selectedNodeId}
            selectedEdgeId={selectedEdgeId}
            relatedRefs={selectedNodeRefs}
            edgeFrom={edgeFrom}
            edgeTo={edgeTo}
            t={t}
            onUseEdgeEndpoints={() => {
              if (isSelectedEdge(selected)) {
                setEdgeFrom(String(selected.source || ""));
                setEdgeTo(String(selected.target || ""));
                setActiveTool("edge");
              }
            }}
            onDeleteNode={() => void deleteSelectedNodeDraft()}
            onUpdateEdge={() => void updateSelectedEdgeDraft()}
            onDeleteEdge={() => void deleteSelectedEdgeDraft()}
            onSwapEdge={swapSelectedEdgeEndpoints}
            onClose={() => setSelected(null)}
          />
        ) : null}

        <div className="canvas-help-chip">
          <GitBranch size={14} />
          <span>{t.connectHint}</span>
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
          <MiniMap
            pannable
            zoomable
            nodeColor={(node) => (node.selected ? "#7bd99f" : node.className?.includes("preview") ? "#5f8f6a" : "#3a4250")}
            maskColor="rgba(15, 17, 22, 0.72)"
          />
          <Controls />
          <Background />
        </ReactFlow>
        {!l2bNodes.length && !previewNodes.length ? <EmptyL2BHint liveState={liveState} t={t} /> : null}
      </div>
    </section>
  );
}

function IconToolButton({
  active = false,
  danger = false,
  label,
  onClick,
  children
}: {
  active?: boolean;
  danger?: boolean;
  label: string;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      className={`icon-tool${active ? " active" : ""}${danger ? " danger" : ""}`}
      data-tooltip={label}
      title={label}
      aria-label={label}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

function MemoryToolPanel({
  activeTool,
  liveState,
  t,
  nodeLabel,
  setNodeLabel,
  nodeKind,
  setNodeKind,
  edgeFrom,
  setEdgeFrom,
  edgeTo,
  setEdgeTo,
  edgeKind,
  setEdgeKind,
  edgeStrength,
  setEdgeStrength,
  edgeMetaText,
  setEdgeMetaText,
  tagText,
  setTagText,
  filterKind,
  setFilterKind,
  stateColors,
  setStateColors,
  subgraphLabel,
  setSubgraphLabel,
  graphDestination,
  setGraphDestination,
  graphTransformKind,
  setGraphTransformKind,
  graphHealth,
  onDraftNode,
  onDraftEdge,
  onUpdateEdge,
  onDeleteEdge,
  onDraftImportPolicy,
  onCreateSubgraph,
  onDraftTransform,
  onRefreshHealth,
  onDraftTag,
  poolHealth,
  buckets,
  maxBucketCount,
  pushReceipt,
  onGraphitiPreview
}: {
  activeTool: MemoryToolId;
  liveState: LiveState;
  t: ConsoleCopy;
  nodeLabel: string;
  setNodeLabel: (value: string) => void;
  nodeKind: string;
  setNodeKind: (value: string) => void;
  edgeFrom: string;
  setEdgeFrom: (value: string) => void;
  edgeTo: string;
  setEdgeTo: (value: string) => void;
  edgeKind: string;
  setEdgeKind: (value: string) => void;
  edgeStrength: string;
  setEdgeStrength: (value: string) => void;
  edgeMetaText: string;
  setEdgeMetaText: (value: string) => void;
  tagText: string;
  setTagText: (value: string) => void;
  filterKind: string;
  setFilterKind: (value: string) => void;
  stateColors: boolean;
  setStateColors: (value: boolean) => void;
  subgraphLabel: string;
  setSubgraphLabel: (value: string) => void;
  graphDestination: string;
  setGraphDestination: (value: string) => void;
  graphTransformKind: string;
  setGraphTransformKind: (value: string) => void;
  graphHealth: Record<string, unknown> | null;
  onDraftNode: () => void;
  onDraftEdge: () => void;
  onUpdateEdge: () => void;
  onDeleteEdge: () => void;
  onDraftImportPolicy: () => void;
  onCreateSubgraph: () => void;
  onDraftTransform: () => void;
  onRefreshHealth: () => void;
  onDraftTag: () => void;
  poolHealth: Record<string, unknown>;
  buckets: Array<Record<string, unknown>>;
  maxBucketCount: number;
  pushReceipt: (receipt: Receipt | null) => void;
  onGraphitiPreview: (preview: GraphitiPreviewPayload) => void;
}) {
  if (activeTool === "node") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Plus size={16} />} title={t.createNode} />
        <label><span>{t.nodeLabel}</span><input value={nodeLabel} onChange={(event) => setNodeLabel(event.target.value)} /></label>
        <label><span>{t.nodeKind}</span><select value={nodeKind} onChange={(event) => setNodeKind(event.target.value)}>{NODE_KIND_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
        <button className="button primary" onClick={onDraftNode}><Plus size={16} /> {t.createNode}</button>
      </section>
    );
  }
  if (activeTool === "edge") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<GitBranch size={16} />} title={t.draftEdge} />
        <div className="two-field-grid">
          <label><span>{t.fromUuid}</span><input value={edgeFrom} onChange={(event) => setEdgeFrom(event.target.value)} /></label>
          <label><span>{t.toUuid}</span><input value={edgeTo} onChange={(event) => setEdgeTo(event.target.value)} /></label>
        </div>
        <div className="two-field-grid">
          <label><span>{t.edgeKind}</span><select value={edgeKind} onChange={(event) => setEdgeKind(event.target.value)}>{EDGE_KIND_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
          <label><span>{t.edgeStrength}</span><input value={edgeStrength} onChange={(event) => setEdgeStrength(event.target.value)} inputMode="decimal" /></label>
        </div>
        <label><span>{t.edgeMeta}</span><textarea value={edgeMetaText} onChange={(event) => setEdgeMetaText(event.target.value)} rows={4} /></label>
        <div className="button-row">
          <button className="button primary" onClick={onDraftEdge}><Link2 size={16} /> {t.draftEdge}</button>
          <button className="button" onClick={onUpdateEdge}><Pencil size={16} /> {t.updateEdge}</button>
          <button className="button danger" onClick={onDeleteEdge}><Trash2 size={16} /> {t.deleteEdge}</button>
        </div>
      </section>
    );
  }
  if (activeTool === "subgraph") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Layers size={16} />} title={t.subgraph} />
        <label><span>{t.nodeLabel}</span><input value={subgraphLabel} onChange={(event) => setSubgraphLabel(event.target.value)} /></label>
        <label>
          <span>{t.importDestination}</span>
          <select value={graphDestination} onChange={(event) => setGraphDestination(event.target.value)}>
            {GRAPH_IMPORT_DESTINATIONS.map((destination) => <option key={destination} value={destination}>{destination}</option>)}
          </select>
        </label>
        <label>
          <span>{t.graphTransform}</span>
          <select value={graphTransformKind} onChange={(event) => setGraphTransformKind(event.target.value)}>
            {GRAPH_TRANSFORM_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}
          </select>
        </label>
        <div className="button-row">
          <button className="button" onClick={onDraftImportPolicy}><Workflow size={16} /> {t.previewPolicy}</button>
          <button className="button primary" onClick={onCreateSubgraph}><Layers size={16} /> {t.overlayDraft}</button>
          <button className="button" onClick={onDraftTransform}><Activity size={16} /> {t.previewTransform}</button>
        </div>
      </section>
    );
  }
  if (activeTool === "filter") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Filter size={16} />} title={t.filters} />
        <label><span>{t.nodeKind}</span><select value={filterKind} onChange={(event) => setFilterKind(event.target.value)}><option value="all">all</option>{NODE_KIND_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
      </section>
    );
  }
  if (activeTool === "tags") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Tags size={16} />} title={t.tags} />
        <label><span>{t.tags}</span><input value={tagText} onChange={(event) => setTagText(event.target.value)} placeholder="tag-a, tag-b" /></label>
        <button className="button" onClick={onDraftTag}><Tags size={16} /> {t.addTagDraft}</button>
      </section>
    );
  }
  if (activeTool === "state") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Activity size={16} />} title={t.stateView} />
        <label className="toggle-row">
          <input type="checkbox" checked={stateColors} onChange={(event) => setStateColors(event.target.checked)} />
          <span>{t.statusColors}</span>
        </label>
        <div className="state-legend">
          <span className="legend-dot confirmed" /> confirmed
          <span className="legend-dot tentative" /> tentative/expected
          <span className="legend-dot alert" /> alert
        </div>
        <div className="graph-health-card">
          <div className="graph-health-head">
            <strong>{t.graphHealth}</strong>
            <button className="button small" onClick={onRefreshHealth}><RefreshCw size={14} /> {t.refreshHealth}</button>
          </div>
          {graphHealth ? <GraphHealthSummary health={graphHealth} /> : <p className="source-card-note">Read-only CORE-013 health preset.</p>}
        </div>
      </section>
    );
  }
  if (activeTool === "pool") {
    return (
      <section className="tool-panel pool-panel">
        <ToolPanelHead icon={<Database size={16} />} title={t.l15} />
        <L15HealthPanel health={poolHealth} t={t} />
        <SourceBoard liveState={liveState} pushReceipt={pushReceipt} t={t} onGraphitiPreview={onGraphitiPreview} />
        <div className="bucket-board compact">
          {buckets.map((bucket) => (
            <BucketCard key={String(bucket.kind)} bucket={bucket} maxNodeCount={maxBucketCount} pushReceipt={pushReceipt} t={t} />
          ))}
        </div>
      </section>
    );
  }
  return (
    <section className="tool-panel">
      <ToolPanelHead icon={<Settings size={16} />} title={t.settings} />
      <p className="source-card-note">{t.connectHint}</p>
      <p className="source-card-note">RustWorkX stores topology; Node/Edge kind, status, tags and meta stay in payloads for flexible visual mapping.</p>
    </section>
  );
}

function ToolPanelHead({ icon, title }: { icon: ReactNode; title: string }) {
  return (
    <div className="tool-panel-head">
      <strong>{icon}{title}</strong>
    </div>
  );
}

function SelectionInspector({
  selected,
  selectedNodeId,
  selectedEdgeId,
  relatedRefs,
  edgeFrom,
  edgeTo,
  t,
  onUseEdgeEndpoints,
  onDeleteNode,
  onUpdateEdge,
  onDeleteEdge,
  onSwapEdge,
  onClose
}: {
  selected: Record<string, unknown>;
  selectedNodeId: string;
  selectedEdgeId: string;
  relatedRefs: Array<Record<string, string>>;
  edgeFrom: string;
  edgeTo: string;
  t: ConsoleCopy;
  onUseEdgeEndpoints: () => void;
  onDeleteNode: () => void;
  onUpdateEdge: () => void;
  onDeleteEdge: () => void;
  onSwapEdge: () => void;
  onClose: () => void;
}) {
  const isEdge = String(selected.selection_type || "") === "edge";
  const title = isEdge ? t.selectedEdge : t.selectedNode;
  const kind = String(selected.kind || (isEdge ? "edge" : "node"));
  const tags = Array.isArray(selected.tags) ? selected.tags.map(String) : [];
  const selectedMeta = recordFromUnknown(selected.meta);
  const nodeAssetPath = !isEdge
    ? String(selected.reference_image_path || selected.asset_ref || selectedMeta.asset_ref || selectedMeta.asset_path || "")
    : "";
  const nodeAssetUrl = photoAssetPreviewUrl(nodeAssetPath);
  const nodeEpisodeRef = !isEdge
    ? String(selected.episode_ref || selectedMeta.episode_ref || "")
    : "";
  const hasRefOrPhotoDetails = !isEdge && (relatedRefs.length > 0 || Boolean(nodeAssetPath) || Boolean(nodeEpisodeRef));
  return (
    <aside className="selection-float">
      <div className="selection-head">
        <strong>{isEdge ? <GitBranch size={16} /> : <CircleDot size={16} />} {title}</strong>
        <button className="icon-tool tiny" data-tooltip={t.clearSelection} title={t.clearSelection} onClick={onClose}>x</button>
      </div>
      <div className="selection-title">{String(selected.label || selected.id || selectedNodeId || selectedEdgeId || kind)}</div>
      <div className="detail-grid">
        <span>kind</span><strong>{kind}</strong>
        {isEdge ? (
          <>
            <span>{t.fromUuid}</span><strong>{edgeFrom || String(selected.source || "-")}</strong>
            <span>{t.toUuid}</span><strong>{edgeTo || String(selected.target || "-")}</strong>
            <span>{t.edgeStrength}</span><strong>{String(selected.strength ?? "-")}</strong>
            <span>source</span><strong>{String(selected.edge_source || selected.source_tool || "-")}</strong>
          </>
        ) : (
          <>
            <span>status</span><strong>{String(selected.confirmation || "-")}</strong>
            <span>salience</span><strong>{String(selected.salience || "-")}</strong>
            <span>bucket</span><strong>{String(selected.bucket_id || "-")}</strong>
            <span>source</span><strong>{String(selected.source || "-")}</strong>
          </>
        )}
      </div>
      {tags.length ? <div className="tag-row">{tags.map((tag) => <span key={tag}>{tag}</span>)}</div> : null}
      {hasRefOrPhotoDetails ? (
        <div className="ref-link-panel">
          <strong><Link2 size={14} /> Refs / Photos</strong>
          {nodeAssetPath ? (
            <div className="ref-link-row">
              {nodeAssetUrl ? <img className="photo-preview-thumb" src={nodeAssetUrl} alt="Photo asset preview" loading="lazy" /> : null}
              <span>Photo asset</span>
              <small>{nodeAssetPath}</small>
            </div>
          ) : null}
          {nodeEpisodeRef ? (
            <div className="ref-link-row">
              <span>Episode</span>
              <small>{nodeEpisodeRef}</small>
            </div>
          ) : null}
          {relatedRefs.slice(0, 6).map((row) => (
            <div className="ref-link-row" key={row.id}>
              {row.url ? <img className="photo-preview-thumb small" src={row.url} alt="" loading="lazy" /> : null}
              <span>{row.label}</span>
              <small>{row.kind} / {row.source}</small>
              {row.path ? <small>{row.path}</small> : null}
            </div>
          ))}
        </div>
      ) : null}
      <details className="record-details">
        <summary>{t.recordDetails}</summary>
        <JsonBlock value={selected} />
      </details>
      <div className="button-row">
        {isEdge ? (
          <>
            <button className="button small" onClick={onUseEdgeEndpoints}>{t.useAsEndpoints}</button>
            <button className="button small ghost" onClick={onSwapEdge}>{t.swapEdge}</button>
            <button className="button small" onClick={onUpdateEdge}>{t.updateEdge}</button>
            <button className="button small danger" onClick={onDeleteEdge}>{t.deleteEdge}</button>
          </>
        ) : (
          <button className="button small danger" onClick={onDeleteNode}>{t.deleteNode}</button>
        )}
      </div>
    </aside>
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
  const [evidenceRefreshSeq, setEvidenceRefreshSeq] = useState(0);
  const pokeEvidenceRefresh = useCallback(() => {
    setEvidenceRefreshSeq((value) => value + 1);
  }, []);
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

      <LiveKitBridgePanel pushReceipt={pushReceipt} t={t} onEvidenceRefresh={pokeEvidenceRefresh} />

      <VisionEvidencePanel pushReceipt={pushReceipt} t={t} refreshSignal={evidenceRefreshSeq} />

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

function LiveKitBridgePanel({
  pushReceipt,
  t,
  onEvidenceRefresh
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onEvidenceRefresh: () => void;
}) {
  const [config, setConfig] = useState<LiveKitConfig>({});
  const [roomId, setRoomId] = useState("parrot-main");
  const [identity, setIdentity] = useState(`web-console-${Date.now()}`);
  const [tokenPayload, setTokenPayload] = useState<LiveKitToken | null>(null);
  const [connected, setConnected] = useState(false);
  const [micEnabled, setMicEnabled] = useState(false);
  const [screenSharing, setScreenSharing] = useState(false);
  const [status, setStatus] = useState("idle");
  const [events, setEvents] = useState<LiveKitEventRow[]>([]);
  const [transcripts, setTranscripts] = useState<LiveKitEventRow[]>([]);
  const roomRef = useRef<any>(null);
  const screenTrackRef = useRef<MediaStreamTrack | null>(null);
  const remoteAudioElsRef = useRef<Map<string, HTMLMediaElement>>(new Map());

  const pushEvent = useCallback((label: string, detail = "", state: LiveKitEventStatus = "idle") => {
    setEvents((rows) => [{
      at: new Date().toLocaleTimeString(),
      label,
      detail,
      status: state
    }, ...rows].slice(0, 12));
  }, []);

  useEffect(() => {
    let cancelled = false;
    api.livekitConfig()
      .then((nextConfig) => {
        if (cancelled) return;
        setConfig(nextConfig);
        setRoomId(nextConfig.room || "parrot-main");
        const prefix = nextConfig.web_identity_prefix || "web-console";
        setIdentity((current) => current || `${prefix}-${Date.now()}`);
      })
      .catch((exc) => {
        if (cancelled) return;
        setStatus(exc instanceof Error ? exc.message : String(exc));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const mintToken = useCallback(async (quiet = false): Promise<LiveKitToken> => {
    const payload = await api.livekitWebToken({ room: roomId, identity });
    setTokenPayload(payload);
    setStatus(`token ready: ${payload.identity}`);
    pushEvent("token", `${payload.room} / ${payload.identity}`, "good");
    if (!quiet) {
      pushReceipt(localReceipt("livekit.web_token", true, {
        room: payload.room,
        identity: payload.identity,
        url: payload.url,
        expires_at: payload.expires_at,
        token_length: payload.token.length
      }));
    }
    return payload;
  }, [identity, pushEvent, pushReceipt, roomId]);

  const ensureToken = useCallback(async (): Promise<LiveKitToken> => {
    const expiresSoon = !tokenPayload || tokenPayload.expires_at < Math.floor(Date.now() / 1000) + 30;
    const wrongRoom = tokenPayload?.room !== roomId || tokenPayload?.identity !== identity;
    return expiresSoon || wrongRoom ? mintToken(true) : tokenPayload;
  }, [identity, mintToken, roomId, tokenPayload]);

  const cleanupRemoteAudio = useCallback(() => {
    for (const element of remoteAudioElsRef.current.values()) {
      element.remove();
    }
    remoteAudioElsRef.current.clear();
  }, []);

  const disconnect = useCallback(() => {
    stopMediaTrack(screenTrackRef.current);
    screenTrackRef.current = null;
    setScreenSharing(false);
    setMicEnabled(false);
    cleanupRemoteAudio();
    const room = roomRef.current;
    roomRef.current = null;
    if (room) {
      room.disconnect?.();
    }
    setConnected(false);
    setStatus("disconnected");
    pushEvent("disconnect", "", "idle");
  }, [cleanupRemoteAudio, pushEvent]);

  useEffect(() => disconnect, [disconnect]);

  const connect = useCallback(async () => {
    if (roomRef.current) return;
    try {
      setStatus("connecting");
      const [client, session] = await Promise.all([loadLiveKitClient(), ensureToken()]);
      const room = new client.Room({ adaptiveStream: false, dynacast: false });
      roomRef.current = room;
      bindLiveKitRoomEvents({
        room,
        RoomEvent: client.RoomEvent,
        Track: client.Track,
        onEvent: pushEvent,
        onTranscript: (text, detail) => {
          setTranscripts((rows) => [{
            at: new Date().toLocaleTimeString(),
            label: text,
            detail,
            status: "good" as const
          }, ...rows].slice(0, 12));
        },
        onRemoteAudio: (track, participant) => {
          attachRemoteAudio(track, participant, remoteAudioElsRef.current);
        },
        onRemoteAudioDetached: (track) => {
          detachRemoteAudio(track, remoteAudioElsRef.current);
        },
        onDisconnected: (reason) => {
          cleanupRemoteAudio();
          roomRef.current = null;
          screenTrackRef.current = null;
          setConnected(false);
          setMicEnabled(false);
          setScreenSharing(false);
          setStatus(`disconnected${reason ? `: ${reason}` : ""}`);
        },
        onState: setStatus
      });
      await room.connect(session.url, session.token, { autoSubscribe: true });
      if (typeof room.startAudio === "function") await room.startAudio();
      setConnected(true);
      setStatus(`connected: ${session.identity}`);
      pushEvent("connected", session.identity, "good");
      pushReceipt(localReceipt("livekit.web_connect", true, {
        room: session.room,
        identity: session.identity,
        url: session.url,
        screen_share_supported: Boolean(navigator.mediaDevices?.getDisplayMedia)
      }));
    } catch (exc) {
      const message = exc instanceof Error ? exc.message : String(exc);
      setStatus(message);
      pushEvent("error", message, "bad");
      pushReceipt(errorReceipt("livekit.web_connect", exc, { room: roomId, identity }));
      disconnect();
    }
  }, [cleanupRemoteAudio, disconnect, ensureToken, identity, pushEvent, pushReceipt, roomId]);

  const toggleMic = useCallback(async () => {
    const room = roomRef.current;
    if (!room) return;
    try {
      const next = !micEnabled;
      await room.localParticipant?.setMicrophoneEnabled?.(next);
      setMicEnabled(next);
      pushEvent(next ? "mic_on" : "mic_off", "", next ? "good" : "idle");
    } catch (exc) {
      pushEvent("mic_error", exc instanceof Error ? exc.message : String(exc), "bad");
      pushReceipt(errorReceipt("livekit.microphone", exc));
    }
  }, [micEnabled, pushEvent, pushReceipt]);

  const stopScreenShare = useCallback(async () => {
    const track = screenTrackRef.current;
    if (!track) return;
    screenTrackRef.current = null;
    try {
      await roomRef.current?.localParticipant?.unpublishTrack?.(track, true);
    } catch {
      // Older livekit-client builds may not expose unpublishTrack for raw tracks.
    }
    stopMediaTrack(track);
    setScreenSharing(false);
    pushEvent("screen_share_stop", "", "idle");
  }, [pushEvent]);

  const shareScreen = useCallback(async () => {
    const room = roomRef.current;
    if (!room) return;
    if (!navigator.mediaDevices?.getDisplayMedia) {
      pushEvent("screen_share_error", "getDisplayMedia unavailable", "bad");
      return;
    }
    try {
      const client = await loadLiveKitClient();
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: 5 },
        audio: false
      });
      const track = stream.getVideoTracks()[0];
      if (!track) throw new Error("screen_track_missing");
      screenTrackRef.current = track;
      track.addEventListener("ended", () => {
        void stopScreenShare();
      }, { once: true });
      await room.localParticipant?.publishTrack?.(track, {
        source: client.Track?.Source?.ScreenShare,
        name: "web-console-screen"
      });
      setScreenSharing(true);
      pushEvent("screen_share_start", track.label || "screen", "good");
      pushReceipt(localReceipt("livekit.screen_share", true, {
        room: roomId,
        identity,
        track_label: track.label || "screen",
        note: "Brain sampler should see this as a screenshare video track if Brain is in the same room."
      }));
      onEvidenceRefresh();
    } catch (exc) {
      pushEvent("screen_share_error", exc instanceof Error ? exc.message : String(exc), "bad");
      pushReceipt(errorReceipt("livekit.screen_share", exc));
      await stopScreenShare();
    }
  }, [identity, onEvidenceRefresh, pushEvent, pushReceipt, roomId, stopScreenShare]);

  const checkSamples = useCallback(async () => {
    try {
      const checkTimeMs = Date.now();
      const [evidenceStatus, nearest] = await Promise.all([
        api.visionEvidenceStatus(),
        api.visionEvidenceRequest({
          description: "Web checked nearest screen-share evidence.",
          target_time_ms: checkTimeMs,
          require_asset: true,
          window_ms: 15_000
        })
      ]);
      const nearestRecord = nearest as Record<string, unknown>;
      const nearestEvidence = nearestRecord.evidence as Record<string, unknown> | undefined;
      const sampler = evidenceStatus.livekit_sampler ?? {};
      const frameCache = evidenceStatus.frame_cache ?? {};
      const latest = sampler.latest_frame ?? frameCache.latest_frame ?? nearestEvidence ?? null;
      const likelyScreenShare = evidenceLooksScreenShare(nearestEvidence)
        || evidenceLooksScreenShare(latest)
        || Object.values(sampler.tracks ?? {}).some(evidenceLooksScreenShare)
        || Object.values(frameCache.tracks ?? {}).some(evidenceLooksScreenShare);
      const hasAnyFreshEvidence = Boolean(
        sampler.latest_frame_fresh
        || frameCache.latest_frame_fresh
        || nearest.success
      );
      const screenShareConfirmed = hasAnyFreshEvidence && likelyScreenShare;
      pushEvent(
        "sample_check",
        `${hasAnyFreshEvidence ? "fresh" : "stale"} / ${likelyScreenShare ? "screen" : "not-screen"} / ${sampler.recorded_frames ?? 0}f`,
        screenShareConfirmed ? "good" : "warn"
      );
      pushReceipt(localReceipt("livekit.screen_share.evidence_check", screenShareConfirmed, {
        sampler_available: Boolean(sampler.available),
        sampler_fresh: Boolean(sampler.latest_frame_fresh),
        sampler_age_ms: sampler.latest_frame_age_ms ?? null,
        sampler_active_tracks: Array.isArray(sampler.active_tracks) ? sampler.active_tracks.length : 0,
        sampler_recorded_frames: sampler.recorded_frames ?? 0,
        frame_cache_fresh: Boolean(frameCache.latest_frame_fresh),
        frame_cache_age_ms: frameCache.latest_frame_age_ms ?? null,
        frame_count: frameCache.frame_count ?? 0,
        fresh_any_evidence: hasAnyFreshEvidence,
        screen_share_confirmed: screenShareConfirmed,
        likely_screen_share: likelyScreenShare,
        nearest_evidence_found: Boolean(nearest.success),
        nearest_evidence_id: String(nearestEvidence?.evidence_id || ""),
        message: String(nearestRecord.message || nearest.action || "")
      }));
    } catch (exc) {
      pushEvent("sample_check_error", exc instanceof Error ? exc.message : String(exc), "bad");
      pushReceipt(errorReceipt("livekit.screen_share.evidence_check", exc));
    } finally {
      onEvidenceRefresh();
    }
  }, [onEvidenceRefresh, pushEvent, pushReceipt]);

  return (
    <section className="livekit-bridge action-palette">
      <div className="palette-title">
        <strong><Activity size={17} /> {t.liveKitBridge}</strong>
        <span className={connected ? "fresh-state" : "stale-state"}>
          {status}
        </span>
      </div>
      <div className="livekit-bridge-grid">
        <label>
          <span>{t.liveKitRoom}</span>
          <input value={roomId} onChange={(event) => setRoomId(event.target.value)} disabled={connected} />
        </label>
        <label>
          <span>{t.liveKitIdentity}</span>
          <input value={identity} onChange={(event) => setIdentity(event.target.value)} disabled={connected} />
        </label>
        <p className="muted">{t.liveKitBridgeHint}</p>
        <p className="muted">{config.url || "LiveKit URL unavailable"}</p>
      </div>
      <div className="button-row">
        <button className="button small" disabled={connected} onClick={() => void mintToken(false)}>
          {t.mintToken}
        </button>
        <button className="button small primary" disabled={connected} onClick={() => void connect()}>
          {t.connectRoom}
        </button>
        <button className="button small" disabled={!connected} onClick={() => void toggleMic()}>
          {micEnabled ? t.disableMic : t.enableMic}
        </button>
        <button className="button small" disabled={!connected || screenSharing} onClick={() => void shareScreen()}>
          {t.shareScreen}
        </button>
        <button className="button small" disabled={!screenSharing} onClick={() => void stopScreenShare()}>
          {t.stopShare}
        </button>
        <button className="button small" onClick={() => void checkSamples()}>
          <Search size={15} /> {t.checkSamples}
        </button>
        <button className="button small danger" disabled={!connected} onClick={disconnect}>
          {t.disconnectRoom}
        </button>
      </div>
      <div className="livekit-stream-grid">
        <div className="livekit-log">
          <strong>{t.liveKitEvents}</strong>
          {events.length ? events.map((event, index) => (
            <div className={`livekit-row ${event.status}`} key={`${event.at}-${index}`}>
              <span>{event.at}</span>
              <b>{event.label}</b>
              <small>{event.detail}</small>
            </div>
          )) : <p className="muted">No LiveKit events yet.</p>}
        </div>
        <div className="livekit-log">
          <strong>{t.liveKitTranscripts}</strong>
          {transcripts.length ? transcripts.map((row, index) => (
            <div className="livekit-row good" key={`${row.at}-${index}`}>
              <span>{row.at}</span>
              <b>{row.label}</b>
              <small>{row.detail}</small>
            </div>
          )) : <p className="muted">No transcript yet.</p>}
        </div>
      </div>
    </section>
  );
}

function VisionEvidencePanel({
  pushReceipt,
  t,
  refreshSignal
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  refreshSignal: number;
}) {
  const [status, setStatus] = useState<VisionEvidenceStatus>({});
  const [timeline, setTimeline] = useState<VisionEvidenceTimeline>({});
  const [busy, setBusy] = useState(false);

  const loadEvidence = useCallback(async (silent = false) => {
    try {
      const [nextStatus, nextTimeline] = await Promise.all([
        api.visionEvidenceStatus(),
        api.visionEvidenceTimeline(8)
      ]);
      setStatus(nextStatus);
      setTimeline(nextTimeline);
    } catch (exc) {
      if (!silent) {
        pushReceipt(errorReceipt("vision.evidence.load", exc));
      }
    }
  }, [pushReceipt]);

  useEffect(() => {
    void loadEvidence();
  }, [loadEvidence]);

  useEffect(() => {
    if (!refreshSignal) return;
    void loadEvidence(true);
  }, [loadEvidence, refreshSignal]);

  useEffect(() => {
    const timer = window.setInterval(() => void loadEvidence(true), 3000);
    return () => window.clearInterval(timer);
  }, [loadEvidence]);

  const runEvidenceAction = async (action: "request" | "stage" | "frame" | "bbox" | "focus") => {
    setBusy(true);
    try {
      if (action === "request") {
        pushReceipt(await api.visionEvidenceRequest({
          description: "Web operator requested nearest time-aligned evidence.",
          target_time_ms: Date.now(),
          require_asset: true
        }));
      } else if (action === "stage") {
        pushReceipt(await api.visionEvidenceStageHint({
          evidence_id: String(items[0]?.evidence_id || ""),
          target_time_ms: Number(items[0]?.timebase && typeof items[0].timebase === "object"
            ? (items[0].timebase as Record<string, unknown>).wall_time_ms || Date.now()
            : Date.now()),
          description: "Web operator staged visual evidence for GOSLO.",
          notify_requested: true,
          source: "web_console"
        }));
      } else if (action === "frame") {
        pushReceipt(await api.visionFrameCacheUpload({
          image_base64: "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=",
          mime_type: "image/png",
          source_id: "web_console_test_track",
          track_sid: "web_console_test_track",
          wall_time_ms: Date.now(),
          sequence: Date.now() % 1000000,
          description: "Web Console cached-frame smoke sample.",
          dry_run: false,
          operator_mode: true
        }));
      } else {
        pushReceipt(await api.visualAttentionTest({
          kind: action,
          subject_id: `web_${action}_${Date.now()}`,
          label: `web ${action} evidence test`,
          dispatch_harness: action === "bbox",
          timebase: {
            clock_domain: "web",
            wall_time_ms: Date.now(),
            source_id: "web_console"
          }
        }));
      }
      await loadEvidence();
    } catch (exc) {
      pushReceipt(errorReceipt("vision.evidence.action", exc, { evidence_action: action }));
    } finally {
      setBusy(false);
    }
  };

  const items = timeline.items ?? [];
  const samplerTracks = status.livekit_sampler?.active_tracks ?? [];
  const samplerFresh = Boolean(status.livekit_sampler?.latest_frame_fresh);
  const samplerAge = formatEvidenceAge(status.livekit_sampler?.latest_frame_age_ms);
  const frameFresh = Boolean(status.frame_cache?.latest_frame_fresh);
  const frameAge = formatEvidenceAge(status.frame_cache?.latest_frame_age_ms);
  const frameLabel = `${status.frame_cache?.frame_count ?? 0} / ${frameFresh ? t.fresh : t.stale}${frameAge ? ` ${frameAge}` : ""}`;
  const samplerLabel = status.livekit_sampler?.available
    ? `${status.livekit_sampler.recorded_frames ?? 0}f / ${samplerTracks.length}t / ${samplerFresh ? t.fresh : t.stale}${samplerAge ? ` ${samplerAge}` : ""}`
    : String(status.livekit_sampler?.message || "offline");
  return (
    <section className="evidence-console">
      <div className="palette-title">
        <strong><CircleDot size={17} /> {t.evidenceConsole}</strong>
        <span>
          {t.evidenceSamples}: {status.sample_count ?? 0}
          {" / "}
          {t.evidenceAssets}: {status.visual_asset_count ?? 0}
          {" / "}
          <b className={frameFresh ? "fresh-state" : "stale-state"}>{t.frameCache}: {frameLabel}</b>
          {" / "}
          <b className={samplerFresh ? "fresh-state" : "stale-state"}>{t.liveKitSampler}: {samplerLabel}</b>
          {" / "}
          <b>{t.evidenceAutoRefresh}: 3s</b>
        </span>
      </div>
      <div className="button-row">
        <button className="button small" disabled={busy} onClick={() => void loadEvidence()}>
          <RefreshCw size={15} /> {t.refresh}
        </button>
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("request")}>
          <Search size={15} /> {t.requestEvidence}
        </button>
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("stage")}>
          <CircleDot size={15} /> {t.stageEvidenceHint}
        </button>
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("frame")}>
          <Camera size={15} /> {t.cacheFrameTest}
        </button>
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("bbox")}>
          <Filter size={15} /> {t.bboxTest}
        </button>
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("focus")}>
          <CircleDot size={15} /> {t.focusTest}
        </button>
      </div>
      <div className="evidence-timeline">
        {items.length ? items.map((item, index) => (
          <div className="evidence-row" key={String(item.evidence_id || index)}>
            <strong>{String(item.kind || "evidence")}</strong>
            <span>{String(item.status || "ready")}</span>
            <small>{String(item.description || item.evidence_id || "")}</small>
          </div>
        )) : <p className="muted">{t.noEvidence}</p>}
      </div>
    </section>
  );
}

function formatEvidenceAge(ageMs: number | null | undefined): string {
  if (typeof ageMs !== "number" || Number.isNaN(ageMs)) return "";
  if (ageMs < 1000) return "<1s";
  if (ageMs < 60_000) return `${Math.round(ageMs / 1000)}s`;
  return `${Math.round(ageMs / 60_000)}m`;
}

function evidenceLooksScreenShare(row: unknown): boolean {
  if (!row || typeof row !== "object") return false;
  const data = row as Record<string, unknown>;
  const meta = data.meta && typeof data.meta === "object"
    ? data.meta as Record<string, unknown>
    : {};
  const timebase = data.timebase && typeof data.timebase === "object"
    ? data.timebase as Record<string, unknown>
    : {};
  const text = [
    data.track_name,
    data.source_id,
    data.track_sid,
    data.participant_id,
    data.publication_source,
    data.description,
    meta.publication_source,
    meta.track_name,
    meta.source,
    timebase.source_id
  ].map((value) => String(value || "").toLowerCase()).join(" ");
  return text.includes("web-console-screen")
    || text.includes("screen_share")
    || text.includes("screenshare")
    || (text.includes("screen") && text.includes("share"));
}

async function loadLiveKitClient(): Promise<LiveKitClientModule> {
  if (liveKitClientPromise) return liveKitClientPromise;
  liveKitClientPromise = (async () => {
    let lastError: unknown = null;
    for (const url of LIVEKIT_CLIENT_URLS) {
      try {
        const client = await import(/* @vite-ignore */ url) as LiveKitClientModule & {
          setLogLevel?: (level: unknown) => void;
          LogLevel?: Record<string, unknown>;
        };
        // LiveKit's default info logs include connection URLs. Keep browser
        // diagnostics quiet so join tokens never drift into visible logs.
        client.setLogLevel?.(client.LogLevel?.warn ?? "warn");
        return client;
      } catch (exc) {
        lastError = exc;
      }
    }
    throw lastError instanceof Error
      ? lastError
      : new Error("LiveKit browser client failed to load");
  })();
  return liveKitClientPromise;
}

function bindLiveKitRoomEvents({
  room,
  RoomEvent,
  Track,
  onEvent,
  onTranscript,
  onRemoteAudio,
  onRemoteAudioDetached,
  onDisconnected,
  onState
}: {
  room: any;
  RoomEvent?: Record<string, string>;
  Track?: any;
  onEvent: (label: string, detail?: string, state?: LiveKitEventStatus) => void;
  onTranscript: (text: string, detail: string) => void;
  onRemoteAudio: (track: any, participant: any) => void;
  onRemoteAudioDetached: (track: any) => void;
  onDisconnected: (reason: string) => void;
  onState: (state: string) => void;
}) {
  const on = (name: string, handler: (...args: any[]) => void) => {
    const eventName = RoomEvent?.[name];
    if (eventName) room.on(eventName, handler);
  };

  on("ConnectionStateChanged", (state: unknown) => {
    const label = String(state || "");
    onState(label);
    const status: LiveKitEventStatus = label === "connected"
      ? "good"
      : label.includes("reconnect") || label === "connecting"
        ? "warn"
        : "idle";
    onEvent("state", label, status);
  });
  on("SignalReconnecting", () => onEvent("signal_reconnecting", "", "warn"));
  on("Reconnecting", () => onEvent("reconnecting", "", "warn"));
  on("Reconnected", () => onEvent("reconnected", "", "good"));
  on("TrackSubscribed", (track: any, publication: any, participant: any) => {
    const kind = String(track?.kind || publication?.kind || "");
    const source = String(publication?.source || "");
    onEvent("track_subscribed", `${participantIdentity(participant)} / ${kind} / ${source}`, "good");
    if (isAudioTrack(track, Track)) onRemoteAudio(track, participant);
  });
  on("TrackUnsubscribed", (track: any) => {
    onRemoteAudioDetached(track);
    onEvent("track_unsubscribed", String(track?.kind || ""), "idle");
  });
  on("TranscriptionReceived", (segments: unknown, participant: any) => {
    for (const row of normalizeTranscriptSegments(segments)) {
      onTranscript(row, participantIdentity(participant));
    }
  });
  on("DataReceived", (payload: unknown, participant: any, _kind: unknown, topic: unknown) => {
    if (String(topic || "") !== "lk.transcription") return;
    const text = decodeDataPayload(payload);
    if (text) onTranscript(text, participantIdentity(participant));
  });
  on("Disconnected", (reason: unknown) => {
    onEvent("disconnected", String(reason || ""), "idle");
    onDisconnected(String(reason || ""));
  });
}

function isAudioTrack(track: any, Track: any): boolean {
  const kind = String(track?.kind || "").toLowerCase();
  const audioKind = String(Track?.Kind?.Audio || "audio").toLowerCase();
  return kind === "audio" || kind === audioKind;
}

function attachRemoteAudio(
  track: any,
  participant: any,
  registry: Map<string, HTMLMediaElement>
) {
  try {
    const element = track.attach?.() as HTMLMediaElement | undefined;
    if (!element) return;
    const key = `${participantIdentity(participant)}:${String(track.sid || track.mediaStreamTrack?.id || Date.now())}`;
    element.autoplay = true;
    element.controls = false;
    element.style.display = "none";
    element.dataset.parrotLivekitAudio = key;
    document.body.appendChild(element);
    registry.set(key, element);
  } catch {
    // Remote audio attachment is best-effort; connection state is still useful.
  }
}

function detachRemoteAudio(track: any, registry: Map<string, HTMLMediaElement>) {
  try {
    const detached = track.detach?.() as HTMLMediaElement[] | undefined;
    detached?.forEach((element) => element.remove());
  } catch {
    // Fall through to registry cleanup.
  }
  for (const [key, element] of registry.entries()) {
    if (!document.body.contains(element)) {
      registry.delete(key);
      continue;
    }
    if (!track?.sid || key.includes(String(track.sid))) {
      element.remove();
      registry.delete(key);
    }
  }
}

function stopMediaTrack(track: MediaStreamTrack | null) {
  try {
    track?.stop();
  } catch {
    // Some browser tracks are already stopped by the share picker.
  }
}

function normalizeTranscriptSegments(segments: unknown): string[] {
  if (!Array.isArray(segments)) return [];
  return segments
    .map((segment) => {
      if (typeof segment === "string") return segment;
      if (segment && typeof segment === "object") {
        const row = segment as Record<string, unknown>;
        return String(row.text || row.final_text || row.transcript || "");
      }
      return "";
    })
    .map((text) => text.trim())
    .filter(Boolean);
}

function decodeDataPayload(payload: unknown): string {
  try {
    if (payload instanceof Uint8Array) {
      return new TextDecoder().decode(payload);
    }
    if (typeof payload === "string") return payload;
  } catch {
    return "";
  }
  return "";
}

function participantIdentity(participant: any): string {
  return String(participant?.identity || participant?.sid || "remote");
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

function relatedRefsForNode(
  liveState: LiveState,
  nodeId: string,
  selected: Record<string, unknown> | null
): Array<Record<string, string>> {
  if (!nodeId) return [];
  const rows: Array<Record<string, string>> = [];
  const seen = new Set<string>();
  const pushRow = (row: Record<string, unknown>, source: string, fallbackKind = "ref") => {
    const refId = String(row.ref_id || row.photo_id || row.source_event_id || row.id || `${source}:${rows.length}`);
    const stableKey = `${source}:${refId}`;
    if (seen.has(stableKey)) return;
    seen.add(stableKey);
    const meta = recordFromUnknown(row.custom_meta || row.meta);
    const path = String(row.payload_source || row.asset_ref || row.reference_image_path || meta.asset_ref || meta.asset_path || "");
    rows.push({
      id: stableKey,
      ref_id: refId,
      label: String(row.label || row.title || row.photo_id || row.ref_id || refId),
      kind: String(row.kind || row.role || meta.role || fallbackKind),
      source,
      path,
      url: photoAssetPreviewUrl(path)
    });
  };

  (liveState.refs?.refs ?? []).forEach((row) => {
    if (
      String(row.target_kind || "") === "l2b_node"
      && String(row.target_id || "") === nodeId
    ) {
      pushRow(row, "RefBinding", "ref");
    }
  });
  (liveState.intent_workspace?.refs ?? []).forEach((row) => {
    if (
      String(row.related_node_uuid || "") === nodeId
      || String(row.photo_id || "") === nodeId
    ) {
      pushRow(row, "IntentWorkspace", "workspace_ref");
    }
  });

  const selectedMeta = recordFromUnknown(selected?.meta);
  ["focus_refs", "bbox_refs", "ref_ids"].forEach((field) => {
    const values = selectedMeta[field];
    if (!Array.isArray(values)) return;
    values.map(String).filter(Boolean).forEach((refId) => {
      pushRow({ ref_id: refId, kind: field.replace(/_refs$/, "") }, "Node meta", field);
    });
  });
  return rows;
}

function photoAssetPreviewUrl(value: string): string {
  const raw = String(value || "").trim();
  if (!raw) return "";
  const normalized = raw.replace(/\\/g, "/");
  if (normalized.startsWith("/api/photos/asset/")) return normalized;
  if (normalized.startsWith("api/photos/asset/")) return `/${normalized}`;
  const cleanPath = normalized.split(/[?#]/)[0];
  const lowerPath = cleanPath.toLowerCase();
  if (!lowerPath.includes("/upload/photo/") && !lowerPath.includes("/photos/") && !lowerPath.endsWith(".jpg")) {
    return "";
  }
  const match = cleanPath.match(/(?:\/upload\/photo\/|\/)(\d{4}-\d{2}-\d{2})\/([^/]+)$/i);
  if (!match) return "";
  const day = match[1];
  const fileName = match[2].replace(/\.jpg$/i, "");
  if (!fileName || fileName.includes("..")) return "";
  return `/api/photos/asset/${encodeURIComponent(day)}/${encodeURIComponent(fileName)}`;
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

function GraphHealthSummary({ health }: { health: Record<string, unknown> }) {
  const rows = [
    ["Node", health.node_count],
    ["Edge", health.edge_count],
    ["Orphan", health.orphan_count],
    ["WCC", health.wcc_count],
    ["Largest", health.largest_wcc_size],
    ["Tier", health.analysis_tier]
  ];
  return (
    <div className="graph-health-grid">
      {rows.map(([label, value]) => (
        <span key={String(label)}>
          <small>{String(label)}</small>
          <strong>{String(value ?? "-")}</strong>
        </span>
      ))}
    </div>
  );
}

function SourceBoard({
  liveState,
  pushReceipt,
  t,
  onGraphitiPreview
}: {
  liveState: LiveState;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onGraphitiPreview: (preview: GraphitiPreviewPayload) => void;
}) {
  const [activeSource, setActiveSource] = useState<SourceBoardId>("graphiti");
  const sourceTabs = [
    { id: "graphiti" as const, label: t.graphiti, icon: <Database size={15} /> },
    { id: "obsidian" as const, label: "Obsidian", icon: <FileText size={15} /> },
    { id: "calendar" as const, label: t.googleCalendar, icon: <CalendarDays size={15} /> },
    { id: "refs" as const, label: "Refs/Photos", icon: <Link2 size={15} /> },
    { id: "manual" as const, label: t.manualNode, icon: <Plus size={15} /> }
  ];
  return (
    <div className="source-board">
      <div className="source-board-tabs" role="tablist" aria-label={t.sourceBoard}>
        {sourceTabs.map((tab) => (
          <button
            key={tab.id}
            className={activeSource === tab.id ? "source-tab active" : "source-tab"}
            onClick={() => setActiveSource(tab.id)}
            role="tab"
            aria-selected={activeSource === tab.id}
          >
            {tab.icon}
            <span>{tab.label}</span>
          </button>
        ))}
      </div>
      <div className="source-board-active">
        <div className="source-panel" hidden={activeSource !== "graphiti"}>
          <GraphitiSourceCard pushReceipt={pushReceipt} t={t} onPreview={onGraphitiPreview} />
        </div>
        <div className="source-panel" hidden={activeSource !== "obsidian"}>
          <ObsidianDraftCard pushReceipt={pushReceipt} t={t} />
        </div>
        <div className="source-panel" hidden={activeSource !== "calendar"}>
          <CalendarSourceCard pushReceipt={pushReceipt} t={t} />
        </div>
        <div className="source-panel" hidden={activeSource !== "refs"}>
          <RefPhotoSourceCard liveState={liveState} pushReceipt={pushReceipt} />
        </div>
        <div className="source-panel" hidden={activeSource !== "manual"}>
          <ManualNodeSourceCard t={t} />
        </div>
      </div>
      <p className="source-board-note">{t.sourceBoardHint}</p>
    </div>
  );
}

function GraphitiSourceCard({
  pushReceipt,
  t,
  onPreview
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onPreview: (preview: GraphitiPreviewPayload) => void;
}) {
  const [partition, setPartition] = useState("arknights_test");
  const [query, setQuery] = useState("Amiya Chernobog");
  const [limit, setLimit] = useState(6);
  const [hits, setHits] = useState<Array<Record<string, unknown>>>([]);
  const [subgraphNodes, setSubgraphNodes] = useState<Array<Record<string, unknown>>>([]);
  const [subgraphEdges, setSubgraphEdges] = useState<Array<Record<string, unknown>>>([]);
  const [selectedHitKeys, setSelectedHitKeys] = useState<string[]>([]);
  const [exportObservations, setExportObservations] = useState<Array<Record<string, unknown>>>([]);
  const [edgeDrafts, setEdgeDrafts] = useState<Array<Record<string, unknown>>>([]);
  const [edgePolicy, setEdgePolicy] = useState("");
  const [destination, setDestination] = useState("isolated_compartment");
  const selectedHits = useMemo(
    () => hits.filter((hit, index) => selectedHitKeys.includes(graphitiHitKey(hit, index))),
    [hits, selectedHitKeys]
  );
  const selectedPreview = () => buildGraphitiPreviewPayload({
    hits: selectedHits,
    subgraphNodes,
    subgraphEdges,
    partition,
    query
  });
  const search = async () => {
    if (!query.trim()) {
      pushReceipt(localReceipt("graphiti.subgraph.search", false, { error: "missing_query" }));
      return;
    }
    try {
      const receipt = await api.graphitiSubgraphSearch({ query: query.trim(), partition, limit });
      const nextHits = receiptArray(receipt, "hits");
      const subgraph = receiptRecord(receipt, "subgraph");
      const nextSubgraphNodes = recordArrayFrom(subgraph, "nodes");
      const nextSubgraphEdges = recordArrayFrom(subgraph, "edges");
      setHits(nextHits);
      setSubgraphNodes(nextSubgraphNodes);
      setSubgraphEdges(nextSubgraphEdges);
      setSelectedHitKeys(nextHits.map((hit, index) => graphitiHitKey(hit, index)));
      setExportObservations([]);
      setEdgeDrafts([]);
      setEdgePolicy("");
      if (receipt.success !== false && (nextHits.length || nextSubgraphNodes.length)) {
        onPreview(buildGraphitiPreviewPayload({
          hits: nextHits,
          subgraphNodes: nextSubgraphNodes,
          subgraphEdges: nextSubgraphEdges,
          partition,
          query
        }));
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("graphiti.subgraph.search", exc, { partition, query }));
    }
  };
  const toggleHit = (key: string) => {
    setSelectedHitKeys((current) => (
      current.includes(key)
        ? current.filter((item) => item !== key)
        : [...current, key]
    ));
  };
  const selectAllHits = () => {
    setSelectedHitKeys(hits.map((hit, index) => graphitiHitKey(hit, index)));
  };
  const showExportReceipt = (receipt: Receipt) => {
    setExportObservations(receiptArray(receipt, "observations"));
    setEdgeDrafts(receiptArray(receipt, "edge_drafts"));
    setEdgePolicy(String(receipt.data?.edge_write_policy || ""));
    pushReceipt(receipt);
  };
  const exportDraft = async () => {
    if (!selectedHits.length) {
      pushReceipt(localReceipt("graphiti.subgraph.export_draft", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      showExportReceipt(await api.graphitiSubgraphExportDraft({ partition, query: query.trim(), hits: selectedHits }));
    } catch (exc) {
      pushReceipt(errorReceipt("graphiti.subgraph.export_draft", exc, { partition, query }));
    }
  };
  const exportDryRun = async () => {
    if (!selectedHits.length) {
      pushReceipt(localReceipt("graphiti.subgraph.export", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      showExportReceipt(await api.graphitiSubgraphExport({
        partition,
        query: query.trim(),
        hits: selectedHits,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("graphiti.subgraph.export", exc, { partition, query }));
    }
  };
  const previewImportPolicy = async () => {
    if (!selectedHits.length) {
      pushReceipt(localReceipt("l2b.graph_policy.import_draft", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      const itemIds = selectedHits.map((hit, index) => graphitiHitKey(hit, index));
      const edgeDraftPayload = subgraphEdges
        .filter((edge) => {
          const hitId = String(edge.hit_id || "");
          return itemIds.includes(hitId) || itemIds.includes(String(edge.source || "")) || itemIds.includes(String(edge.target || ""));
        })
        .slice(0, 24)
        .map((edge) => ({
          source: edge.source,
          target: edge.target,
          kind: edge.kind || "graphiti_fact",
          source_graphiti_uuid: edge.source_graphiti_uuid,
          target_graphiti_uuid: edge.target_graphiti_uuid,
          label: edge.label || edge.fact,
          edge_source: "graphiti"
        }));
      pushReceipt(await api.l2bGraphImportDraft({
        destination,
        source_kind: "graphiti",
        source_id: `${partition}:${query.trim()}`,
        workspace_id: "memory_graph",
        subgraph_label: query.trim() || partition,
        item_ids: itemIds,
        proposed_edges: edgeDraftPayload,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.graph_policy.import_draft", exc, { partition, query, destination }));
    }
  };

  return (
    <article className="source-card graphiti-source-card">
      <div className="source-card-head">
        <strong><Database size={16} /> {t.graphiti}</strong>
        <small>{t.writeThroughL15}</small>
      </div>
      <label>
        <span>{t.partition}</span>
        <select value={partition} onChange={(event) => setPartition(event.target.value)}>
          <option value="arknights_test">arknights_test</option>
          <option value="goslo">goslo</option>
          <option value="maid">maid</option>
          <option value="scene">scene</option>
          <option value="user">user</option>
        </select>
      </label>
      <label>
        <span>{t.graphitiQuery}</span>
        <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t.graphitiQuery} />
      </label>
      <label>
        <span>{t.limit}</span>
        <input
          type="number"
          min={1}
          max={20}
          value={limit}
          onChange={(event) => setLimit(Math.max(1, Math.min(20, Number(event.target.value) || 1)))}
        />
      </label>
      <label>
        <span>{t.importDestination}</span>
        <select value={destination} onChange={(event) => setDestination(event.target.value)}>
          {GRAPH_IMPORT_DESTINATIONS.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </label>
      <div className="button-row">
        <button className="button primary" onClick={() => void search()}><Search size={16} /> {t.searchGraphiti}</button>
        <button className="button" onClick={() => onPreview(selectedPreview())} disabled={!selectedHits.length}><GitBranch size={16} /> {t.previewOnCanvas}</button>
        <button className="button" onClick={() => void previewImportPolicy()} disabled={!selectedHits.length}><Workflow size={16} /> {t.previewPolicy}</button>
        <button className="button" onClick={() => void exportDraft()} disabled={!selectedHits.length}><UploadCloud size={16} /> {t.exportSubgraphDraft}</button>
        <button className="button ghost" onClick={() => void exportDryRun()} disabled={!selectedHits.length}><ShieldCheck size={16} /> {t.applyExportDryRun}</button>
      </div>
      <div className="hit-list">
        <div className="hit-list-head">
          <strong>{t.resultGraph}</strong>
          <small>{`${selectedHits.length}/${hits.length} ${t.selectedOf} / ${subgraphNodes.length} Node / ${subgraphEdges.length} Edge`}</small>
        </div>
        {hits.length ? (
          <div className="button-row compact">
            <button className="button small" onClick={selectAllHits}>{t.selectAll}</button>
            <button className="button small ghost" onClick={() => setSelectedHitKeys([])}>{t.clearSelection}</button>
          </div>
        ) : null}
        {hits.length ? hits.slice(0, 8).map((hit, index) => {
          const key = graphitiHitKey(hit, index);
          const checked = selectedHitKeys.includes(key);
          return (
            <div className={checked ? "hit-select-row selected" : "hit-select-row"} key={key}>
              <input
                type="checkbox"
                checked={checked}
                onChange={() => toggleHit(key)}
                aria-label={`${t.selectedHits}: ${graphitiHitLabel(hit, index)}`}
              />
              <button
                className="hit-row"
                onClick={() => onPreview(buildGraphitiPreviewPayload({
                  hits: [hit],
                  subgraphNodes,
                  subgraphEdges,
                  partition,
                  query
                }))}
                title={String(hit.text || hit.summary || hit.label || "")}
              >
                <span>{graphitiHitLabel(hit, index)}</span>
                <small>{String(hit.source_description || hit.uuid || hit.score || "")}</small>
              </button>
            </div>
          );
        }) : <small className="muted">{t.noHits}</small>}
      </div>
      {exportObservations.length || edgeDrafts.length ? (
        <div className="note-preview-list graphiti-export-plan">
          <strong>Export plan</strong>
          <small>{`${exportObservations.length} L1.5 observation(s) / ${edgeDrafts.length} Edge draft(s)`}</small>
          {edgePolicy ? <small className="muted">{edgePolicy}</small> : null}
          {exportObservations.slice(0, 3).map((row, index) => (
            <div className="preview-row" key={`${String(row.graphiti_uuid || row.label || index)}:graphiti-observation`}>
              <span>{String(row.label || row.graphiti_uuid || "-")}</span>
              <small>{`Graphiti -> L1.5 / ${String(row.kind || "object")}`}</small>
            </div>
          ))}
          {edgeDrafts.slice(0, 3).map((row, index) => (
            <div className="preview-row mapping-row" key={`${String(row.hit_graphiti_uuid || index)}:graphiti-edge-draft`}>
              <span>{String(row.label || row.kind || "graphiti_fact")}</span>
              <small>{`${String(row.source_graphiti_uuid || "-")} -> ${String(row.target_graphiti_uuid || "-")}`}</small>
              <small>{String(row.write_policy || "requires_resolved_l2b_node_uuid")}</small>
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function CalendarSourceCard({
  pushReceipt,
  t
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
}) {
  const defaultCalendarRaw = JSON.stringify([
    {
      id: "react_source_board_calendar_event",
      calendar_id: "primary",
      summary: "React Source Board calendar preview",
      start: { dateTime: "2026-05-15T10:00:00+08:00", timeZone: "Asia/Shanghai" },
      end: { dateTime: "2026-05-15T10:30:00+08:00", timeZone: "Asia/Shanghai" },
      htmlLink: "https://calendar.google.com/",
      status: "confirmed",
      objects: ["blue mug"]
    }
  ], null, 2);
  const [rawPayload, setRawPayload] = useState(defaultCalendarRaw);
  const [normalizedEvents, setNormalizedEvents] = useState<Array<Record<string, unknown>>>([]);
  const [observations, setObservations] = useState<Array<Record<string, unknown>>>([]);
  const [mappingRows, setMappingRows] = useState<Array<Record<string, unknown>>>([]);
  const [resultRows, setResultRows] = useState<Array<Record<string, unknown>>>([]);
  const [resultStatus, setResultStatus] = useState("");
  const calendarPayload = () => ({ raw: rawPayload.trim() || defaultCalendarRaw });
  const showCalendarReceipt = (receipt: Receipt) => {
    setNormalizedEvents(receiptArray(receipt, "normalized_events"));
    setObservations(receiptArray(receipt, "observations"));
    setMappingRows(receiptArray(receipt, "mapping_rows"));
    pushReceipt(receipt);
  };
  const fetchPreview = async () => {
    try {
      pushReceipt(await api.googleCalendarFetch({ dry_run: true, operator_mode: false }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.fetch", exc));
    }
  };
  const fetchExecute = async () => {
    try {
      pushReceipt(await api.googleCalendarFetch({ dry_run: false, operator_mode: true }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.fetch.execute", exc));
    }
  };
  const loadResults = async () => {
    try {
      const receipt = await api.googleCalendarResults(12);
      setResultRows(receiptArray(receipt, "rows"));
      const data = receipt.data ?? {};
      setResultStatus(data.available === false
        ? t.calendarResultUnavailable
        : t.calendarResultEmpty);
      pushReceipt(receipt);
    } catch (exc) {
      setResultStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("google.calendar.results", exc));
    }
  };
  const preview = async () => {
    try {
      showCalendarReceipt(await api.googleCalendarPreview(calendarPayload()));
    } catch (exc) {
      pushReceipt(errorReceipt("calendar.preview", exc));
    }
  };
  const importDraft = async () => {
    try {
      showCalendarReceipt(await api.googleCalendarImportDraft(calendarPayload()));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.import_draft", exc));
    }
  };
  const importPreview = async () => {
    try {
      showCalendarReceipt(await api.googleCalendarImport({
        ...calendarPayload(),
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.import", exc));
    }
  };
  const importExecute = async () => {
    try {
      showCalendarReceipt(await api.googleCalendarImport({
        ...calendarPayload(),
        dry_run: false,
        operator_mode: true
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.import.execute", exc));
    }
  };
  return (
    <article className="source-card">
      <div className="source-card-head">
        <strong><CalendarDays size={16} /> {t.googleCalendar}</strong>
        <small>{t.writeThroughL15}</small>
      </div>
      <label>
        <span>{t.calendarPayload}</span>
        <textarea value={rawPayload} onChange={(event) => setRawPayload(event.target.value)} rows={8} />
      </label>
      <div className="button-row compact">
        <button className="button" onClick={() => void fetchPreview()}><CalendarDays size={16} /> {t.calendarFetch}</button>
        <button className="button ghost" onClick={() => void fetchExecute()}><Play size={16} /> {t.calendarFetchExecute}</button>
        <button className="button" onClick={() => void loadResults()}><RefreshCw size={16} /> {t.calendarResults}</button>
        <button className="button" onClick={() => void preview()}><Bell size={16} /> {t.calendarPreview}</button>
        <button className="button" onClick={() => void importDraft()}><UploadCloud size={16} /> {t.importDraft}</button>
        <button className="button ghost" onClick={() => void importPreview()}><ShieldCheck size={16} /> {t.dryApply}</button>
        <button className="button ghost" onClick={() => void importExecute()}><UploadCloud size={16} /> {t.calendarImportExecute}</button>
      </div>
      {resultRows.length ? (
        <div className="note-preview-list calendar-result-list">
          <strong>{t.calendarResults}</strong>
          {resultRows.slice(0, 4).map((row, index) => (
            <div className="preview-row mapping-row" key={`${String(row.stream_id || row.task_id || index)}:calendar-result`}>
              <span>{`${String(row.status || "-")} · ${String(row.event_count ?? 0)} events`}</span>
              <small>{`${String(row.task_id || "-")} / ${String(row.original_type || "-")}`}</small>
              <small>{String(row.result_summary || "")}</small>
            </div>
          ))}
        </div>
      ) : resultStatus ? (
        <div className="note-preview-list calendar-result-list">
          <strong>{t.calendarResults}</strong>
          <small className="muted">{resultStatus}</small>
        </div>
      ) : null}
      {normalizedEvents.length ? (
        <div className="note-preview-list">
          <strong>{t.normalizedPreview}</strong>
          {normalizedEvents.slice(0, 3).map((event, index) => (
            <div className="preview-row" key={`${String(event.id || index)}:calendar`}>
              <span>{String(event.title || event.id || "-")}</span>
              <small>{`${String(event.start_time || "")} / ${String(event.timezone || "")}`}</small>
            </div>
          ))}
        </div>
      ) : null}
      {observations.length ? (
        <div className="note-preview-list">
          <strong>{t.observationPreview}</strong>
          {observations.slice(0, 3).map((observation, index) => (
            <div className="preview-row" key={`${String(observation.label || index)}:obs`}>
              <span>{String(observation.label || "-")}</span>
              <small>{String((observation.meta as Record<string, unknown> | undefined)?.calendar_event_id || observation.source || "")}</small>
            </div>
          ))}
        </div>
      ) : null}
      {mappingRows.length ? (
        <div className="note-preview-list">
          <strong>{t.calendarMapping}</strong>
          {mappingRows.slice(0, 4).map((row, index) => (
            <div className="preview-row mapping-row" key={`${String(row.provider_ref || row.calendar_event_id || index)}:mapping`}>
              <span>{String(row.title || row.calendar_event_id || "-")}</span>
              <small>{`${t.calendarTarget}: ${String(row.l15_bucket || "-")} -> L2-B ${String(row.l2b_kind || "-")} / ${String(row.l2b_action || "-")}`}</small>
              <small>{`${t.calendarPolicy}: ${String(row.intent_workspace_policy || "-")} / ${String(row.policy_note || "-")}`}</small>
            </div>
          ))}
        </div>
      ) : null}
    </article>
  );
}

function ManualNodeSourceCard({ t }: { t: ConsoleCopy }) {
  return (
    <article className="source-card">
      <div className="source-card-head">
        <strong><FileText size={16} /> {t.manualNode}</strong>
        <small>{t.roleplayModeHint}</small>
      </div>
      <p className="source-card-note">{t.manualNodeHint}</p>
    </article>
  );
}

function RefPhotoSourceCard({
  liveState,
  pushReceipt
}: {
  liveState: LiveState;
  pushReceipt: (receipt: Receipt | null) => void;
}) {
  const refRows = liveState.refs?.refs ?? [];
  const resolvedTargets = liveState.refs?.resolved_l2b_targets ?? [];
  const intentRefs = liveState.intent_workspace?.refs ?? [];
  const isPhotoLikeRef = (row: Record<string, unknown>) => {
    const kind = String(row.kind || "").toLowerCase();
    const role = String(row.role || "").toLowerCase();
    return kind === "photo" || role.startsWith("photo");
  };
  const seenPhotoRefs = new Set<string>();
  const photoRefs = [...refRows.filter(isPhotoLikeRef), ...intentRefs.filter(isPhotoLikeRef)].filter((row) => {
    const stableId = String(row.ref_id || row.photo_id || row.source_event_id || JSON.stringify(row));
    if (seenPhotoRefs.has(stableId)) return false;
    seenPhotoRefs.add(stableId);
    return true;
  });
  const photoNodes = (liveState.l2b?.nodes ?? []).filter((row) => String(row.kind || "").toLowerCase() === "photo");
  const [refId, setRefId] = useState("");
  const [targetKind, setTargetKind] = useState("l2b_node");
  const [targetId, setTargetId] = useState("");
  const [draftPlan, setDraftPlan] = useState<Record<string, unknown> | null>(null);
  const selectRef = (row: Record<string, unknown>) => {
    setRefId(String(row.ref_id || ""));
    setTargetKind(String(row.target_kind || "l2b_node"));
    setTargetId(String(row.target_id || ""));
  };
  const selectPhoto = (row: Record<string, unknown>) => {
    setRefId(String(row.ref_id || ""));
    setTargetKind(String(row.target_kind || "l2b_node"));
    setTargetId(String(row.target_id || row.related_node_uuid || row.photo_id || ""));
  };
  const showDraftReceipt = (receipt: Receipt) => {
    setDraftPlan(receipt.data ?? {});
    pushReceipt(receipt);
  };
  const draftBinding = async () => {
    if (!refId.trim()) {
      showDraftReceipt(localReceipt("refs.binding.draft", false, { error: "missing_ref_id", core_candidate: "CORE-006" }));
      return;
    }
    try {
      showDraftReceipt(await api.refBindingDraft({
        ref_id: refId.trim(),
        target_kind: targetKind,
        target_id: targetId.trim(),
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showDraftReceipt(errorReceipt("refs.binding.draft", exc, { ref_id: refId, target_kind: targetKind, target_id: targetId }));
    }
  };
  return (
    <article className="source-card ref-photo-card">
      <div className="source-card-head">
        <strong><Link2 size={16} /> Refs / Photos</strong>
        <small>CORE-006 draft only</small>
      </div>
      <div className="source-mini-grid">
        <span><strong>{refRows.length}</strong><small>RefBindings</small></span>
        <span><strong>{resolvedTargets.length}</strong><small>L2-B targets</small></span>
        <span><strong>{photoRefs.length}</strong><small>PHOTO refs</small></span>
        <span><strong>{photoNodes.length}</strong><small>Photo Nodes</small></span>
      </div>
      <p className="source-card-note">
        Ref/file/photo repair is still a Web-only draft surface until CORE-006 is ratified.
      </p>
      {refRows.length ? (
        <div className="note-preview-list">
          <strong>Session RefBindings</strong>
          {refRows.slice(0, 5).map((row, index) => (
            <button className="hit-row" key={`${String(row.ref_id || index)}:ref-row`} onClick={() => selectRef(row)}>
              <span>{String(row.label || row.ref_id || "-")}</span>
              <small>{`${String(row.kind || "-")} -> ${String(row.target_kind || "unresolved")} / ${String(row.target_id || "")}`}</small>
            </button>
          ))}
        </div>
      ) : (
        <div className="note-preview-list">
          <strong>Session RefBindings</strong>
          <small className="muted">No Focus/BBox RefBinding rows in the current session.</small>
        </div>
      )}
      {photoRefs.length || photoNodes.length ? (
        <div className="note-preview-list">
          <strong>Photo refs</strong>
          {photoRefs.slice(0, 3).map((row, index) => {
            const meta = recordFromUnknown(row.custom_meta);
            return (
              <button className="hit-row" key={`${String(row.ref_id || row.photo_id || index)}:photo-ref`} onClick={() => selectPhoto(row)}>
                <span>{String(row.title || row.photo_id || row.ref_id || "photo")}</span>
                <small>{`${String(row.role || meta.role || "photo")} / Node ${String(row.related_node_uuid || row.photo_id || "-")}`}</small>
              </button>
            );
          })}
          {photoNodes.slice(0, 3).map((row, index) => {
            const meta = recordFromUnknown(row.meta);
            const assetPath = String(row.reference_image_path || meta.asset_path || meta.asset_ref || "");
            const assetUrl = photoAssetPreviewUrl(assetPath);
            return (
              <div className="preview-row mapping-row photo-node-row" key={`${String(row.uuid || index)}:photo-node`}>
                {assetUrl ? <img className="photo-preview-thumb" src={assetUrl} alt="Photo Node preview" loading="lazy" /> : <span className="photo-preview-empty">no preview</span>}
                <div>
                  <span>{String(row.label || row.uuid || "Photo Node")}</span>
                  <small>{assetPath || "asset path pending"}</small>
                </div>
              </div>
            );
          })}
        </div>
      ) : null}
      <div className="note-preview-list">
        <strong>Binding draft</strong>
        <label>
          <span>ref_id</span>
          <input value={refId} onChange={(event) => setRefId(event.target.value)} placeholder="ref_..." />
        </label>
        <label>
          <span>target kind</span>
          <select value={targetKind} onChange={(event) => setTargetKind(event.target.value)}>
            <option value="l2b_node">l2b_node</option>
            <option value="graphiti_uuid">graphiti_uuid</option>
            <option value="episode">episode</option>
            <option value="l2b_edge">l2b_edge</option>
            <option value="unresolved">unresolved</option>
          </select>
        </label>
        <label>
          <span>target id</span>
          <input value={targetId} onChange={(event) => setTargetId(event.target.value)} placeholder="Node uuid / Graphiti uuid / episode id" />
        </label>
        <button className="button" onClick={() => void draftBinding()}><Link2 size={16} /> Preview binding</button>
      </div>
      {draftPlan ? (
        <div className="note-preview-list ref-draft-plan">
          <strong>Ref draft plan</strong>
          <div className={draftPlan.error ? "preview-row import-error-row" : "preview-row import-plan-row"}>
            <span>{String(draftPlan.ref_id || draftPlan.error || "-")}</span>
            <small>{String(draftPlan.write_path || draftPlan.policy || "draft only")}</small>
            <small>{String(draftPlan.core_candidate || "CORE-006")} / {String(draftPlan.shared_status || "candidate_only")}</small>
          </div>
        </div>
      ) : null}
    </article>
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
  const [vaultPath, setVaultPath] = useState("D:/GOSLOParrot/GOSLObsidian");
  const [scanNotes, setScanNotes] = useState<Array<Record<string, unknown>>>([]);
  const [invalidNotes, setInvalidNotes] = useState<Array<Record<string, unknown>>>([]);
  const [selectedNotePaths, setSelectedNotePaths] = useState<string[]>([]);
  const [vaultStatus, setVaultStatus] = useState<Record<string, unknown> | null>(null);
  const [importItems, setImportItems] = useState<Array<Record<string, unknown>>>([]);
  const [importErrors, setImportErrors] = useState<Array<Record<string, unknown>>>([]);
  const [importPlanMeta, setImportPlanMeta] = useState<Record<string, unknown> | null>(null);
  const visibleScanNotes = scanNotes.slice(0, 12);
  const refMissingUuid = profile === "ref" && !obsidianUuid.trim();
  const showImportReceipt = (receipt: Receipt) => {
    const data = receipt.data ?? {};
    const nextErrors = receiptArray(receipt, "errors");
    if (!nextErrors.length && data.error) {
      nextErrors.push({ error: data.error });
    }
    setImportItems(receiptArray(receipt, "items"));
    setImportErrors(nextErrors);
    setImportPlanMeta({
      action: receipt.action || "l15.obsidian_vault.import_draft",
      success: receipt.success !== false,
      selected_count: data.selected_count ?? 0,
      write_path: data.write_path || "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)",
      runtime_path: data.runtime_path || "ObsidianIngestTrigger -> TriggerOutcome.commit_observations -> L15Pool.admit",
      would_apply: data.would_apply ?? false,
      apply_skipped_reason: data.apply_skipped_reason || ""
    });
    pushReceipt(receipt);
  };
  const scanVault = async () => {
    try {
      const receipt = await api.obsidianVaultScan(vaultPath);
      const notes = receiptArray(receipt, "notes");
      setScanNotes(notes);
      setSelectedNotePaths([]);
      setInvalidNotes(receiptArray(receipt, "invalid_notes"));
      const nextVaultStatus = receipt.data?.vault;
      setVaultStatus((nextVaultStatus && typeof nextVaultStatus === "object" && !Array.isArray(nextVaultStatus))
        ? nextVaultStatus as Record<string, unknown>
        : null);
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l15.obsidian_vault.scan", exc, { vault_path: vaultPath }));
    }
  };
  const useScannedNote = (note: Record<string, unknown>) => {
    const payload = (note.payload && typeof note.payload === "object" && !Array.isArray(note.payload))
      ? note.payload as Record<string, unknown>
      : note;
    setProfile(String(payload.profile || note.profile || "daily"));
    setLabel(String(payload.label || note.label || ""));
    setObsidianUuid(String(payload.obsidian_uuid || note.obsidian_uuid || ""));
  };
  const toggleSelectedNote = (path: string) => {
    setSelectedNotePaths((current) => (
      current.includes(path)
        ? current.filter((item) => item !== path)
        : [...current, path]
    ));
  };
  const selectVisibleNotes = () => {
    setSelectedNotePaths(visibleScanNotes.map((note) => String(note.path || "")).filter(Boolean));
  };
  const draftImport = async () => {
    if (!selectedNotePaths.length) {
      showImportReceipt(localReceipt("l15.obsidian_vault.import_draft", false, { error: "no_notes_selected" }));
      return;
    }
    try {
      showImportReceipt(await api.obsidianVaultImportDraft({
        vault_path: vaultPath,
        paths: selectedNotePaths,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showImportReceipt(errorReceipt("l15.obsidian_vault.import_draft", exc, { vault_path: vaultPath, paths: selectedNotePaths }));
    }
  };
  const applyImportPreview = async () => {
    if (!selectedNotePaths.length) {
      showImportReceipt(localReceipt("l15.obsidian_vault.import", false, { error: "no_notes_selected" }));
      return;
    }
    try {
      showImportReceipt(await api.obsidianVaultImport({
        vault_path: vaultPath,
        paths: selectedNotePaths,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showImportReceipt(errorReceipt("l15.obsidian_vault.import", exc, { vault_path: vaultPath, paths: selectedNotePaths }));
    }
  };
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
    <article className="source-card obsidian-card">
      <div className="source-card-head">
        <strong><FileText size={16} /> {t.obsidianSettings}</strong>
        <small className={refMissingUuid ? "warn-text" : ""}>{profile === "ref" ? t.refRequiresUuid : t.uuidFree}</small>
      </div>
      <label>
        <span>{t.obsidianVaultPath}</span>
        <input value={vaultPath} onChange={(event) => setVaultPath(event.target.value)} placeholder="D:/GOSLOParrot/GOSLObsidian" />
      </label>
      <button className="button" onClick={() => void scanVault()}><Search size={16} /> {t.scanVault}</button>
      {vaultStatus ? (
        <div className="preview-row">
          <span>{`${t.vaultStatus}: ${String(vaultStatus.status || "-")}`}</span>
          <small>{`${t.readyCount}: ${String(vaultStatus.ingest_ready_count ?? 0)} / ${String(vaultStatus.markdown_count ?? 0)}; ${t.invalidNotes}: ${String(vaultStatus.invalid_count ?? 0)}`}</small>
        </div>
      ) : null}
      {scanNotes.length ? (
        <div className="note-preview-list">
          <strong>{t.readyNotes}</strong>
          <small>{t.selectedNotes}: {selectedNotePaths.length}</small>
          <div className="button-row compact">
            <button className="button small" onClick={selectVisibleNotes}>{t.selectVisibleNotes}</button>
            <button className="button small ghost" onClick={() => setSelectedNotePaths([])}>{t.clearSelection}</button>
          </div>
          {visibleScanNotes.map((note, index) => (
            <div className="note-select-row" key={`${String(note.path || note.label)}:${index}`}>
              <input
                type="checkbox"
                checked={selectedNotePaths.includes(String(note.path || ""))}
                onChange={() => toggleSelectedNote(String(note.path || ""))}
                aria-label={`${t.selectedNotes}: ${String(note.label || note.path || "")}`}
              />
              <button className="hit-row" onClick={() => useScannedNote(note)}>
                <span>{String(note.label || "-")}</span>
                <small>{`${String(note.profile || "")} / ${String(note.path || "")}`}</small>
              </button>
            </div>
          ))}
          <div className="button-row compact">
            <button className="button" onClick={() => void draftImport()}><UploadCloud size={16} /> {t.importDraft}</button>
            <button className="button ghost" onClick={() => void applyImportPreview()}><ShieldCheck size={16} /> {t.dryApply}</button>
          </div>
        </div>
      ) : null}
      {invalidNotes.length ? <small className="warn-text">{t.invalidNotes}: {invalidNotes.length}</small> : null}
      {importPlanMeta || importItems.length || importErrors.length ? (
        <div className="note-preview-list import-plan">
          <div className="import-plan-head">
            <strong>Import plan</strong>
            <small className={importPlanMeta?.success === false ? "warn-text" : "muted"}>
              {`${String(importPlanMeta?.selected_count ?? importItems.length)} ready / ${importErrors.length} issue(s)`}
            </small>
          </div>
          <small className="muted">{String(importPlanMeta?.write_path || "UserTagFilter -> L15Pool.admit(USER_TAG_OBSIDIAN)")}</small>
          {importItems.slice(0, 4).map((item, index) => {
            const observation = recordFromUnknown(item.observation);
            const meta = recordFromUnknown(observation.meta);
            const tags = Array.isArray(meta.tags) ? meta.tags.map(String).slice(0, 4).join(", ") : "";
            return (
              <div className="preview-row import-plan-row" key={`${String(item.path || item.label || index)}:obsidian-import-item`}>
                <span>{String(item.label || item.path || "-")}</span>
                <small>{`${String(item.profile || "-")} -> ${String(item.target_bucket || "-")} / ${String(item.bind_policy || "-")}`}</small>
                <small>{`Node ${String(observation.kind || "object")} / source ${String(observation.source || "user_tag_obsidian")}${tags ? ` / tags ${tags}` : ""}`}</small>
                <small>{String(item.path || "")}</small>
              </div>
            );
          })}
          {importErrors.slice(0, 4).map((row, index) => (
            <div className="preview-row import-error-row" key={`${String(row.path || index)}:obsidian-import-error`}>
              <span>{String(row.path || row.error || "-")}</span>
              <small>{String(row.error || row.reason || "import_error")}</small>
              {row.reason ? <small>{String(row.reason)}</small> : null}
            </div>
          ))}
          {String(importPlanMeta?.apply_skipped_reason || "") ? (
            <small className="muted">{String(importPlanMeta?.apply_skipped_reason)}</small>
          ) : null}
        </div>
      ) : null}
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
  const sourceHandle = String(selected.source_handle || "");
  const targetHandle = String(selected.target_handle || "");
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
      <small>{`${previousSource} -> ${previousTarget}${sourceHandle || targetHandle ? ` (${sourceHandle || "?"} -> ${targetHandle || "?"})` : ""}`}</small>
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

function ReceiptRail({
  receipts,
  t,
  open,
  onToggle
}: {
  receipts: Receipt[];
  t: ConsoleCopy;
  open: boolean;
  onToggle: () => void;
}) {
  if (!open) {
    return (
      <aside className="receipt-rail collapsed">
        <button className="rail-toggle" onClick={onToggle} title={t.receiptTimeline}>
          <PanelRightOpen size={17} />
        </button>
      </aside>
    );
  }
  return (
    <aside className="receipt-rail">
      <div className="rail-head">
        <h2>{t.receiptTimeline}</h2>
        <button className="rail-toggle" onClick={onToggle} title="Collapse">
          <PanelRightOpen size={17} />
        </button>
      </div>
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
    { side: "top", position: Position.Top },
    { side: "right", position: Position.Right },
    { side: "bottom", position: Position.Bottom },
    { side: "left", position: Position.Left }
  ] as const;

  return (
    <div className={selected ? "memory-node-card selected" : "memory-node-card"}>
      {handlePositions.map((handle) => (
        <Fragment key={handle.side}>
          <Handle
            id={sourceHandleId(handle.side)}
            type="source"
            position={handle.position}
            isConnectable={isConnectable}
            className="memory-handle memory-handle-source"
          />
          <Handle
            id={targetHandleId(handle.side)}
            type="target"
            position={handle.position}
            isConnectable={isConnectable}
            className="memory-handle memory-handle-target"
          />
        </Fragment>
      ))}
      <div className="memory-node-title">{data.label}</div>
      <div className="memory-node-meta">
        <span>{nodeKind}</span>
        {compactId ? <span>{compactId}</span> : null}
      </div>
    </div>
  );
}

function receiptArray(receipt: Receipt, key: string): Array<Record<string, unknown>> {
  const data = receipt.data ?? {};
  const raw = data[key];
  if (!Array.isArray(raw)) return [];
  return raw.filter((row): row is Record<string, unknown> => Boolean(row) && typeof row === "object" && !Array.isArray(row));
}

function receiptRecord(receipt: Receipt, key: string): Record<string, unknown> {
  const raw = (receipt.data ?? {})[key];
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};
  return raw as Record<string, unknown>;
}

function recordFromUnknown(raw: unknown): Record<string, unknown> {
  if (!raw || typeof raw !== "object" || Array.isArray(raw)) return {};
  return raw as Record<string, unknown>;
}

function recordArrayFrom(source: Record<string, unknown>, key: string): Array<Record<string, unknown>> {
  const raw = source[key];
  if (!Array.isArray(raw)) return [];
  return raw.filter((row): row is Record<string, unknown> => Boolean(row) && typeof row === "object" && !Array.isArray(row));
}

function uniqueStrings(values: Array<string | null | undefined>): string[] {
  const seen = new Set<string>();
  const result: string[] = [];
  values.forEach((value) => {
    const text = String(value || "").trim();
    if (!text || seen.has(text)) return;
    seen.add(text);
    result.push(text);
  });
  return result;
}

function graphitiHitKey(hit: Record<string, unknown>, index: number): string {
  return String(
    hit.uuid
    || hit.graphiti_uuid
    || hit.id
    || `${hit.source_node_uuid || ""}:${hit.target_node_uuid || ""}:${index}`
  );
}

function buildGraphitiPreviewPayload({
  hits,
  subgraphNodes,
  subgraphEdges,
  partition,
  query
}: {
  hits: Array<Record<string, unknown>>;
  subgraphNodes: Array<Record<string, unknown>>;
  subgraphEdges: Array<Record<string, unknown>>;
  partition: string;
  query: string;
}): GraphitiPreviewPayload {
  const hitNodeIds = new Set(hits.map((hit, index) => graphitiPreviewNodeId(hit, index)));
  const selectedEdges = subgraphEdges.filter((edge) => {
    const hitId = String(edge.hit_id || "");
    return hitNodeIds.has(hitId) || hitNodeIds.has(String(edge.source || "")) || hitNodeIds.has(String(edge.target || ""));
  });
  const selectedNodeIds = new Set(hitNodeIds);
  selectedEdges.forEach((edge) => {
    selectedNodeIds.add(String(edge.source || ""));
    selectedNodeIds.add(String(edge.target || ""));
  });
  const nodes = subgraphNodes.filter((node) => selectedNodeIds.has(String(node.id || node.uuid || node.graphiti_uuid || "")));
  return {
    hits,
    nodes: nodes.length ? nodes : hits,
    edges: selectedEdges,
    partition,
    query: query.trim()
  };
}

function graphitiPreviewNodeId(hit: Record<string, unknown>, index: number): string {
  const id = String(hit.id || "").trim();
  if (id) return id;
  const uuid = String(hit.uuid || hit.graphiti_uuid || "").trim();
  return uuid ? `graphiti:${uuid}` : `graphiti:hit:${index}:${String(hit.label || hit.text || "").slice(0, 18)}`;
}

function graphitiHitLabel(hit: Record<string, unknown>, index: number): string {
  const raw = String(hit.label || hit.summary || hit.text || "").replace(/\s+/g, " ").trim();
  if (!raw) return `Graphiti hit ${index + 1}`;
  const firstClause = raw.split(/[.。:：]/, 1)[0] || raw;
  return firstClause.slice(0, 72);
}

function memoryNode(row: Record<string, unknown>, index: number, stateColors = true): Node {
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
    className: `memory-node kind-${String(row.kind || "node")}${stateColors ? ` ${memoryStateClass(row)}` : ""}`,
    connectable: true
  };
}

function memoryStateClass(row: Record<string, unknown>): string {
  const confirmation = String(row.confirmation || "expected").toLowerCase();
  const salience = String(row.salience || "").toLowerCase();
  if (salience === "alert") return "state-alert";
  if (confirmation === "confirmed") return "state-confirmed";
  if (confirmation === "uncertain" || confirmation === "ghost") return "state-uncertain";
  return "state-tentative";
}

function isDraftableMemoryNodeId(id: string): boolean {
  return Boolean(id) && !id.startsWith("placeholder:");
}

function makeDraftId(kind: string): string {
  return `draft:${kind}:${Date.now()}:${Math.random().toString(36).slice(2, 8)}`;
}

function normalizeHandleSide(value: string | null | undefined): HandleSide | null {
  const raw = String(value || "").replace(/^(source|target)-/, "");
  if (raw === "top" || raw === "right" || raw === "bottom" || raw === "left") return raw;
  return null;
}

function sourceHandleId(side: HandleSide): string {
  return `source-${side}`;
}

function targetHandleId(side: HandleSide): string {
  return `target-${side}`;
}

function formatHandleSide(value: string | null | undefined): string {
  return normalizeHandleSide(value) || "";
}

function completeEdgeHandles(
  source: string,
  target: string,
  positions: NodePositionMap,
  handles: EdgeHandlePair
): Required<EdgeHandlePair> {
  const inferred = inferEdgeHandles(source, target, positions);
  return {
    sourceHandle: sourceHandleId(normalizeHandleSide(handles.sourceHandle) || normalizeHandleSide(inferred.sourceHandle) || "right"),
    targetHandle: targetHandleId(normalizeHandleSide(handles.targetHandle) || normalizeHandleSide(inferred.targetHandle) || "left")
  };
}

function inferEdgeHandles(source: string, target: string, positions: NodePositionMap): Required<EdgeHandlePair> {
  const sourcePosition = positions.get(source);
  const targetPosition = positions.get(target);
  if (!sourcePosition || !targetPosition) {
    return { sourceHandle: sourceHandleId("right"), targetHandle: targetHandleId("left") };
  }
  const dx = targetPosition.x - sourcePosition.x;
  const dy = targetPosition.y - sourcePosition.y;
  if (Math.abs(dx) >= Math.abs(dy)) {
    return dx >= 0
      ? { sourceHandle: sourceHandleId("right"), targetHandle: targetHandleId("left") }
      : { sourceHandle: sourceHandleId("left"), targetHandle: targetHandleId("right") };
  }
  return dy >= 0
    ? { sourceHandle: sourceHandleId("bottom"), targetHandle: targetHandleId("top") }
    : { sourceHandle: sourceHandleId("top"), targetHandle: targetHandleId("bottom") };
}

function edgeEndpoint(row: Record<string, unknown>, side: "source" | "target"): string {
  const fallback = side === "source" ? row.from_uuid : row.to_uuid;
  return String(row[side] ?? fallback ?? "");
}

function parseJsonObject(text: string): Record<string, unknown> {
  const raw = text.trim();
  if (!raw || raw === "{}") return {};
  try {
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
      return parsed as Record<string, unknown>;
    }
  } catch {
    return { raw_text: raw, parse_error: "invalid_json" };
  }
  return { raw_text: raw };
}

function parseTags(text: string): string[] {
  const raw = text.trim();
  if (!raw) return [];
  if (raw.startsWith("{")) {
    const parsed = parseJsonObject(raw);
    const tags = parsed.tags;
    if (Array.isArray(tags)) return tags.map(String).filter(Boolean);
  }
  return raw.split(",").map((item) => item.trim()).filter(Boolean).slice(0, 12);
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
