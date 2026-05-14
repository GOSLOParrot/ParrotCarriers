import type { ConsoleConfig, L15Pool, LiveState, Receipt, RuntimeFlow, TriggerCatalog } from "./types";

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
  l15Pool: () => json<L15Pool>("/api/l15/pool"),
  runtimeFlow: () => json<RuntimeFlow>("/api/runtime/flow"),
  triggerCatalog: () => json<TriggerCatalog>("/api/dsg/triggers/catalog"),
  runtimeFlowChanges: (since: number) =>
    json<{ changed: boolean; sequence: number; snapshot?: RuntimeFlow }>("/api/runtime/flow/changes?since=" + since),
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
  l2bEdgeDraft: (body: Record<string, unknown>) =>
    json<Receipt>("/api/l2b/edge/draft", {
      method: "POST",
      body: JSON.stringify(body)
    }),
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
    })
};
