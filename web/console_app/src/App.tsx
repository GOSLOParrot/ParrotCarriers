import { Fragment, useCallback, useEffect, useLayoutEffect, useMemo, useReducer, useRef, useState, type MouseEvent as ReactMouseEvent, type ReactNode } from "react";
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
  type NodeDragHandler,
  type NodeMouseHandler,
  type NodeProps,
  type NodeTypes,
  Position,
  type ReactFlowInstance
} from "reactflow";
import { Rnd, type DraggableData } from "react-rnd";
import {
  Activity,
  Bell,
  Camera,
  CalendarDays,
  CheckCircle2,
  CircleDot,
  Database,
  Download,
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
  Save,
  Search,
  Settings,
  ShieldCheck,
  Sparkles,
  Tags,
  Trash2,
  UploadCloud,
  Workflow,
  X
} from "lucide-react";
import { api } from "./api";
import type {
  ConsoleConfig,
  L15Pool,
  Language,
  LiveKitConfig,
  LiveKitToken,
  LiveState,
  MemoryLiveStateChanges,
  Receipt,
  RuntimeCapabilityCatalog,
  RuntimeFlowChanges,
  RuntimeFlow,
  RuntimeWorkflowDrafts,
  TriggerCatalog,
  VisionEvidenceStatus,
  VisionEvidenceTimeline
} from "./types";

type ViewId = "memory" | "runtime";
type TransportMode = "idle" | "connecting" | "sse" | "polling";
type ExecutionMode = "operator" | "preview";
type RuntimeAction =
  | "message_check"
  | "message_push"
  | "llm_push"
  | "scheduler_tick"
  | "calendar_test"
  | "scene_switch"
  | "roleplay_open";

type WorkflowDraftNode = {
  workflow_node_id: string;
  capability: Record<string, unknown>;
  created_at: string;
};

type MemoryNodeData = {
  label: string;
  source?: Record<string, unknown>;
  preview?: boolean;
};

type EdgeHandlePair = {
  sourceHandle?: string;
  targetHandle?: string;
};

type L2BViewGraphSnapshot = {
  nodes: Array<Record<string, unknown>>;
  edges: Array<Record<string, unknown>>;
  signature: string;
  emptyPolls: number;
  heldEmptySnapshot: boolean;
};

type RefreshMemoryOptions = {
  quiet?: boolean;
};

type GraphitiPreviewPayload = {
  hits?: Array<Record<string, unknown>>;
  nodes?: Array<Record<string, unknown>>;
  edges?: Array<Record<string, unknown>>;
  partition?: string;
  query?: string;
  silent?: boolean;
};

type GraphitiStatusSummary = {
  installed: boolean;
  provider: string;
  model: string;
  secretConfigured: boolean;
  embeddingProvider: string;
  embeddingConfigured: boolean;
  partitions: string[];
  message: string;
};

type SourceBoardId = "graphiti" | "obsidian" | "calendar" | "refs" | "manual";
type MemoryToolId = "node" | "edge" | "filter" | "tags" | "subgraph" | "state" | "pool" | "settings";
type FloatingPanelId = "toolbar" | "tool" | "selection";

type FloatingPanelState = {
  x: number;
  y: number;
  width: number | "auto";
  height: number | "auto";
  z: number;
};

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

const FLOATING_PANEL_EDGE_GAP = 8;
const FLOATING_PANEL_STACK_GAP = 12;
const FLOATING_PANEL_DOCK_MARGIN = 16;
const FLOATING_TOOLBAR_DOCK_LIMIT = 10;
const FLOATING_PANEL_MIN_WIDTH = 430;
const FLOATING_PANEL_MIN_HEIGHT = 180;
const FLOATING_PANEL_DEFAULT_HEIGHT = 360;
const FLOATING_PANEL_SELECTION_HEIGHT = 350;
const FLOATING_PANEL_GRID: [number, number] = [8, 8];
const MAX_SAVED_FLOW_POSITION_ABS = 50000;
const EMPTY_L2B_SNAPSHOT_CONFIRM_POLLS = 3;
const NODE_DRAG_EMPTY_SNAPSHOT_GRACE_MS = 1800;
const BLANK_VIEWPORT_HARD_RESET_ATTEMPTS = 2;
const FLOATING_PANEL_RESIZE_ENABLE = {
  top: false,
  topLeft: false,
  topRight: false,
  right: true,
  bottomRight: true,
  bottom: true,
  bottomLeft: true,
  left: true
};
const FLOATING_PANEL_RESIZE_HANDLE_CLASSES = {
  left: "floating-rnd-handle floating-rnd-handle-left",
  right: "floating-rnd-handle floating-rnd-handle-right",
  bottom: "floating-rnd-handle floating-rnd-handle-bottom",
  bottomLeft: "floating-rnd-handle floating-rnd-handle-bottom-left",
  bottomRight: "floating-rnd-handle floating-rnd-handle-bottom-right"
};
const FLOATING_PANEL_DRAG_CANCEL = "button,input,select,textarea,a,details,.nodrag";

