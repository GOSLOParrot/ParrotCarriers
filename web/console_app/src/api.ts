import type {
  ConsoleConfig,
  L15Pool,
  LiveKitConfig,
  LiveKitToken,
  LiveState,
  MemoryLiveStateChanges,
  Receipt,
  RuntimeFlow,
  RuntimeFlowChanges,
  TriggerCatalog,
  VisionEvidenceStatus,
  VisionEvidenceTimeline
} from "./types";

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  config: () => json<ConsoleConfig>("/api/console/config"),
  liveState: () => json<LiveState>("/api/app/live-state?limit=120"),
  memoryLiveChanges: (since: number, limit = 120) =>
    json<MemoryLiveStateChanges>(
      "/api/memory/live-state/changes?since="
        + encodeURIComponent(String(since))
        + "&limit="
        + encodeURIComponent(String(limit))
    ),
  l15Pool: () => json<L15Pool>("/api/l15/pool"),
  runtimeFlow: () => json<RuntimeFlow>("/api/runtime/flow"),
  livekitConfig: () => json<LiveKitConfig>("/api/livekit/config"),
  livekitWebToken: (body: Record<string, unknown>) =>
    json<LiveKitToken>("/api/livekit/web-token", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  triggerCatalog: () => json<TriggerCatalog>("/api/dsg/triggers/catalog"),
  runtimeFlowChanges: (since: number) =>
    json<RuntimeFlowChanges>("/api/runtime/flow/changes?since=" + since),
  visionEvidenceStatus: () => json<VisionEvidenceStatus>("/api/vision/evidence/status"),
  visionEvidenceTimeline: (limit = 24, kind = "") => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (kind) params.set("kind", kind);
    return json<VisionEvidenceTimeline>("/api/vision/evidence/timeline?" + params.toString());
  },
  visionEvidenceRequest: (body: Record<string, unknown>) =>
    json<Receipt>("/api/vision/evidence/request", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  visionEvidenceStageHint: (body: Record<string, unknown>) =>
    json<Receipt>("/api/vision/evidence/stage-hint", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  visionEvidenceMemoryDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/vision/evidence/memory-draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  visionFrameCacheUpload: (body: Record<string, unknown>) =>
    json<Receipt>("/api/vision/evidence/frame-cache/upload", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  visionScreenShareSmoke: (windowMs = 15_000) =>
    json<Receipt>(
      "/api/vision/evidence/screen-share-smoke?window_ms="
        + encodeURIComponent(String(windowMs))
    ),
  visualAttentionTest: (body: Record<string, unknown>) =>
    json<Receipt>("/api/app/test/visual-attention", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  hitlPending: () => json<{ gates: Array<Record<string, unknown>> }>("/api/runtime/hitl/pending"),
  hitlDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/runtime/hitl/draft-decision", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  hitlApply: (body: Record<string, unknown>) =>
    json<Receipt>("/api/runtime/hitl/apply-decision", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l15BucketDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l15/bucket-op/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  refBindingDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/refs/binding/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  obsidianVaultScan: (vaultPath = "") => {
    const params = new URLSearchParams({ limit: "24" });
    if (vaultPath.trim()) params.set("vault_path", vaultPath.trim());
    return json<Receipt>("/api/l15/obsidian-vault/scan?" + params.toString());
  },
  obsidianVaultImportDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l15/obsidian-vault/import-draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  obsidianVaultImport: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l15/obsidian-vault/import", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l15ObsidianNodeDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l15/obsidian-node/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  graphitiStatus: () => json<Record<string, unknown>>("/api/graphiti/status"),
  graphitiSubgraphSearch: (body: Record<string, unknown>) =>
    json<Receipt>("/api/graphiti/subgraph/search", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  graphitiSubgraphExportDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/graphiti/subgraph/export-draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  graphitiSubgraphExport: (body: Record<string, unknown>) =>
    json<Receipt>("/api/graphiti/subgraph/export", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bNodeDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/node/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bNodeDelete: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/node/delete", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bEdgeDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/edge/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bEdgeUpdate: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/edge/update", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bEdgeDelete: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/edge/delete", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bGraphImportDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/graph-policy/import-draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bSubgraphDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/subgraphs/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bTransformDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/transforms/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  l2bGraphHealth: () => json<Record<string, unknown>>("/api/l2b/analysis/health"),
  triggerDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/dsg/triggers/draft-event", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  messageCheck: () =>
    json<Receipt>("/api/google/messages/check", {
      method: "POST",
      body: JSON.stringify({ dry_run: true, operator_mode: false })
    }),
  messagePush: () =>
    json<Receipt>("/api/google/messages/push-test", {
      method: "POST",
      body: JSON.stringify({ subject: "Runtime Flow message push test", dry_run: true })
    }),
  googleCalendarPreview: (body: Record<string, unknown>) =>
    json<Receipt>("/api/google/calendar/preview", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  googleCalendarFetch: (body: Record<string, unknown>) =>
    json<Receipt>("/api/google/calendar/fetch", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  googleCalendarResults: (limit = 12) =>
    json<Receipt>("/api/google/calendar/results?limit=" + encodeURIComponent(String(limit))),
  googleCalendarImportDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/google/calendar/import-draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
  googleCalendarImport: (body: Record<string, unknown>) =>
    json<Receipt>("/api/google/calendar/import", {
      method: "POST",
      body: JSON.stringify(body)
    })
};
