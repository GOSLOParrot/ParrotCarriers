export type Language = "en" | "zh";

export type Receipt = {
  receipt_id?: string;
  receipt?: Record<string, unknown>;
  action?: string;
  success?: boolean;
  dry_run?: boolean;
  operator_mode?: boolean;
  data?: Record<string, unknown>;
  audit?: Record<string, unknown>;
};

export type LiveState = {
  sequence?: number;
  generated_at?: number;
  blackboard?: {
    declared_count?: number;
    present_count?: number;
    present_keys?: Array<Record<string, unknown>>;
  };
  intent_workspace?: {
    ref_count?: number;
    refs?: Array<Record<string, unknown>>;
    pressure?: Record<string, unknown>;
  };
  refs?: {
    refs?: Array<Record<string, unknown>>;
    resolved_l2b_targets?: Array<Record<string, unknown>>;
  };
  l2b?: {
    node_count?: number;
    edge_count?: number;
    nodes?: Array<Record<string, unknown>>;
    edges?: Array<Record<string, unknown>>;
  };
};

export type MemoryLiveStateChanges = {
  success?: boolean;
  action?: string;
  since?: number;
  sequence?: number;
  changed?: boolean;
  events?: Array<Record<string, unknown>>;
  snapshot?: LiveState | null;
  audit?: Record<string, unknown>;
};

export type L15Pool = {
  success?: boolean;
  health?: Record<string, unknown>;
  buckets?: Array<Record<string, unknown>>;
  timeline?: Array<Record<string, unknown>>;
};

export type RuntimeFlow = {
  success?: boolean;
  sequence?: number;
  generated_at?: number;
  lanes?: Array<{ id: string; label: string }>;
  nodes?: Array<Record<string, unknown>>;
  edges?: Array<Record<string, unknown>>;
  events?: Array<Record<string, unknown>>;
  pending_human_gates?: Array<Record<string, unknown>>;
};

export type TriggerCatalog = {
  success?: boolean;
  action?: string;
  triggers?: Array<Record<string, unknown>>;
  audit?: Record<string, unknown>;
};

export type VisionEvidenceStatus = {
  action?: string;
  sample_count?: number;
  by_kind?: Record<string, number>;
  latest_by_kind?: Record<string, Record<string, unknown>>;
  visual_asset_count?: number;
  frame_cache?: {
    frame_count?: number;
    latest_frame?: Record<string, unknown> | null;
    root?: string;
  };
  now_ms?: number;
  schema?: string;
};

export type VisionEvidenceTimeline = {
  action?: string;
  success?: boolean;
  items?: Array<Record<string, unknown>>;
  limit?: number;
  kind?: string;
  now_ms?: number;
};

export type ConsoleConfig = {
  orchestrator_auth_mode?: string;
  refresh_interval_s?: number;
};