const DEFAULT_FLOATING_PANELS: Record<FloatingPanelId, FloatingPanelState> = {
  toolbar: { x: 12, y: 12, width: "auto", height: "auto", z: 24 },
  tool: { x: 24, y: 24, width: 560, height: FLOATING_PANEL_DEFAULT_HEIGHT, z: 22 },
  selection: { x: 24, y: 120, width: 560, height: FLOATING_PANEL_SELECTION_HEIGHT, z: 21 }
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
    triggerChannels: "Ascending channels",
    triggerModules: "Modules",
    triggerInformationTags: "Information tags",
    triggerFireKinds: "Fire kinds",
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
    inspectContext: "Inspect context",
    contextDepth: "Depth",
    contextNodes: "Live nodes",
    contextEdges: "Live edges",
    contextClusters: "Clusters",
    trueConnection: "True connection",
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
    capabilityCatalog: "Capability Catalog",
    capabilitySearch: "Search interfaces, triggers, refs, nodes...",
    capabilityKind: "Kind",
    interactionMode: "Interaction mode",
    allKinds: "All kinds",
    allInteractionModes: "All modes",
    insertWorkflowNode: "Insert",
    workflowDraft: "Workflow draft",
    workflowTitle: "Workflow title",
    saveWorkflow: "Save",
    validateWorkflow: "Validate",
    exportWorkflow: "Export",
    importPreview: "Import preview",
    loadImport: "Load import",
    workflowImportJson: "workflow_schema_v1 JSON",
    workflowDiff: "Import diff",
    loadWorkflow: "Load",
    deleteWorkflow: "Delete",
    runWorkflow: "Run",
    resultRoutes: "Routes",
    resultIntake: "Intake",
    resultIntakeLog: "Result intake",
    noResultIntakes: "No result intake entries.",
    deleteResultIntake: "Delete intake",
    actionGates: "Action gates",
    createGate: "Gate",
    applyGate: "Apply",
    savedWorkflows: "Saved workflows",
    noWorkflowNodes: "No workflow nodes inserted yet.",
    noSavedWorkflows: "No saved workflows.",
    noCapabilityMatches: "No matching capabilities.",
    executeNode: "Fire",
    draftPlan: "Import Plan",
    planCompatible: "Plan compatible",
    capabilityPolicy: "Policy",
    operatorSafe: "preview mode",
    dryRunOnly: "preview only",
    previewMode: "preview",
    executeMode: "execute",
    safeMode: "preview",
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
    memoryDraft: "Memory Draft",
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
    previewGraphitiMaterialize: "Preview L2-B Import",
    materializeGraphitiSubgraph: "Import Subgraph to L2-B",
    identityIndex: "Identity Index",
    verifyRefs: "Verify Refs",
    refScanPlan: "Ref Scan Plan",
    dispatchRefScan: "Dispatch Scan",
    refScanResults: "Scan Results",
    resolveGraphitiEdges: "Resolve Edges",
    previewGraphitiEdge: "Preview Edge Apply",
    materializeGraphitiEdge: "Import Edge to L2-B",
    graphitiRefWriteback: "Graphiti Ref Write-back",
    draftGraphitiRef: "Preview Ref",
    applyGraphitiRef: "Apply RefIndex",
    writeAuditEpisode: "Write audit Episode",
    resolverPreview: "Resolver preview",
    selectedHits: "Selected hits",
    selectAll: "Select all",
    selectedOf: "selected",
    resultGraph: "Result graph",
    noHits: "No hits yet.",
    writeThroughL15: "writes through L1.5",
    graphitiWriteThroughL2B: "materializes Graphiti pointers into L2-B",
    sourceBoardHint: "Graphiti can materialize pointer subgraphs directly into L2-B; other sources still preview or admit through L1.5 first.",
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
    sampleSmoke: "Sampling smoke",
    screenReady: "Screen evidence ready",
    notReady: "Not ready",
    nextSteps: "Next steps",
    freshAnyEvidence: "fresh evidence",
    likelyScreenShare: "screen source",
    freshScreenShare: "fresh screen",
    liveKitEvents: "Events",
    liveKitTranscripts: "Transcript",
    liveKitBridgeHint: "Use screen share when there is no camera. Brain must be running in the same room.",
    googleCalendar: "Google Calendar",
    calendarFetch: "Fetch Preview",
    calendarFetchExecute: "Dispatch Fetch",
    calendarApiFetch: "Local API",
    calendarNanobotFetch: "ECS Nanobot",
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
    capabilityCatalog: "能力目录",
    capabilitySearch: "搜索接口、触发器、Refs、Nodes...",
    capabilityKind: "类型",
    interactionMode: "互动模式",
    allKinds: "全部类型",
    allInteractionModes: "全部模式",
    insertWorkflowNode: "插入",
    workflowDraft: "工作流草稿",
    workflowTitle: "工作流标题",
    saveWorkflow: "保存",
    validateWorkflow: "校验",
    exportWorkflow: "导出",
    importPreview: "导入预览",
    loadImport: "载入导入",
    workflowImportJson: "workflow_schema_v1 JSON",
    workflowDiff: "导入差异",
    loadWorkflow: "加载",
    deleteWorkflow: "删除",
    runWorkflow: "运行",
    resultRoutes: "结果路由",
    resultIntake: "结果回流",
    resultIntakeLog: "结果回流",
    noResultIntakes: "暂无结果回流记录。",
    deleteResultIntake: "删除回流",
    actionGates: "动作 Gate",
    createGate: "建 Gate",
    applyGate: "执行",
    savedWorkflows: "已保存工作流",
    noWorkflowNodes: "还没有插入工作流节点。",
    noSavedWorkflows: "暂无已保存工作流。",
    noCapabilityMatches: "没有匹配的能力。",
    executeNode: "触发",
    draftPlan: "导入 Plan",
    planCompatible: "可进 Plan",
    capabilityPolicy: "策略",
    operatorSafe: "预演模式",
    dryRunOnly: "仅预演",
    previewMode: "预演",
    executeMode: "执行",
    safeMode: "未执行",
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
    memorySummary: "L1.5、L2-B、Graphiti、Refs、Evidence Board 和图上 Mode 管理操作。",
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
    memoryDraft: "Memory 草稿",
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
    previewGraphitiMaterialize: "预演 L2-B 导入",
    materializeGraphitiSubgraph: "导入子图到 L2-B",
    selectedHits: "选中结果",
    selectAll: "全选",
    selectedOf: "已选",
    resultGraph: "结果子图",
    noHits: "暂无结果。",
    writeThroughL15: "通过 L1.5 写入",
    graphitiWriteThroughL2B: "Graphiti 指针子图物化到 L2-B",
    sourceBoardHint: "Graphiti 可直接物化指针子图到 L2-B；其他来源仍先预览或进入 L1.5。",
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
    sampleSmoke: "采样检查",
    screenReady: "屏幕证据已就绪",
    notReady: "尚未就绪",
    nextSteps: "下一步",
    freshAnyEvidence: "新鲜证据",
    likelyScreenShare: "屏幕来源",
    freshScreenShare: "新鲜屏幕帧",
    liveKitEvents: "事件",
    liveKitTranscripts: "转写",
    liveKitBridgeHint: "没有摄像头时用屏幕共享。Brain 必须在同一个房间运行。",
    googleCalendar: "Google 日程",
    calendarFetch: "请求获取",
    calendarFetchExecute: "真实请求",
    calendarApiFetch: "本地 API",
    calendarNanobotFetch: "ECS Nanobot",
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

function parseMemoryDeltaEvent(event: Event): MemoryLiveStateChanges | null {
  try {
    const data = (event as MessageEvent<string>).data;
    return JSON.parse(data) as MemoryLiveStateChanges;
  } catch {
    return null;
  }
}

function parseRuntimeDeltaEvent(event: Event): RuntimeFlowChanges | null {
  try {
    const data = (event as MessageEvent<string>).data;
    return JSON.parse(data) as RuntimeFlowChanges;
  } catch {
    return null;
  }
}

function transportTone(mode: TransportMode): "idle" | "connecting" | "live" | "fallback" {
  if (mode === "sse") return "live";
  if (mode === "polling") return "fallback";
  if (mode === "connecting") return "connecting";
  return "idle";
}

function transportText(mode: TransportMode, fallbackText: string): string {
  if (mode === "sse") return "SSE · LIVE";
  if (mode === "polling") return "POLL · FALLBACK";
  if (mode === "connecting") return "CONNECTING";
  return fallbackText;
}

function clampNumber(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function defaultFloatingPanelWidth(canvasWidth: number): number {
  const available = Math.max(FLOATING_PANEL_MIN_WIDTH, canvasWidth - FLOATING_PANEL_DOCK_MARGIN * 2);
  const preferred = Math.max(560, Math.round(canvasWidth * 0.42));
  return Math.min(680, available, preferred);
}

function floatingPanelStateEquals(left: FloatingPanelState, right: FloatingPanelState): boolean {
  return left.x === right.x
    && left.y === right.y
    && left.width === right.width
    && left.height === right.height
    && left.z === right.z;
}

export function App() {
  const [view, setView] = useState<ViewId>("memory");
  const [language, setLanguage] = useState<Language>(() => (localStorage.getItem("parrot.console.lang") as Language) || "zh");
  const [executionMode, setExecutionMode] = useState<ExecutionMode>(() => {
    const saved = localStorage.getItem("parrot.console.executionMode");
    return saved === "preview" || saved === "operator" ? saved : "operator";
  });
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [config, setConfig] = useState<ConsoleConfig>({});
  const [liveState, setLiveState] = useState<LiveState>({});
  const [l15Pool, setL15Pool] = useState<L15Pool>({});
  const [runtimeFlow, setRuntimeFlow] = useState<RuntimeFlow>({});
  const [triggerCatalog, setTriggerCatalog] = useState<TriggerCatalog>({});
  const [capabilityCatalog, setCapabilityCatalog] = useState<RuntimeCapabilityCatalog>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [memoryTransport, setMemoryTransport] = useState<TransportMode>("connecting");
  const [runtimeTransport, setRuntimeTransport] = useState<TransportMode>("idle");
  const [receipts, pushReceipt] = useReducer(receiptReducer, []);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [recordsOpen, setRecordsOpen] = useState(false);
  const [applyingProfile, setApplyingProfile] = useState("");
  const [connectionEpoch, setConnectionEpoch] = useState(0);
  const memorySequenceRef = useRef(0);
  const runtimeSequenceRef = useRef(0);
  const memorySseOpenRef = useRef(false);
  const runtimeSseOpenRef = useRef(false);
  const t = { ...dict.en, ...dict[language], ...(language === "zh" ? zhRuntimeCopy : {}) };
  const configuredRefreshIntervalS = Math.max(3, Math.round(Number(config.refresh_interval_s ?? 5)));
  const refreshIntervalS = view === "memory" ? Math.min(configuredRefreshIntervalS, 5) : configuredRefreshIntervalS;
  const activeTransport = view === "memory" ? memoryTransport : runtimeTransport;
  const transportStatusText = transportText(activeTransport, `${t.autoRefresh} ${refreshIntervalS}s`);
  const livePillClass = `live-pill ${transportTone(activeTransport)}${loading ? " loading" : ""}`;
  const operatorMode = executionMode === "operator";
  const environment = config.environment ?? {};
  const environmentActive = recordFromUnknown(environment.active);
  const environmentProfile = environment.profile || "local-bff";
  const environmentService = environment.service || "web-console";
  const memoryBackendKey = [
    String(environmentProfile),
    String(environmentService),
    String(environmentActive.app_api_base_url || ""),
    String(environmentActive.graphiti_proxy_url || ""),
    String(environmentActive.livekit_url || ""),
    String(environmentActive.room || "")
  ].join("|");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [nextConfig, memoryChanges, nextPool, flowChanges, nextTriggerCatalog, nextCapabilityCatalog] = await Promise.all([
        api.config(),
        memorySseOpenRef.current
          ? Promise.resolve({ changed: false, sequence: memorySequenceRef.current } as MemoryLiveStateChanges)
          : api.memoryLiveChanges(memorySequenceRef.current),
        api.l15Pool(),
        runtimeSseOpenRef.current
          ? Promise.resolve({ changed: false, sequence: runtimeSequenceRef.current } as RuntimeFlowChanges)
          : api.runtimeFlowChanges(runtimeSequenceRef.current),
        api.triggerCatalog(),
        api.runtimeCapabilities()
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
      setCapabilityCatalog(nextCapabilityCatalog);
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshMemoryNow = useCallback(async (options: RefreshMemoryOptions = {}) => {
    const quiet = options.quiet === true;
    if (!quiet) {
      setLoading(true);
      setError("");
    }
    try {
      const [snapshot, nextPool] = await Promise.all([
        api.liveState(),
        api.l15Pool()
      ]);
      setLiveState(snapshot);
      setL15Pool(nextPool);
      if (!quiet) {
        const buckets = nextPool.buckets ?? [];
        pushReceipt(localReceipt("memory.refresh_after_import", true, {
          l2b_nodes: snapshot.l2b?.node_count ?? 0,
          l2b_edges: snapshot.l2b?.edge_count ?? 0,
          l15_buckets: buckets.length,
          l15_nodes: buckets.reduce((total, bucket) => total + Number(bucket.node_count ?? 0), 0),
          blackboard: snapshot.blackboard?.present_count ?? 0,
          intent_refs: snapshot.intent_workspace?.ref_count ?? 0
        }, { dryRun: false }));
      }
    } catch (exc) {
      if (!quiet) {
        setError(exc instanceof Error ? exc.message : String(exc));
        pushReceipt(errorReceipt("memory.refresh_after_import", exc));
      }
    } finally {
      if (!quiet) {
        setLoading(false);
      }
    }
  }, []);

  const applyConnectionProfile = useCallback(async (profile: string) => {
    const target = profile.trim();
    if (!target) return;
    setApplyingProfile(target);
    setLoading(true);
    setError("");
    try {
      const receipt = await api.consoleProfileApply({ profile: target });
      if (receipt.config) {
        setConfig(receipt.config);
      }
      memorySequenceRef.current = 0;
      runtimeSequenceRef.current = 0;
      setLiveState({});
      setRuntimeFlow({});
      setConnectionEpoch((value) => value + 1);
      pushReceipt(localReceipt("console.profile.apply", receipt.success !== false, {
        profile: receipt.profile || target,
        service: receipt.config?.environment?.service || "web-console",
        graphiti_proxy_url: String(receipt.config?.environment?.active?.graphiti_proxy_url || ""),
        app_api_base_url: String(receipt.config?.environment?.active?.app_api_base_url || ""),
        note: "SSE sequence reset; next refresh reads the selected profile."
      }, { dryRun: false }));
      await refreshMemoryNow();
    } catch (exc) {
      setError(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("console.profile.apply", exc, { profile: target }));
    } finally {
      setApplyingProfile("");
      setLoading(false);
    }
  }, [refreshMemoryNow]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    const timer = window.setInterval(() => void load(), refreshIntervalS * 1000);
    return () => window.clearInterval(timer);
  }, [load, refreshIntervalS]);

  useEffect(() => {
    if (typeof window.EventSource !== "function") {
      setMemoryTransport("polling");
      return;
    }

    const params = new URLSearchParams({
      since: String(memorySequenceRef.current),
      limit: "120",
      interval_s: "1",
      heartbeat_s: "15"
    });
    const source = new EventSource("/api/memory/live-state/stream?" + params.toString());

    source.onopen = () => {
      memorySseOpenRef.current = true;
      setMemoryTransport("sse");
    };
    source.onerror = () => {
      memorySseOpenRef.current = false;
      setMemoryTransport("polling");
    };
    source.addEventListener("memory_delta", (event) => {
      const payload = parseMemoryDeltaEvent(event);
      if (!payload) return;
      if (typeof payload.sequence === "number") {
        memorySequenceRef.current = payload.sequence;
      }
      if (payload.changed && payload.snapshot) {
        setLiveState(payload.snapshot);
      }
    });

    return () => {
      memorySseOpenRef.current = false;
      source.close();
    };
  }, [connectionEpoch]);

  useEffect(() => {
    if (view !== "runtime") {
      runtimeSseOpenRef.current = false;
      setRuntimeTransport("idle");
      return;
    }
    if (typeof window.EventSource !== "function") {
      setRuntimeTransport("polling");
      return;
    }

    setRuntimeTransport("connecting");
    const params = new URLSearchParams({
      since: String(runtimeSequenceRef.current),
      interval_s: "1",
      heartbeat_s: "15"
    });
    const source = new EventSource("/api/runtime/flow/stream?" + params.toString());

    source.onopen = () => {
      runtimeSseOpenRef.current = true;
      setRuntimeTransport("sse");
    };
    source.onerror = () => {
      runtimeSseOpenRef.current = false;
      setRuntimeTransport("polling");
    };
    source.addEventListener("runtime_delta", (event) => {
      const payload = parseRuntimeDeltaEvent(event);
      if (!payload) return;
      if (typeof payload.sequence === "number") {
        runtimeSequenceRef.current = payload.sequence;
      }
      if (payload.changed && payload.snapshot) {
        setRuntimeFlow(payload.snapshot);
      }
    });

    return () => {
      runtimeSseOpenRef.current = false;
      source.close();
    };
  }, [connectionEpoch, view]);

  const setLang = (next: Language) => {
    localStorage.setItem("parrot.console.lang", next);
    setLanguage(next);
  };

  const setMode = (next: ExecutionMode) => {
    localStorage.setItem("parrot.console.executionMode", next);
    setExecutionMode(next);
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
            <span className={livePillClass}>
              <Sparkles size={15} /> {t.live} / {transportStatusText}
            </span>
            <span className="mode-chip">
              <Link2 size={14} /> {environmentProfile} / {environmentService}
            </span>
            <span className={operatorMode ? "mode-chip active" : "mode-chip"}>
              <ShieldCheck size={14} /> {operatorMode ? "真实连接" : "预演模式"}
            </span>
            {error ? <span className="error-pill">{error}</span> : null}
            <button className="button" onClick={() => void load()}><RefreshCw size={16} /> {t.refresh}</button>
            <div className="settings-wrap">
              <button className={settingsOpen ? "button ghost active" : "button ghost"} onClick={() => setSettingsOpen((open) => !open)}>
                <Settings size={16} /> {t.settings}
              </button>
              {settingsOpen ? (
                <div className="settings-popover">
                  <strong>Mode</strong>
                  <small>Web Console is a test bench. Default is real operator execution.</small>
                  <button
                    className={operatorMode ? "mode-option active" : "mode-option"}
                    onClick={() => setMode("operator")}
                  >
                    <ShieldCheck size={15} />
                    <span>
                      <strong>真实连接测试</strong>
                      <small>dry_run=false / operator_mode=true</small>
                    </span>
                  </button>
                  <button
                    className={!operatorMode ? "mode-option active" : "mode-option"}
                    onClick={() => setMode("preview")}
                  >
                    <CircleDot size={15} />
                    <span>
                      <strong>预演检查</strong>
                      <small>dry_run=true / operator_mode=false</small>
                    </span>
                  </button>
                  <ConsoleConnectionSummary
                    config={config}
                    applyingProfile={applyingProfile}
                    onApplyProfile={(profile) => void applyConnectionProfile(profile)}
                  />
                </div>
              ) : null}
            </div>
          </div>
        </header>

        {view === "memory" ? (
          <MemoryGraphWorkspace
            liveState={liveState}
            l15Pool={l15Pool}
            memoryBackendKey={memoryBackendKey}
            pushReceipt={pushReceipt}
            t={t}
            operatorMode={operatorMode}
            onRefreshMemory={refreshMemoryNow}
          />
        ) : (
          <RuntimeFlowWorkspace flow={runtimeFlow} triggerCatalog={triggerCatalog} capabilityCatalog={capabilityCatalog} pushReceipt={pushReceipt} t={t} operatorMode={operatorMode} />
        )}
      </main>

      <ReceiptRail receipts={receipts} t={t} open={recordsOpen} onToggle={() => setRecordsOpen((open) => !open)} />
    </div>
  );
}

function ConsoleConnectionSummary({
  config,
  applyingProfile,
  onApplyProfile
}: {
  config: ConsoleConfig;
  applyingProfile: string;
  onApplyProfile: (profile: string) => void;
}) {
  const environment = config.environment ?? {};
  const active = recordFromUnknown(environment.active);
  const secrets = recordFromUnknown(environment.secrets);
  const profiles = Array.isArray(environment.profiles)
    ? environment.profiles.filter((row): row is Record<string, unknown> => Boolean(row) && typeof row === "object" && !Array.isArray(row))
    : [];
  const warnings = Array.isArray(environment.warnings)
    ? environment.warnings.map((warning) => String(warning || "")).filter(Boolean)
    : [];
  const profile = String(environment.profile || active.profile || "unknown");
  const service = String(environment.service || "unknown");
  const appTarget = String(active.dev_proxy_target || active.app_api_base_url || active.api_path || "/api");
  const graphitiTarget = String(active.graphiti_proxy_url || "same target");
  const runtimeRoot = String(active.runtime_data_root || "server default");

  return (
    <div className="connection-panel">
      <strong><Link2 size={14} /> Connection</strong>
      <div className="connection-grid">
        <span>Profile</span><code>{profile}</code>
        <span>Service</span><code>{service}</code>
        <span>API target</span><code>{appTarget}</code>
        <span>Graphiti</span><code>{graphitiTarget}</code>
        <span>Runtime data</span><code>{runtimeRoot}</code>
      </div>
      <div className="connection-secrets">
        <span className={secrets.app_monitor_secret_configured ? "secret-dot on" : "secret-dot"}>App write</span>
        <span className={secrets.orchestrator_secret_configured ? "secret-dot on" : "secret-dot"}>Orch auth</span>
        <span className={secrets.google_credentials_configured ? "secret-dot on" : "secret-dot"}>Google OAuth</span>
      </div>
      {profiles.length ? (
        <div className="connection-profiles">
          {profiles.map((row) => (
            <button
              key={String(row.id || row.label)}
              className={String(row.id || "") === profile ? "profile-switch active" : "profile-switch"}
              disabled={!row.id || applyingProfile === String(row.id)}
              onClick={() => onApplyProfile(String(row.id || ""))}
            >
              <strong>{applyingProfile === String(row.id) ? "switching..." : String(row.id || row.label)}</strong>
              <small>{String(row.app_api_base_url || "")}</small>
            </button>
          ))}
        </div>
      ) : null}
      {warnings.length ? (
        <div className="connection-warnings">
          {warnings.map((warning) => <small key={warning}>{warning}</small>)}
        </div>
      ) : null}
    </div>
  );
}

function MemoryGraphWorkspace({
  liveState,
  l15Pool,
  memoryBackendKey,
  pushReceipt,
  t,
  operatorMode,
  onRefreshMemory
}: {
  liveState: LiveState;
  l15Pool: L15Pool;
  memoryBackendKey: string;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  operatorMode: boolean;
  onRefreshMemory: (options?: RefreshMemoryOptions) => Promise<void>;
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
  const [subgraphDepth, setSubgraphDepth] = useState("1");
  const [subgraphContext, setSubgraphContext] = useState<Record<string, unknown> | null>(null);
  const [graphDestination, setGraphDestination] = useState("isolated_compartment");
  const [graphTransformKind, setGraphTransformKind] = useState("wrap_selection");
  const [graphHealth, setGraphHealth] = useState<Record<string, unknown> | null>(null);
  const [stateColors, setStateColors] = useState(true);
  const [manualPositions, setManualPositions] = useState<Record<string, { x: number; y: number }>>({});
  const [dragBufferedGraph, setDragBufferedGraph] = useState<{
    nodes: Array<Record<string, unknown>>;
    edges: Array<Record<string, unknown>>;
  } | null>(null);
  const [l2bViewGraph, setL2bViewGraph] = useState<L2BViewGraphSnapshot>({
    nodes: [],
    edges: [],
    signature: "",
    emptyPolls: 0,
    heldEmptySnapshot: false
  });
  const [flowRenderVersion, setFlowRenderVersion] = useState(0);
  const [flowInstance, setFlowInstance] = useState<ReactFlowInstance<MemoryNodeData> | null>(null);
  const lastAutoFitSignatureRef = useRef("");
  const lastBlankViewportRecoveryKeyRef = useRef("");
  const blankViewportRecoveryAttemptsRef = useRef(0);
  const nodeDragActiveRef = useRef(false);
  const lastNodeDragEndedAtRef = useRef(0);
  const lastCountedEmptyL2bSnapshotKeyRef = useRef("");
  const lastIncompleteL2bSnapshotRefreshKeyRef = useRef("");
  const incompleteL2bSnapshotRefreshInFlightRef = useRef(false);
  const dragBufferReleaseTimerRef = useRef<number | null>(null);
  const [activeTool, setActiveTool] = useState<MemoryToolId | null>(null);
  const canvasRef = useRef<HTMLDivElement | null>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 0, height: 0 });
  const userMovedPanelsRef = useRef<Partial<Record<FloatingPanelId, boolean>>>({});
  const [floatingPanels, setFloatingPanels] = useState<Record<FloatingPanelId, FloatingPanelState>>(DEFAULT_FLOATING_PANELS);
  const floatingPanelZRef = useRef(30);
  const [toolbarVertical, setToolbarVertical] = useState(false);
  const [panelOpenVersion, setPanelOpenVersion] = useState({ tool: 0, selection: 0 });
  const layoutReady = canvasSize.width > 0 && canvasSize.height > 0;

  const bringPanelForward = useCallback((panelId: FloatingPanelId) => {
    const next = floatingPanelZRef.current + 1;
    floatingPanelZRef.current = next;
    setFloatingPanels((panels) => ({
      ...panels,
      [panelId]: { ...panels[panelId], z: next }
    }));
  }, []);

  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const updateCanvasSize = () => {
      const rect = canvas.getBoundingClientRect();
      const width = Math.round(rect.width);
      const height = Math.round(rect.height);
      setCanvasSize((current) => (
        Math.abs(current.width - width) < 2 && Math.abs(current.height - height) < 2
          ? current
          : { width, height }
      ));
    };

    updateCanvasSize();
    if (typeof ResizeObserver === "undefined") {
      window.addEventListener("resize", updateCanvasSize);
      return () => window.removeEventListener("resize", updateCanvasSize);
    }

    const observer = new ResizeObserver(updateCanvasSize);
    observer.observe(canvas);
    return () => observer.disconnect();
  }, []);

  useEffect(() => () => {
    if (dragBufferReleaseTimerRef.current != null) {
      window.clearTimeout(dragBufferReleaseTimerRef.current);
    }
  }, []);

  useEffect(() => {
    if (dragBufferReleaseTimerRef.current != null) {
      window.clearTimeout(dragBufferReleaseTimerRef.current);
      dragBufferReleaseTimerRef.current = null;
    }
    nodeDragActiveRef.current = false;
    lastNodeDragEndedAtRef.current = 0;
    lastCountedEmptyL2bSnapshotKeyRef.current = "";
    lastIncompleteL2bSnapshotRefreshKeyRef.current = "";
    incompleteL2bSnapshotRefreshInFlightRef.current = false;
    lastAutoFitSignatureRef.current = "";
    lastBlankViewportRecoveryKeyRef.current = "";
    blankViewportRecoveryAttemptsRef.current = 0;
    setL2bViewGraph({
      nodes: [],
      edges: [],
      signature: "",
      emptyPolls: 0,
      heldEmptySnapshot: false
    });
    setDragBufferedGraph(null);
    setFlowInstance(null);
    setFlowRenderVersion((version) => version + 1);
    setManualPositions({});
    setPreviewNodes([]);
    setPreviewEdges([]);
    setSubgraphContext(null);
    setGraphHealth(null);
    setSelected(null);
    setEdgeFrom("");
    setEdgeTo("");
  }, [memoryBackendKey]);

  // react-rnd owns pointer drag/resize; this only keeps controlled panel state inside the canvas after release.
  const fitFloatingPanelState = useCallback((
    panelId: FloatingPanelId,
    rawPanel: FloatingPanelState,
    measuredWidth?: number,
    measuredHeight?: number
  ): FloatingPanelState => {
    if (!canvasSize.width || !canvasSize.height) return rawPanel;

    const edgeGap = FLOATING_PANEL_EDGE_GAP;
    const measuredPanelWidth = measuredWidth
      ?? (typeof rawPanel.width === "number" ? rawPanel.width : 180);
    const measuredPanelHeight = measuredHeight
      ?? (typeof rawPanel.height === "number" ? rawPanel.height : 48);
    const maxWidth = Math.max(FLOATING_PANEL_MIN_WIDTH, canvasSize.width - edgeGap * 2);
    const maxHeight = Math.max(FLOATING_PANEL_MIN_HEIGHT, canvasSize.height - edgeGap * 2);
    const panelWidth = panelId === "toolbar"
      ? measuredPanelWidth
      : clampNumber(measuredPanelWidth, FLOATING_PANEL_MIN_WIDTH, maxWidth);
    const panelHeight = panelId === "toolbar"
      ? measuredPanelHeight
      : clampNumber(measuredPanelHeight, FLOATING_PANEL_MIN_HEIGHT, maxHeight);
    const maxX = Math.max(edgeGap, canvasSize.width - panelWidth - edgeGap);
    const maxY = Math.max(edgeGap, canvasSize.height - panelHeight - edgeGap);
    let nextX = clampNumber(rawPanel.x, edgeGap, maxX);
    let nextY = clampNumber(rawPanel.y, edgeGap, maxY);

    if (nextX <= FLOATING_PANEL_DOCK_MARGIN) nextX = edgeGap;
    if (nextY <= FLOATING_PANEL_DOCK_MARGIN) nextY = edgeGap;
    if (canvasSize.width - (nextX + panelWidth) <= FLOATING_PANEL_DOCK_MARGIN) nextX = maxX;
    if (canvasSize.height - (nextY + panelHeight) <= FLOATING_PANEL_DOCK_MARGIN) nextY = maxY;

    return {
      ...rawPanel,
      x: nextX,
      y: nextY,
      width: panelId === "toolbar" ? rawPanel.width : panelWidth,
      height: panelId === "toolbar" ? rawPanel.height : panelHeight
    };
  }, [canvasSize.height, canvasSize.width]);

  const defaultFloatingPanelLayout = useCallback((
    panelId: FloatingPanelId,
    panels: Record<FloatingPanelId, FloatingPanelState>,
    nextActiveTool = activeTool,
    hasSelection = Boolean(selected)
  ): FloatingPanelState => {
    const panel = panels[panelId];
    if (!layoutReady || panelId === "toolbar") {
      return fitFloatingPanelState(panelId, panel);
    }

    const bothPanelsOpen = Boolean(hasSelection && nextActiveTool);
    const sideBySideAvailableWidth = canvasSize.width - (FLOATING_PANEL_DOCK_MARGIN * 2) - FLOATING_PANEL_STACK_GAP;
    const canPlaceSideBySide = bothPanelsOpen && sideBySideAvailableWidth >= FLOATING_PANEL_MIN_WIDTH * 2;
    const dockWidth = canPlaceSideBySide
      ? clampNumber(Math.floor(sideBySideAvailableWidth / 2), FLOATING_PANEL_MIN_WIDTH, 560)
      : defaultFloatingPanelWidth(canvasSize.width);
    const dockX = Math.max(
      FLOATING_PANEL_EDGE_GAP,
      canvasSize.width - dockWidth - FLOATING_PANEL_DOCK_MARGIN
    );
    const stackHeight = bothPanelsOpen && !canPlaceSideBySide
      ? clampNumber(
        Math.floor((canvasSize.height - FLOATING_PANEL_DOCK_MARGIN * 2 - FLOATING_PANEL_STACK_GAP) / 2),
        FLOATING_PANEL_MIN_HEIGHT,
        FLOATING_PANEL_DEFAULT_HEIGHT
      )
      : undefined;

    if (panelId === "tool" && nextActiveTool) {
      return fitFloatingPanelState("tool", {
        ...panel,
        x: canPlaceSideBySide ? FLOATING_PANEL_DOCK_MARGIN : dockX,
        y: FLOATING_PANEL_DOCK_MARGIN,
        width: dockWidth,
        height: stackHeight ?? (typeof panel.height === "number" ? panel.height : FLOATING_PANEL_DEFAULT_HEIGHT)
      });
    }

    if (panelId === "selection" && hasSelection) {
      return fitFloatingPanelState("selection", {
        ...panel,
        x: dockX,
        y: bothPanelsOpen && !canPlaceSideBySide && stackHeight
          ? FLOATING_PANEL_DOCK_MARGIN + stackHeight + FLOATING_PANEL_STACK_GAP
          : FLOATING_PANEL_DOCK_MARGIN,
        width: dockWidth,
        height: stackHeight ?? (typeof panel.height === "number" ? panel.height : FLOATING_PANEL_SELECTION_HEIGHT)
      });
    }

    return fitFloatingPanelState(panelId, panel);
  }, [activeTool, canvasSize.width, fitFloatingPanelState, layoutReady, selected]);

  const openMemoryTool = useCallback((tool: MemoryToolId) => {
    if (activeTool === tool) {
      setActiveTool(null);
      return;
    }

    userMovedPanelsRef.current.tool = false;
    setFloatingPanels((panels) => {
      let nextPanels = {
        ...panels,
        tool: defaultFloatingPanelLayout("tool", panels, tool, Boolean(selected))
      };
      if (selected && !userMovedPanelsRef.current.selection) {
        nextPanels = {
          ...nextPanels,
          selection: defaultFloatingPanelLayout("selection", nextPanels, tool, true)
        };
      }
      return nextPanels;
    });
    setPanelOpenVersion((current) => ({ ...current, tool: current.tool + 1 }));
    setActiveTool(tool);
  }, [activeTool, defaultFloatingPanelLayout, selected]);

  const openSelectionInspector = useCallback((nextSelected: Record<string, unknown>) => {
    userMovedPanelsRef.current.selection = false;
    setFloatingPanels((panels) => {
      let nextPanels = panels;
      if (activeTool && !userMovedPanelsRef.current.tool) {
        nextPanels = {
          ...nextPanels,
          tool: defaultFloatingPanelLayout("tool", nextPanels, activeTool, true)
        };
      }
      return {
        ...nextPanels,
        selection: defaultFloatingPanelLayout("selection", nextPanels, activeTool, true)
      };
    });
    setPanelOpenVersion((current) => ({ ...current, selection: current.selection + 1 }));
    setSelected(nextSelected);
  }, [activeTool, defaultFloatingPanelLayout]);

  useLayoutEffect(() => {
    if (!layoutReady) return;

    setFloatingPanels((panels) => {
      let nextPanels = panels;
      const assignPanel = (panelId: FloatingPanelId, panel: FloatingPanelState) => {
        if (floatingPanelStateEquals(nextPanels[panelId], panel)) return;
        nextPanels = {
          ...nextPanels,
          [panelId]: panel
        };
      };

      assignPanel("toolbar", fitFloatingPanelState("toolbar", panels.toolbar));

      if (activeTool && !userMovedPanelsRef.current.tool) {
        assignPanel("tool", defaultFloatingPanelLayout("tool", nextPanels));
      }

      if (selected && !userMovedPanelsRef.current.selection) {
        assignPanel("selection", defaultFloatingPanelLayout("selection", nextPanels));
      }

      return nextPanels;
    });
  }, [activeTool, defaultFloatingPanelLayout, fitFloatingPanelState, layoutReady, selected]);

  const markFloatingPanelInteraction = useCallback((panelId: FloatingPanelId) => {
    userMovedPanelsRef.current[panelId] = true;
    bringPanelForward(panelId);
  }, [bringPanelForward]);

  const handleFloatingDragStop = useCallback((panelId: FloatingPanelId, data: DraggableData) => {
    const width = data.node.offsetWidth;
    const height = data.node.offsetHeight;
    setFloatingPanels((panels) => ({
      ...panels,
      [panelId]: fitFloatingPanelState(
        panelId,
        { ...panels[panelId], x: data.x, y: data.y },
        width,
        height
      )
    }));
    if (panelId === "toolbar") {
      const nextX = fitFloatingPanelState(panelId, { ...floatingPanels[panelId], x: data.x, y: data.y }, width, height).x;
      setToolbarVertical(nextX <= FLOATING_TOOLBAR_DOCK_LIMIT || nextX >= canvasSize.width - width - FLOATING_TOOLBAR_DOCK_LIMIT);
    }
  }, [canvasSize.width, fitFloatingPanelState, floatingPanels]);

  const handleFloatingResizeStop = useCallback((
    panelId: FloatingPanelId,
    ref: HTMLElement,
    position: { x: number; y: number }
  ) => {
    setFloatingPanels((panels) => ({
      ...panels,
      [panelId]: fitFloatingPanelState(
        panelId,
        { ...panels[panelId], x: position.x, y: position.y, width: ref.offsetWidth, height: ref.offsetHeight },
        ref.offsetWidth,
        ref.offsetHeight
      )
    }));
  }, [fitFloatingPanelState]);

  const floatingPanelPosition = (panelId: FloatingPanelId) => {
    const panel = floatingPanels[panelId];
    return { x: panel.x, y: panel.y };
  };

  const floatingPanelSize = (panelId: FloatingPanelId) => {
    const panel = floatingPanels[panelId];
    if (panel.width === "auto" || panel.height === "auto") return undefined;
    return { width: panel.width, height: panel.height };
  };

  const floatingPanelMaxWidth = Math.max(FLOATING_PANEL_MIN_WIDTH, canvasSize.width - FLOATING_PANEL_EDGE_GAP * 2);
  const floatingPanelMaxHeight = Math.max(FLOATING_PANEL_MIN_HEIGHT, canvasSize.height - FLOATING_PANEL_EDGE_GAP * 2);

  const rawL2bNodes = liveState.l2b?.nodes ?? [];
  const rawL2bEdges = liveState.l2b?.edges ?? [];
  const reportedL2bNodeCount = Number(liveState.l2b?.node_count ?? 0);
  const reportedL2bEdgeCount = Number(liveState.l2b?.edge_count ?? 0);
  const rawL2bSignature = useMemo(
    () => l2bGraphSignature(rawL2bNodes, rawL2bEdges),
    [rawL2bEdges, rawL2bNodes]
  );
  const liveSnapshotVersion = String(liveState.sequence ?? liveState.generated_at ?? rawL2bSignature);
  const rawL2bSnapshotKey = `${liveSnapshotVersion}:${rawL2bSignature}`;
  const hasIncomingLiveGraph = rawL2bNodes.length > 0 || rawL2bEdges.length > 0;
  const hasReportedL2bGraph = reportedL2bNodeCount > 0 || reportedL2bEdgeCount > 0;
  const hasIncompleteL2bSnapshot = hasReportedL2bGraph && !hasIncomingLiveGraph;

  useEffect(() => {
    const shouldCountEmptySnapshot = (
      !hasIncomingLiveGraph
      && !hasIncompleteL2bSnapshot
      && lastCountedEmptyL2bSnapshotKeyRef.current !== rawL2bSnapshotKey
    );
    if (hasIncomingLiveGraph) {
      lastCountedEmptyL2bSnapshotKeyRef.current = "";
    } else if (shouldCountEmptySnapshot) {
      lastCountedEmptyL2bSnapshotKeyRef.current = rawL2bSnapshotKey;
    }

    setL2bViewGraph((current) => {
      const hasLiveGraph = hasIncomingLiveGraph;
      const hasCurrentGraph = current.nodes.length > 0 || current.edges.length > 0;

      if (hasLiveGraph) {
        const nodes = mergeGraphRowsByStableId(current.nodes, rawL2bNodes);
        const edges = rawL2bEdges;
        const signature = l2bGraphSignature(nodes, edges);
        if (
          current.signature === signature
          && current.emptyPolls === 0
          && !current.heldEmptySnapshot
        ) {
          return current;
        }
        return {
          nodes,
          edges,
          signature,
          emptyPolls: 0,
          heldEmptySnapshot: false
        };
      }

      if (hasIncompleteL2bSnapshot) {
        return hasCurrentGraph
          ? {
              ...current,
              heldEmptySnapshot: true
            }
          : {
              nodes: [],
              edges: [],
              signature: rawL2bSignature,
              emptyPolls: 0,
              heldEmptySnapshot: true
            };
      }

      if (!hasCurrentGraph) {
        if (current.signature === rawL2bSignature && current.emptyPolls === 0) return current;
        return {
          nodes: [],
          edges: [],
          signature: rawL2bSignature,
          emptyPolls: 0,
          heldEmptySnapshot: false
        };
      }

      const emptyPolls = shouldCountEmptySnapshot ? current.emptyPolls + 1 : current.emptyPolls;
      const dragGraceActive = (
        nodeDragActiveRef.current
        || Date.now() - lastNodeDragEndedAtRef.current < NODE_DRAG_EMPTY_SNAPSHOT_GRACE_MS
      );
      if (dragGraceActive || emptyPolls < EMPTY_L2B_SNAPSHOT_CONFIRM_POLLS) {
        return {
          ...current,
          emptyPolls,
          heldEmptySnapshot: true
        };
      }

      return {
        nodes: [],
        edges: [],
        signature: rawL2bSignature,
        emptyPolls,
        heldEmptySnapshot: false
      };
    });
  }, [
    hasIncompleteL2bSnapshot,
    hasIncomingLiveGraph,
    rawL2bEdges,
    rawL2bNodes,
    rawL2bSignature,
    rawL2bSnapshotKey
  ]);

  useEffect(() => {
    if (!hasIncompleteL2bSnapshot) return;
    if (lastIncompleteL2bSnapshotRefreshKeyRef.current === rawL2bSnapshotKey) return;
    lastIncompleteL2bSnapshotRefreshKeyRef.current = rawL2bSnapshotKey;
    if (incompleteL2bSnapshotRefreshInFlightRef.current) return;
    incompleteL2bSnapshotRefreshInFlightRef.current = true;
    let refreshStarted = false;
    const timer = window.setTimeout(() => {
      refreshStarted = true;
      void onRefreshMemory({ quiet: true }).finally(() => {
        incompleteL2bSnapshotRefreshInFlightRef.current = false;
      });
    }, 80);
    return () => {
      window.clearTimeout(timer);
      if (!refreshStarted) {
        incompleteL2bSnapshotRefreshInFlightRef.current = false;
      }
    };
  }, [hasIncompleteL2bSnapshot, onRefreshMemory, rawL2bSnapshotKey]);

  const l2bNodes = dragBufferedGraph?.nodes ?? l2bViewGraph.nodes;
  const l2bEdges = dragBufferedGraph?.edges ?? l2bViewGraph.edges;
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
      position: isFiniteFlowPosition(manualPositions[node.id]) ? manualPositions[node.id] : node.position,
      selected: node.id === selectedNodeId
    }));
  }, [filterKind, l2bNodes, manualPositions, previewNodes, selectedNodeId, stateColors]);
  const graphNodeSignature = useMemo(
    () => graphNodes.map((node) => node.id).sort().join("|"),
    [graphNodes]
  );
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
    openSelectionInspector({ selection_type: "node", ...source });
    const uuid = String(source.uuid || node.id);
    if (!draftableNodeIds.has(uuid)) return;
    if (!edgeFrom) setEdgeFrom(uuid);
    else if (!edgeTo && edgeFrom !== uuid) setEdgeTo(uuid);
  };

  const onEdgeClick: EdgeMouseHandler = (_, edge) => {
    const source = (edge.data as { source?: Record<string, unknown> } | undefined)?.source ?? {};
    openSelectionInspector({
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
    if (isFiniteFlowPosition(position)) {
      setManualPositions((current) => ({ ...current, [uuid]: position }));
    }
    openSelectionInspector({ selection_type: "node", ...nodeSource });
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
      if (preview.silent) return;
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
      const payload = {
        label,
        kind: nodeKind,
        description: `Created from React Memory Graph Workspace (${origin}).`,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      };
      const receipt = operatorMode
        ? await api.l2bNodeApply(payload)
        : await api.l2bNodeDraft(payload);
      if (receipt.success !== false) {
        if (operatorMode) {
          await onRefreshMemory();
        } else {
          stagePreviewNode(makeDraftId("node"), label, position);
        }
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
      const payload = {
        from_uuid: source,
        to_uuid: target,
        kind: edgeKind,
        strength: Number(edgeStrength) || 0.5,
        meta: edgeMetaPayload(reason, meta),
        dry_run: !operatorMode,
        operator_mode: operatorMode
      };
      const receipt = operatorMode
        ? await api.l2bEdgeApply(payload)
        : await api.l2bEdgeDraft(payload);
      if (receipt.success !== false && operatorMode) {
        await onRefreshMemory();
      }
      if (receipt.success !== false && !operatorMode && draftableNodeIds.has(source) && draftableNodeIds.has(target)) {
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
        if (!isFiniteFlowPosition(change.position)) return;
        if (next === current) next = { ...current };
        next[change.id] = change.position;
      });
      return next;
    });
  }, []);

  const recoverBlankViewport = useCallback((allowRepeat = false) => {
    if (!flowInstance || !layoutReady || !graphNodeSignature || !graphNodes.length) return;
    if (nodeDragActiveRef.current) return;
    const recoveryKey = [
      graphNodeSignature,
      canvasSize.width,
      canvasSize.height,
      activeTool || "none",
      selectedNodeId || selectedEdgeId || "none"
    ].join(":");
    window.setTimeout(() => {
      if (nodeDragActiveRef.current) return;
      const canvas = canvasRef.current;
      if (!canvas) return;
      const canvasRect = canvas.getBoundingClientRect();
      const recoverCamera = () => {
        blankViewportRecoveryAttemptsRef.current += 1;
        lastBlankViewportRecoveryKeyRef.current = recoveryKey;
        flowInstance.fitView({ padding: 0.34, duration: 180, maxZoom: 0.78 });
        if (blankViewportRecoveryAttemptsRef.current < BLANK_VIEWPORT_HARD_RESET_ATTEMPTS) return;

        blankViewportRecoveryAttemptsRef.current = 0;
        lastAutoFitSignatureRef.current = "";
        lastBlankViewportRecoveryKeyRef.current = "";
        setManualPositions({});
        setFlowRenderVersion((version) => version + 1);
      };
      const renderedNodes = Array.from(canvas.querySelectorAll(".react-flow__node"));
      if (!renderedNodes.length) {
        // ReactFlow may virtualize nodes out of the DOM after an accidental long pane drag.
        // The L2-B view model still has data, so recover the camera instead of showing a blank canvas.
        if (!allowRepeat && lastBlankViewportRecoveryKeyRef.current === recoveryKey) return;
        recoverCamera();
        return;
      }
      const anyNodeVisible = renderedNodes.some((node) => {
        const rect = node.getBoundingClientRect();
        return (
          rect.width > 1
          && rect.height > 1
          && rect.right > canvasRect.left + 12
          && rect.left < canvasRect.right - 12
          && rect.bottom > canvasRect.top + 12
          && rect.top < canvasRect.bottom - 12
        );
      });
      if (anyNodeVisible) {
        blankViewportRecoveryAttemptsRef.current = 0;
        return;
      }
      if (!allowRepeat && lastBlankViewportRecoveryKeyRef.current === recoveryKey) return;
      recoverCamera();
    }, 80);
  }, [
    activeTool,
    canvasSize.height,
    canvasSize.width,
    flowInstance,
    graphNodeSignature,
    graphNodes.length,
    layoutReady,
    selectedEdgeId,
    selectedNodeId
  ]);

  const onNodeDragStart: NodeDragHandler = useCallback(() => {
    if (dragBufferReleaseTimerRef.current != null) {
      window.clearTimeout(dragBufferReleaseTimerRef.current);
      dragBufferReleaseTimerRef.current = null;
    }
    nodeDragActiveRef.current = true;
    setDragBufferedGraph({ nodes: l2bNodes, edges: l2bEdges });
  }, [l2bEdges, l2bNodes]);

  const onNodeDragStop: NodeDragHandler = useCallback((_, node) => {
    nodeDragActiveRef.current = false;
    lastNodeDragEndedAtRef.current = Date.now();
    if (isFiniteFlowPosition(node.position)) {
      setManualPositions((current) => ({ ...current, [node.id]: node.position }));
    }
    if (dragBufferReleaseTimerRef.current != null) {
      window.clearTimeout(dragBufferReleaseTimerRef.current);
    }
    dragBufferReleaseTimerRef.current = window.setTimeout(() => {
      dragBufferReleaseTimerRef.current = null;
      setDragBufferedGraph(null);
    }, 650);
    window.setTimeout(() => recoverBlankViewport(true), 120);
  }, [recoverBlankViewport]);

  useEffect(() => {
    if (!flowInstance || !layoutReady || !graphNodeSignature || !graphNodes.length) return;
    if (lastAutoFitSignatureRef.current === graphNodeSignature) return;
    lastAutoFitSignatureRef.current = graphNodeSignature;
    blankViewportRecoveryAttemptsRef.current = 0;
    const timer = window.setTimeout(() => {
      flowInstance.fitView({ padding: 0.32, duration: 180, maxZoom: 0.78 });
    }, 40);
    return () => window.clearTimeout(timer);
  }, [flowInstance, graphNodeSignature, graphNodes.length, layoutReady]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      recoverBlankViewport(false);
    }, 80);
    return () => window.clearTimeout(timer);
  }, [recoverBlankViewport]);

  useEffect(() => {
    if (!flowInstance || !layoutReady || !graphNodeSignature || !graphNodes.length) return;
    // Safety net for missed ReactFlow move/drag events: only acts when no graph node is visible.
    const timer = window.setInterval(() => {
      recoverBlankViewport(true);
    }, 1600);
    return () => window.clearInterval(timer);
  }, [flowInstance, graphNodeSignature, graphNodes.length, layoutReady, recoverBlankViewport]);

  const onReconnect = (oldEdge: Edge, connection: Connection) => {
    const source = connection.source || oldEdge.source;
    const target = connection.target || oldEdge.target;
    setEdgeFrom(source);
    setEdgeTo(target);
    openSelectionInspector({
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
        dry_run: !operatorMode,
        operator_mode: operatorMode
      }));
      if (operatorMode) await onRefreshMemory();
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
    if (operatorMode && !window.confirm("Delete this L2-B Edge from the runtime graph?")) return;
    const matchKind = isSelectedEdge(selected) ? String(selected.kind || "") : "";
    const matchSource = isSelectedEdge(selected) ? String(selected.edge_source || selected.source_tool || "") : "";
    if (selectedEdgeId && previewEdges.some((edge) => edge.id === selectedEdgeId)) {
      setPreviewEdges((rows) => rows.filter((edge) => edge.id !== selectedEdgeId));
    }
    try {
      const receipt = await api.l2bEdgeDelete({
        from_uuid: source,
        to_uuid: target,
        match_kind: matchKind,
        match_source: matchSource,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      });
      pushReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        setL2bViewGraph((current) => {
          const edges = current.edges.filter((row) => {
            const rowSource = edgeEndpoint(row, "source");
            const rowTarget = edgeEndpoint(row, "target");
            const kindMatches = !matchKind || String(row.kind || "") === matchKind;
            const sourceMatches = !matchSource || String(row.edge_source || row.source_tool || "") === matchSource;
            return !(rowSource === source && rowTarget === target && kindMatches && sourceMatches);
          });
          return {
            ...current,
            edges,
            signature: l2bGraphSignature(current.nodes, edges)
          };
        });
        await onRefreshMemory();
      }
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
    if (operatorMode && !window.confirm("Delete this L2-B Node through L1.5 eviction?")) return;
    if (previewNodes.some((row) => String(row.uuid) === uuid)) {
      setPreviewNodes((rows) => rows.filter((row) => String(row.uuid) !== uuid));
      setPreviewEdges((rows) => rows.filter((edge) => edge.source !== uuid && edge.target !== uuid));
      setSelected(null);
    }
    try {
      const receipt = await api.l2bNodeDelete({ node_uuid: uuid, dry_run: !operatorMode, operator_mode: operatorMode });
      pushReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        setL2bViewGraph((current) => {
          const nodes = current.nodes.filter((row) => graphRowStableId(row) !== uuid);
          const edges = current.edges.filter((row) => (
            edgeEndpoint(row, "source") !== uuid && edgeEndpoint(row, "target") !== uuid
          ));
          return {
            ...current,
            nodes,
            edges,
            signature: l2bGraphSignature(nodes, edges)
          };
        });
        setManualPositions((current) => {
          if (!(uuid in current)) return current;
          const next = { ...current };
          delete next[uuid];
          return next;
        });
        setSelected(null);
        await onRefreshMemory();
      }
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
        openSelectionInspector({ selection_type: "node", ...nodeSource });
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.subgraph.draft", exc, { label }));
    }
  };

  const inspectLiveSubgraphContext = async () => {
    const label = subgraphLabel.trim() || "Live L2-B context";
    const nodeSelection = policyNodeSelection();
    if (!nodeSelection.length) {
      pushReceipt(localReceipt("l2b.subgraph.context", false, { error: "missing_node_selection" }));
      return;
    }
    try {
      const receipt = await api.l2bSubgraphContext({
        label,
        node_uuids: nodeSelection,
        depth: Number.parseInt(subgraphDepth || "1", 10),
        include_clusters: true,
        dry_run: true,
        operator_mode: false
      });
      if (receipt.success !== false) {
        setSubgraphContext(receipt.data ?? null);
      }
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("l2b.subgraph.context", exc, { label, node_uuids: nodeSelection }));
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
      flowInstance.fitView({ padding: 0.3, duration: 220, maxZoom: 0.78 });
      return;
    }
    if (selectedNodeId) {
      flowInstance.fitView({ nodes: [{ id: selectedNodeId }], padding: 0.9, duration: 220, maxZoom: 0.82 });
      return;
    }
    const edge = graphEdges.find((candidate) => candidate.id === selectedEdgeId);
    if (edge) {
      flowInstance.fitView({
        nodes: [{ id: edge.source }, { id: edge.target }],
        padding: 0.55,
        duration: 220,
        maxZoom: 0.82
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
    window.setTimeout(() => flowInstance?.fitView({ padding: 0.3, duration: 220, maxZoom: 0.78 }), 0);
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

      <div className="canvas-panel" ref={canvasRef}>
        <Rnd
          className={`canvas-toolbar icon-toolbar floating-toolbar${toolbarVertical ? " vertical" : ""}`}
          position={floatingPanelPosition("toolbar")}
          bounds="parent"
          dragGrid={FLOATING_PANEL_GRID}
          enableResizing={false}
          dragHandleClassName="toolbar-drag-grip"
          cancel={FLOATING_PANEL_DRAG_CANCEL}
          onDragStart={() => markFloatingPanelInteraction("toolbar")}
          onDragStop={(_, data) => handleFloatingDragStop("toolbar", data)}
          style={{ zIndex: floatingPanels.toolbar.z }}
          onMouseDown={() => bringPanelForward("toolbar")}
        >
          <span
            className="toolbar-drag-grip panel-drag-handle"
            title="Drag toolbar"
          />
          <IconToolButton active={activeTool === "node"} label={t.createNode} onClick={() => openMemoryTool("node")}><Plus size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "edge"} label={t.draftEdge} onClick={() => openMemoryTool("edge")}><GitBranch size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "subgraph"} label={t.subgraph} onClick={() => openMemoryTool("subgraph")}><Layers size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "filter"} label={t.filters} onClick={() => openMemoryTool("filter")}><Filter size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "tags"} label={t.tags} onClick={() => openMemoryTool("tags")}><Tags size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "state"} label={t.stateView} onClick={() => openMemoryTool("state")}><Activity size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "pool"} label={t.l15} onClick={() => openMemoryTool("pool")}><Database size={18} /></IconToolButton>
          <IconToolButton active={activeTool === "settings"} label={t.settings} onClick={() => openMemoryTool("settings")}><Settings size={18} /></IconToolButton>
          <span className="tool-divider" />
          <IconToolButton label={t.focusSelection} onClick={focusSelection}><CircleDot size={18} /></IconToolButton>
          <IconToolButton label={t.layoutGraph} onClick={layoutGraph}><Workflow size={18} /></IconToolButton>
          <IconToolButton label={t.clear} danger onClick={clearPreview}><Trash2 size={18} /></IconToolButton>
        </Rnd>

        {activeTool && layoutReady ? (
          <Rnd
            key={`tool-${activeTool}-${panelOpenVersion.tool}`}
            className="tool-dock floating-canvas-panel"
            size={floatingPanelSize("tool")}
            position={floatingPanelPosition("tool")}
            bounds="parent"
            minWidth={FLOATING_PANEL_MIN_WIDTH}
            minHeight={FLOATING_PANEL_MIN_HEIGHT}
            maxWidth={floatingPanelMaxWidth}
            maxHeight={floatingPanelMaxHeight}
            dragGrid={FLOATING_PANEL_GRID}
            resizeGrid={FLOATING_PANEL_GRID}
            enableResizing={FLOATING_PANEL_RESIZE_ENABLE}
            resizeHandleClasses={FLOATING_PANEL_RESIZE_HANDLE_CLASSES}
            dragHandleClassName="panel-drag-handle"
            cancel={FLOATING_PANEL_DRAG_CANCEL}
            onDragStart={() => markFloatingPanelInteraction("tool")}
            onDragStop={(_, data) => handleFloatingDragStop("tool", data)}
            onResizeStart={() => markFloatingPanelInteraction("tool")}
            onResizeStop={(_, __, ref, ___, position) => handleFloatingResizeStop("tool", ref, position)}
            style={{ zIndex: floatingPanels.tool.z }}
            onMouseDown={() => bringPanelForward("tool")}
            >
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
              subgraphDepth={subgraphDepth}
              setSubgraphDepth={setSubgraphDepth}
              subgraphContext={subgraphContext}
              graphDestination={graphDestination}
              setGraphDestination={setGraphDestination}
              graphTransformKind={graphTransformKind}
              setGraphTransformKind={setGraphTransformKind}
              graphHealth={graphHealth}
              operatorMode={operatorMode}
              onDraftNode={() => void draftNode()}
              onDraftEdge={() => void draftEdgeBetween(edgeFrom, edgeTo, "toolbar")}
              onUpdateEdge={() => void updateSelectedEdgeDraft()}
              onDeleteEdge={() => void deleteSelectedEdgeDraft()}
              onDraftImportPolicy={() => void draftImportPolicy()}
              onCreateSubgraph={() => void createSubgraphPreview()}
              onInspectSubgraphContext={() => void inspectLiveSubgraphContext()}
              onDraftTransform={() => void draftGraphTransform()}
              onRefreshHealth={() => void refreshGraphHealth()}
              onDraftTag={draftTagForSelection}
              poolHealth={poolHealth}
              buckets={buckets}
              maxBucketCount={maxBucketCount}
              pushReceipt={pushReceipt}
              onGraphitiPreview={stageGraphitiPreview}
              onSourceApplied={onRefreshMemory}
              onClose={() => setActiveTool(null)}
              />
            </Rnd>
        ) : null}

        {selected && layoutReady ? (
          <Rnd
            key={`selection-${selectedNodeId || selectedEdgeId || panelOpenVersion.selection}-${panelOpenVersion.selection}`}
            className="selection-float floating-canvas-panel"
            size={floatingPanelSize("selection")}
            position={floatingPanelPosition("selection")}
            bounds="parent"
            minWidth={FLOATING_PANEL_MIN_WIDTH}
            minHeight={FLOATING_PANEL_MIN_HEIGHT}
            maxWidth={floatingPanelMaxWidth}
            maxHeight={floatingPanelMaxHeight}
            dragGrid={FLOATING_PANEL_GRID}
            resizeGrid={FLOATING_PANEL_GRID}
            enableResizing={FLOATING_PANEL_RESIZE_ENABLE}
            resizeHandleClasses={FLOATING_PANEL_RESIZE_HANDLE_CLASSES}
            dragHandleClassName="panel-drag-handle"
            cancel={FLOATING_PANEL_DRAG_CANCEL}
            onDragStart={() => markFloatingPanelInteraction("selection")}
            onDragStop={(_, data) => handleFloatingDragStop("selection", data)}
            onResizeStart={() => markFloatingPanelInteraction("selection")}
            onResizeStop={(_, __, ref, ___, position) => handleFloatingResizeStop("selection", ref, position)}
            style={{ zIndex: floatingPanels.selection.z }}
            onMouseDown={() => bringPanelForward("selection")}
          >
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
                  openMemoryTool("edge");
                }
              }}
              onDeleteNode={() => void deleteSelectedNodeDraft()}
              onUpdateEdge={() => void updateSelectedEdgeDraft()}
              onDeleteEdge={() => void deleteSelectedEdgeDraft()}
              onSwapEdge={swapSelectedEdgeEndpoints}
              onClose={() => setSelected(null)}
            />
          </Rnd>
        ) : null}

        <div className="canvas-help-chip">
          <GitBranch size={14} />
          <span>{t.connectHint}</span>
        </div>
        <ReactFlow
          key={`${memoryBackendKey}:${flowRenderVersion}`}
          nodes={graphNodes}
          edges={graphEdges}
          nodeTypes={memoryNodeTypes}
          connectionMode={ConnectionMode.Loose}
          connectionRadius={28}
          onConnect={onConnect}
          onEdgeClick={onEdgeClick}
          onReconnect={onReconnect}
          onNodesChange={onNodesChange}
          onMoveEnd={() => recoverBlankViewport(true)}
          onNodeDragStart={onNodeDragStart}
          onNodeDragStop={onNodeDragStop}
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
          fitViewOptions={{ padding: 0.34, maxZoom: 0.72 }}
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
  subgraphDepth,
  setSubgraphDepth,
  subgraphContext,
  graphDestination,
  setGraphDestination,
  graphTransformKind,
  setGraphTransformKind,
  graphHealth,
  operatorMode,
  onDraftNode,
  onDraftEdge,
  onUpdateEdge,
  onDeleteEdge,
  onDraftImportPolicy,
  onCreateSubgraph,
  onInspectSubgraphContext,
  onDraftTransform,
  onRefreshHealth,
  onDraftTag,
  poolHealth,
  buckets,
  maxBucketCount,
  pushReceipt,
  onGraphitiPreview,
  onSourceApplied,
  onClose
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
  subgraphDepth: string;
  setSubgraphDepth: (value: string) => void;
  subgraphContext: Record<string, unknown> | null;
  graphDestination: string;
  setGraphDestination: (value: string) => void;
  graphTransformKind: string;
  setGraphTransformKind: (value: string) => void;
  graphHealth: Record<string, unknown> | null;
  operatorMode: boolean;
  onDraftNode: () => void;
  onDraftEdge: () => void;
  onUpdateEdge: () => void;
  onDeleteEdge: () => void;
  onDraftImportPolicy: () => void;
  onCreateSubgraph: () => void;
  onInspectSubgraphContext: () => void;
  onDraftTransform: () => void;
  onRefreshHealth: () => void;
  onDraftTag: () => void;
  poolHealth: Record<string, unknown>;
  buckets: Array<Record<string, unknown>>;
  maxBucketCount: number;
  pushReceipt: (receipt: Receipt | null) => void;
  onGraphitiPreview: (preview: GraphitiPreviewPayload) => void;
  onSourceApplied: () => Promise<void>;
  onClose: () => void;
}) {
  if (activeTool === "node") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Plus size={16} />} title={t.createNode} onClose={onClose} />
        <WriteModeBanner operatorMode={operatorMode} t={t} />
        <label><span>{t.nodeLabel}</span><input value={nodeLabel} onChange={(event) => setNodeLabel(event.target.value)} /></label>
        <label><span>{t.nodeKind}</span><select value={nodeKind} onChange={(event) => setNodeKind(event.target.value)}>{NODE_KIND_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
        <button className="button primary" onClick={onDraftNode}><Plus size={16} /> {t.createNode}</button>
      </section>
    );
  }
  if (activeTool === "edge") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<GitBranch size={16} />} title={t.draftEdge} onClose={onClose} />
        <WriteModeBanner operatorMode={operatorMode} t={t} />
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
    const contextNodes = subgraphContext ? recordArrayFrom(subgraphContext, "nodes") : [];
    const contextEdges = subgraphContext ? recordArrayFrom(subgraphContext, "edges") : [];
    const contextClusters = subgraphContext ? recordArrayFrom(subgraphContext, "clusters") : [];
    const trueConnection = recordFromUnknown(subgraphContext?.true_connection);
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Layers size={16} />} title={t.subgraph} onClose={onClose} />
        <label><span>{t.nodeLabel}</span><input value={subgraphLabel} onChange={(event) => setSubgraphLabel(event.target.value)} /></label>
        <label><span>{t.contextDepth}</span><input value={subgraphDepth} onChange={(event) => setSubgraphDepth(event.target.value)} inputMode="numeric" /></label>
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
          <button className="button" onClick={onInspectSubgraphContext}><Search size={16} /> {t.inspectContext}</button>
          <button className="button" onClick={onDraftTransform}><Activity size={16} /> {t.previewTransform}</button>
        </div>
        {subgraphContext ? (
          <div className="subgraph-context-card">
            <div className="subgraph-context-grid">
              <span><small>{t.contextNodes}</small><strong>{contextNodes.length}</strong></span>
              <span><small>{t.contextEdges}</small><strong>{contextEdges.length}</strong></span>
              <span><small>{t.contextClusters}</small><strong>{contextClusters.length}</strong></span>
            </div>
            <small>{`${t.trueConnection}: ${trueConnection.used_live_l2b_graph === true ? "live L2-B" : "unknown"} · depth ${String(subgraphContext.depth ?? "")}`}</small>
          </div>
        ) : null}
      </section>
    );
  }
  if (activeTool === "filter") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Filter size={16} />} title={t.filters} onClose={onClose} />
        <label><span>{t.nodeKind}</span><select value={filterKind} onChange={(event) => setFilterKind(event.target.value)}><option value="all">all</option>{NODE_KIND_OPTIONS.map((kind) => <option key={kind} value={kind}>{kind}</option>)}</select></label>
      </section>
    );
  }
  if (activeTool === "tags") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Tags size={16} />} title={t.tags} onClose={onClose} />
        <label><span>{t.tags}</span><input value={tagText} onChange={(event) => setTagText(event.target.value)} placeholder="tag-a, tag-b" /></label>
        <button className="button" onClick={onDraftTag}><Tags size={16} /> {t.addTagDraft}</button>
      </section>
    );
  }
  if (activeTool === "state") {
    return (
      <section className="tool-panel">
        <ToolPanelHead icon={<Activity size={16} />} title={t.stateView} onClose={onClose} />
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
        <ToolPanelHead icon={<Database size={16} />} title={t.l15} onClose={onClose} />
        <L15HealthPanel health={poolHealth} t={t} />
        <SourceBoard liveState={liveState} pushReceipt={pushReceipt} t={t} onGraphitiPreview={onGraphitiPreview} onSourceApplied={onSourceApplied} operatorMode={operatorMode} />
        <div className="bucket-board compact">
          {buckets.map((bucket) => (
          <BucketCard key={String(bucket.kind)} bucket={bucket} maxNodeCount={maxBucketCount} operatorMode={operatorMode} pushReceipt={pushReceipt} t={t} />
          ))}
        </div>
      </section>
    );
  }
  return (
    <section className="tool-panel">
      <ToolPanelHead icon={<Settings size={16} />} title={t.settings} onClose={onClose} />
      <p className="source-card-note">{t.connectHint}</p>
      <p className="source-card-note">RustWorkX stores topology; Node/Edge kind, status, tags and meta stay in payloads for flexible visual mapping.</p>
    </section>
  );
}

