# GOSLO Intent Tooling Policy - Gemini Live Search, Vision, Graphiti

Date: 2026-05-18

Scope: GOSLO T1 Intent/Thinking tools, Gemini Live provider tools, visual
recognition, Web lookup, Graphiti noble_etiquette memory search, and T3 fallback
routes.

## Stable User Requirements

- GOSLO normally decides, confirms with the user, and monitors. Slow or complex
  work goes to Tasks/Nanobot.
- T1 tools may run inside a felt thinking moment only when they are quick,
  read-only, and useful before the next spoken response.
- If a T1 lookup is slow or unavailable, GOSLO should quickly dispatch a T3 task
  and tell the user, instead of silently blocking the conversation.
- Web/App test tools exist to prove the same capabilities that GOSLO Intent,
  Plans, Collaboration Flow, and Nanobot can use.
- L2-B is a working-memory / Graphiti-buffer adaptation layer. T1 tools must not
  pretend L2-B is the strict SSOT, and must not flatten away Graphiti raw
  semantics.
- Need a dedicated natural-language Graphiti query path for the imported
  `noble_etiquette` / ladies etiquette corpus.

## Official Capability Notes

Gemini Live:

- Google Live API tool docs say Live API supports Google Search and function
  calling. Search is a supported provider-side tool; Google Maps, code
  execution, and URL context are not supported in the Live table currently.
- Function calling is sequential/blocking by default. Gemini 2.5 Live supports
  async function calling with non-blocking behavior; Gemini 3.1 Live currently
  does not support async function calling.
- LiveKit's Gemini Live plugin supports text, audio, and video input. In this
  repo, `src/parrot/brain/agent.py` already starts the room with
  `RoomOptions(video_input=True)`.
- LiveKit's Google plugin exposes `google.tools.GoogleSearch()` as a provider
  tool that can sit in the Agent tools list alongside function tools for Gemini
  Live. This repo registers it only for Line A to avoid Line B provider/function
  mixing limits.

Image recognition:

- Gemini models support multimodal image understanding, classification, visual
  question answering, object detection, and segmentation.
- This is not the same as a native reverse-image-search or Google Lens API.
  The practical GOSLO flow is:
  1. Native Gemini Live video sees the scene conversationally.
  2. `identify_object` uses Parrot's auditable visual evidence path plus L0/L1
     / Graphiti matching.
  3. `web_lookup_intent` or native Google Search checks current web facts from
     extracted visual hints such as logo text, cup color, packaging, and user
     context.

Reference URLs:

- https://ai.google.dev/gemini-api/docs/live-api/tools
- https://ai.google.dev/gemini-api/docs/google-search
- https://ai.google.dev/gemini-api/docs/image-understanding
- https://docs.livekit.io/agents/models/realtime/plugins/gemini/
- https://docs.livekit.io/agents/models/llm/gemini/

## Implemented Tools

### Native Provider Tool: Gemini Google Search

Registration:

- File: `src/parrot/brain/tools/__init__.py`
- Enabled by default only when `_active_pipeline_hint() == "line_a"`.
- Controlled by `PARROT_ENABLE_GEMINI_SEARCH_TOOL`; set to `0` to disable.
- Tool id exposed by LiveKit: `gemini_google_search`.

Use:

- Let Gemini Live ground short current-information answers server-side.
- Best for quick factual checks where no explicit Parrot audit payload is
  required.
- Not used on Line B by default because text-pipeline provider/function mixing
  has stricter limitations.

### Function Tool: `web_lookup_intent`

Registration:

- File: `src/parrot/brain/tools/web_lookup_intent.py`
- Included in `tools_for_active_model()` for GOSLO.

Use:

- T1 read-only grounded web lookup for Intent/Thinking.
- Uses Gemini `generate_content` with Google Search grounding and a short
  timeout.
- Good when GOSLO needs an explicit tool receipt, source cues, and a fallback
  route.
- If the T1 call times out or cannot run, it can dispatch a T3 `research` task
  through Scheduler/Nanobot with `source=web_lookup_intent_t1_fallback`.

Non-effects:

- No Calendar write.
- No Graphiti write.
- No L2-B mutation.
- No file or Ref mutation.

Visual brand flow:

- Use native video or `identify_object` to get visual hints.
- Call `web_lookup_intent(query=..., purpose="visual_brand_check",
  context_hint=...)`.
- Treat brand identification as evidence-weighted, not guaranteed, unless
  visual text and web sources agree.

### Function Tool: `identify_object`

Registration:

- File: `src/parrot/brain/tools/__init__.py`
- Existing implementation in `src/parrot/brain/tools/identify_object.py`.
- Default-on now. Set `PARROT_ENABLE_IDENTIFY_OBJECT_TOOL=0` to disable.

Use:

- T1 visual recognition bridge with auditable visual evidence.
- It is the Parrot-side complement to Gemini Live native video input because
  Gemini internal video frames are not persisted as evidence.
- Uses L0 text/working-memory matching and L1 Graphiti search. It can emit
  sighting events and preserve traceability for later L1.5/L2-B/Graphiti
  projection.

Boundary:

- It is not a deep web search tool. Pair it with `web_lookup_intent`,
  native Google Search, or T3 `research` when external facts are needed.

### Function Tool: `query_etiquette_memory`

Registration:

- File: `src/parrot/brain/tools/query_etiquette_memory.py`
- Included in `tools_for_active_model()`.

Use:

- Dedicated T1 natural-language Graphiti query against
  `PARTITIONS.NOBLE_ETIQUETTE`.
- Calls `search_graphiti_subgraph(... strategy="iterative_hybrid", depth=1..3,
  limit=1..10, enrich=True)`.
- Returns compact hits with UUID/source/target cues, subgraph counts, and raw
  envelope counts.

Non-effects:

- No Graphiti write.
- No L2-B materialization.
- No Episode write.
- No Ref/file mutation.

Why dedicated if `query_memory(partition="noble_etiquette")` already exists:

- GOSLO gets a clearly named, low-friction tool for the imported ladies
  etiquette test corpus.
- The docstring can encode the exact role boundary: read Graphiti, preserve raw
  semantics, let Web/L2-B import-plan handle later materialization.

## Current T1/T3 Routing Guidance

- Fast direct context: `calendar_context`, `query_etiquette_memory`,
  `query_memory`, `query_scene`, `web_lookup_intent`, native Google Search.
- Visual context: Gemini Live native video plus `identify_object`.
- Draft decisions: `calendar_change_request` and future Plan/HITL draft tools.
- Background work: `dispatch_task` with task types such as `research`,
  `calendar_fetch`, `calendar_create`, `calendar_patch`, `calendar_delete`,
  `memory_consolidation`.
- For visual brand questions, prefer:
  1. observe/extract visual hints;
  2. T1 `web_lookup_intent` or native Google Search;
  3. T3 `research` if uncertain or slow;
  4. only later project useful results into IntentWorkspace / L1.5 / L2-B /
     Graphiti if a Plan/HITL route asks for it.

## Verification Checklist

- `tools_for_active_model()` includes `gemini_google_search` on Line A.
- `tools_for_active_model()` skips `gemini_google_search` on Line B.
- `tools_for_active_model()` includes `web_lookup_intent`,
  `query_etiquette_memory`, and `identify_object`.
- `query_etiquette_memory` clamps depth/limit and searches
  `noble_etiquette` with `iterative_hybrid`.
- `web_lookup_intent` returns a grounded T1 receipt with sources when search is
  available, and dispatches a T3 `research` fallback on timeout/failure.
