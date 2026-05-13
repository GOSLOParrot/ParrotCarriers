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

export type ConsoleConfig = {
  orchestrator_auth_mode?: string;
  refresh_interval_s?: number;
};