function ToolPanelHead({
  icon,
  title,
  onClose
}: {
  icon: ReactNode;
  title: string;
  onClose: () => void;
}) {
  return (
    <div className="tool-panel-head panel-drag-handle">
      <strong>{icon}{title}</strong>
      <button
        className="icon-tool tiny"
        aria-label="Close panel"
        title="Close panel"
        onPointerDown={(event) => event.stopPropagation()}
        onClick={onClose}
      >
        <X size={14} />
      </button>
    </div>
  );
}

function WriteModeBanner({ operatorMode, t }: { operatorMode: boolean; t: ConsoleCopy }) {
  return (
    <div className={operatorMode ? "write-mode-banner operator" : "write-mode-banner"}>
      <ShieldCheck size={14} />
      <span>{operatorMode ? `${t.executeMode} / ${t.operatorMode}` : `${t.previewMode} / ${t.safeMode}`}</span>
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
    <div className="selection-float-inner">
      <div className="selection-head panel-drag-handle">
        <strong>{isEdge ? <GitBranch size={16} /> : <CircleDot size={16} />} {title}</strong>
        <button
          className="icon-tool tiny"
          data-tooltip={t.clearSelection}
          title={t.clearSelection}
          onPointerDown={(event) => event.stopPropagation()}
          onClick={onClose}
        >
          <X size={14} />
        </button>
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
    </div>
  );
}

function RuntimeFlowWorkspace({
  flow,
  triggerCatalog,
  capabilityCatalog,
  pushReceipt,
  t,
  operatorMode
}: {
  flow: RuntimeFlow;
  triggerCatalog: TriggerCatalog;
  capabilityCatalog: RuntimeCapabilityCatalog;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  operatorMode: boolean;
}) {
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);
  const [capabilityQuery, setCapabilityQuery] = useState("");
  const [capabilityKind, setCapabilityKind] = useState("");
  const [capabilityInteractionMode, setCapabilityInteractionMode] = useState("");
  const [workflowTitle, setWorkflowTitle] = useState("Runtime Flow custom workflow");
  const [savedWorkflowId, setSavedWorkflowId] = useState("");
  const [workflowDraft, setWorkflowDraft] = useState<WorkflowDraftNode[]>([]);
  const [workflowDrafts, setWorkflowDrafts] = useState<RuntimeWorkflowDrafts>({});
  const [workflowImportText, setWorkflowImportText] = useState("");
  const [workflowImportPreview, setWorkflowImportPreview] = useState<Record<string, unknown> | null>(null);
  const [workflowActionGates, setWorkflowActionGates] = useState<Array<Record<string, unknown>>>([]);
  const [workflowResultIntakes, setWorkflowResultIntakes] = useState<Array<Record<string, unknown>>>([]);
  const [evidenceRefreshSeq, setEvidenceRefreshSeq] = useState(0);
  const pokeEvidenceRefresh = useCallback(() => {
    setEvidenceRefreshSeq((value) => value + 1);
  }, []);
  const catalogGroups = useMemo(() => groupTriggerCatalog(triggerCatalog), [triggerCatalog]);
  const capabilityRows = useMemo(
    () => (capabilityCatalog.capabilities ?? []).filter((row) => row && typeof row === "object"),
    [capabilityCatalog]
  );
  const capabilityKinds = useMemo(() => capabilityKindOptions(capabilityRows), [capabilityRows]);
  const capabilityInteractionModes = useMemo(
    () => capabilityInteractionModeOptions(capabilityCatalog, capabilityRows),
    [capabilityCatalog, capabilityRows]
  );
  const filteredCapabilities = useMemo(
    () => capabilityRows
      .filter((row) => !capabilityKind || String(row.kind || "") === capabilityKind)
      .filter((row) => !capabilityInteractionMode || stringsFromUnknown(row.interaction_modes).includes(capabilityInteractionMode))
      .filter((row) => capabilityMatchesQuery(row, capabilityQuery))
      .slice(0, 36),
    [capabilityRows, capabilityKind, capabilityInteractionMode, capabilityQuery]
  );
  const savedWorkflowRows = useMemo(
    () => (workflowDrafts.drafts ?? []).filter((row) => row && typeof row === "object"),
    [workflowDrafts]
  );
  const pendingActionGates = useMemo(
    () => workflowActionGates.filter((row) => String(row.state || "") === "pending"),
    [workflowActionGates]
  );
  const resultIntakeRows = useMemo(
    () => workflowResultIntakes.filter((row) => row && typeof row === "object"),
    [workflowResultIntakes]
  );

  const refreshWorkflowDrafts = useCallback(async () => {
    try {
      setWorkflowDrafts(await api.runtimeWorkflowDrafts());
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow_drafts.list", exc));
    }
  }, [pushReceipt]);

  const refreshWorkflowActionGates = useCallback(async () => {
    try {
      const body = await api.runtimeWorkflowActionGates("pending");
      setWorkflowActionGates((body.gates ?? []).filter((row) => row && typeof row === "object"));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.action_gates.list", exc));
    }
  }, [pushReceipt]);

  const refreshWorkflowResultIntakes = useCallback(async () => {
    try {
      const body = await api.runtimeWorkflowResultIntakes();
      setWorkflowResultIntakes((body.entries ?? []).filter((row) => row && typeof row === "object"));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.result_intake.list", exc));
    }
  }, [pushReceipt]);

  useEffect(() => {
    void refreshWorkflowDrafts();
    void refreshWorkflowActionGates();
    void refreshWorkflowResultIntakes();
  }, [refreshWorkflowDrafts, refreshWorkflowActionGates, refreshWorkflowResultIntakes]);

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
    const execution = { dry_run: !operatorMode, operator_mode: operatorMode };
    const triggerAction = operatorMode ? api.triggerFire : api.triggerDraft;
    try {
      if (action === "message_check") {
        pushReceipt(await api.messageCheck(execution));
        return;
      }
      if (action === "message_push") {
        pushReceipt(await api.messagePush(execution));
        return;
      }
      if (action === "llm_push") {
        pushReceipt(await triggerAction({
          trigger_name: "intent_event_boundary",
          ...execution,
          event: {
            type: "intent_boundary",
            kind: "web_llm_context_push",
            summary: operatorMode ? "React Runtime Flow operator context push." : "React Runtime Flow dry-run context push."
          }
        }));
        return;
      }
      if (action === "scheduler_tick") {
        pushReceipt(await triggerAction({
          trigger_name: "intent_event_boundary",
          ...execution,
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
        pushReceipt(await triggerAction({
          trigger_name: "calendar",
          ...execution,
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
        pushReceipt(await triggerAction({
          trigger_name: "scene_switch",
          ...execution,
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
        pushReceipt(await triggerAction({
          trigger_name: "roleplay_mode",
          ...execution,
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

  const insertCapability = (capability: Record<string, unknown>) => {
    const node: WorkflowDraftNode = {
      workflow_node_id: `wf-${Date.now()}-${Math.random().toString(16).slice(2, 7)}`,
      capability,
      created_at: new Date().toISOString()
    };
    setWorkflowDraft((rows) => [...rows, node].slice(-24));
    setSelected(capability);
    pushReceipt(localReceipt("runtime.workflow.node_insert", true, {
      workflow_node_id: node.workflow_node_id,
      capability_id: String(capability.capability_id || ""),
      kind: String(capability.kind || ""),
      route: String(capability.route || ""),
      plan_step_compatible: Boolean(capability.plan_step_compatible)
    }));
  };

  const removeWorkflowNode = (nodeId: string) => {
    setWorkflowDraft((rows) => rows.filter((row) => row.workflow_node_id !== nodeId));
  };

  const currentWorkflowArtifact = (): Record<string, unknown> => ({
    schema: "workflow_schema_v1",
    schema_version: 1,
    workflow_id: savedWorkflowId,
    title: workflowTitle,
    nodes: workflowDraft,
    edges: []
  });

  const extractWorkflowArtifact = (raw: unknown): Record<string, unknown> => {
    const record = recordFromUnknown(raw);
    const directWorkflow = recordFromUnknown(record.workflow);
    if (Object.keys(directWorkflow).length) return directWorkflow;
    const draft = recordFromUnknown(record.draft);
    if (Object.keys(draft).length) return draft;
    const dataWorkflow = recordFromUnknown(recordFromUnknown(record.data).workflow);
    if (Object.keys(dataWorkflow).length) return dataWorkflow;
    return record;
  };

  const parseWorkflowImportArtifact = (): Record<string, unknown> | null => {
    try {
      const parsed = JSON.parse(workflowImportText);
      const artifact = extractWorkflowArtifact(parsed);
      if (!Object.keys(artifact).length) {
        pushReceipt(localReceipt("runtime.workflow.import_parse", false, { error: "empty_workflow_json" }));
        return null;
      }
      return artifact;
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.import_parse", exc));
      return null;
    }
  };

  const applyWorkflowArtifact = (artifact: Record<string, unknown>) => {
    const rows = Array.isArray(artifact.nodes) ? artifact.nodes : [];
    setWorkflowDraft(rows
      .map((row) => recordFromUnknown(row))
      .filter((row) => Object.keys(row).length)
      .map((row, index) => ({
        workflow_node_id: String(row.workflow_node_id || `wf-import-${index + 1}`),
        capability: recordFromUnknown(row.capability).capability_id ? recordFromUnknown(row.capability) : row,
        created_at: String(row.created_at || artifact.updated_at || new Date().toISOString())
      })));
    setWorkflowTitle(String(artifact.title || "Runtime Flow custom workflow"));
    setSavedWorkflowId(String(artifact.workflow_id || ""));
  };

  const validateWorkflowDraft = async () => {
    try {
      const receipt = await api.runtimeWorkflowValidate({ workflow: currentWorkflowArtifact() });
      setWorkflowImportPreview(recordFromUnknown(receipt.data));
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.validate", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const exportWorkflowDraft = async () => {
    try {
      const receipt = savedWorkflowId
        ? await api.runtimeWorkflowExport(savedWorkflowId)
        : await api.runtimeWorkflowValidate({ workflow: currentWorkflowArtifact() });
      const data = recordFromUnknown(receipt.data);
      const artifact = extractWorkflowArtifact(data);
      if (Object.keys(artifact).length) {
        setWorkflowImportText(JSON.stringify(artifact, null, 2));
      }
      setWorkflowImportPreview(recordFromUnknown(data.validation).valid !== undefined ? recordFromUnknown(data.validation) : data);
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.export", exc, { workflow_id: savedWorkflowId }));
    }
  };

  const previewWorkflowImport = async () => {
    const artifact = parseWorkflowImportArtifact();
    if (!artifact) return;
    try {
      const receipt = await api.runtimeWorkflowImportPreview({
        workflow: artifact,
        target_workflow: currentWorkflowArtifact()
      });
      setWorkflowImportPreview(recordFromUnknown(receipt.data));
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.import_preview", exc));
    }
  };

  const loadWorkflowImport = async () => {
    const artifact = parseWorkflowImportArtifact();
    if (!artifact) return;
    try {
      const receipt = await api.runtimeWorkflowValidate({ workflow: artifact });
      const data = recordFromUnknown(receipt.data);
      const workflow = extractWorkflowArtifact(data);
      setWorkflowImportPreview(data);
      pushReceipt(receipt);
      if (receipt.success && Object.keys(workflow).length) {
        applyWorkflowArtifact(workflow);
      }
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.import_load", exc));
    }
  };

  const saveWorkflowDraft = async () => {
    if (!workflowDraft.length) {
      pushReceipt(localReceipt("runtime.workflow_drafts.save", false, { error: "empty_workflow_draft" }));
      return;
    }
    try {
      const receipt = await api.runtimeWorkflowDraftSave({
        workflow_id: savedWorkflowId,
        title: workflowTitle,
        workflow_nodes: workflowDraft
      });
      const saved = recordFromUnknown(receipt);
      const summary = recordFromUnknown(saved.summary);
      setSavedWorkflowId(String(saved.workflow_id || summary.workflow_id || savedWorkflowId || ""));
      pushReceipt(receipt);
      await refreshWorkflowDrafts();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow_drafts.save", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const loadWorkflowDraft = async (workflowId: string) => {
    try {
      const receipt = await api.runtimeWorkflowDraftGet(workflowId);
      const loaded = recordFromUnknown(recordFromUnknown(receipt).draft);
      const nodes = Array.isArray(loaded.nodes) ? loaded.nodes : [];
      setWorkflowDraft(nodes
        .map((row) => recordFromUnknown(row))
        .filter((row) => Object.keys(row).length)
        .map((row, index) => ({
          workflow_node_id: String(row.workflow_node_id || `wf-loaded-${index + 1}`),
          capability: recordFromUnknown(row.capability).capability_id ? recordFromUnknown(row.capability) : row,
          created_at: String(row.created_at || loaded.updated_at || new Date().toISOString())
        })));
      setWorkflowTitle(String(loaded.title || "Runtime Flow custom workflow"));
      setSavedWorkflowId(String(loaded.workflow_id || workflowId));
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow_drafts.get", exc, { workflow_id: workflowId }));
    }
  };

  const deleteWorkflowDraft = async (workflowId: string) => {
    try {
      const receipt = await api.runtimeWorkflowDraftDelete(workflowId);
      if (workflowId === savedWorkflowId) {
        setSavedWorkflowId("");
      }
      pushReceipt(receipt);
      await refreshWorkflowDrafts();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow_drafts.delete", exc, { workflow_id: workflowId }));
    }
  };

  const executeWorkflowNode = async (node: WorkflowDraftNode) => {
    const capability = node.capability;
    if (String(capability.kind || "") !== "trigger") {
      pushReceipt(localReceipt("runtime.workflow.node_execute", false, {
        workflow_node_id: node.workflow_node_id,
        capability_id: String(capability.capability_id || ""),
        error: "only_trigger_capabilities_execute_in_first_slice"
      }));
      return;
    }
    const samplePayload = recordFromUnknown(capability.sample_payload);
    const event = Object.keys(recordFromUnknown(samplePayload.event)).length
      ? recordFromUnknown(samplePayload.event)
      : {
        type: "workflow_capability_fire",
        kind: String(capability.trigger_name || capability.capability_id || "trigger"),
        source: "runtime_flow_workbench"
      };
    const body = {
      ...samplePayload,
      trigger_name: String(samplePayload.trigger_name || capability.trigger_name || ""),
      event,
      dry_run: !operatorMode,
      operator_mode: operatorMode
    };
    try {
      pushReceipt(await (operatorMode ? api.triggerFire(body) : api.triggerDraft(body)));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.node_execute", exc, {
        workflow_node_id: node.workflow_node_id,
        capability_id: String(capability.capability_id || "")
      }));
    }
  };

  const createWorkflowActionGate = async (node: WorkflowDraftNode) => {
    try {
      const receipt = await api.runtimeWorkflowActionGateDraft({
        workflow_id: savedWorkflowId,
        workflow_node_id: node.workflow_node_id,
        workflow_node: node,
        title: `${String(node.capability.title || node.capability.capability_id || "Workflow action")} gate`
      });
      pushReceipt(receipt);
      await refreshWorkflowActionGates();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.action_gate.draft", exc, {
        workflow_node_id: node.workflow_node_id,
        capability_id: String(node.capability.capability_id || "")
      }));
    }
  };

  const decideWorkflowActionGate = async (gate: Record<string, unknown>, decision: string) => {
    try {
      const receipt = await api.runtimeWorkflowActionGateDecision({
        gate_id: gate.gate_id,
        decision,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      });
      pushReceipt(receipt);
      await refreshWorkflowActionGates();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.action_gate.apply", exc, {
        gate_id: String(gate.gate_id || ""),
        decision
      }));
    }
  };

  const importWorkflowPlan = async () => {
    if (!workflowDraft.length) {
      pushReceipt(localReceipt("runtime.workflow.plan_draft", false, { error: "empty_workflow_draft" }));
      return;
    }
    try {
      pushReceipt(await api.runtimeWorkflowPlanDraft({
        title: workflowTitle,
        workflow_id: savedWorkflowId,
        workflow_nodes: workflowDraft,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.plan_draft", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const previewWorkflowResultRoutes = async () => {
    if (!workflowDraft.length) {
      pushReceipt(localReceipt("runtime.workflow.result_contract", false, { error: "empty_workflow_draft" }));
      return;
    }
    try {
      pushReceipt(await api.runtimeWorkflowResultContract({
        title: workflowTitle,
        workflow_id: savedWorkflowId,
        workflow_nodes: workflowDraft
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.result_contract", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const intakeWorkflowResult = async () => {
    if (!workflowDraft.length) {
      pushReceipt(localReceipt("runtime.workflow.result_intake", false, { error: "empty_workflow_draft" }));
      return;
    }
    try {
      const firstPlanNode = workflowDraft.find((node) => Boolean(node.capability.plan_step_compatible));
      const body: Record<string, unknown> = {
        title: workflowTitle,
        workflow_id: savedWorkflowId,
        workflow_nodes: workflowDraft,
        workflow_node_id: firstPlanNode?.workflow_node_id || workflowDraft[0]?.workflow_node_id || "",
        result_payload: {
          source: "runtime_flow_workbench",
          summary: "Operator-reviewed workflow result intake probe.",
          workflow_title: workflowTitle,
          created_at: new Date().toISOString()
        },
        dry_run: !operatorMode,
        operator_mode: operatorMode
      };
      const receipt = await api.runtimeWorkflowResultIntake(body);
      pushReceipt(receipt);
      await refreshWorkflowResultIntakes();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.result_intake", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const deleteWorkflowResultIntake = async (entryId: string) => {
    try {
      const receipt = await api.runtimeWorkflowResultIntakeDelete(entryId);
      pushReceipt(receipt);
      await refreshWorkflowResultIntakes();
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.result_intake.delete", exc, { entry_id: entryId }));
    }
  };

  const runWorkflow = async () => {
    if (!workflowDraft.length) {
      pushReceipt(localReceipt("runtime.workflow.run", false, { error: "empty_workflow_draft" }));
      return;
    }
    try {
      pushReceipt(await api.runtimeWorkflowRun({
        title: workflowTitle,
        workflow_id: savedWorkflowId,
        workflow_nodes: workflowDraft,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      }));
    } catch (exc) {
      pushReceipt(errorReceipt("runtime.workflow.run", exc, { workflow_node_count: workflowDraft.length }));
    }
  };

  const draftGate = async (gate: Record<string, unknown>, decision: string, apply = false) => {
    const execution = apply
      ? { dry_run: !operatorMode, operator_mode: operatorMode }
      : { dry_run: true, operator_mode: false };
    const body = {
      gate_id: gate.gate_id,
      decision,
      ...execution
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
          <span className={operatorMode ? "mode-chip active" : "mode-chip"}>
            <ShieldCheck size={14} /> {operatorMode ? `${t.executeMode} / ${t.operatorMode}` : t.operatorSafe}
          </span>
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
                    <small>{operatorMode ? t.executeMode : t.dryRunOnly}</small>
                  </button>
                ))}
              </div>
            </section>
          ))}
        </div>
        <div className="capability-workbench">
          <div className="trigger-catalog-title">
            <strong><Search size={15} /> {t.capabilityCatalog}</strong>
            <small>{capabilityRows.length} / {filteredCapabilities.length}</small>
          </div>
          <div className="capability-filters">
            <label>
              <span>{t.capabilitySearch}</span>
              <input
                value={capabilityQuery}
                onChange={(event) => setCapabilityQuery(event.target.value)}
                placeholder={t.capabilitySearch}
              />
            </label>
            <label>
              <span>{t.capabilityKind}</span>
              <select value={capabilityKind} onChange={(event) => setCapabilityKind(event.target.value)}>
                <option value="">{t.allKinds}</option>
                {capabilityKinds.map((kind) => (
                  <option key={kind} value={kind}>{kind}</option>
                ))}
              </select>
            </label>
            <label>
              <span>{t.interactionMode}</span>
              <select value={capabilityInteractionMode} onChange={(event) => setCapabilityInteractionMode(event.target.value)}>
                <option value="">{t.allInteractionModes}</option>
                {capabilityInteractionModes.map((mode) => (
                  <option key={mode.id} value={mode.id}>
                    {mode.id} {mode.label}{mode.count ? ` (${mode.count})` : ""}
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="capability-grid">
            {filteredCapabilities.length ? filteredCapabilities.map((capability) => (
              <div
                className="capability-row"
                key={String(capability.capability_id)}
                role="button"
                tabIndex={0}
                onClick={() => setSelected(capability)}
                onDoubleClick={() => insertCapability(capability)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") insertCapability(capability);
                }}
              >
                <span>
                  <strong>{String(capability.title || capability.capability_id || "capability")}</strong>
                  <small>{String(capability.route || "")}</small>
                </span>
                <b>{String(capability.kind || "")}</b>
                <small>{`${t.capabilityPolicy}: ${String(capability.execution_policy || "-")}`}</small>
                <div>
                  {capabilityTags(capability).slice(0, 4).map((tag) => (
                    <i key={tag}>{tag}</i>
                  ))}
                </div>
                <em>{Boolean(capability.plan_step_compatible) ? t.planCompatible : String(recordFromUnknown(capability.true_connection).state || "")}</em>
                <button
                  className="button tiny"
                  type="button"
                  onClick={(event) => {
                    event.stopPropagation();
                    insertCapability(capability);
                  }}
                >
                  <Plus size={13} /> {t.insertWorkflowNode}
                </button>
              </div>
            )) : <p className="muted">{t.noCapabilityMatches}</p>}
          </div>
          <div className="workflow-draft-panel">
            <div className="trigger-catalog-title">
              <strong><Workflow size={15} /> {t.workflowDraft}</strong>
              <span className="workflow-draft-actions">
                <button className="button small" onClick={() => void saveWorkflowDraft()}>
                  <Save size={14} /> {t.saveWorkflow}
                </button>
                <button className="button small" onClick={() => void validateWorkflowDraft()}>
                  <CheckCircle2 size={14} /> {t.validateWorkflow}
                </button>
                <button className="button small" onClick={() => void exportWorkflowDraft()}>
                  <Download size={14} /> {t.exportWorkflow}
                </button>
                <button className="button small" onClick={() => void previewWorkflowImport()}>
                  <GitBranch size={14} /> {t.importPreview}
                </button>
                <button className="button small" onClick={() => void loadWorkflowImport()}>
                  <UploadCloud size={14} /> {t.loadImport}
                </button>
                <button className="button small" onClick={() => void runWorkflow()}>
                  <Play size={14} /> {t.runWorkflow}
                </button>
                <button className="button small" onClick={() => void previewWorkflowResultRoutes()}>
                  <GitBranch size={14} /> {t.resultRoutes}
                </button>
                <button className="button small" onClick={() => void intakeWorkflowResult()}>
                  <Download size={14} /> {t.resultIntake}
                </button>
                <button className="button small" onClick={() => void importWorkflowPlan()}>
                  <UploadCloud size={14} /> {t.draftPlan}
                </button>
              </span>
            </div>
            <label className="workflow-title-field">
              <span>{t.workflowTitle}</span>
              <input value={workflowTitle} onChange={(event) => setWorkflowTitle(event.target.value)} />
            </label>
            <label className="workflow-title-field workflow-import-field">
              <span>{t.workflowImportJson}</span>
              <textarea
                value={workflowImportText}
                onChange={(event) => setWorkflowImportText(event.target.value)}
                spellCheck={false}
              />
            </label>
            {workflowImportPreview ? (
              <div className="workflow-import-preview">
                <strong>{t.workflowDiff}</strong>
                <small>{workflowImportPreviewSummary(workflowImportPreview)}</small>
              </div>
            ) : null}
            {workflowDraft.length ? (
              <div className="workflow-draft-list">
                {workflowDraft.map((node, index) => (
                  <div className="workflow-draft-row" key={node.workflow_node_id}>
                    <b>{index + 1}</b>
                    <span>
                      <strong>{String(node.capability.title || node.capability.capability_id || "capability")}</strong>
                      <small>{String(node.capability.nanobot_task_type || node.capability.route || node.capability.kind || "")}</small>
                    </span>
                    {String(node.capability.kind || "") === "trigger" ? (
                      <button className="button tiny" onClick={() => void executeWorkflowNode(node)}>
                        <Play size={13} /> {t.executeNode}
                      </button>
                    ) : null}
                    {workflowNodeCanGate(node) ? (
                      <button className="button tiny" onClick={() => void createWorkflowActionGate(node)}>
                        <ShieldCheck size={13} /> {t.createGate}
                      </button>
                    ) : null}
                    <button className="button tiny danger" onClick={() => removeWorkflowNode(node.workflow_node_id)} aria-label={t.clear}>
                      <X size={14} />
                    </button>
                  </div>
                ))}
              </div>
            ) : <p className="muted">{t.noWorkflowNodes}</p>}
            <div className="saved-workflow-panel">
              <strong>{t.savedWorkflows}</strong>
              {savedWorkflowRows.length ? (
                <div className="saved-workflow-list">
                  {savedWorkflowRows.slice(0, 8).map((row) => {
                    const workflowId = String(row.workflow_id || "");
                    return (
                      <div className={workflowId === savedWorkflowId ? "saved-workflow-row active" : "saved-workflow-row"} key={workflowId || String(row.title)}>
                        <span>
                          <b>{String(row.title || workflowId || "workflow")}</b>
                          <small>{`${String(row.node_count ?? 0)} nodes / ${String(row.plan_compatible_count ?? 0)} Plan`}</small>
                        </span>
                        <button className="button tiny" onClick={() => void loadWorkflowDraft(workflowId)}>
                          <Download size={13} /> {t.loadWorkflow}
                        </button>
                        <button className="button tiny danger" onClick={() => void deleteWorkflowDraft(workflowId)} aria-label={t.deleteWorkflow}>
                          <Trash2 size={13} />
                        </button>
                      </div>
                    );
                  })}
                </div>
              ) : <p className="muted">{t.noSavedWorkflows}</p>}
            </div>
            <div className="saved-workflow-panel">
              <strong>{t.actionGates}</strong>
              {pendingActionGates.length ? (
                <div className="saved-workflow-list">
                  {pendingActionGates.slice(0, 8).map((gate) => (
                    <div className="saved-workflow-row" key={String(gate.gate_id || gate.title)}>
                      <span>
                        <b>{String(gate.title || gate.gate_id || "action gate")}</b>
                        <small>{`${String(gate.action_kind || "-")} / ${String(gate.capability_id || "-")}`}</small>
                      </span>
                      <button className="button tiny" onClick={() => void decideWorkflowActionGate(gate, "apply")}>
                        <Play size={13} /> {t.applyGate}
                      </button>
                      <button className="button tiny ghost" onClick={() => void decideWorkflowActionGate(gate, "reject")}>
                        <X size={13} /> {t.reject}
                      </button>
                    </div>
                  ))}
                </div>
              ) : <p className="muted">{t.noPendingGate}</p>}
            </div>
            <div className="saved-workflow-panel">
              <strong>{t.resultIntakeLog}</strong>
              {resultIntakeRows.length ? (
                <div className="saved-workflow-list">
                  {resultIntakeRows.slice(0, 8).map((entry) => (
                    <div className="saved-workflow-row" key={String(entry.entry_id || entry.created_at)}>
                      <span>
                        <b>{String(entry.workflow_id || entry.entry_id || "result intake")}</b>
                        <small>{`${String(entry.route_count ?? 0)} route(s) / ${String(entry.staged_ref_count ?? 0)} staged`}</small>
                      </span>
                      <small>{String(entry.result_channel || entry.task_id || entry.state || "")}</small>
                      <button
                        className="button tiny danger"
                        onClick={() => void deleteWorkflowResultIntake(String(entry.entry_id || ""))}
                        aria-label={t.deleteResultIntake}
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  ))}
                </div>
              ) : <p className="muted">{t.noResultIntakes}</p>}
            </div>
          </div>
        </div>
        <div className="trigger-catalog">
          <div className="trigger-catalog-title">
            <strong>{t.registeredTriggers}</strong>
            <small>{t.triggerChannels}</small>
          </div>
          <div className="trigger-channel-grid">
            {catalogGroups.map((group) => (
              <details className="trigger-channel-card" key={group.id} open={catalogGroups.length <= 4}>
                <summary>
                  <span>
                    <strong>{group.label}</strong>
                    <small>{group.description || group.id}</small>
                  </span>
                  <b>{group.names.length}</b>
                </summary>
                <div className="trigger-card-section">
                  <span>{group.names.join(", ")}</span>
                </div>
                <TriggerTagRow label={t.triggerModules} values={group.modules} />
                <TriggerTagRow label={t.triggerInformationTags} values={group.tags} />
                <TriggerTagRow label={t.triggerFireKinds} values={group.kinds} />
              </details>
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

function TriggerTagRow({ label, values }: { label: string; values: string[] }) {
  if (!values.length) return null;
  return (
    <div className="trigger-tag-row">
      <small>{label}</small>
      <div>
        {values.map((value) => (
          <span className="trigger-chip" key={value}>{value}</span>
        ))}
      </div>
    </div>
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
  const [sampleCheck, setSampleCheck] = useState<Record<string, unknown> | null>(null);
  const roomRef = useRef<any>(null);
  const screenTrackRef = useRef<MediaStreamTrack | null>(null);
  const screenShareModeRef = useRef<"livekit" | "manual" | null>(null);
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
    screenShareModeRef.current = null;
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
        onLocalScreenShareStopped: () => {
          if (!screenShareModeRef.current && !screenTrackRef.current) return;
          screenTrackRef.current = null;
          screenShareModeRef.current = null;
          setScreenSharing(false);
          pushEvent("screen_share_stop", "local publication ended", "idle");
        },
        onDisconnected: (reason) => {
          cleanupRemoteAudio();
          roomRef.current = null;
          screenTrackRef.current = null;
          screenShareModeRef.current = null;
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

  const stopScreenShare = useCallback(async (silent = false) => {
    const room = roomRef.current;
    const mode = screenShareModeRef.current;
    const track = screenTrackRef.current;
    screenTrackRef.current = null;
    screenShareModeRef.current = null;
    try {
      if (mode === "livekit") {
        await room?.localParticipant?.setScreenShareEnabled?.(false);
      } else if (track) {
        await room?.localParticipant?.unpublishTrack?.(track, true);
      }
    } catch {
      // Older livekit-client builds may not expose every screen-share helper.
    }
    stopMediaTrack(track);
    setScreenSharing(false);
    if (!silent) {
      pushEvent("screen_share_stop", "", "idle");
    }
  }, [pushEvent]);

  const shareScreen = useCallback(async () => {
    const room = roomRef.current;
    if (!room) return;
    try {
      const client = await loadLiveKitClient();
      if (typeof room.localParticipant?.setScreenShareEnabled === "function") {
        const publication = await room.localParticipant.setScreenShareEnabled(true);
        if (!publication) {
          throw new Error("screen_share_not_published");
        }
        screenShareModeRef.current = "livekit";
        screenTrackRef.current = null;
        setSampleCheck(null);
        setScreenSharing(true);
        pushEvent("screen_share_start", String(publication.source || "screen_share"), "good");
        pushReceipt(localReceipt("livekit.screen_share", true, {
          room: roomId,
          identity,
          method: "setScreenShareEnabled",
          publication_source: String(publication.source || ""),
          track_sid: String(publication.trackSid || publication.sid || ""),
          track_name: String(publication.trackName || publication.name || ""),
          expected_source: "screen_share / SOURCE_SCREEN_SHARE",
          note: "Brain sampler should see this as a screenshare video track if Brain is in the same room."
        }));
        onEvidenceRefresh();
        return;
      }
      if (!navigator.mediaDevices?.getDisplayMedia) {
        throw new Error("getDisplayMedia unavailable");
      }
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { frameRate: 5 },
        audio: false
      });
      const track = stream.getVideoTracks()[0];
      if (!track) throw new Error("screen_track_missing");
      screenTrackRef.current = track;
      screenShareModeRef.current = "manual";
      setSampleCheck(null);
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
        method: "getDisplayMedia+publishTrack",
        track_label: track.label || "screen",
        note: "Brain sampler should see this as a screenshare video track if Brain is in the same room."
      }));
      onEvidenceRefresh();
    } catch (exc) {
      pushEvent("screen_share_error", exc instanceof Error ? exc.message : String(exc), "bad");
      pushReceipt(errorReceipt("livekit.screen_share", exc));
      await stopScreenShare(true);
    }
  }, [identity, onEvidenceRefresh, pushEvent, pushReceipt, roomId, stopScreenShare]);

  const checkSamples = useCallback(async () => {
    try {
      const receipt = await api.visionScreenShareSmoke(15_000);
      const data = receipt.data ?? {};
      const freshAnyEvidence = Boolean(data.fresh_any_evidence);
      const likelyScreenShare = Boolean(data.likely_screen_share);
      const screenShareConfirmed = Boolean(data.screen_share_confirmed);
      setSampleCheck(data);
      pushEvent(
        "sample_check",
        `${freshAnyEvidence ? "fresh" : "stale"} / ${likelyScreenShare ? "screen" : "not-screen"} / ${data.sampler_recorded_frames ?? 0}f`,
        screenShareConfirmed ? "good" : "warn"
      );
      pushReceipt(receipt);
    } catch (exc) {
      setSampleCheck({
        error: exc instanceof Error ? exc.message : String(exc),
        next_steps: ["Check Web Console connectivity and retry the sampler smoke."]
      });
      pushEvent("sample_check_error", exc instanceof Error ? exc.message : String(exc), "bad");
      pushReceipt(errorReceipt("livekit.screen_share.evidence_check", exc));
    } finally {
      onEvidenceRefresh();
    }
  }, [onEvidenceRefresh, pushEvent, pushReceipt]);

  const sampleCheckGood = Boolean(sampleCheck?.screen_share_confirmed);
  const sampleCheckNextSteps = sampleCheck?.next_steps;
  const sampleCheckSteps = Array.isArray(sampleCheckNextSteps)
    ? sampleCheckNextSteps.map((step) => String(step))
    : [];
  const sampleCheckAge = typeof sampleCheck?.sampler_latest_age_ms === "number"
    ? formatEvidenceAge(sampleCheck.sampler_latest_age_ms)
    : "";

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
      {sampleCheck ? (
        <div className={`sample-check-panel ${sampleCheckGood ? "good" : "warn"}`}>
          <div className="sample-check-head">
            <strong>{t.sampleSmoke}</strong>
            <span className={sampleCheckGood ? "fresh-state" : "stale-state"}>
              {sampleCheckGood ? t.screenReady : t.notReady}
            </span>
          </div>
          <div className="sample-check-grid">
            <span className={sampleCheck.fresh_any_evidence ? "good" : "warn"}>{t.freshAnyEvidence}</span>
            <span className={sampleCheck.likely_screen_share ? "good" : "warn"}>{t.likelyScreenShare}</span>
            <span className={sampleCheck.fresh_screen_share ? "good" : "warn"}>{t.freshScreenShare}</span>
            <span>{t.liveKitSampler}: {String(sampleCheck.sampler_recorded_frames ?? 0)}f{sampleCheckAge ? ` / ${sampleCheckAge}` : ""}</span>
            <span>{t.frameCache}: {String(sampleCheck.frame_cache_count ?? 0)}</span>
          </div>
          {sampleCheckSteps.length ? (
            <div className="sample-next-steps">
              <b>{t.nextSteps}</b>
              <ol>
                {sampleCheckSteps.map((step, index) => <li key={`${step}-${index}`}>{step}</li>)}
              </ol>
            </div>
          ) : null}
        </div>
      ) : null}
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

  const runEvidenceAction = async (action: "request" | "stage" | "memory" | "frame" | "bbox" | "focus") => {
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
      } else if (action === "memory") {
        pushReceipt(await api.visionEvidenceMemoryDraft({
          evidence_id: String(items[0]?.evidence_id || ""),
          target_time_ms: Number(items[0]?.timebase && typeof items[0].timebase === "object"
            ? (items[0].timebase as Record<string, unknown>).wall_time_ms || Date.now()
            : Date.now()),
          label: String(items[0]?.description || items[0]?.kind || "Evidence memory"),
          mode: "create_node",
          dry_run: true,
          operator_mode: false
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
        <button className="button small" disabled={busy} onClick={() => void runEvidenceAction("memory")}>
          <Database size={15} /> {t.memoryDraft}
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
  onLocalScreenShareStopped,
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
  onLocalScreenShareStopped: () => void;
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
  on("LocalTrackUnpublished", (publication: any) => {
    if (isScreenSharePublication(publication)) {
      onLocalScreenShareStopped();
    }
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

function isScreenSharePublication(publication: any): boolean {
  const text = [
    publication?.source,
    publication?.trackName,
    publication?.track?.name,
    publication?.track?.source,
    publication?.track?.mediaStreamTrack?.label
  ].map((value) => String(value || "").toLowerCase()).join(" ");
  return text.includes("screen")
    || text.includes("screenshare")
    || text.includes("screen_share");
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

function capabilityKindOptions(rows: Array<Record<string, unknown>>): string[] {
  return uniqueStrings(rows.map((row) => String(row.kind || "")).filter(Boolean));
}

function capabilityInteractionModeOptions(
  catalog: RuntimeCapabilityCatalog,
  rows: Array<Record<string, unknown>>
): Array<{ id: string; label: string; count: number }> {
  const fromCatalog = Array.isArray(catalog.interaction_modes)
    ? catalog.interaction_modes
      .map((mode) => ({
        id: String(mode.id || "").trim(),
        label: String(mode.label || mode.title || "").trim(),
        count: Number(mode.count ?? 0)
      }))
      .filter((mode) => Boolean(mode.id))
    : [];
  if (fromCatalog.length) return fromCatalog;
  return uniqueStrings(rows.flatMap((row) => stringsFromUnknown(row.interaction_modes)))
    .map((id) => ({ id, label: id, count: rows.filter((row) => stringsFromUnknown(row.interaction_modes).includes(id)).length }));
}

function workflowNodeCanGate(node: WorkflowDraftNode): boolean {
  return (
    String(node.capability.kind || "") === "trigger"
    || String(node.capability.nanobot_task_type || "") === "message_check"
  );
}

function workflowImportPreviewSummary(data: Record<string, unknown>): string {
  const diff = recordFromUnknown(data.diff);
  const added = stringsFromUnknown(diff.added_nodes);
  const removed = stringsFromUnknown(diff.removed_nodes);
  const kept = stringsFromUnknown(diff.kept_nodes);
  const errors = Array.isArray(data.errors) ? data.errors.length : 0;
  const warnings = Array.isArray(data.warnings) ? data.warnings.length : 0;
  const valid = data.valid === false ? "invalid" : "valid";
  return `${valid} / +${added.length} node(s), -${removed.length}, ${kept.length} kept / ${errors} error(s), ${warnings} warning(s)`;
}

function capabilityMatchesQuery(row: Record<string, unknown>, query: string): boolean {
  const needle = query.trim().toLowerCase();
  if (!needle) return true;
  const trueConnection = recordFromUnknown(row.true_connection);
  const values = [
    row.capability_id,
    row.title,
    row.description,
    row.kind,
    row.route,
    row.draft_route,
    row.execution_policy,
    row.trigger_name,
    row.nanobot_task_type,
    trueConnection.state,
    ...stringsFromUnknown(row.interaction_modes),
    ...stringsFromUnknown(row.ascent_channels),
    ...stringsFromUnknown(row.interaction_modules),
    ...stringsFromUnknown(row.information_tags),
    ...stringsFromUnknown(row.result_destinations),
    ...stringsFromUnknown(row.fire_kinds)
  ];
  return values.join(" ").toLowerCase().includes(needle);
}

function capabilityTags(row: Record<string, unknown>): string[] {
  return uniqueStrings([
    ...stringsFromUnknown(row.interaction_modes),
    ...stringsFromUnknown(row.ascent_channels),
    ...stringsFromUnknown(row.interaction_modules),
    ...stringsFromUnknown(row.information_tags)
  ]);
}

type TriggerCatalogGroup = {
  id: string;
  label: string;
  description: string;
  names: string[];
  modules: string[];
  tags: string[];
  kinds: string[];
};

function groupTriggerCatalog(catalog: TriggerCatalog): TriggerCatalogGroup[] {
  const triggers = catalog.triggers ?? [];
  const byName = new Map(triggers.map((trigger) => [String(trigger.name || trigger.class || "trigger"), trigger]));
  const grouped = recordArrayFrom(recordFromUnknown(catalog.groups), "ascending_channel");
  if (grouped.length) {
    return grouped.map((group) => {
      const names = stringsFromUnknown(group.trigger_names);
      const members = names.map((name) => byName.get(name)).filter(Boolean) as Array<Record<string, unknown>>;
      return {
        id: String(group.id || group.label || "channel"),
        label: String(group.label || group.id || "channel"),
        description: String(group.description || ""),
        names,
        modules: uniqueStrings(members.flatMap((trigger) => stringsFromUnknown(trigger.interaction_modules))),
        tags: uniqueStrings(members.flatMap((trigger) => stringsFromUnknown(trigger.information_tags))),
        kinds: uniqueStrings(members.flatMap((trigger) => stringsFromUnknown(trigger.kinds)))
      };
    });
  }

  const groups = new Map<string, Array<Record<string, unknown>>>();
  triggers.forEach((trigger) => {
    const names = groupsForTrigger(trigger);
    names.forEach((kind) => {
      const rows = groups.get(kind) ?? [];
      rows.push(trigger);
      groups.set(kind, rows);
    });
  });
  return Array.from(groups.entries()).map(([kind, rows]) => ({
    id: kind,
    label: kind,
    description: "",
    names: rows.map((trigger) => String(trigger.name || trigger.class || "trigger")),
    modules: uniqueStrings(rows.flatMap((trigger) => stringsFromUnknown(trigger.interaction_modules))),
    tags: uniqueStrings(rows.flatMap((trigger) => stringsFromUnknown(trigger.information_tags))),
    kinds: uniqueStrings(rows.flatMap((trigger) => stringsFromUnknown(trigger.kinds)))
  }));
}

function groupsForTrigger(trigger: Record<string, unknown>): string[] {
  const channels = stringsFromUnknown(trigger.ascending_channels);
  if (channels.length) return channels;
  const raw = stringsFromUnknown(trigger.kinds);
  if (!raw.length) return ["unknown"];
  return raw;
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
  onGraphitiPreview,
  onSourceApplied,
  operatorMode
}: {
  liveState: LiveState;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onGraphitiPreview: (preview: GraphitiPreviewPayload) => void;
  onSourceApplied: () => Promise<void>;
  operatorMode: boolean;
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
          <GraphitiSourceCard pushReceipt={pushReceipt} t={t} onPreview={onGraphitiPreview} onSourceApplied={onSourceApplied} operatorMode={operatorMode} />
        </div>
        <div className="source-panel" hidden={activeSource !== "obsidian"}>
          <ObsidianDraftCard pushReceipt={pushReceipt} t={t} onSourceApplied={onSourceApplied} operatorMode={operatorMode} />
        </div>
        <div className="source-panel" hidden={activeSource !== "calendar"}>
          <CalendarSourceCard pushReceipt={pushReceipt} t={t} onSourceApplied={onSourceApplied} operatorMode={operatorMode} />
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

function ImportLandingMap({
  source,
  sourceDetail = "",
  l15Label = "L1.5 observations",
  l2bLabel = "L2-B target",
  importPolicy,
  observationCount = 0,
  edgeCount = 0,
  applyRoute = "",
  operatorRequired = true
}: {
  source: string;
  sourceDetail?: string;
  l15Label?: string;
  l2bLabel?: string;
  importPolicy?: Record<string, unknown> | null;
  observationCount?: number;
  edgeCount?: number;
  applyRoute?: string;
  operatorRequired?: boolean;
}) {
  const policy = recordFromUnknown(importPolicy);
  const destination = String(policy.destination || "review target");
  const sourceKind = String(policy.source_kind || source.toLowerCase());
  const writePath = String(policy.write_path || "L1.5 admit -> L2-B policy");
  const reason = String(policy.reason || "");
  return (
    <div className="import-landing-map">
      <div className="landing-rail">
        <div className="landing-step source">
          <small>Source</small>
          <strong>{source}</strong>
          <span>{sourceDetail || sourceKind}</span>
        </div>
        <span className="landing-link" aria-hidden="true" />
        <div className="landing-step l15">
          <small>L1.5</small>
          <strong>{l15Label}</strong>
          <span>{`${observationCount} observation(s)`}</span>
        </div>
        <span className="landing-link" aria-hidden="true" />
        <div className="landing-step l2b">
          <small>L2-B</small>
          <strong>{destination}</strong>
          <span>{l2bLabel}</span>
        </div>
      </div>
      <div className="landing-meta-row">
        <span>{writePath}</span>
        {edgeCount ? <span>{`${edgeCount} Edge draft(s)`}</span> : null}
        {applyRoute ? <span>{applyRoute}</span> : null}
        <span>{operatorRequired ? "operator apply required" : "preview only"}</span>
        {reason ? <span>{reason}</span> : null}
      </div>
    </div>
  );
}

function GraphitiSourceCard({
  pushReceipt,
  t,
  onPreview,
  onSourceApplied,
  operatorMode
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onPreview: (preview: GraphitiPreviewPayload) => void;
  onSourceApplied: () => Promise<void>;
  operatorMode: boolean;
}) {
  const [partition, setPartition] = useState("arknights_test");
  const [query, setQuery] = useState("Amiya Chernobog");
  const [limit, setLimit] = useState(6);
  const [searchStrategy, setSearchStrategy] = useState("iterative_hybrid");
  const [searchRecipe, setSearchRecipe] = useState("");
  const [searchDepth, setSearchDepth] = useState(2);
  const [focalNodeUuid, setFocalNodeUuid] = useState("");
  const [searchNodeLabelsText, setSearchNodeLabelsText] = useState("");
  const [searchEdgeTypesText, setSearchEdgeTypesText] = useState("");
  const [hits, setHits] = useState<Array<Record<string, unknown>>>([]);
  const [subgraphNodes, setSubgraphNodes] = useState<Array<Record<string, unknown>>>([]);
  const [subgraphEdges, setSubgraphEdges] = useState<Array<Record<string, unknown>>>([]);
  const [selectedHitKeys, setSelectedHitKeys] = useState<string[]>([]);
  const [exportObservations, setExportObservations] = useState<Array<Record<string, unknown>>>([]);
  const [edgeDrafts, setEdgeDrafts] = useState<Array<Record<string, unknown>>>([]);
  const [identityRefDrafts, setIdentityRefDrafts] = useState<Array<Record<string, unknown>>>([]);
  const [edgePolicy, setEdgePolicy] = useState("");
  const [identityIndex, setIdentityIndex] = useState<Record<string, unknown> | null>(null);
  const [identityHealth, setIdentityHealth] = useState<Record<string, unknown> | null>(null);
  const [refScanPlanRows, setRefScanPlanRows] = useState<Array<Record<string, unknown>>>([]);
  const [refScanResultRows, setRefScanResultRows] = useState<Array<Record<string, unknown>>>([]);
  const [refScanPlanStatus, setRefScanPlanStatus] = useState("");
  const [refScanRemoteChecks, setRefScanRemoteChecks] = useState(false);
  const [refScanDispatching, setRefScanDispatching] = useState(false);
  const [resolvedGraphitiEdges, setResolvedGraphitiEdges] = useState<Array<Record<string, unknown>>>([]);
  const [selectedGraphitiEdgeIndex, setSelectedGraphitiEdgeIndex] = useState(0);
  const [graphitiEdgeApplyStatus, setGraphitiEdgeApplyStatus] = useState("");
  const [graphitiEdgeApplying, setGraphitiEdgeApplying] = useState(false);
  const [selectedIdentityRefDraftIndex, setSelectedIdentityRefDraftIndex] = useState(0);
  const [graphitiRefId, setGraphitiRefId] = useState("");
  const [graphitiRefKind, setGraphitiRefKind] = useState("graphiti_fact");
  const [graphitiRefLocator, setGraphitiRefLocator] = useState("");
  const [graphitiRefWriteAudit, setGraphitiRefWriteAudit] = useState(false);
  const [graphitiRefWritebackStatus, setGraphitiRefWritebackStatus] = useState("");
  const [graphitiRefWritebackPlan, setGraphitiRefWritebackPlan] = useState<Record<string, unknown> | null>(null);
  const [graphitiRefApplying, setGraphitiRefApplying] = useState(false);
  const [graphitiBundle, setGraphitiBundle] = useState<Record<string, unknown> | null>(null);
  const [graphitiMaterialization, setGraphitiMaterialization] = useState<Record<string, unknown> | null>(null);
  const [importPolicy, setImportPolicy] = useState<Record<string, unknown> | null>(null);
  const [policySkippedReason, setPolicySkippedReason] = useState("");
  const [flowSteps, setFlowSteps] = useState<string[]>([]);
  const [destination, setDestination] = useState("isolated_compartment");
  const [status, setStatus] = useState<GraphitiStatusSummary | null>(null);
  const [operatorImporting, setOperatorImporting] = useState(false);
  const operatorImportingRef = useRef(false);
  const graphitiEdgeApplyingRef = useRef(false);
  const graphitiRefApplyingRef = useRef(false);
  const refScanDispatchingRef = useRef(false);
  const selectedHits = useMemo(
    () => hits.filter((hit, index) => selectedHitKeys.includes(graphitiHitKey(hit, index))),
    [hits, selectedHitKeys]
  );
  const selectedIdentityRefDraft = useMemo(
    () => identityRefDrafts[Math.min(selectedIdentityRefDraftIndex, Math.max(0, identityRefDrafts.length - 1))] ?? null,
    [identityRefDrafts, selectedIdentityRefDraftIndex]
  );
  useEffect(() => {
    const draft = selectedIdentityRefDraft;
    if (!draft) {
      setGraphitiRefId("");
      setGraphitiRefKind("graphiti_fact");
      setGraphitiRefLocator("");
      return;
    }
    setGraphitiRefId(String(draft.ref_id || ""));
    setGraphitiRefKind(String(draft.ref_kind || graphitiRefKindFromDraft(draft)));
    setGraphitiRefLocator(graphitiRefLocatorFromDraft(draft));
  }, [selectedIdentityRefDraft]);
  const selectedPreview = () => buildGraphitiPreviewPayload({
    hits: selectedHits,
    subgraphNodes,
    subgraphEdges,
    partition,
    query
  });
  const refreshSelectionPreview = (nextSelectedKeys: string[], silent = true) => {
    const nextSelectedHits = hits.filter((hit, index) => nextSelectedKeys.includes(graphitiHitKey(hit, index)));
    onPreview({
      ...buildGraphitiPreviewPayload({
        hits: nextSelectedHits,
        subgraphNodes,
        subgraphEdges,
        partition,
        query
      }),
      silent
    });
  };
  const clearGraphitiPreview = (reason = "graphiti.subgraph.preview.clear") => {
    onPreview({ hits: [], nodes: [], edges: [], partition, query });
    if (reason) {
      pushReceipt(localReceipt(reason, true, { partition, query: query.trim(), canvas_preview_cleared: true }));
    }
  };
  const clearGraphitiPlanState = (reason = "") => {
    setExportObservations([]);
    setEdgeDrafts([]);
    setIdentityRefDrafts([]);
    setEdgePolicy("");
    setResolvedGraphitiEdges([]);
    setSelectedGraphitiEdgeIndex(0);
    setGraphitiEdgeApplyStatus("");
    setSelectedIdentityRefDraftIndex(0);
    setGraphitiRefWritebackStatus("");
    setGraphitiRefWritebackPlan(null);
    setGraphitiBundle(null);
    setGraphitiMaterialization(null);
    setImportPolicy(null);
    setPolicySkippedReason(reason);
    setFlowSteps([]);
  };
  const showGraphitiError = (
    action: string,
    exc: unknown,
    data: Record<string, unknown> = {},
    clearSource = false
  ) => {
    const receipt = errorReceipt(action, exc, data);
    const reason = String((receipt.data ?? {}).error || "request_failed");
    if (clearSource) {
      setHits([]);
      setSubgraphNodes([]);
      setSubgraphEdges([]);
      setSelectedHitKeys([]);
      clearGraphitiPreview("");
    }
    clearGraphitiPlanState(reason);
    pushReceipt(receipt);
  };
  const clearGraphitiSearchResults = () => {
    setHits([]);
    setSubgraphNodes([]);
    setSubgraphEdges([]);
    setSelectedHitKeys([]);
    clearGraphitiPlanState("");
    clearGraphitiPreview("");
  };
  const loadStatus = async () => {
    try {
      const receipt = await api.graphitiStatus();
      const normalized = normalizeGraphitiStatus(receipt);
      setStatus(normalized);
      pushReceipt({
        action: "graphiti.status",
        success: true,
        dry_run: true,
        operator_mode: false,
        data: { status: normalized }
      });
    } catch (exc) {
      setStatus({
        installed: false,
        provider: "unknown",
        model: "",
        secretConfigured: false,
        embeddingProvider: "unknown",
        embeddingConfigured: false,
        partitions: [],
        message: exc instanceof Error ? exc.message : String(exc)
      });
      pushReceipt(errorReceipt("graphiti.status", exc));
    }
  };
  const search = async () => {
    if (!query.trim()) {
      setHits([]);
      setSubgraphNodes([]);
      setSubgraphEdges([]);
      setSelectedHitKeys([]);
      clearGraphitiPlanState("missing_query");
      clearGraphitiPreview();
      pushReceipt(localReceipt("graphiti.subgraph.search", false, { error: "missing_query" }));
      return;
    }
    try {
      const receipt = await api.graphitiSubgraphSearch({
        query: query.trim(),
        partition,
        limit,
        strategy: searchStrategy,
        search_recipe: searchRecipe,
        depth: searchDepth,
        expansion_limit: 3,
        focal_node_uuid: focalNodeUuid.trim(),
        node_labels: parseTags(searchNodeLabelsText),
        edge_types: parseTags(searchEdgeTypesText),
        enrich: true
      });
      const nextHits = receiptArray(receipt, "hits");
      const subgraph = receiptRecord(receipt, "subgraph");
      const nextBundle = receiptRecord(receipt, "graphiti_bundle");
      const nextSubgraphNodes = recordArrayFrom(subgraph, "nodes");
      const nextSubgraphEdges = recordArrayFrom(subgraph, "edges");
      setHits(nextHits);
      setSubgraphNodes(nextSubgraphNodes);
      setSubgraphEdges(nextSubgraphEdges);
      setSelectedHitKeys(nextHits.map((hit, index) => graphitiHitKey(hit, index)));
      clearGraphitiPlanState("");
      setGraphitiBundle(Object.keys(nextBundle).length ? nextBundle : null);
      if (receipt.success === false || (!nextHits.length && !nextSubgraphNodes.length)) {
        clearGraphitiPreview("");
      }
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
      showGraphitiError("graphiti.subgraph.search", exc, { partition, query }, true);
    }
  };
  const toggleHit = (key: string) => {
    setSelectedHitKeys((current) => {
      const nextKeys = current.includes(key)
        ? current.filter((item) => item !== key)
        : [...current, key];
      clearGraphitiPlanState(nextKeys.length ? "" : "no_hits_selected");
      refreshSelectionPreview(nextKeys);
      return nextKeys;
    });
  };
  const selectAllHits = () => {
    const nextKeys = hits.map((hit, index) => graphitiHitKey(hit, index));
    setSelectedHitKeys(nextKeys);
    clearGraphitiPlanState(nextKeys.length ? "" : "no_hits_selected");
    refreshSelectionPreview(nextKeys);
  };
  const lookupFocalUuid = async () => {
    const uuid = focalNodeUuid.trim();
    if (!uuid) {
      pushReceipt(localReceipt("graphiti.lookup", false, { error: "missing_uuid", partition }));
      return;
    }
    try {
      pushReceipt(await api.graphitiLookup({ uuid, partition }));
    } catch (exc) {
      showGraphitiError("graphiti.lookup", exc, { partition, uuid });
    }
  };
  const clearHitSelection = () => {
    setSelectedHitKeys([]);
    clearGraphitiPlanState("no_hits_selected");
    clearGraphitiPreview();
  };
  const showExportReceipt = (receipt: Receipt) => {
    const data = receipt.data ?? {};
    const nextBundle = recordFromUnknown(data.graphiti_bundle);
    const topTransform = recordFromUnknown(data.transform_preview);
    const isMaterializeReceipt = String(receipt.action || "") === "graphiti.subgraph.materialize_l2b"
      || "would_materialize" in data
      || ("direct_l2b_write" in data && "node_count" in data);
    const materialization = isMaterializeReceipt ? {
      materialization_state: String(data.materialization_state || (data.direct_l2b_write ? "materialized_l2b_pointer_graph" : "preview_only_not_materialized")),
      direct_l2b_write: Boolean(data.direct_l2b_write),
      would_materialize: Boolean(data.would_materialize),
      node_count: data.node_count ?? recordArrayFrom(topTransform, "l2b_nodes").length,
      edge_count: data.edge_count ?? (recordArrayFrom(topTransform, "l2b_edges").length + recordArrayFrom(topTransform, "episode_links").length),
      nodes_upserted: data.nodes_upserted ?? 0,
      edges_added: data.edges_added ?? 0,
      edges_skipped_duplicate: data.edges_skipped_duplicate ?? 0,
      context_node_uuids: Array.isArray(data.context_node_uuids) ? data.context_node_uuids.map(String) : [],
      context_route: String(data.context_route || "/api/l2b/subgraphs/context"),
      remote_proxy: recordFromUnknown(data.remote_proxy)
    } : {};
    let displayBundle = nextBundle;
    if (Object.keys(nextBundle).length && Object.keys(topTransform).length) {
      const overlay = recordFromUnknown(nextBundle.import_overlay);
      const contextPolicy = recordFromUnknown(overlay.context_route_policy);
      displayBundle = {
        ...nextBundle,
        import_overlay: {
          ...overlay,
          destination: String(data.destination || overlay.destination || destination),
          materialization_state: String(data.materialization_state || overlay.materialization_state || "preview_or_materialized_l2b_pointer_graph"),
          transform_preview: topTransform,
          apply_route: "/api/graphiti/subgraph/materialize-l2b",
          context_route_policy: {
            ...contextPolicy,
            route: String(data.context_route || contextPolicy.route || "/api/l2b/subgraphs/context"),
            requires_materialized_l2b_uuid: true,
            preview_uuid_prefix: "graphiti:"
          }
        }
      };
    }
    setExportObservations(receiptArray(receipt, "observations"));
    setEdgeDrafts(receiptArray(receipt, "edge_drafts"));
    const nextIdentityRefDrafts = receiptArray(receipt, "identity_ref_drafts");
    setIdentityRefDrafts(nextIdentityRefDrafts);
    setSelectedIdentityRefDraftIndex(0);
    setGraphitiRefWritebackPlan(null);
    setGraphitiRefWritebackStatus(nextIdentityRefDrafts.length ? "" : "no_identity_ref_drafts");
    setEdgePolicy(String(data.edge_write_policy || ""));
    setResolvedGraphitiEdges([]);
    setSelectedGraphitiEdgeIndex(0);
    setGraphitiEdgeApplyStatus("");
    const nextPolicy = recordFromUnknown(data.import_policy);
    setImportPolicy(Object.keys(nextPolicy).length ? nextPolicy : null);
    setPolicySkippedReason(String(data.policy_skipped_reason || data.error || ""));
    const steps = Array.isArray(data.flow_steps) ? data.flow_steps.map(String) : [];
    setFlowSteps(steps);
    setGraphitiMaterialization(Object.keys(materialization).length ? materialization : null);
    setGraphitiBundle(Object.keys(displayBundle).length ? displayBundle : null);
    pushReceipt(receipt);
  };
  const exportDraft = async () => {
    if (!selectedHits.length) {
      clearGraphitiPlanState("no_hits_selected");
      pushReceipt(localReceipt("graphiti.subgraph.export_draft", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      showExportReceipt(await api.graphitiSubgraphExportDraft({ partition, query: query.trim(), hits: selectedHits }));
    } catch (exc) {
      showGraphitiError("graphiti.subgraph.export_draft", exc, { partition, query });
    }
  };
  const graphitiMaterializePayload = (execute: boolean): Record<string, unknown> => {
    const payload: Record<string, unknown> = {
      partition,
      query: query.trim(),
      hits: selectedHits,
      destination,
      subgraph_label: query.trim() || partition,
      dry_run: !execute || !operatorMode,
      operator_mode: execute && operatorMode
    };
    if (graphitiBundle && Object.keys(graphitiBundle).length) {
      payload.graphiti_bundle = graphitiBundle;
    }
    return payload;
  };
  const previewMaterializeGraphitiSubgraph = async () => {
    if (!selectedHits.length) {
      clearGraphitiPlanState("no_hits_selected");
      pushReceipt(localReceipt("graphiti.subgraph.materialize_l2b", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      showExportReceipt(await api.graphitiSubgraphMaterializeL2B(graphitiMaterializePayload(false)));
    } catch (exc) {
      showGraphitiError("graphiti.subgraph.materialize_l2b", exc, { partition, query, destination });
    }
  };
  const materializeGraphitiSubgraph = async () => {
    if (operatorImportingRef.current) {
      pushReceipt(localReceipt("graphiti.subgraph.materialize_l2b", false, { error: "operator_import_in_flight", partition, query }));
      return;
    }
    if (!selectedHits.length) {
      clearGraphitiPlanState("no_hits_selected");
      clearGraphitiPreview("");
      pushReceipt(localReceipt("graphiti.subgraph.materialize_l2b", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    operatorImportingRef.current = true;
    setOperatorImporting(true);
    try {
      const receipt = await api.graphitiSubgraphMaterializeL2B(graphitiMaterializePayload(true));
      showExportReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        await onSourceApplied();
        onPreview({ ...selectedPreview(), silent: true });
      }
    } catch (exc) {
      showGraphitiError("graphiti.subgraph.materialize_l2b.execute", exc, { partition, query, destination });
    } finally {
      operatorImportingRef.current = false;
      setOperatorImporting(false);
    }
  };
  const previewImportPolicy = async () => {
    if (!selectedHits.length) {
      clearGraphitiPlanState("no_hits_selected");
      pushReceipt(localReceipt("graphiti.subgraph.import_plan", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    try {
      showExportReceipt(await api.graphitiSubgraphImportPlan({
        partition,
        query: query.trim(),
        hits: selectedHits,
        destination,
        workspace_id: "memory_graph",
        subgraph_label: query.trim() || partition,
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showGraphitiError("graphiti.subgraph.import_plan", exc, { partition, query, destination });
    }
  };
  const loadIdentityIndex = async () => {
    try {
      const receipt = await api.memoryIdentityRefIndex(80);
      setIdentityIndex(receipt.data ?? {});
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("memory.identity_ref_index.snapshot", exc));
    }
  };
  const verifyIdentityRefs = async () => {
    try {
      const receipt = await api.memoryIdentityRefVerify({
        update_index: false,
        dry_run: true,
        operator_mode: false
      });
      setIdentityHealth(receipt.data ?? {});
      pushReceipt(receipt);
    } catch (exc) {
      pushReceipt(errorReceipt("memory.identity_ref_index.verify", exc));
    }
  };
  const refScanRemotePayload = () => ({
    remote_checks: refScanRemoteChecks ? ["url", "ecs", "graphiti"] : []
  });
  const draftRefScanPlan = async () => {
    try {
      const receipt = await api.memoryIdentityRefScanPlan({
        limit: 80,
        priority: "low",
        ...refScanRemotePayload()
      });
      const rows = receiptArray(receipt, "ref_scan_plan");
      setRefScanPlanRows(rows);
      const counts = recordFromUnknown((receipt.data ?? {}).counts);
      setRefScanPlanStatus(String((receipt.data ?? {}).error || `${rows.length} ref(s) / ${String(counts.ref_count ?? rows.length)} planned`));
      pushReceipt(receipt);
    } catch (exc) {
      setRefScanPlanStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.ref_scan_plan", exc));
    }
  };
  const dispatchRefScan = async () => {
    if (refScanDispatchingRef.current) {
      pushReceipt(localReceipt("memory.identity_ref_index.ref_scan_dispatch", false, { error: "ref_scan_dispatch_in_flight", partition, query }));
      return;
    }
    refScanDispatchingRef.current = true;
    setRefScanDispatching(true);
    try {
      const receipt = await api.memoryIdentityRefScanDispatch({
        limit: 80,
        priority: "low",
        dry_run: !operatorMode,
        operator_mode: operatorMode,
        ...refScanRemotePayload()
      });
      const rows = receiptArray(receipt, "ref_scan_plan");
      if (rows.length) {
        setRefScanPlanRows(rows);
      }
      setRefScanPlanStatus(String((receipt.data ?? {}).error || (receipt.data ?? {}).dispatch_skipped_reason || (receipt.data ?? {}).task_id || "ref_scan_dispatched"));
      pushReceipt(receipt);
    } catch (exc) {
      setRefScanPlanStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.ref_scan_dispatch", exc));
    } finally {
      refScanDispatchingRef.current = false;
      setRefScanDispatching(false);
    }
  };
  const loadRefScanResults = async () => {
    try {
      const receipt = await api.memoryIdentityRefScanResults(12);
      const rows = receiptArray(receipt, "rows");
      setRefScanResultRows(rows);
      setRefScanPlanStatus((receipt.data ?? {}).available === false
        ? String((receipt.data ?? {}).error || "ref_scan_results_unavailable")
        : `${rows.length} result row(s)`);
      pushReceipt(receipt);
    } catch (exc) {
      setRefScanPlanStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.ref_scan_results", exc));
    }
  };
  const graphitiRefWritebackPayload = (execute: boolean) => {
    const draft = selectedIdentityRefDraft ?? {};
    const graphitiKind = graphitiRefKindFromDraft(draft);
    const graphitiUuid = graphitiRefUuidFromDraft(draft);
    const refKind = graphitiRefKind.trim() || String(draft.ref_kind || graphitiKind);
    const refId = graphitiRefId.trim() || String(draft.ref_id || `graphiti:${partition}:${graphitiKind}:${graphitiUuid}`);
    const locator = graphitiRefLocator.trim();
    const externalRef: Record<string, unknown> = {
      ref_id: refId,
      ref_kind: refKind,
      managed_by: "web_console_operator",
      meta: {
        source_tool: "web_console.graphiti_ref_writeback_panel",
        graphiti_partition: partition,
        graphiti_kind: graphitiKind
      }
    };
    if (locator) {
      if (/^https?:\/\//i.test(locator)) {
        externalRef.url = locator;
      } else {
        externalRef.locator = locator;
      }
    }
    const externalRefs = locator ? [externalRef] : [];
    return {
      ...draft,
      partition,
      graphiti_kind: graphitiKind,
      graphiti_uuid: graphitiUuid,
      graphiti_raw: Object.keys(recordFromUnknown(draft.graphiti_raw)).length ? draft.graphiti_raw : draft,
      external_refs: externalRefs,
      requested_by: "web_console_source_board",
      dry_run: !execute || !operatorMode,
      operator_mode: execute && operatorMode,
      write_graphiti_audit_episode: execute && operatorMode && graphitiRefWriteAudit
    };
  };
  const previewGraphitiRefWriteback = async () => {
    if (!selectedIdentityRefDraft || !graphitiRefUuidFromDraft(selectedIdentityRefDraft)) {
      setGraphitiRefWritebackStatus("no_identity_ref_draft");
      pushReceipt(localReceipt("memory.identity_ref_index.graphiti_ref_writeback_draft", false, { error: "no_identity_ref_draft", partition, query }));
      return;
    }
    try {
      const receipt = await api.memoryIdentityRefGraphitiRefDraft(graphitiRefWritebackPayload(false));
      setGraphitiRefWritebackPlan(receipt.data ?? null);
      setGraphitiRefWritebackStatus(String((receipt.data ?? {}).error || "preview_ready"));
      pushReceipt(receipt);
    } catch (exc) {
      setGraphitiRefWritebackStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.graphiti_ref_writeback_draft", exc, { partition, query }));
    }
  };
  const applyGraphitiRefWriteback = async () => {
    if (graphitiRefApplyingRef.current) {
      pushReceipt(localReceipt("memory.identity_ref_index.graphiti_ref_writeback_apply", false, { error: "graphiti_ref_apply_in_flight", partition, query }));
      return;
    }
    if (!selectedIdentityRefDraft || !graphitiRefUuidFromDraft(selectedIdentityRefDraft)) {
      setGraphitiRefWritebackStatus("no_identity_ref_draft");
      pushReceipt(localReceipt("memory.identity_ref_index.graphiti_ref_writeback_apply", false, { error: "no_identity_ref_draft", partition, query }));
      return;
    }
    graphitiRefApplyingRef.current = true;
    setGraphitiRefApplying(true);
    try {
      const receipt = await api.memoryIdentityRefGraphitiRefApply(graphitiRefWritebackPayload(true));
      const data = receipt.data ?? {};
      const snapshot = recordFromUnknown(data.snapshot);
      if (Object.keys(snapshot).length) {
        setIdentityIndex(snapshot);
      }
      setGraphitiRefWritebackPlan(data);
      setGraphitiRefWritebackStatus(String(data.error || data.apply_skipped_reason || data.mutation_scope || "ref_writeback_done"));
      pushReceipt(receipt);
    } catch (exc) {
      setGraphitiRefWritebackStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.graphiti_ref_writeback_apply", exc, { partition, query }));
    } finally {
      graphitiRefApplyingRef.current = false;
      setGraphitiRefApplying(false);
    }
  };
  const graphitiEdgeResolverPayload = () => ({
    partition,
    edge_drafts: edgeDrafts,
    edge_index: selectedGraphitiEdgeIndex
  });
  const resolveGraphitiEdgeDrafts = async () => {
    if (!edgeDrafts.length) {
      setResolvedGraphitiEdges([]);
      setGraphitiEdgeApplyStatus("no_edge_drafts");
      pushReceipt(localReceipt("memory.identity_ref_index.resolve_graphiti", false, { error: "no_edge_drafts", partition, query }));
      return;
    }
    try {
      const receipt = await api.memoryIdentityRefResolveGraphiti({
        partition,
        edge_drafts: edgeDrafts
      });
      const edges = receiptArray(receipt, "edges");
      setResolvedGraphitiEdges(edges);
      setGraphitiEdgeApplyStatus(String((receipt.data ?? {}).error || `${edges.length} edge(s) resolved`));
      pushReceipt(receipt);
    } catch (exc) {
      setGraphitiEdgeApplyStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.resolve_graphiti", exc, { partition, query }));
    }
  };
  const previewGraphitiEdgeApply = async () => {
    if (!edgeDrafts.length) {
      setGraphitiEdgeApplyStatus("no_edge_drafts");
      pushReceipt(localReceipt("memory.identity_ref_index.apply_graphiti_edge", false, { error: "no_edge_drafts", partition, query }));
      return;
    }
    try {
      const receipt = await api.memoryIdentityRefApplyGraphitiEdge({
        ...graphitiEdgeResolverPayload(),
        dry_run: true,
        operator_mode: false
      });
      setResolvedGraphitiEdges(receiptArray(receipt, "edges").length ? receiptArray(receipt, "edges") : resolvedGraphitiEdges);
      setGraphitiEdgeApplyStatus(String((receipt.data ?? {}).error || (receipt.data ?? {}).apply_skipped_reason || "preview_ready"));
      pushReceipt(receipt);
    } catch (exc) {
      setGraphitiEdgeApplyStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.apply_graphiti_edge", exc, graphitiEdgeResolverPayload()));
    }
  };
  const materializeGraphitiEdge = async () => {
    if (graphitiEdgeApplyingRef.current) {
      pushReceipt(localReceipt("memory.identity_ref_index.apply_graphiti_edge", false, { error: "edge_apply_in_flight", partition, query }));
      return;
    }
    if (!edgeDrafts.length) {
      setGraphitiEdgeApplyStatus("no_edge_drafts");
      pushReceipt(localReceipt("memory.identity_ref_index.apply_graphiti_edge", false, { error: "no_edge_drafts", partition, query }));
      return;
    }
    graphitiEdgeApplyingRef.current = true;
    setGraphitiEdgeApplying(true);
    try {
      const receipt = await api.memoryIdentityRefApplyGraphitiEdge({
        ...graphitiEdgeResolverPayload(),
        dry_run: !operatorMode,
        operator_mode: operatorMode
      });
      setGraphitiEdgeApplyStatus(String((receipt.data ?? {}).error || (receipt.data ?? {}).apply_skipped_reason || (receipt.data ?? {}).mutation_scope || "edge_apply_done"));
      pushReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        await onSourceApplied();
      }
    } catch (exc) {
      setGraphitiEdgeApplyStatus(exc instanceof Error ? exc.message : String(exc));
      pushReceipt(errorReceipt("memory.identity_ref_index.apply_graphiti_edge", exc, graphitiEdgeResolverPayload()));
    } finally {
      graphitiEdgeApplyingRef.current = false;
      setGraphitiEdgeApplying(false);
    }
  };
  const previewSelectedOnCanvas = () => {
    if (!selectedHits.length) {
      clearGraphitiPlanState("no_hits_selected");
      clearGraphitiPreview("");
      pushReceipt(localReceipt("graphiti.subgraph.preview", false, { error: "no_hits_selected", partition, query }));
      return;
    }
    onPreview(selectedPreview());
  };
  const updateDestination = (value: string) => {
    setDestination(value);
    clearGraphitiPlanState("destination_changed");
  };
  const updatePartition = (value: string) => {
    setPartition(value);
    clearGraphitiSearchResults();
  };
  const updateQuery = (value: string) => {
    setQuery(value);
    clearGraphitiSearchResults();
  };
  const updateLimit = (value: string) => {
    setLimit(Math.max(1, Math.min(20, Number(value) || 1)));
    clearGraphitiSearchResults();
  };
  const updateSearchStrategy = (value: string) => {
    setSearchStrategy(value);
    clearGraphitiSearchResults();
  };
  const updateSearchRecipe = (value: string) => {
    setSearchRecipe(value);
    clearGraphitiSearchResults();
  };
  const updateSearchDepth = (value: string) => {
    setSearchDepth(Math.max(1, Math.min(3, Number(value) || 1)));
    clearGraphitiSearchResults();
  };
  const updateFocalNodeUuid = (value: string) => {
    setFocalNodeUuid(value);
    clearGraphitiSearchResults();
  };
  const updateSearchNodeLabels = (value: string) => {
    setSearchNodeLabelsText(value);
    clearGraphitiSearchResults();
  };
  const updateSearchEdgeTypes = (value: string) => {
    setSearchEdgeTypesText(value);
    clearGraphitiSearchResults();
  };
  const graphitiRefPlanData = graphitiRefWritebackPlan ?? {};
  const graphitiRecordRef = recordFromUnknown(graphitiRefPlanData.graphiti_record_ref);
  const graphitiAuditDraft = recordFromUnknown(graphitiRefPlanData.audit_episode_draft);
  const graphitiExternalRefs = Array.isArray(graphitiRefPlanData.external_ref_records)
    ? graphitiRefPlanData.external_ref_records.filter(
      (row): row is Record<string, unknown> => Boolean(row) && typeof row === "object" && !Array.isArray(row)
    )
    : [];

  return (
    <article className="source-card graphiti-source-card">
      <div className="source-card-head">
        <strong><Database size={16} /> {t.graphiti}</strong>
        <small>{t.graphitiWriteThroughL2B}</small>
      </div>
      <div className={status?.installed ? "graphiti-status-strip ok" : "graphiti-status-strip"}>
        <span><CircleDot size={13} /> {status ? `${status.provider || "-"} / ${status.model || "-"}` : "Graphiti status"}</span>
        <small>{status ? `${status.installed ? "installed" : "missing"} / secret ${status.secretConfigured ? "ok" : "missing"} / ${status.partitions.length} partitions` : "not checked"}</small>
        <button className="button small" onClick={() => void loadStatus()}><RefreshCw size={14} /> Status</button>
      </div>
      <div className="identity-index-strip">
        <span>
          <strong>{String(identityIndex?.identity_count ?? "-")}</strong>
          <small>Identity</small>
        </span>
        <span>
          <strong>{String(identityIndex?.ref_count ?? "-")}</strong>
          <small>Refs</small>
        </span>
        <span>
          <strong>{String(recordFromUnknown(identityHealth?.health_counts).ok ?? "-")}</strong>
          <small>Ref ok</small>
        </span>
        <button className="button small" onClick={() => void loadIdentityIndex()}><Database size={14} /> {t.identityIndex}</button>
        <button className="button small" onClick={() => void verifyIdentityRefs()}><ShieldCheck size={14} /> {t.verifyRefs}</button>
        <label className="identity-ref-remote-toggle">
          <input type="checkbox" checked={refScanRemoteChecks} onChange={(event) => setRefScanRemoteChecks(event.target.checked)} />
          <span>Remote probes</span>
        </label>
        <button className="button small" onClick={() => void draftRefScanPlan()}><Workflow size={14} /> {t.refScanPlan}</button>
        <button className="button small ghost" onClick={() => void dispatchRefScan()} disabled={refScanDispatching}><Play size={14} /> {operatorMode ? t.dispatchRefScan : t.dryApply}</button>
        <button className="button small" onClick={() => void loadRefScanResults()}><RefreshCw size={14} /> {t.refScanResults}</button>
      </div>
      {refScanPlanRows.length || refScanResultRows.length || refScanPlanStatus ? (
        <div className="edge-resolver-panel ref-scan-panel">
          <div className="edge-resolver-head">
            <strong>{t.refScanPlan}</strong>
            <small>{`${refScanPlanRows.length} ref(s) / ${refScanResultRows.length} result(s)`}</small>
          </div>
          {refScanPlanStatus ? <small className="muted">{refScanPlanStatus}</small> : null}
          {refScanPlanRows.slice(0, 4).map((row, index) => {
            const scanTargets = Array.isArray(row.scan_targets)
              ? (row.scan_targets as Array<Record<string, unknown>>)
              : [];
            const checks = Array.isArray(row.nanobot_checks)
              ? row.nanobot_checks.map(String)
              : [];
            return (
              <div className="preview-row mapping-row" key={`${String(row.ref_id || index)}:ref-scan-plan`}>
                <span>{String(row.ref_id || row.kind || "ref")}</span>
                <small>{`${String(row.kind || "external")} / ${String(row.risk_level || "unknown")}`}</small>
                <small>{`${scanTargets.map((target) => String(target.target_type || "-")).join(", ") || "no locator"} / ${checks.slice(0, 3).join(", ")}`}</small>
              </div>
            );
          })}
          {refScanResultRows.slice(0, 4).map((row, index) => {
            const samples = Array.isArray(row.ref_result_sample)
              ? (row.ref_result_sample as Array<Record<string, unknown>>)
              : [];
            return (
              <div className="preview-row import-plan-row" key={`${String(row.stream_id || index)}:ref-scan-result`}>
                <span>{`${String(row.status || "-")} / ${String(row.task_id || "-")}`}</span>
                <small>{`${String(row.ref_result_count ?? 0)} ref result(s) / ${String(row.manifest_delta_count ?? 0)} manifest delta(s)`}</small>
                <small>{samples.map((sample) => `${String(sample.ref_id || "-")}:${String(sample.health || "-")}`).join(", ") || String(row.result_summary || "")}</small>
              </div>
            );
          })}
        </div>
      ) : null}
      <label>
        <span>{t.partition}</span>
        <select value={partition} onChange={(event) => updatePartition(event.target.value)}>
          <option value="arknights_test">arknights_test</option>
          <option value="noble_etiquette">noble_etiquette</option>
          <option value="goslo">goslo</option>
          <option value="maid">maid</option>
          <option value="scene">scene</option>
          <option value="user">user</option>
        </select>
      </label>
      <label>
        <span>{t.graphitiQuery}</span>
        <input value={query} onChange={(event) => updateQuery(event.target.value)} placeholder={t.graphitiQuery} />
      </label>
      <label>
        <span>{t.limit}</span>
        <input
          type="number"
          min={1}
          max={20}
          value={limit}
          onChange={(event) => updateLimit(event.target.value)}
        />
      </label>
      <label>
        <span>Strategy</span>
        <select value={searchStrategy} onChange={(event) => updateSearchStrategy(event.target.value)}>
          <option value="iterative_hybrid">iterative hybrid</option>
          <option value="hybrid">hybrid</option>
          <option value="node_distance">node distance</option>
        </select>
      </label>
      <label>
        <span>Recipe</span>
        <select value={searchRecipe} onChange={(event) => updateSearchRecipe(event.target.value)}>
          <option value="">public/default</option>
          <option value="combined_rrf">combined RRF</option>
          <option value="combined_mmr">combined MMR</option>
          <option value="combined_cross_encoder">combined cross encoder</option>
          <option value="edge_rrf">edge RRF</option>
          <option value="edge_mmr">edge MMR</option>
          <option value="edge_node_distance">edge node distance</option>
          <option value="edge_episode_mentions">edge episode mentions</option>
          <option value="edge_cross_encoder">edge cross encoder</option>
          <option value="node_rrf">node RRF</option>
          <option value="node_mmr">node MMR</option>
          <option value="node_node_distance">node node distance</option>
          <option value="node_episode_mentions">node episode mentions</option>
          <option value="node_cross_encoder">node cross encoder</option>
          <option value="community_rrf">community RRF</option>
        </select>
      </label>
      <label>
        <span>Depth</span>
        <input
          type="number"
          min={1}
          max={3}
          value={searchDepth}
          onChange={(event) => updateSearchDepth(event.target.value)}
        />
      </label>
      <label>
        <span>Focal UUID</span>
        <input
          value={focalNodeUuid}
          onChange={(event) => updateFocalNodeUuid(event.target.value)}
          placeholder="optional"
        />
      </label>
      <label>
        <span>Node labels</span>
        <input
          value={searchNodeLabelsText}
          onChange={(event) => updateSearchNodeLabels(event.target.value)}
          placeholder="Entity, Person"
        />
      </label>
      <label>
        <span>Edge types</span>
        <input
          value={searchEdgeTypesText}
          onChange={(event) => updateSearchEdgeTypes(event.target.value)}
          placeholder="RELATES_TO, CrisisFact"
        />
      </label>
      <label>
        <span>{t.importDestination}</span>
        <select value={destination} onChange={(event) => updateDestination(event.target.value)}>
          {GRAPH_IMPORT_DESTINATIONS.map((item) => <option key={item} value={item}>{item}</option>)}
        </select>
      </label>
      <div className="button-row">
        <button className="button primary" onClick={() => void search()}><Search size={16} /> {t.searchGraphiti}</button>
        <button className="button" onClick={() => void lookupFocalUuid()}><CircleDot size={16} /> Lookup UUID</button>
        <button className="button" onClick={previewSelectedOnCanvas}><GitBranch size={16} /> {t.previewOnCanvas}</button>
        <button className="button" onClick={() => void previewImportPolicy()}><Workflow size={16} /> {t.previewPolicy}</button>
        <button className="button" onClick={() => void exportDraft()}><UploadCloud size={16} /> {t.exportSubgraphDraft}</button>
        <button className="button ghost" onClick={() => void previewMaterializeGraphitiSubgraph()}><ShieldCheck size={16} /> {t.previewGraphitiMaterialize}</button>
        <button className="button ghost" onClick={() => void materializeGraphitiSubgraph()} disabled={operatorImporting}><UploadCloud size={16} /> {operatorMode ? t.materializeGraphitiSubgraph : t.dryApply}</button>
      </div>
      <div className="hit-list">
        <div className="hit-list-head">
          <strong>{t.resultGraph}</strong>
          <small>{`${selectedHits.length}/${hits.length} ${t.selectedOf} / ${subgraphNodes.length} Node / ${subgraphEdges.length} Edge`}</small>
        </div>
        {hits.length ? (
          <div className="button-row compact">
            <button className="button small" onClick={selectAllHits}>{t.selectAll}</button>
            <button className="button small ghost" onClick={clearHitSelection}>{t.clearSelection}</button>
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
      {graphitiBundle ? <GraphitiBundlePanel bundle={graphitiBundle} /> : null}
      {graphitiMaterialization ? (
        <div className="edge-resolver-panel graphiti-materialization-panel">
          <div className="edge-resolver-head">
            <strong>L2-B materialization</strong>
            <small>{String(graphitiMaterialization.materialization_state || "preview_only_not_materialized")}</small>
          </div>
          <div className="graphiti-bundle-stats">
            <span>
              <strong>{String(graphitiMaterialization.node_count ?? 0)}</strong>
              <small>pointer nodes</small>
            </span>
            <span>
              <strong>{String(graphitiMaterialization.edge_count ?? 0)}</strong>
              <small>pointer edges</small>
            </span>
            <span>
              <strong>{String(graphitiMaterialization.nodes_upserted ?? 0)}</strong>
              <small>upserted</small>
            </span>
            <span>
              <strong>{`${String(graphitiMaterialization.edges_added ?? 0)}/${String(graphitiMaterialization.edges_skipped_duplicate ?? 0)}`}</strong>
              <small>edge add/skip</small>
            </span>
          </div>
          <div className="preview-row import-plan-row">
            <span>{graphitiMaterialization.direct_l2b_write ? "direct L2-B write confirmed" : "dry-run materialization preview"}</span>
            <small>{String(graphitiMaterialization.context_route || "/api/l2b/subgraphs/context")}</small>
            <small>{(Array.isArray(graphitiMaterialization.context_node_uuids) ? graphitiMaterialization.context_node_uuids : []).slice(0, 2).map(String).join(", ") || "context UUIDs appear after projection"}</small>
          </div>
        </div>
      ) : null}
      {exportObservations.length || edgeDrafts.length || identityRefDrafts.length || policySkippedReason ? (
        <div className="note-preview-list graphiti-export-plan">
          <strong>Import plan</strong>
          <small>{`${exportObservations.length} L1.5 observation(s) / ${edgeDrafts.length} Edge draft(s) / ${identityRefDrafts.length} Ref draft(s)`}</small>
          {policySkippedReason ? <small className="warn-text">{policySkippedReason}</small> : null}
          {edgePolicy ? <small className="muted">{edgePolicy}</small> : null}
          <ImportLandingMap
            source="Graphiti"
            sourceDetail={`${partition} / ${query.trim() || "search"}`}
            l15Label="USER_EXPLICIT"
            l2bLabel="subgraph overlay"
            importPolicy={importPolicy}
            observationCount={exportObservations.length}
            edgeCount={edgeDrafts.length}
            applyRoute="/api/graphiti/subgraph/materialize-l2b"
          />
          {identityRefDrafts.length ? (
            <div className="edge-resolver-panel graphiti-ref-writeback-panel">
              <div className="edge-resolver-head">
                <strong>{t.graphitiRefWriteback}</strong>
                <small>{`${selectedIdentityRefDraftIndex + 1}/${identityRefDrafts.length}`}</small>
              </div>
              <label>
                <span>Graphiti record</span>
                <select
                  value={selectedIdentityRefDraftIndex}
                  onChange={(event) => {
                    setSelectedIdentityRefDraftIndex(Number(event.target.value) || 0);
                    setGraphitiRefWritebackPlan(null);
                    setGraphitiRefWritebackStatus("");
                  }}
                >
                  {identityRefDrafts.map((row, index) => (
                    <option key={`${graphitiRefUuidFromDraft(row) || index}:identity-ref-draft`} value={index}>
                      {`${index + 1}. ${graphitiRefKindFromDraft(row)} / ${String(row.alias || row.ref_id || graphitiRefUuidFromDraft(row)).slice(0, 56)}`}
                    </option>
                  ))}
                </select>
              </label>
              <div className="graphiti-ref-input-grid">
                <label>
                  <span>Ref ID</span>
                  <input value={graphitiRefId} onChange={(event) => setGraphitiRefId(event.target.value)} />
                </label>
                <label>
                  <span>Ref kind</span>
                  <select value={graphitiRefKind} onChange={(event) => setGraphitiRefKind(event.target.value)}>
                    <option value="graphiti_fact">graphiti_fact</option>
                    <option value="graphiti_entity">graphiti_entity</option>
                    <option value="graphiti_episode">graphiti_episode</option>
                    <option value="obsidian_doc">obsidian_doc</option>
                    <option value="url">url</option>
                    <option value="file_path">file_path</option>
                    <option value="ecs_path">ecs_path</option>
                    <option value="photo">photo</option>
                  </select>
                </label>
              </div>
              <label>
                <span>Locator / URL</span>
                <input value={graphitiRefLocator} onChange={(event) => setGraphitiRefLocator(event.target.value)} placeholder="path, ECS path, photo path, or URL" />
              </label>
              <label className="identity-ref-remote-toggle">
                <input type="checkbox" checked={graphitiRefWriteAudit} onChange={(event) => setGraphitiRefWriteAudit(event.target.checked)} />
                <span>{t.writeAuditEpisode}</span>
              </label>
              <div className="button-row compact">
                <button className="button small" onClick={() => void previewGraphitiRefWriteback()}><ShieldCheck size={14} /> {t.draftGraphitiRef}</button>
                <button className="button small ghost" onClick={() => void applyGraphitiRefWriteback()} disabled={graphitiRefApplying}><UploadCloud size={14} /> {operatorMode ? t.applyGraphitiRef : t.dryApply}</button>
              </div>
              {graphitiRefWritebackStatus ? <small className="muted">{graphitiRefWritebackStatus}</small> : null}
              {Object.keys(graphitiRecordRef).length ? (
                <div className="preview-row mapping-row">
                  <span>{String(graphitiRecordRef.graphiti_kind || "graphiti_record")}</span>
                  <small>{`${String(graphitiRecordRef.partition || partition)} / ${String(graphitiRecordRef.graphiti_uuid || "-")}`}</small>
                  <small>{String(graphitiRefPlanData.write_path || graphitiRefPlanData.policy || "GraphitiRecordRef + ExternalRefRecord")}</small>
                </div>
              ) : null}
              {graphitiExternalRefs.slice(0, 3).map((row, index) => (
                <div className="preview-row import-plan-row" key={`${String(row.ref_id || index)}:graphiti-ref-writeback`}>
                  <span>{String(row.ref_id || "external_ref")}</span>
                  <small>{`${String(row.kind || row.ref_kind || "-")} / ${String(row.health || "unknown")}`}</small>
                  <small>{String(row.primary_locator || row.url || row.locator || "")}</small>
                </div>
              ))}
              {Object.keys(graphitiAuditDraft).length ? (
                <div className="preview-row mapping-row">
                  <span>{String(graphitiAuditDraft.name || "audit Episode")}</span>
                  <small>{String(graphitiAuditDraft.write_status || "draft_only")}</small>
                  <small>{String(graphitiAuditDraft.source_description || "parrot-web-console-ref-writeback-audit")}</small>
                </div>
              ) : null}
            </div>
          ) : null}
          {edgeDrafts.length ? (
            <div className="edge-resolver-panel">
              <div className="edge-resolver-head">
                <strong>{t.resolverPreview}</strong>
                <small>{`${readyGraphitiEdgeCount(resolvedGraphitiEdges)}/${resolvedGraphitiEdges.length || edgeDrafts.length} ready`}</small>
              </div>
              <label>
                <span>Graphiti Edge</span>
                <select
                  value={selectedGraphitiEdgeIndex}
                  onChange={(event) => setSelectedGraphitiEdgeIndex(Number(event.target.value) || 0)}
                >
                  {edgeDrafts.map((row, index) => (
                    <option key={`${String(row.hit_graphiti_uuid || index)}:edge-option`} value={index}>
                      {`${index + 1}. ${String(row.label || row.hit_graphiti_uuid || row.graphiti_uuid || "graphiti_fact")}`}
                    </option>
                  ))}
                </select>
              </label>
              <div className="button-row compact">
                <button className="button small" onClick={() => void resolveGraphitiEdgeDrafts()}><Link2 size={14} /> {t.resolveGraphitiEdges}</button>
                <button className="button small" onClick={() => void previewGraphitiEdgeApply()}><ShieldCheck size={14} /> {t.previewGraphitiEdge}</button>
                <button className="button small ghost" onClick={() => void materializeGraphitiEdge()} disabled={graphitiEdgeApplying}><UploadCloud size={14} /> {operatorMode ? t.materializeGraphitiEdge : t.dryApply}</button>
              </div>
              {graphitiEdgeApplyStatus ? <small className="muted">{graphitiEdgeApplyStatus}</small> : null}
              {resolvedGraphitiEdges.slice(0, 4).map((row, index) => {
                const source = recordFromUnknown(row.source);
                const target = recordFromUnknown(row.target);
                const ready = row.can_materialize_l2b_edge === true;
                const blockedReasons = Array.isArray(row.blocked_reasons)
                  ? row.blocked_reasons.map(String).join(", ")
                  : "";
                return (
                  <div className={ready ? "preview-row import-plan-row" : "preview-row import-error-row"} key={`${String(row.hit_graphiti_uuid || index)}:resolved-edge`}>
                    <span>{String(row.label || row.hit_graphiti_uuid || "Graphiti fact edge")}</span>
                    <small>{`${String(source.status || "-")} ${String(source.l2b_uuid || source.value || "")} -> ${String(target.status || "-")} ${String(target.l2b_uuid || target.value || "")}`}</small>
                    <small>{ready ? "ready for L2-B GRAPHITI_FACT" : blockedReasons || "blocked"}</small>
                  </div>
                );
              })}
            </div>
          ) : null}
          {importPolicy ? (
            <div className="preview-row import-plan-row">
              <span>{`Destination: ${String(importPolicy.destination || destination)}`}</span>
              <small>{String(importPolicy.write_path || "Graphiti -> L1.5 -> L2-B policy")}</small>
              <small>{String(importPolicy.reason || "")}</small>
            </div>
          ) : null}
          {flowSteps.length ? (
            <div className="flow-step-list">
              {flowSteps.slice(0, 5).map((step, index) => <small key={`${step}:${index}`}>{`${index + 1}. ${step}`}</small>)}
            </div>
          ) : null}
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

function GraphitiBundlePanel({ bundle }: { bundle: Record<string, unknown> }) {
  const selection = recordFromUnknown(bundle.selection);
  const sectionCounts = recordFromUnknown(selection.section_counts);
  const search = recordFromUnknown(bundle.search);
  const sections = recordFromUnknown(bundle.sections);
  const overlay = recordFromUnknown(bundle.import_overlay);
  const transformPreview = recordFromUnknown(overlay.transform_preview || bundle.l2b_transform_preview);
  const rustworkxPreview = recordFromUnknown(transformPreview.rustworkx_preview);
  const projectionPolicy = recordFromUnknown(bundle.l2b_projection_policy);
  const facts = recordArrayFrom(sections, "facts");
  const entities = recordArrayFrom(sections, "entities");
  const episodes = recordArrayFrom(sections, "episodes");
  const communities = recordArrayFrom(sections, "communities");
  const l2bNodes = recordArrayFrom(transformPreview, "l2b_nodes");
  const l2bEdges = recordArrayFrom(transformPreview, "l2b_edges");
  const searchPlan = Array.isArray(search.search_plan) ? search.search_plan : [];
  const lookup = recordFromUnknown(search.lookup);
  const selectedCount = String(selection.selected_count ?? 0);
  const schema = String(bundle.schema_version || "1");
  const recipe = String(search.search_recipe || "public/default");
  const strategy = String(search.strategy || "hybrid");
  const destination = String(overlay.destination || "");

  return (
    <div className="edge-resolver-panel graphiti-bundle-panel">
      <div className="edge-resolver-head">
        <strong>Graphiti bundle</strong>
        <small>{`schema v${schema} / ${selectedCount} selected`}</small>
      </div>
      <div className="graphiti-bundle-stats">
        <span>
          <strong>{String(sectionCounts.facts ?? facts.length)}</strong>
          <small>facts</small>
        </span>
        <span>
          <strong>{String(sectionCounts.entities ?? entities.length)}</strong>
          <small>entities</small>
        </span>
        <span>
          <strong>{String(sectionCounts.episodes ?? episodes.length)}</strong>
          <small>episodes</small>
        </span>
        <span>
          <strong>{String(sectionCounts.communities ?? communities.length)}</strong>
          <small>communities</small>
        </span>
      </div>
      <div className="graphiti-bundle-meta">
        <div className="preview-row mapping-row">
          <span>{`${strategy} / ${recipe}`}</span>
          <small>{`search_plan ${searchPlan.length} / lookup ${String(lookup.found_count ?? "-")}/${String(lookup.requested_count ?? "-")}`}</small>
          <small>{String(search.node_labels || search.edge_types || "Graphiti SearchConfig and local expansion are preserved")}</small>
        </div>
        <div className={destination ? "preview-row import-plan-row" : "preview-row mapping-row"}>
          <span>{destination ? `Import overlay: ${destination}` : "Projection policy"}</span>
          <small>{String(projectionPolicy.edge_materialization_policy || "requires_resolved_l2b_node_uuid")}</small>
          <small>{String(projectionPolicy.l2b_role || "L2-B preserves Graphiti raw data and adds overlay/buff policy")}</small>
        </div>
        {Object.keys(transformPreview).length ? (
          <div className="preview-row import-plan-row">
            <span>{String(transformPreview.projection_kind || "L2-B transform preview")}</span>
            <small>{`L2-B preview ${l2bNodes.length} node(s) / ${l2bEdges.length} edge(s)`}</small>
            <small>{`RustWorkX ${String(rustworkxPreview.node_count ?? "-")}/${String(rustworkxPreview.edge_count ?? "-")} / ${String(rustworkxPreview.rwx_idx_policy || "ephemeral preview only")}`}</small>
          </div>
        ) : null}
      </div>
      <GraphitiBundleSection title="facts" rows={facts} />
      <GraphitiBundleSection title="entities" rows={entities} />
      <GraphitiBundleSection title="episodes" rows={episodes} />
      {communities.length ? <GraphitiBundleSection title="communities" rows={communities} /> : null}
      <GraphitiBundleSection title="l2b preview nodes" rows={l2bNodes} />
      <GraphitiBundleSection title="l2b preview edges" rows={l2bEdges} />
    </div>
  );
}

function GraphitiBundleSection({
  title,
  rows
}: {
  title: string;
  rows: Array<Record<string, unknown>>;
}) {
  if (!rows.length) return null;
  return (
    <div className="graphiti-bundle-section">
      <div className="graphiti-bundle-section-head">
        <span>{title}</span>
        <small>{`${rows.length} row(s)`}</small>
      </div>
      {rows.slice(0, 4).map((row, index) => (
        <div className="preview-row" key={`${title}:${String(row.uuid || index)}`}>
          <span>{graphitiBundleRowLabel(row, index)}</span>
          <small>{graphitiBundleRowMeta(row)}</small>
          <small>{graphitiBundleRowUuid(row)}</small>
        </div>
      ))}
    </div>
  );
}

function CalendarSourceCard({
  pushReceipt,
  t,
  onSourceApplied,
  operatorMode
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onSourceApplied: () => Promise<void>;
  operatorMode: boolean;
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
  const [importPolicy, setImportPolicy] = useState<Record<string, unknown> | null>(null);
  const [policySkippedReason, setPolicySkippedReason] = useState("");
  const [flowSteps, setFlowSteps] = useState<string[]>([]);
  const [operatorFetching, setOperatorFetching] = useState(false);
  const [operatorImporting, setOperatorImporting] = useState(false);
  const operatorFetchingRef = useRef(false);
  const operatorImportingRef = useRef(false);
  const calendarPayload = () => ({ raw: rawPayload.trim() || defaultCalendarRaw });
  const clearCalendarPreviewState = () => {
    setNormalizedEvents([]);
    setObservations([]);
    setMappingRows([]);
    setImportPolicy(null);
    setPolicySkippedReason("");
    setFlowSteps([]);
  };
  const updateCalendarPayload = (value: string) => {
    setRawPayload(value);
    clearCalendarPreviewState();
  };
  const showCalendarReceipt = (receipt: Receipt) => {
    const data = receipt.data ?? {};
    const nextErrors = receiptArray(receipt, "errors");
    const firstError = nextErrors[0];
    const inlineReason = String(
      data.policy_skipped_reason
      || data.error
      || firstError?.error
      || firstError?.reason
      || (receipt.success === false ? "no_calendar_events" : "")
    );
    setNormalizedEvents(receiptArray(receipt, "normalized_events"));
    setObservations(receiptArray(receipt, "observations"));
    setMappingRows(receiptArray(receipt, "mapping_rows"));
    const nextPolicy = recordFromUnknown(data.import_policy);
    setImportPolicy(Object.keys(nextPolicy).length ? nextPolicy : null);
    setPolicySkippedReason(inlineReason);
    setFlowSteps(Array.isArray(data.flow_steps) ? data.flow_steps.map(String) : []);
    pushReceipt(receipt);
  };
  const showCalendarFetchReceipt = (receipt: Receipt) => {
    showCalendarReceipt(receipt);
    const fetchedEvents = receiptArray(receipt, "events");
    if (fetchedEvents.length) {
      setRawPayload(JSON.stringify(fetchedEvents, null, 2));
    }
  };
  const fetchPreview = async () => {
    try {
      pushReceipt(await api.googleCalendarFetch({ dry_run: true, operator_mode: false }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.fetch", exc));
    }
  };
  const fetchExecute = async () => {
    if (operatorFetchingRef.current) {
      pushReceipt(localReceipt("google.calendar.fetch.execute", false, { error: "operator_fetch_in_flight" }));
      return;
    }
    operatorFetchingRef.current = true;
    setOperatorFetching(true);
    try {
      pushReceipt(await api.googleCalendarFetch({ dry_run: !operatorMode, operator_mode: operatorMode }));
    } catch (exc) {
      pushReceipt(errorReceipt("google.calendar.fetch.execute", exc));
    } finally {
      operatorFetchingRef.current = false;
      setOperatorFetching(false);
    }
  };
  const fetchLocalApi = async () => {
    try {
      showCalendarFetchReceipt(await api.googleCalendarApiFetch({ limit: 20, timezone: "Asia/Shanghai" }));
    } catch (exc) {
      showCalendarReceipt(errorReceipt("google.calendar.api_fetch", exc));
    }
  };
  const fetchNanobotApi = async () => {
    try {
      showCalendarFetchReceipt(await api.googleCalendarNanobotFetch({ limit: 20, timezone: "Asia/Shanghai" }));
    } catch (exc) {
      showCalendarReceipt(errorReceipt("google.calendar.nanobot_fetch", exc));
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
      showCalendarReceipt(errorReceipt("calendar.preview", exc));
    }
  };
  const importDraft = async () => {
    try {
      showCalendarReceipt(await api.googleCalendarImportPlan({
        ...calendarPayload(),
        destination: "isolated_compartment",
        workspace_id: "memory_graph",
        subgraph_label: "Google Calendar source pack",
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showCalendarReceipt(errorReceipt("google.calendar.import_plan", exc));
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
      showCalendarReceipt(errorReceipt("google.calendar.import", exc));
    }
  };
  const importExecute = async () => {
    if (operatorImportingRef.current) {
      showCalendarReceipt(localReceipt("google.calendar.import.execute", false, { error: "operator_import_in_flight" }));
      return;
    }
    operatorImportingRef.current = true;
    setOperatorImporting(true);
    try {
      const receipt = await api.googleCalendarImport({
        ...calendarPayload(),
        dry_run: !operatorMode,
        operator_mode: operatorMode
      });
      showCalendarReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        await onSourceApplied();
      }
    } catch (exc) {
      showCalendarReceipt(errorReceipt("google.calendar.import.execute", exc));
    } finally {
      operatorImportingRef.current = false;
      setOperatorImporting(false);
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
        <textarea value={rawPayload} onChange={(event) => updateCalendarPayload(event.target.value)} rows={8} />
      </label>
      <div className="button-row compact">
        <button className="button" onClick={() => void fetchPreview()}><CalendarDays size={16} /> {t.calendarFetch}</button>
        <button className="button ghost" onClick={() => void fetchExecute()} disabled={operatorFetching}><Play size={16} /> {operatorMode ? t.calendarFetchExecute : t.dryApply}</button>
        <button className="button" onClick={() => void fetchLocalApi()}><RefreshCw size={16} /> {t.calendarApiFetch}</button>
        <button className="button" onClick={() => void fetchNanobotApi()}><Sparkles size={16} /> {t.calendarNanobotFetch}</button>
        <button className="button" onClick={() => void loadResults()}><RefreshCw size={16} /> {t.calendarResults}</button>
        <button className="button" onClick={() => void preview()}><Bell size={16} /> {t.calendarPreview}</button>
        <button className="button" onClick={() => void importDraft()}><UploadCloud size={16} /> {t.importDraft}</button>
        <button className="button ghost" onClick={() => void importPreview()}><ShieldCheck size={16} /> {t.dryApply}</button>
        <button className="button ghost" onClick={() => void importExecute()} disabled={operatorImporting}><UploadCloud size={16} /> {operatorMode ? t.calendarImportExecute : t.dryApply}</button>
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
      {mappingRows.length || policySkippedReason ? (
        <div className="note-preview-list import-plan">
          <strong>{t.calendarMapping}</strong>
          {policySkippedReason ? <small className="warn-text">{policySkippedReason}</small> : null}
          {importPolicy ? (
            <ImportLandingMap
              source="Google Calendar"
              sourceDetail="manual fetch/import"
              l15Label="GOOGLE_CALENDAR"
              l2bLabel="EVENT Node policy"
              importPolicy={importPolicy}
              observationCount={observations.length || mappingRows.length}
              applyRoute="/api/google/calendar/import"
            />
          ) : null}
          {importPolicy ? (
            <div className="preview-row import-plan-row">
              <span>{`Destination: ${String(importPolicy.destination || "isolated_compartment")}`}</span>
              <small>{String(importPolicy.write_path || "Calendar -> L1.5 -> L2-B policy")}</small>
              <small>{String(importPolicy.reason || "")}</small>
            </div>
          ) : null}
          {flowSteps.length ? (
            <div className="flow-step-list">
              {flowSteps.slice(0, 5).map((step, index) => <small key={`${step}:${index}`}>{`${index + 1}. ${step}`}</small>)}
            </div>
          ) : null}
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
  t,
  onSourceApplied,
  operatorMode
}: {
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
  onSourceApplied: () => Promise<void>;
  operatorMode: boolean;
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
  const [operatorImporting, setOperatorImporting] = useState(false);
  const operatorImportingRef = useRef(false);
  const visibleScanNotes = scanNotes.slice(0, 12);
  const refMissingUuid = profile === "ref" && !obsidianUuid.trim();
  const clearObsidianImportState = (reason = "") => {
    setImportItems([]);
    setImportErrors([]);
    setImportPlanMeta(reason ? {
      action: "l15.obsidian_vault.import_plan",
      success: false,
      selected_count: 0,
      policy_skipped_reason: reason,
      flow_steps: []
    } : null);
  };
  const updateVaultPath = (value: string) => {
    setVaultPath(value);
    setScanNotes([]);
    setInvalidNotes([]);
    setSelectedNotePaths([]);
    setVaultStatus(null);
    clearObsidianImportState();
  };
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
      apply_skipped_reason: data.apply_skipped_reason || "",
      policy_skipped_reason: data.policy_skipped_reason || data.error || "",
      import_policy: data.import_policy || null,
      flow_steps: data.flow_steps || []
    });
    pushReceipt(receipt);
  };
  const scanVault = async () => {
    try {
      const receipt = await api.obsidianVaultScan(vaultPath);
      const notes = receiptArray(receipt, "notes");
      setScanNotes(notes);
      setSelectedNotePaths([]);
      clearObsidianImportState();
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
    clearObsidianImportState();
  };
  const selectVisibleNotes = () => {
    setSelectedNotePaths(visibleScanNotes.map((note) => String(note.path || "")).filter(Boolean));
    clearObsidianImportState();
  };
  const clearSelectedNotes = () => {
    setSelectedNotePaths([]);
    clearObsidianImportState("no_notes_selected");
  };
  const draftImport = async () => {
    if (!selectedNotePaths.length) {
      showImportReceipt(localReceipt("l15.obsidian_vault.import_draft", false, { error: "no_notes_selected" }));
      return;
    }
    try {
      showImportReceipt(await api.obsidianVaultImportPlan({
        vault_path: vaultPath,
        paths: selectedNotePaths,
        destination: "isolated_compartment",
        workspace_id: "memory_graph",
        subgraph_label: "Obsidian source pack",
        dry_run: true,
        operator_mode: false
      }));
    } catch (exc) {
      showImportReceipt(errorReceipt("l15.obsidian_vault.import_plan", exc, { vault_path: vaultPath, paths: selectedNotePaths }));
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
  const applyImportExecute = async () => {
    if (operatorImportingRef.current) {
      showImportReceipt(localReceipt("l15.obsidian_vault.import.execute", false, { error: "operator_import_in_flight", vault_path: vaultPath, paths: selectedNotePaths }));
      return;
    }
    if (!selectedNotePaths.length) {
      showImportReceipt(localReceipt("l15.obsidian_vault.import", false, { error: "no_notes_selected" }));
      return;
    }
    operatorImportingRef.current = true;
    setOperatorImporting(true);
    try {
      const receipt = await api.obsidianVaultImport({
        vault_path: vaultPath,
        paths: selectedNotePaths,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      });
      showImportReceipt(receipt);
      if (receipt.success !== false && operatorMode) {
        await onSourceApplied();
      }
    } catch (exc) {
      showImportReceipt(errorReceipt("l15.obsidian_vault.import.execute", exc, { vault_path: vaultPath, paths: selectedNotePaths }));
    } finally {
      operatorImportingRef.current = false;
      setOperatorImporting(false);
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
      const payload = {
        profile,
        label: label.trim(),
        obsidian_uuid: obsidianUuid.trim(),
        description: `Drafted from React Memory Graph Workspace (${profile}).`,
        dry_run: !operatorMode,
        operator_mode: operatorMode
      };
      const receipt = operatorMode
        ? await api.l15ObsidianNodeApply(payload)
        : await api.l15ObsidianNodeDraft(payload);
      pushReceipt(receipt);
      if (receipt.success !== false && operatorMode) await onSourceApplied();
    } catch (exc) {
      pushReceipt(errorReceipt("l15.obsidian_node.draft", exc, { profile, label }));
    }
  };
  const obsidianImportPolicy = recordFromUnknown(importPlanMeta?.import_policy);
  const obsidianFlowStepsRaw = importPlanMeta?.flow_steps;
  const obsidianFlowSteps = Array.isArray(obsidianFlowStepsRaw)
    ? obsidianFlowStepsRaw.map(String)
    : [];
  return (
    <article className="source-card obsidian-card">
      <div className="source-card-head">
        <strong><FileText size={16} /> {t.obsidianSettings}</strong>
        <small className={refMissingUuid ? "warn-text" : ""}>{profile === "ref" ? t.refRequiresUuid : t.uuidFree}</small>
      </div>
      <label>
        <span>{t.obsidianVaultPath}</span>
        <input value={vaultPath} onChange={(event) => updateVaultPath(event.target.value)} placeholder="D:/GOSLOParrot/GOSLObsidian" />
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
            <button className="button small ghost" onClick={clearSelectedNotes}>{t.clearSelection}</button>
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
            <button className="button ghost" onClick={() => void applyImportExecute()} disabled={operatorImporting}><UploadCloud size={16} /> {operatorMode ? t.calendarImportExecute : t.dryApply}</button>
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
          {obsidianImportPolicy.destination ? (
            <ImportLandingMap
              source="Obsidian"
              sourceDetail={vaultPath}
              l15Label="USER_TAG_OBSIDIAN"
              l2bLabel="setting/source pack policy"
              importPolicy={obsidianImportPolicy}
              observationCount={importItems.length}
              applyRoute="/api/l15/obsidian-vault/import"
            />
          ) : null}
          {obsidianImportPolicy.destination ? (
            <div className="preview-row import-plan-row">
              <span>{`Destination: ${String(obsidianImportPolicy.destination || "isolated_compartment")}`}</span>
              <small>{String(obsidianImportPolicy.write_path || "Obsidian -> L1.5 -> L2-B policy")}</small>
              <small>{String(obsidianImportPolicy.reason || "")}</small>
            </div>
          ) : null}
          {obsidianFlowSteps.length ? (
            <div className="flow-step-list">
              {obsidianFlowSteps.slice(0, 5).map((step, index) => <small key={`${step}:${index}`}>{`${index + 1}. ${step}`}</small>)}
            </div>
          ) : null}
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
          {String(importPlanMeta?.policy_skipped_reason || "") ? (
            <small className="warn-text">{String(importPlanMeta?.policy_skipped_reason)}</small>
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
  operatorMode,
  pushReceipt,
  t
}: {
  bucket: Record<string, unknown>;
  maxNodeCount: number;
  operatorMode: boolean;
  pushReceipt: (receipt: Receipt | null) => void;
  t: ConsoleCopy;
}) {
  const kind = String(bucket.kind || "");
  const nodeCount = Number(bucket.node_count ?? 0);
  const frozen = Boolean(bucket.frozen);
  const ratio = Math.max(0.04, Math.min(1, nodeCount / Math.max(1, maxNodeCount)));
  const lastActivity = Math.max(Number(bucket.last_modified_at ?? 0), Number(bucket.created_at ?? 0));
  const op = async (operation: string) => {
    if (operatorMode && operation === "clear" && !window.confirm(`Clear L1.5 bucket ${kind}?`)) return;
    try {
      const payload = { kind, op: operation, dry_run: !operatorMode, operator_mode: operatorMode };
      pushReceipt(operatorMode
        ? await api.l15BucketApply(payload)
        : await api.l15BucketDraft(payload));
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

function readyGraphitiEdgeCount(edges: Array<Record<string, unknown>>): number {
  return edges.filter((row) => row.can_materialize_l2b_edge === true).length;
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

function stringsFromUnknown(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return raw.map((item) => String(item || "").trim()).filter(Boolean);
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

function graphitiBundleRowLabel(row: Record<string, unknown>, index: number): string {
  const raw = recordFromUnknown(row.raw);
  const sourceEnvelope = recordFromUnknown(row.source_envelope);
  const text = String(
    raw.name
    || raw.label
    || raw.title
    || raw.fact
    || sourceEnvelope.text
    || sourceEnvelope.label
    || row.label
    || row.uuid
    || ""
  ).replace(/\s+/g, " ").trim();
  return text ? text.slice(0, 96) : `Graphiti row ${index + 1}`;
}

function graphitiBundleRowMeta(row: Record<string, unknown>): string {
  const raw = recordFromUnknown(row.raw);
  const sourceEnvelope = recordFromUnknown(row.source_envelope);
  const sourceNode = recordFromUnknown(raw.source_node || sourceEnvelope.source_node);
  const targetNode = recordFromUnknown(raw.target_node || sourceEnvelope.target_node);
  const sourceName = String(sourceNode.name || row.source_node_uuid || sourceEnvelope.source_node_uuid || "").trim();
  const targetName = String(targetNode.name || row.target_node_uuid || sourceEnvelope.target_node_uuid || "").trim();
  const previewSource = String(row.source || "").trim();
  const previewTarget = String(row.target || "").trim();
  const kind = String(row.kind || row.node_kind || raw.kind || sourceEnvelope.kind || "graphiti").trim();
  const score = row.score ?? sourceEnvelope.score ?? raw.score;
  const parts = [kind];
  if (sourceName || targetName) parts.push(`${sourceName || "-"} -> ${targetName || "-"}`);
  if (previewSource || previewTarget) parts.push(`${previewSource || "-"} -> ${previewTarget || "-"}`);
  if (score !== undefined && score !== null && score !== "") parts.push(`score ${String(score)}`);
  return parts.join(" / ");
}

function graphitiBundleRowUuid(row: Record<string, unknown>): string {
  const raw = recordFromUnknown(row.raw);
  const sourceEnvelope = recordFromUnknown(row.source_envelope);
  return String(
    row.uuid
    || row.graphiti_uuid
    || raw.uuid
    || sourceEnvelope.uuid
    || sourceEnvelope.graphiti_edge_uuid
    || sourceEnvelope.parent_fact_uuid
    || ""
  );
}

function graphitiHitKey(hit: Record<string, unknown>, index: number): string {
  return String(
    hit.uuid
    || hit.graphiti_uuid
    || hit.id
    || `${hit.source_node_uuid || ""}:${hit.target_node_uuid || ""}:${index}`
  );
}

function graphitiSelectionIds(hit: Record<string, unknown>, index: number): string[] {
  return uniqueStrings([
    graphitiHitKey(hit, index),
    graphitiPreviewNodeId(hit, index),
    String(hit.uuid || ""),
    String(hit.graphiti_uuid || ""),
    String(hit.id || ""),
    hit.source_node_uuid ? `graphiti:${String(hit.source_node_uuid)}` : "",
    hit.target_node_uuid ? `graphiti:${String(hit.target_node_uuid)}` : ""
  ]);
}

function normalizeGraphitiStatus(raw: Record<string, unknown>): GraphitiStatusSummary {
  const data = recordFromUnknown(raw.data);
  const graphitiLlm = recordFromUnknown(data.graphiti_llm);
  const partitions = Array.isArray(data.partitions) ? data.partitions.map(String) : [];
  return {
    installed: Boolean(data.installed),
    provider: String(graphitiLlm.provider || graphitiLlm.requested_provider || "unknown"),
    model: String(graphitiLlm.model || ""),
    secretConfigured: Boolean(graphitiLlm.secret_configured),
    embeddingProvider: String(graphitiLlm.embedding_provider || "unknown"),
    embeddingConfigured: Boolean(graphitiLlm.embedding_secret_configured),
    partitions,
    message: String(raw.message || "")
  };
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
  const selectedIds = new Set(hits.flatMap((hit, index) => graphitiSelectionIds(hit, index)));
  const selectedEdges = subgraphEdges.filter((edge) => {
    const hitId = String(edge.hit_id || "");
    return selectedIds.has(hitId) || selectedIds.has(String(edge.source || "")) || selectedIds.has(String(edge.target || ""));
  });
  const selectedNodeIds = new Set(selectedIds);
  selectedEdges.forEach((edge) => {
    selectedNodeIds.add(String(edge.source || ""));
    selectedNodeIds.add(String(edge.target || ""));
  });
  const nodes = subgraphNodes.filter((node, index) => (
    graphitiSelectionIds(node, index).some((id) => selectedNodeIds.has(id))
  ));
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

function graphitiRefKindFromDraft(draft: Record<string, unknown>): string {
  if (draft.graphiti_episode_uuid) return "episode";
  if (draft.graphiti_entity_uuid) return "entity";
  if (draft.graphiti_edge_uuid || draft.hit_graphiti_uuid) return "edge";
  return String(draft.graphiti_kind || "edge");
}

function graphitiRefUuidFromDraft(draft: Record<string, unknown>): string {
  return String(
    draft.graphiti_uuid
    || draft.graphiti_edge_uuid
    || draft.graphiti_entity_uuid
    || draft.graphiti_episode_uuid
    || draft.hit_graphiti_uuid
    || ""
  ).trim();
}

function graphitiRefLocatorFromDraft(draft: Record<string, unknown>): string {
  return String(draft.locator || draft.url || draft.path || "").trim();
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

function mergeGraphRowsByStableId(
  previousRows: Array<Record<string, unknown>>,
  incomingRows: Array<Record<string, unknown>>
): Array<Record<string, unknown>> {
  const incomingById = new Map<string, Record<string, unknown>>();
  incomingRows.forEach((row) => {
    const id = graphRowStableId(row);
    if (id) incomingById.set(id, row);
  });

  const seen = new Set<string>();
  const merged: Array<Record<string, unknown>> = [];
  previousRows.forEach((row) => {
    const id = graphRowStableId(row);
    if (!id) return;
    const incoming = incomingById.get(id);
    if (!incoming) return;
    merged.push(incoming);
    seen.add(id);
  });

  incomingRows.forEach((row) => {
    const id = graphRowStableId(row);
    if (id && seen.has(id)) return;
    merged.push(row);
    if (id) seen.add(id);
  });
  return merged;
}

function l2bGraphSignature(
  nodes: Array<Record<string, unknown>>,
  edges: Array<Record<string, unknown>>
): string {
  const nodePart = nodes.map((row, index) => graphRowSignature(row, index, "node")).sort().join("|");
  const edgePart = edges.map((row, index) => graphRowSignature(row, index, "edge")).sort().join("|");
  return `${nodes.length}:${nodePart}::${edges.length}:${edgePart}`;
}

function graphRowStableId(row: Record<string, unknown>): string {
  return String(
    row.uuid
    || row.id
    || row.graphiti_uuid
    || row.canonical_uuid
    || ""
  ).trim();
}

function graphRowSignature(row: Record<string, unknown>, index: number, fallbackKind: string): string {
  const source = String(row.source ?? row.from_uuid ?? "");
  const target = String(row.target ?? row.to_uuid ?? "");
  const stableId = graphRowStableId(row) || `${fallbackKind}:${source}:${target}:${index}`;
  return [
    stableId,
    String(row.label || row.name || ""),
    String(row.kind || row.type || fallbackKind),
    String(row.confirmation || ""),
    String(row.salience || ""),
    source,
    target,
    String(row.strength || ""),
    String(row.edge_source || row.source_tool || "")
  ].join("\u001f");
}

function memoryStateClass(row: Record<string, unknown>): string {
  const confirmation = String(row.confirmation || "expected").toLowerCase();
  const salience = String(row.salience || "").toLowerCase();
  if (salience === "alert") return "state-alert";
  if (confirmation === "confirmed") return "state-confirmed";
  if (confirmation === "uncertain" || confirmation === "ghost") return "state-uncertain";
  return "state-tentative";
}

function isFiniteFlowPosition(position: { x: number; y: number } | null | undefined): position is { x: number; y: number } {
  return (
    position != null
    && Number.isFinite(position.x)
    && Number.isFinite(position.y)
    && Math.abs(position.x) <= MAX_SAVED_FLOW_POSITION_ABS
    && Math.abs(position.y) <= MAX_SAVED_FLOW_POSITION_ABS
  );
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

function localReceipt(
  action: string,
  success: boolean,
  data: Record<string, unknown>,
  options: { dryRun?: boolean; operatorMode?: boolean } = {}
): Receipt {
  return {
    receipt_id: `local_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    action,
    success,
    dry_run: options.dryRun ?? true,
    operator_mode: options.operatorMode ?? false,
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
  if ("would_materialize" in data || ("direct_l2b_write" in data && ("nodes_upserted" in data || "edges_added" in data))) {
    const mode = data.direct_l2b_write ? "wrote" : "preview";
    const nodes = String(data.nodes_upserted ?? data.node_count ?? 0);
    const edges = String(data.edges_added ?? data.edge_count ?? 0);
    const skipped = Number(data.edges_skipped_duplicate ?? 0);
    return `Graphiti -> L2-B ${mode}: ${nodes} node(s), ${edges} edge(s)${skipped ? `, ${skipped} duplicate edge(s)` : ""}`;
  }
  const resultContract = recordFromUnknown(data.result_contract);
  if (resultContract.schema) {
    const nodeCount = String(resultContract.node_count ?? data.workflow_node_count ?? 0);
    const counts = recordFromUnknown(resultContract.destination_counts);
    const destinations = Object.entries(counts)
      .map(([key, value]) => `${key}:${String(value)}`)
      .join(", ");
    return `Result routes ${nodeCount} node(s)${destinations ? ` / ${destinations}` : ""}`;
  }
  if ("route_results" in data || "staged_refs" in data) {
    const staged = Array.isArray(data.staged_refs) ? data.staged_refs.length : 0;
    return `Result intake ${String(data.route_count ?? 0)} route(s) / ${staged} staged`;
  }
  const gate = recordFromUnknown(data.gate);
  if (gate.gate_id) {
    return `Action gate ${String(gate.state || "-")} / ${String(gate.action_kind || "-")}`;
  }
  const skipped = data.publish_skipped_reason || data.apply_skipped_reason || data.dispatch_skipped_reason;
  if (skipped) return String(skipped);
  if ("l2b_nodes" in data || "l15_buckets" in data) {
    return `L2-B ${String(data.l2b_nodes ?? 0)}/${String(data.l2b_edges ?? 0)} · L1.5 ${String(data.l15_buckets ?? 0)} buckets / ${String(data.l15_nodes ?? 0)} Nodes`;
  }
  const event = data.event;
  if (event && typeof event === "object") {
    const row = event as Record<string, unknown>;
    return String(row.kind || row.type || "");
  }
  return "";
}
