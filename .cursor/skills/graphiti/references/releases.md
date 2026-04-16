# Releases

Version history for this repository (191 releases).

## v0.28.1: v0.28.1 - remove diskcache
**Published:** 2026-02-19

## What's Changed
* fix: extract custom edge attributes on first episode ingestion by @prasmussen15 in https://github.com/getzep/graphiti/pull/1242
* fix: replace diskcache with sqlite-based cache to resolve CVE by @jackaldenryan in https://github.com/getzep/graphiti/pull/1238
* chore: bump version to 0.28.1 by @prasmussen15 in https://github.com/getzep/graphiti/pull/1243


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.28.0...v0.28.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.28.1)

---

## v0.28.0: v0.28.0 - Update GraphDriver Integrations
**Published:** 2026-02-17

## What's Changed
* feat: simplify extraction pipeline and add batch entity summarization by @prasmussen15 in https://github.com/getzep/graphiti/pull/1224
* chore(deps): update dependencies to fix dependabot alerts by @jackaldenryan in https://github.com/getzep/graphiti/pull/1225
* feat: driver operations architecture redesign by @prasmussen15 in https://github.com/getzep/graphiti/pull/1232
* Bump graphiti-core[falkordb] from 0.26.3 to 0.27.1 in /mcp_server by @dependabot[bot] in https://github.com/getzep/graphiti/pull/1231
* feat: implement Neptune and Kuzu driver operations by @prasmussen15 in https://github.com/getzep/graphiti/pull/1235
* chore: bump version to 0.28.0 and document graph driver architecture by @prasmussen15 in https://github.com/getzep/graphiti/pull/1236
* fix: remove PII from log messages by @prasmussen15 in https://github.com/getzep/graphiti/pull/1237


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.27.1...v0.28.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.28.0)

---

## v0.27.2pre1: v0.27.2pre1 - more ingestion efficiency gains
**Published:** 2026-02-12
**Pre-release**

## What's Changed
* feat: simplify extraction pipeline and add batch entity summarization by @prasmussen15 in https://github.com/getzep/graphiti/pull/1224


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.27.1...v0.27.2pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.27.2pre1)

---

## v0.27.1: v0.27.1 - fix duplicate info appearing in summaries
**Published:** 2026-02-12

## What's Changed
* fix(summary): exclude duplicate edges from node summary generation by @prasmussen15 in https://github.com/getzep/graphiti/pull/1223


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.27.0...v0.27.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.27.1)

---

## v0.27.0: v0.27.0 - efficiency gains
**Published:** 2026-02-11

## What's Changed
* Add extracted edge facts to entity summaries by @prasmussen15 in https://github.com/getzep/graphiti/pull/1182
* Fix dependabot security vulnerabilities by @danielchalef in https://github.com/getzep/graphiti/pull/1184
* Revert "Fix dependabot security vulnerabilities" by @danielchalef in https://github.com/getzep/graphiti/pull/1185
* Pin mcp_server to graphiti-core 0.26.3 by @danielchalef in https://github.com/getzep/graphiti/pull/1186
* Update manual code review workflow to use claude-opus-4-5-20251101 by @danielchalef in https://github.com/getzep/graphiti/pull/1189
* Refactor prompt system for efficiency and clarity by @prasmussen15 in https://github.com/getzep/graphiti/pull/1191
* fix(falkordb): sanitize pipe and slash chars in fulltext queries by @Milofax in https://github.com/getzep/graphiti/pull/1183
* feat(nodes): generate entity summary from episode when no edges exist by @prasmussen15 in https://github.com/getzep/graphiti/pull/1196
* chore: bump version to 0.27.0pre2 by @prasmussen15 in https://github.com/getzep/graphiti/pull/1200
* fix(falkordb): escape group_ids in RediSearch fulltext queries by @Milofax in https://github.com/getzep/graphiti/pull/1175
* feat(gemini): add support for Gemini 3 preview models by @geojaz in https://github.com/getzep/graphiti/pull/1202
* Fix Azure OpenAI integration for v1 API compatibility by @andreibogdan in https://github.com/getzep/graphiti/pull/1192
* fix(edges): preserve all signatures when edge type is reused across node pairs by @prasmussen15 in https://github.com/getzep/graphiti/pull/1197
* fix(graphiti): prevent add_triplet from overwriting edges with different src/dst by @prasmussen15 in https://github.com/getzep/graphiti/pull/1212
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/1219

## New Contributors
* @Milofax made their first contribution in https://github.com/getzep/graphiti/pull/1183
* @geojaz made their first contribution in https://github.com/getzep/graphiti/pull/1202
* @andreibogdan made their first contribution in https://github.com/getzep/graphiti/pull/1192

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.26.3...v0.27.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.27.0)

---

## v0.27.0pre2: v0.27.0pre2 - efficiency gains
**Published:** 2026-02-05
**Pre-release**

## What's Changed
* Fix dependabot security vulnerabilities by @danielchalef in https://github.com/getzep/graphiti/pull/1184
* Revert "Fix dependabot security vulnerabilities" by @danielchalef in https://github.com/getzep/graphiti/pull/1185
* Pin mcp_server to graphiti-core 0.26.3 by @danielchalef in https://github.com/getzep/graphiti/pull/1186
* Update manual code review workflow to use claude-opus-4-5-20251101 by @danielchalef in https://github.com/getzep/graphiti/pull/1189
* Refactor prompt system for efficiency and clarity by @prasmussen15 in https://github.com/getzep/graphiti/pull/1191
* fix(falkordb): sanitize pipe and slash chars in fulltext queries by @Milofax in https://github.com/getzep/graphiti/pull/1183
* feat(nodes): generate entity summary from episode when no edges exist by @prasmussen15 in https://github.com/getzep/graphiti/pull/1196
* chore: bump version to 0.27.0pre2 by @prasmussen15 in https://github.com/getzep/graphiti/pull/1200

## New Contributors
* @Milofax made their first contribution in https://github.com/getzep/graphiti/pull/1183

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.27.0pre1...v0.27.0pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.27.0pre2)

---

## v0.27.0pre1: v0.27.0pre1 - Add Episode Efficiency
**Published:** 2026-01-29
**Pre-release**

## What's Changed
* Add extracted edge facts to entity summaries by @prasmussen15 in https://github.com/getzep/graphiti/pull/1182


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.26.3...v0.27.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.27.0pre1)

---

## v0.26.3: v0.26.3 - update GraphOperationsInterface
**Published:** 2026-01-22

## What's Changed
* Add interface override paths for direct database calls by @prasmussen15 in https://github.com/getzep/graphiti/pull/1172


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.26.2...v0.26.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.26.3)

---

## v0.26.2: v0.26.2
**Published:** 2026-01-21

## What's Changed
* Remove filter_existing_duplicate_of_edges call from resolve_extracted_nodes by @prasmussen15 in https://github.com/getzep/graphiti/pull/1169


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.26.1...v0.26.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.26.2)

---

## v0.26.1: v0.26.1 - GraphOperationsInterface update
**Published:** 2026-01-21

## What's Changed
* Move saga logic into retrieve_episodes utility function by @prasmussen15 in https://github.com/getzep/graphiti/pull/1167
* update by @prasmussen15 in https://github.com/getzep/graphiti/pull/1168


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.26.0...v0.26.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.26.1)

---

## v0.26.0: v0.26.0 - New support of Sagas and Custom Instructions
**Published:** 2026-01-16

## What's Changed
* Add Sagas by @prasmussen15 in https://github.com/getzep/graphiti/pull/1149
* Add NotImplementedError fallback for GraphOperationsInterface methods by @prasmussen15 in https://github.com/getzep/graphiti/pull/1154


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.5...v0.26.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.26.0)

---

## v0.25.5: v0.25.5 - edge chunking with large numbers of nodes
**Published:** 2026-01-13

## What's Changed
* Edge extraction efficiency by @prasmussen15 in https://github.com/getzep/graphiti/pull/1140


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.4...v0.25.5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.5)

---

## v0.25.4: v0.25.4 - update custom instructions
**Published:** 2026-01-12

## What's Changed
* use custom instructions in all extraction steps by @prasmussen15 in https://github.com/getzep/graphiti/pull/1148


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.3...v0.25.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.4)

---

## v0.25.3: v0.25.3 - Fix entity extraction for large episode inputs with adaptive chunking
**Published:** 2026-01-07

## What's Changed
* Fix entity extraction for large episode inputs with adaptive chunking by @danielchalef in https://github.com/getzep/graphiti/pull/1129
* Bump version by @danielchalef in https://github.com/getzep/graphiti/pull/1139


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.2...v0.25.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.3)

---

## v0.25.2: v0.25.2 - date filter updates
**Published:** 2026-01-07

## What's Changed
* chore: Add None defaults to DateFilter date field and PropertyFilter property_value field by @paul-paliychuk in https://github.com/getzep/graphiti/pull/1134
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/1138


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.1...v0.25.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.2)

---

## v0.25.1: v0.25.1 - add_triplet bug fixes
**Published:** 2026-01-07

## What's Changed
* Update Add Triple by @prasmussen15 in https://github.com/getzep/graphiti/pull/1133


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.25.0...v0.25.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.1)

---

## v0.25.0: v0.25.0 - graph improvements and custom prompts
**Published:** 2025-12-24

## What's Changed
* Fix/model name config by @ronaldmego in https://github.com/getzep/graphiti/pull/1094
* Add SEO keyword to Zep link in README by @danielchalef in https://github.com/getzep/graphiti/pull/1114
* Add triplet update by @prasmussen15 in https://github.com/getzep/graphiti/pull/1115
* Custom prompt by @prasmussen15 in https://github.com/getzep/graphiti/pull/1122
* Fix limited number of edges by @prasmussen15 in https://github.com/getzep/graphiti/pull/1124

## New Contributors
* @ronaldmego made their first contribution in https://github.com/getzep/graphiti/pull/1094

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.24.3...v0.25.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.25.0)

---

## v0.24.3: v0.24.3 - property filters
**Published:** 2025-12-08

## What's Changed
* bump by @prasmussen15 in https://github.com/getzep/graphiti/pull/1093
* add property filters by @prasmussen15 in https://github.com/getzep/graphiti/pull/1099


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.24.2...v0.24.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.24.3)

---

## v0.24.2: v0.24.2 - language prompt update
**Published:** 2025-12-04

## What's Changed
* fix: replace deprecated gemini-2.5-flash-lite-preview with `gemini-2.5-flash-lite` by @danielchalef in https://github.com/getzep/graphiti/pull/1076
* Disable issue triage and daily maintenance workflows by @danielchalef in https://github.com/getzep/graphiti/pull/1089
* foreign language fix by @prasmussen15 in https://github.com/getzep/graphiti/pull/1090


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.24.1...v0.24.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.24.2)

---

## v0.24.1: v0.24.1 - minor changes
**Published:** 2025-11-18

## What's Changed
* [Doc]: fixing typos in various files by @didier-durand in https://github.com/getzep/graphiti/pull/1067
* Update default Anthropic model to claude-haiku-4-5 by @danielchalef in https://github.com/getzep/graphiti/pull/1070
* update summary character limit by @prasmussen15 in https://github.com/getzep/graphiti/pull/1073


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.24.0...v0.24.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.24.1)

---

## v0.24.0: v0.24.0 - Improved GenericOpenAI, Azure OpenAI, and Anthropic Support
**Published:** 2025-11-14

## What's Changed
* Bump graphiti-core to v0.23.1 in mcp_server by @danielchalef in https://github.com/getzep/graphiti/pull/1060
* Use OpenAI structured output API for response validation by @danielchalef in https://github.com/getzep/graphiti/pull/1061
* Add Azure OpenAI example with Neo4j by @danielchalef in https://github.com/getzep/graphiti/pull/1064
* Add dynamic max_tokens configuration for Anthropic models by @supmo668 in https://github.com/getzep/graphiti/pull/1043
* [Doc]: fixing typos in various files by @didier-durand in https://github.com/getzep/graphiti/pull/1065
* Bump v0.24.0 by @danielchalef in https://github.com/getzep/graphiti/pull/1066

## New Contributors
* @supmo668 made their first contribution in https://github.com/getzep/graphiti/pull/1043
* @didier-durand made their first contribution in https://github.com/getzep/graphiti/pull/1065

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.23.1...v0.24.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.24.0)

---

## v0.23.1: v0.23.1 - FalkorDB: Fix entity edge save
**Published:** 2025-11-09

## What's Changed
* Fix entity edge save by @galshubeli in https://github.com/getzep/graphiti/pull/1013


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.23.0...v0.23.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.23.1)

---

## mcp-v1.0.1: mcp-v1.0.1 - Bump graphiti-core to v0.23.1; Bug fixes
**Published:** 2025-11-09

## What's Changed
* Bump graphiti-core to v0.23.1 in mcp_server by @danielchalef in https://github.com/getzep/graphiti/pull/1060


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.23.1...mcp-v1.0.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/mcp-v1.0.1)

---

## v0.23.0: v0.23.0 - FalkorDB Enhancements, Improvements & Bug Fixes
**Published:** 2025-11-08

## What's Changed
2. **[Improvement] Add GraphID isolation support for FalkorDB multi-tenant architecture** (#835)
3. **Integrate MCP for FalkorDB** (#910)
4. **Implement build_indices_and_constraints for Kuzu and Neptune drivers** (#1048)
5. **update mmr to use bulk load overrides** (#1029)
6. **Fix Azure structured completions** (#1039)
7. **Enable FalkorDB fulltext search tests** (#1050)
8. **Fix: Enable FalkorDB Browser startup in MCP Server Docker image** (#1045)
9. **Add FalkorDB support for docker compose** (#911)
10. **Add MCP server release workflow** (#1025)
11. **Add automated FastAPI server container release workflow** (#1031)
12. **Fix MCP server release workflow to build all Dockerfile variants** (#1037)
13. **Potential fix for code scanning alert no. 24: Workflow does not contain permissions** (#1036)
14. **Disable fork PR comment job in workflow** (#1047)
15. **Search client update** (#1026)
16. **Bump version to 0.23.0** (#1056)
17. **Add Zep vs Graphiti comparison table to README** (#1014)
18. **Update Zep comparison table description** (#1046)

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0...v0.23.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.23.0)

---

## mcp-v1.0.0: Graphiti MCP Server v1.0.0
**Published:** 2025-10-31

## 🆕 New Features

- **Multi-provider support** - OpenAI, Anthropic, Gemini, Groq, Azure LLMs; multiple embedders; FalkorDB or Neo4j databases
- **Default entity ontology** - 9 preconfigured entity types (Preference, Requirement, Procedure, Location, Event, Organization, Document, Topic, Object)
- **YAML configuration** - Type-safe config with environment variable expansion and CLI overrides
- **Enhanced node properties** - Complete entity metadata including custom attributes and all labels (embeddings excluded)

## ⚡ Improvements

- **Simplified deployment** - All-in-one Docker image with FalkorDB, or connect to external databases
- **Modular architecture** - Factory pattern for providers, separated service layers
- **Health check endpoint** - Proper `/health` endpoint for Docker and load balancers
- **Comprehensive testing** - 4,000+ lines of tests covering integration, async operations, stress/load scenarios

## 💥 Breaking Changes

- **Configuration** - YAML is now primary format (env vars still supported)
- **Default database** - Changed to FalkorDB (use `docker-compose-neo4j.yml` for Neo4j)
- **Transport** - SSE deprecated, use HTTP (default) or stdio
- **Dependencies** - `pytest` and `azure-identity` moved to optional extras

More in the [MCP Readme](mcp_server/README.md)

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/mcp-v1.0.0)

---

## v0.22.1pre2: v0.22.1pre2 - minor bug fixes
**Published:** 2025-10-29
**Pre-release**

## What's Changed
* Add Zep vs Graphiti comparison table to README by @jackaldenryan in https://github.com/getzep/graphiti/pull/1014
* Add FalkorDB support for docker compose by @Naseem77 in https://github.com/getzep/graphiti/pull/911
* Integrate MCP for FalkorDB by @Naseem77 in https://github.com/getzep/graphiti/pull/910
* Search client update by @prasmussen15 in https://github.com/getzep/graphiti/pull/1026
* Add MCP server release workflow by @danielchalef in https://github.com/getzep/graphiti/pull/1025
* update mmr to use bulk load overrides by @prasmussen15 in https://github.com/getzep/graphiti/pull/1029


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0...v0.22.1pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.1pre2)

---

## v0.22.1pre1: v0.22.1pre1 - minor bugs
**Published:** 2025-10-27
**Pre-release**

## What's Changed
* Add Zep vs Graphiti comparison table to README by @jackaldenryan in https://github.com/getzep/graphiti/pull/1014
* Add FalkorDB support for docker compose by @Naseem77 in https://github.com/getzep/graphiti/pull/911
* Integrate MCP for FalkorDB by @Naseem77 in https://github.com/getzep/graphiti/pull/910
* Search client update by @prasmussen15 in https://github.com/getzep/graphiti/pull/1026


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0...v0.22.1pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.1pre1)

---

## v0.22.0: v0.22.0 - OpenTelemetry Support; Bug fixes and improvements
**Published:** 2025-10-13

## What's Changed
* Refactor node extraction; remove summary from attribute extraction by @danielchalef in https://github.com/getzep/graphiti/pull/977
* Enforce shorter summaries with 8 sentence limit by @danielchalef in https://github.com/getzep/graphiti/pull/978
* Refactor summary prompts to use character limit and prevent meta-commentary by @danielchalef in https://github.com/getzep/graphiti/pull/979
* Refactor prompt structure: move MESSAGES after instructions by @danielchalef in https://github.com/getzep/graphiti/pull/980
* Add OpenTelemetry distributed tracing support by @danielchalef in https://github.com/getzep/graphiti/pull/982
* Bump pre-release version to 0.22.0pre4 by @danielchalef in https://github.com/getzep/graphiti/pull/983
* Remove JSON indentation from prompts to reduce token usage by @danielchalef in https://github.com/getzep/graphiti/pull/985
* bump 0.22.0pre5 by @danielchalef in https://github.com/getzep/graphiti/pull/986
* Add OpenTelemetry stdout example with Kuzu by @danielchalef in https://github.com/getzep/graphiti/pull/987
* Fix datetime comparison errors by normalizing to UTC by @danielchalef in https://github.com/getzep/graphiti/pull/988
* add search and graph operations interfaces by @prasmussen15 in https://github.com/getzep/graphiti/pull/984
* fix deprecated cypher pattern by @prasmussen15 in https://github.com/getzep/graphiti/pull/993
* Update README.md fix wrong link by @gkorland in https://github.com/getzep/graphiti/pull/768
* Separate unit, database, and API integration tests by @danielchalef in https://github.com/getzep/graphiti/pull/997
* Fix FalkorDB index deletion implementation by @danielchalef in https://github.com/getzep/graphiti/pull/998
* Secure Claude PR reviews with two-workflow approach by @danielchalef in https://github.com/getzep/graphiti/pull/999
* fix: wrap embeddings with vecf32() in FalkorDB single save paths by @Naseem77 in https://github.com/getzep/graphiti/pull/991
* Remove integration markers from database tests by @danielchalef in https://github.com/getzep/graphiti/pull/1000
* v0.22.0 bump by @danielchalef in https://github.com/getzep/graphiti/pull/1003

## New Contributors
* @Naseem77 made their first contribution in https://github.com/getzep/graphiti/pull/991

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0...v0.22.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0)

---

## v0.22.0pre5: v0.22.0pre5 - Remove JSON indentation from prompts to reduce token usage
**Published:** 2025-10-06
**Pre-release**

## What's Changed
* Remove JSON indentation from prompts to reduce token usage by @danielchalef in https://github.com/getzep/graphiti/pull/985
* bump 0.22.0pre5 by @danielchalef in https://github.com/getzep/graphiti/pull/986


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0pre4...v0.22.0pre5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre5)

---

## v0.22.0pre4: v0.22.0pre4 - Add OpenTelemetry distributed tracing support
**Published:** 2025-10-05
**Pre-release**

## What's Changed
* Add OpenTelemetry distributed tracing support by @danielchalef in https://github.com/getzep/graphiti/pull/982
* Bump pre-release version to 0.22.0pre4 by @danielchalef in https://github.com/getzep/graphiti/pull/983


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0pre3...v0.22.0pre4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre4)

---

## v0.22.0pre3: v0.22.0pre3 - Truncate Entity Summaries; Prompt Optimizations
**Published:** 2025-10-05
**Pre-release**

## What's Changed
* Refactor prompt structure: move MESSAGES after instructions by @danielchalef in https://github.com/getzep/graphiti/pull/980


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0pre2...v0.22.0pre3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre3)

---

## v0.22.0pre2: v0.22.0pre2- Refactor summary prompts to prevent meta-commentary
**Published:** 2025-10-04
**Pre-release**

## What's Changed
* Refactor summary prompts to use character limit and prevent meta-commentary by @danielchalef in https://github.com/getzep/graphiti/pull/979


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0pre1...v0.22.0pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre2)

---

## v0.22.0pre1: v0.22.0pre1 - Prompt for shorter summaries with 8 sentence limit
**Published:** 2025-10-04
**Pre-release**

## What's Changed
* Prompt for shorter summaries with 8 sentence limit by @danielchalef in https://github.com/getzep/graphiti/pull/978


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.22.0pre0...v0.22.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre1)

---

## v0.22.0pre0: v0.22.0pre0 - Refactor node extraction; remove summary from attribute extraction
**Published:** 2025-10-04
**Pre-release**

## What's Changed
* Refactor node extraction; remove summary from attribute extraction by @danielchalef in https://github.com/getzep/graphiti/pull/977


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0...v0.22.0pre0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.22.0pre0)

---

## v0.21.0: v0.21.0 - Improved Performance
**Published:** 2025-10-03

## What's Changed
Since the release of v0.20.4 we have dramatically improved the quality of extractions, significantly reduced the number of runtime errors when adding an episode, and improved consistency and reliability of graph building.

* OpenSearch Integration for Neo4j by @prasmussen15 in https://github.com/getzep/graphiti/pull/896
* OpenSearch updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/906
* Embedding fix by @prasmussen15 in https://github.com/getzep/graphiti/pull/917
* fix-fulltext-syntax-error by @galshubeli in https://github.com/getzep/graphiti/pull/914
* Graph quality updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/922
* Skip entity attribute extraction when no fields defined by @danielchalef in https://github.com/getzep/graphiti/pull/924
* pre5 by @prasmussen15 in https://github.com/getzep/graphiti/pull/926
* don't save duplicate edges by @prasmussen15 in https://github.com/getzep/graphiti/pull/927
* Improve node deduplication w/ deterministic matching, LLM fallbacks by @danielchalef in https://github.com/getzep/graphiti/pull/929
* Bump v0.30.0pre0 by @danielchalef in https://github.com/getzep/graphiti/pull/932
* Refactor batch deduplication logic to enhance node resolution and track duplicate pairs (#929) by @danielchalef in https://github.com/getzep/graphiti/pull/936
* Update pyproject.toml to 0.30.0pre1 by @danielchalef in https://github.com/getzep/graphiti/pull/938
* Fix index out of range errors in LLM deduplication responses by @danielchalef in https://github.com/getzep/graphiti/pull/939
* chore: Bump version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/940
* Improve node dedup prompts by @danielchalef in https://github.com/getzep/graphiti/pull/942
* bump 0.30.0pre3 by @danielchalef in https://github.com/getzep/graphiti/pull/946
* fix: Add edge type validation based on node labels by @danielchalef in https://github.com/getzep/graphiti/pull/948
* Allow Edge extraction to keep discovered edge labels by @danielchalef in https://github.com/getzep/graphiti/pull/950
* Improve JSON entity extraction prompt by @jackaldenryan in https://github.com/getzep/graphiti/pull/949
* Make natural language extraction configurable by @danielchalef in https://github.com/getzep/graphiti/pull/943
* 21 pre 7 by @prasmussen15 in https://github.com/getzep/graphiti/pull/954
* fix: Prevent duplicate edge facts within same episode by @danielchalef in https://github.com/getzep/graphiti/pull/955
* bump pre8 by @danielchalef in https://github.com/getzep/graphiti/pull/956
* chore: Update edge extraction prompt to paraphrase instead of quote by @danielchalef in https://github.com/getzep/graphiti/pull/957
* Bump version to 0.21.0pre9 by @danielchalef in https://github.com/getzep/graphiti/pull/958
* fix: Fix typo in JSON entity extraction prompt by @jackaldenryan in https://github.com/getzep/graphiti/pull/953
* Update Claude review prompt to focus on critical feedback by @danielchalef in https://github.com/getzep/graphiti/pull/960
* feat: Add optional callback to control node summary generation by @danielchalef in https://github.com/getzep/graphiti/pull/959
* Bump version to 0.21.0pre10 by @danielchalef in https://github.com/getzep/graphiti/pull/962
* Refactor issue workflows for improved automation by @danielchalef in https://github.com/getzep/graphiti/pull/964
* fix: Improve deduplication ID validation and logging by @danielchalef in https://github.com/getzep/graphiti/pull/965
* filter out falsey values before creating embeddings by @prasmussen15 in https://github.com/getzep/graphiti/pull/966
* Remove ensure_ascii configuration parameter by @danielchalef in https://github.com/getzep/graphiti/pull/969
* Optimize edge deduplication prompt for caching and clarity by @danielchalef in https://github.com/getzep/graphiti/pull/970
* fix: Improve edge extraction entity ID validation by @danielchalef in https://github.com/getzep/graphiti/pull/968
* Bump version to 0.21.0pre12 by @danielchalef in https://github.com/getzep/graphiti/pull/967
* validate nodes and edges aren't falsey by @prasmussen15 in https://github.com/getzep/graphiti/pull/973
* Add group_id parameter to language extraction function by @danielchalef in https://github.com/getzep/graphiti/pull/952
* Update issue triage workflow to allow non-write users for duplicate checks by @danielchalef in https://github.com/getzep/graphiti/pull/974
* remove generic aoss_client interactions for release build by @prasmussen15 in https://github.com/getzep/graphiti/pull/975


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.4...v0.21.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0)

---

## v0.21.0pre13: v0.21.0pre13 - filter out empty nodes and edges
**Published:** 2025-10-03
**Pre-release**

## What's Changed
* validate nodes and edges aren't falsey by @prasmussen15 in https://github.com/getzep/graphiti/pull/973


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre12...v0.21.0pre13

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre13)

---

## v0.21.0pre12: v0.21.0pre12 - Improved edge deduping & extraction; utf-8 use
**Published:** 2025-10-03
**Pre-release**

## What's Changed
* Remove ensure_ascii configuration parameter by @danielchalef in https://github.com/getzep/graphiti/pull/969
* Optimize edge deduplication prompt for caching and clarity by @danielchalef in https://github.com/getzep/graphiti/pull/970
* fix: Improve edge extraction entity ID validation by @danielchalef in https://github.com/getzep/graphiti/pull/968
* Bump version to 0.21.0pre12 by @danielchalef in https://github.com/getzep/graphiti/pull/967


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre11...v0.21.0pre12

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre12)

---

## v0.21.0pre11: v0.21.0pre11 - minor bug fixes
**Published:** 2025-10-02
**Pre-release**

## What's Changed
* Refactor issue workflows for improved automation by @danielchalef in https://github.com/getzep/graphiti/pull/964
* fix: Improve deduplication ID validation and logging by @danielchalef in https://github.com/getzep/graphiti/pull/965
* filter out falsey values before creating embeddings by @prasmussen15 in https://github.com/getzep/graphiti/pull/966


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre10...v0.21.0pre11

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre11)

---

## v0.21.0pre9: v0.21.0pre9 - Update edge extraction prompt to paraphrase instead of quote
**Published:** 2025-10-01
**Pre-release**

## What's Changed
* chore: Update edge extraction prompt to paraphrase instead of quote by @danielchalef in https://github.com/getzep/graphiti/pull/957
* Bump version to 0.21.0pre9 by @danielchalef in https://github.com/getzep/graphiti/pull/958


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre8...v0.21.0pre9

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre9)

---

## v0.21.0pre8: v0.21.0pre8 - fix: Prevent duplicate edge facts within same episode
**Published:** 2025-10-01
**Pre-release**

## What's Changed
* fix: Prevent duplicate edge facts within same episode by @danielchalef in https://github.com/getzep/graphiti/pull/955
* bump pre8 by @danielchalef in https://github.com/getzep/graphiti/pull/956


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre7...v0.21.0pre8

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre8)

---

## v0.21.0pre10: v0.21.0pre10 - Add optional callback to control node summary generation; Fixes
**Published:** 2025-10-02
**Pre-release**

## What's Changed
* fix: Fix typo in JSON entity extraction prompt by @jackaldenryan in https://github.com/getzep/graphiti/pull/953
* Update Claude review prompt to focus on critical feedback by @danielchalef in https://github.com/getzep/graphiti/pull/960
* feat: Add optional callback to control node summary generation by @danielchalef in https://github.com/getzep/graphiti/pull/959
* Bump version to 0.21.0pre10 by @danielchalef in https://github.com/getzep/graphiti/pull/962


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre9...v0.21.0pre10

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre10)

---

## v0.30.0pre5: v0.30.0pre5 - Allow Edge extraction to keep discovered edge labels
**Published:** 2025-09-30
**Pre-release**

## What's Changed
* Allow Edge extraction to keep discovered edge labels by @danielchalef in https://github.com/getzep/graphiti/pull/950


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre4...v0.30.0pre5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre5)

---

## v0.21.0pre7: v0.21.0pre7 - prerelease for v0.21 as 0.21 hasn't released yet
**Published:** 2025-09-30
**Pre-release**

## What's Changed
* Improve JSON entity extraction prompt by @jackaldenryan in https://github.com/getzep/graphiti/pull/949
* Make natural language extraction configurable by @danielchalef in https://github.com/getzep/graphiti/pull/943
* 21 pre 7 by @prasmussen15 in https://github.com/getzep/graphiti/pull/954


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre5...v0.21.0pre7

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre7)

---

## v0.30.0pre4: v0.30.0pre4 - Add edge type validation based on node labels
**Published:** 2025-09-29
**Pre-release**

## What's Changed
* fix: Add edge type validation based on node labels by @danielchalef in https://github.com/getzep/graphiti/pull/948


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre3...v0.30.0pre4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre4)

---

## v0.30.0pre3: v0.30.0pre3 - Improve node dedup prompts
**Published:** 2025-09-29
**Pre-release**

## What's Changed
* Improve node dedup prompts by @danielchalef in https://github.com/getzep/graphiti/pull/942
* bump 0.30.0pre3 by @danielchalef in https://github.com/getzep/graphiti/pull/946


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre2...v0.30.0pre3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre3)

---

## v0.30.0pre2: v0.30.0pre2 - Fix index out of range errors
**Published:** 2025-09-26
**Pre-release**

## What's Changed
* Fix index out of range errors in LLM deduplication responses by @danielchalef in https://github.com/getzep/graphiti/pull/939
* chore: Bump version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/940


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre1...v0.30.0pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre2)

---

## v0.30.0pre1: v0.30.0pre1 - Improve Batch Node Deduplication
**Published:** 2025-09-26
**Pre-release**

## What's Changed
* Refactor batch deduplication logic to enhance node resolution and track duplicate pairs (#929) by @danielchalef in https://github.com/getzep/graphiti/pull/936
* Update pyproject.toml to 0.30.0pre1 by @danielchalef in https://github.com/getzep/graphiti/pull/938


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.30.0pre0...v0.30.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre1)

---

## v0.30.0pre0: v0.30.0pre0 - Improve node and edge deduplication w/ deterministic matching, LLM fallbacks
**Published:** 2025-09-25
**Pre-release**

## What's Changed
* Improve node/edge deduplication w/ deterministic matching, LLM fallbacks by @danielchalef in https://github.com/getzep/graphiti/pull/929


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre6...v0.30.0pre0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.30.0pre0)

---

## v0.21.0pre6: v0.21.0pre6
**Published:** 2025-09-24
**Pre-release**

## What's Changed
* don't save duplicate edges by @prasmussen15 in https://github.com/getzep/graphiti/pull/927


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre5...v0.21.0pre6

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre6)

---

## v0.21.0pre5: v0.21.0pre5 - optimize cost
**Published:** 2025-09-24
**Pre-release**

## What's Changed
* Skip entity attribute extraction when no fields defined by @danielchalef in https://github.com/getzep/graphiti/pull/924
* pre5 by @prasmussen15 in https://github.com/getzep/graphiti/pull/926


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre4...v0.21.0pre5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre5)

---

## v0.21.0pre4: v0.21.0pre4 - prompt improvements
**Published:** 2025-09-23
**Pre-release**

## What's Changed
* fix-fulltext-syntax-error by @galshubeli in https://github.com/getzep/graphiti/pull/914
* Graph quality updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/922


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre3...v0.21.0pre4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre4)

---

## v0.21.0pre3: v0.21.0pre3 - embedding fix
**Published:** 2025-09-20
**Pre-release**

## What's Changed
* Embedding fix by @prasmussen15 in https://github.com/getzep/graphiti/pull/917


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre2...v0.21.0pre3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre3)

---

## v0.21.0pre2: v0.21.0pre2 - updated OpenSearch
**Published:** 2025-09-14
**Pre-release**

## What's Changed
* OpenSearch updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/906


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.21.0pre1...v0.21.0pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre2)

---

## v0.21.0pre1: v0.21.0pre1
**Published:** 2025-09-11
**Pre-release**

## What's Changed
* OpenSearch Integration for Neo4j by @prasmussen15 in https://github.com/getzep/graphiti/pull/896


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.4...v0.21.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.21.0pre1)

---

## v0.20.4: v0.20.4 - add triplet return type
**Published:** 2025-09-08

## What's Changed
* Add return to add_triplet by @prasmussen15 in https://github.com/getzep/graphiti/pull/898


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.3...v0.20.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.20.4)

---

## v0.20.3: v0.20.3 - bulk episode return type
**Published:** 2025-09-08

## What's Changed
* add episode bulk search results by @prasmussen15 in https://github.com/getzep/graphiti/pull/897


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.2...v0.20.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.20.3)

---

## v0.20.2: v0.20.2 - efficiency gains
**Published:** 2025-09-05

## What's Changed
* cleanup by @prasmussen15 in https://github.com/getzep/graphiti/pull/894


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.1...v0.20.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.20.2)

---

## v0.20.1: v0.20.1
**Published:** 2025-09-03

## What's Changed
* update by @prasmussen15 in https://github.com/getzep/graphiti/pull/891


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.20.0...v0.20.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.20.1)

---

## v0.20.0: v0.20.0 - Remove parallel runtime option
**Published:** 2025-09-03

## What's Changed
* Remove the USE_PARALLEL_RUNTIME option for Neo4j Cypher Queries - optimizations have been made such  that this option is no longer beneficial
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/889


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.19.0...v0.20.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.20.0)

---

## v0.19.0: v0.19.0 - Kuzu integration
**Published:** 2025-09-02

## What's Changed
* Amazon Neptune Support by @bechbd in https://github.com/getzep/graphiti/pull/793
* Gpt 5 default by @prasmussen15 in https://github.com/getzep/graphiti/pull/849
* fix broken link by @gkorland in https://github.com/getzep/graphiti/pull/855
* feat: Add GitHub AI Moderator for automated spam detection by @danielchalef in https://github.com/getzep/graphiti/pull/856
* use hnsw indexes by @prasmussen15 in https://github.com/getzep/graphiti/pull/859
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/860
* dont create extra search embeddings by @prasmussen15 in https://github.com/getzep/graphiti/pull/861
* Fixed issue where creating indices was not called for Neptune and added missing quickstart example by @bechbd in https://github.com/getzep/graphiti/pull/850
* docs: Update Ollama integration to use OpenAIGenericClient by @danielchalef in https://github.com/getzep/graphiti/pull/866
* update migration by @prasmussen15 in https://github.com/getzep/graphiti/pull/870
* Add support for Kuzu as the graph driver by @sdht0 in https://github.com/getzep/graphiti/pull/799
* docs: Add Azure OpenAI v1 API opt-in requirement documentation by @jackaldenryan in https://github.com/getzep/graphiti/pull/873
* Update claude-code-review.yml by @danielchalef in https://github.com/getzep/graphiti/pull/876
* Update claude.yml by @danielchalef in https://github.com/getzep/graphiti/pull/877
* Update claude-code-review.yml by @danielchalef in https://github.com/getzep/graphiti/pull/880
* Update claude-code-review.yml by @danielchalef in https://github.com/getzep/graphiti/pull/883
* Update cla.yml by @danielchalef in https://github.com/getzep/graphiti/pull/884
* update-tests by @prasmussen15 in https://github.com/getzep/graphiti/pull/872
* don't return index labels by @prasmussen15 in https://github.com/getzep/graphiti/pull/887

## New Contributors
* @bechbd made their first contribution in https://github.com/getzep/graphiti/pull/793
* @sdht0 made their first contribution in https://github.com/getzep/graphiti/pull/799

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.9...v0.19.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.19.0)

---

## v0.19.0pre3: v0.19.0pre3 - migration update
**Published:** 2025-08-27
**Pre-release**

## What's Changed
* Fixed issue where creating indices was not called for Neptune and added missing quickstart example by @bechbd in https://github.com/getzep/graphiti/pull/850
* docs: Update Ollama integration to use OpenAIGenericClient by @danielchalef in https://github.com/getzep/graphiti/pull/866
* update migration by @prasmussen15 in https://github.com/getzep/graphiti/pull/870


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.19.0pre2...v0.19.0pre3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.19.0pre3)

---

## v0.19.0pre2: v0.19.0pre2
**Published:** 2025-08-26
**Pre-release**

## What's Changed
* dont create extra search embeddings by @prasmussen15 in https://github.com/getzep/graphiti/pull/861


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.19.0pre1...v0.19.0pre2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.19.0pre2)

---

## v0.19.0pre1: v0.19.0pre1 - add HNSW indexes
**Published:** 2025-08-25
**Pre-release**

## What's Changed
* Amazon Neptune Support by @bechbd in https://github.com/getzep/graphiti/pull/793
* Gpt 5 default by @prasmussen15 in https://github.com/getzep/graphiti/pull/849
* fix broken link by @gkorland in https://github.com/getzep/graphiti/pull/855
* feat: Add GitHub AI Moderator for automated spam detection by @danielchalef in https://github.com/getzep/graphiti/pull/856
* use hnsw indexes by @prasmussen15 in https://github.com/getzep/graphiti/pull/859
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/860

## New Contributors
* @bechbd made their first contribution in https://github.com/getzep/graphiti/pull/793

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.9...v0.19.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.19.0pre1)

---

## v0.18.9: v0.18.9 - updated thinking prompts
**Published:** 2025-08-19

## What's Changed
* update prompts and support thinking models by @prasmussen15 in https://github.com/getzep/graphiti/pull/846


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.8...v0.18.9

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.9)

---

## v0.18.8: v0.18.8 - minor bug fixes
**Published:** 2025-08-18

## What's Changed
* Fix Community Operations with FalkorDB by @galshubeli in https://github.com/getzep/graphiti/pull/824
* fix typo and model selector by @prasmussen15 in https://github.com/getzep/graphiti/pull/843


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.7...v0.18.8

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.8)

---

## v0.18.7: v0.18.7 - deletion optimizations
**Published:** 2025-08-15

## What's Changed
* Update CONTRIBUTING.md by @danielchalef in https://github.com/getzep/graphiti/pull/830
* Fix: Search methods configuration ignored (#788) by @liebertar in https://github.com/getzep/graphiti/pull/829
* add bulk delete by @prasmussen15 in https://github.com/getzep/graphiti/pull/837

## New Contributors
* @liebertar made their first contribution in https://github.com/getzep/graphiti/pull/829

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.6...v0.18.7

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.7)

---

## v0.18.6: v0.18.6 - update search filters to support null checks
**Published:** 2025-08-12

## What's Changed
* Null search datetimes by @prasmussen15 in https://github.com/getzep/graphiti/pull/818


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.5...v0.18.6

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.6)

---

## v0.18.5: v0.18.5 - properly support ascii characters
**Published:** 2025-08-08

## What's Changed
* Add support for non-ASCII characters in LLM prompts by @hugo-son in https://github.com/getzep/graphiti/pull/805
* ensure ascii default to false by @prasmussen15 in https://github.com/getzep/graphiti/pull/817

## New Contributors
* @hugo-son made their first contribution in https://github.com/getzep/graphiti/pull/805

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.4...v0.18.5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.5)

---

## v0.18.4: v0.18.4 - batch delete to optimize CPU usage
**Published:** 2025-08-07

## What's Changed
* Fix Azure OpenAI configuration parameter in README by @jackaldenryan in https://github.com/getzep/graphiti/pull/807
* add batch delete capabilities by @prasmussen15 in https://github.com/getzep/graphiti/pull/813


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.3...v0.18.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.4)

---

## v0.18.3: v0.18.3 - minor bug fixes
**Published:** 2025-08-05

## What's Changed
* add community group id index by @prasmussen15 in https://github.com/getzep/graphiti/pull/802
* update add triple to always have embeddings by @prasmussen15 in https://github.com/getzep/graphiti/pull/803
* test updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/806


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.2...v0.18.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.3)

---

## v0.18.2: v0.18.2 - Calculate summaries separate from node attributes
**Published:** 2025-07-31

## What's Changed
* move summary out of attribute extraction by @prasmussen15 in https://github.com/getzep/graphiti/pull/792


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.1...v0.18.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.2)

---

## v0.18.1: v0.18.1 - improve runaway generations and index out of range errors
**Published:** 2025-07-29

## What's Changed
* feat/falkordb dynamic graph names by @danielchalef in https://github.com/getzep/graphiti/pull/761
* add concurrency explanation, update Zep by @danielchalef in https://github.com/getzep/graphiti/pull/766
* chore/prepare kuzu integration by @danielchalef in https://github.com/getzep/graphiti/pull/762
* validate pydantic objects by @prasmussen15 in https://github.com/getzep/graphiti/pull/783


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.18.0...v0.18.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.1)

---

## v0.18.0: v0.18.0 - return search reranker scores
**Published:** 2025-07-23

## What's Changed
* Return reranker scores by @prasmussen15 in https://github.com/getzep/graphiti/pull/758


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.11...v0.18.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.18.0)

---

## v0.17.11: v0.17.11 - Group ID filtering in BFS and full-text queries
**Published:** 2025-07-23

## What's Changed
* Group ID filtering in BFS and full-text queries by @danielchalef in https://github.com/getzep/graphiti/pull/754
* bump 0.17.11 by @danielchalef in https://github.com/getzep/graphiti/pull/755


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.10...v0.17.11

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.11)

---

## v0.17.10: v0.17.10 - fulltext updates
**Published:** 2025-07-22

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.9...v0.17.10

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.10)

---

## v0.17.9: v0.17.9 - fix full text edge search
**Published:** 2025-07-22

## What's Changed
* Edge search updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/753


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.8...v0.17.9

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.9)

---

## v0.17.8: v0.17.8 - fix: missing group filter on node ft search
**Published:** 2025-07-22

## What's Changed
* fix: missing group filter on node ft search by @danielchalef in https://github.com/getzep/graphiti/pull/752


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.7...v0.17.8

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.8)

---

## v0.17.7: v0.17.7 - update full text search max length
**Published:** 2025-07-21

## What's Changed
* [Bug Fix] Fix the Group ID usage with FalkorDB by @galshubeli in https://github.com/getzep/graphiti/pull/733


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.6...v0.17.7

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.7)

---

## v0.17.6: v0.17.6 - edge_operations are more robust
**Published:** 2025-07-16

## What's Changed
* make egg_operations more robust by @prasmussen15 in https://github.com/getzep/graphiti/pull/737


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.5...v0.17.6

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.6)

---

## v0.17.5: v0.17.5 - bulk add episode updates
**Published:** 2025-07-16

## What's Changed
* Bulk updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/732
* Return embeddings option in get_by_uuids by @prasmussen15 in https://github.com/getzep/graphiti/pull/736


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.4...v0.17.5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.5)

---

## v0.17.4: v0.17.4 - Use union find in bulk ingestion
**Published:** 2025-07-15

## What's Changed
* fix: discord badge by @paul-paliychuk in https://github.com/getzep/graphiti/pull/726
* bulk utils update by @prasmussen15 in https://github.com/getzep/graphiti/pull/727


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.3...v0.17.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.4)

---

## v0.17.3: v0.17.3 - Edge save query fixes
**Published:** 2025-07-14

## What's Changed
* save edge update by @prasmussen15 in https://github.com/getzep/graphiti/pull/721


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.2...v0.17.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.3)

---

## v0.17.2: v0.17.2 - Bugfixes and improvements
**Published:** 2025-07-14

## What's Changed
* fix: neo4j username/password should not be hardcoded by @charlesmcchan in https://github.com/getzep/graphiti/pull/711
* feat(gemini): embedding batch size & lite default by @zeroasterisk in https://github.com/getzep/graphiti/pull/680
* feat: enhance GeminiClient with max tokens management by @danielchalef in https://github.com/getzep/graphiti/pull/712
* bump for bugfix release by @danielchalef in https://github.com/getzep/graphiti/pull/714

## New Contributors
* @charlesmcchan made their first contribution in https://github.com/getzep/graphiti/pull/711

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.1...v0.17.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.2)

---

## v0.17.1: v0.17.1 - Search filter fixes
**Published:** 2025-07-11

## What's Changed
* docs: add comprehensive database configuration instructions to README by @danielchalef in https://github.com/getzep/graphiti/pull/703
* update search filters by @prasmussen15 in https://github.com/getzep/graphiti/pull/706


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.17.0...v0.17.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.1)

---

## v0.17.0: v0.17.0 - Revert to using default neo4j db name. Drop DEFAULT_DATABASE env var.
**Published:** 2025-07-10

## What's Changed
* Move away from DEFAULT_DATABASE environment variable in favour of driver-config support (dc) by @urmzd in https://github.com/getzep/graphiti/pull/699
* bump v0.17.0 by @danielchalef in https://github.com/getzep/graphiti/pull/700

First contribution: @urmzd. Thank you!


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.16.0...v0.17.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.17.0)

---

## v0.16.0: v0.16.0 - Bulk ingestion
**Published:** 2025-07-10

## What's Changed
* feat(gemini): simplify config for Gemini clients by @zeroasterisk in https://github.com/getzep/graphiti/pull/679
* Add Claude Code GitHub Workflow by @danielchalef in https://github.com/getzep/graphiti/pull/690
* feat: add issue and pull request templates with compliance workflow by @danielchalef in https://github.com/getzep/graphiti/pull/689
* feat: add template compliance check and update type checking to Pyright by @danielchalef in https://github.com/getzep/graphiti/pull/692
* docs: improve Neo4j database configuration documentation by @danielchalef in https://github.com/getzep/graphiti/pull/691
* Fix Claude actions by @danielchalef in https://github.com/getzep/graphiti/pull/693
* Bulk ingestion by @prasmussen15 in https://github.com/getzep/graphiti/pull/698

## New Contributors
* @zeroasterisk made their first contribution in https://github.com/getzep/graphiti/pull/679

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.15.1...v0.16.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.16.0)

---

## v0.15.1: v0.15.1 - MCP DockerHub Images; bug fixes
**Published:** 2025-07-05

## What's Changed
* reformat by @prasmussen15 in https://github.com/getzep/graphiti/pull/655
* Add GitHub Actions workflow for building and pushing MCP Server Docker image by @danielchalef in https://github.com/getzep/graphiti/pull/656
* feat: add pre-built Docker image for Graphiti MCP server by @danielchalef in https://github.com/getzep/graphiti/pull/657
* Fix: Add missing name_embedding field to community search queries by @jamesindeed in https://github.com/getzep/graphiti/pull/664
* Refactor: Replace dictionary responses with structured response classes in graphiti_mcp_server.py by @danielchalef in https://github.com/getzep/graphiti/pull/668
* docs: add FalkorDB support and update installation instructions by @danielchalef in https://github.com/getzep/graphiti/pull/677
* feat: support OpenAIClient in OpenAIRerankerClient by @danielchalef in https://github.com/getzep/graphiti/pull/676
* REFACTOR: use env variables in docker-compose for mcp by @jawwadfirdousi in https://github.com/getzep/graphiti/pull/663
* Refactor imports by @danielchalef in https://github.com/getzep/graphiti/pull/675
* bump v0.15.1 by @danielchalef in https://github.com/getzep/graphiti/pull/678

## New Contributors
* @jamesindeed made their first contribution in https://github.com/getzep/graphiti/pull/664
* @jawwadfirdousi made their first contribution in https://github.com/getzep/graphiti/pull/663

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.15.0...v0.15.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.15.1)

---

## v0.15.0: v0.15.0 - Improved FalkorDB support; Gemini Reranker and Client improvements
**Published:** 2025-07-01

## What's Changed
* update mcp to graphiti 0.14 by @danielchalef in https://github.com/getzep/graphiti/pull/641
* FalkorDB Integration: Bug Fixes and Unit Tests by @galshubeli in https://github.com/getzep/graphiti/pull/607
* migrate to pyright by @danielchalef in https://github.com/getzep/graphiti/pull/646
* fix falkordb linting issues by @danielchalef in https://github.com/getzep/graphiti/pull/650
* Gemini client improvements; Gemini reranker by @danielchalef in https://github.com/getzep/graphiti/pull/645
* Update README.md to clarify OpenAI API usage and Azure OpenAI configuration details by @danielchalef in https://github.com/getzep/graphiti/pull/649
* Potential fix for code scanning alert no. 18: Workflow does not contain permissions by @danielchalef in https://github.com/getzep/graphiti/pull/648
* Potential fix for code scanning alert no. 17: Workflow does not contain permissions by @danielchalef in https://github.com/getzep/graphiti/pull/651

## New Contributors
* @galshubeli made their first contribution in https://github.com/getzep/graphiti/pull/607

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.14.0...v0.15.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.15.0)

---

## v0.14.0: v0.14.0 - Exclude Entity Types Filter, Fix FT Query, Telemetry, migrate to uv
**Published:** 2025-06-27

## Important: Addition of Anonymous Telemetry
This release includes the addition of anonymous telemetry. Please review the [README](https://github.com/getzep/graphiti?tab=readme-ov-file#telemetry) for a detailed description of data sent via telemetry, how telemetry works, and how to deactivate it.

## What's Changed
* Excluded entity type filtering by @danielchalef in https://github.com/getzep/graphiti/pull/624
* migrate to uv by @danielchalef in https://github.com/getzep/graphiti/pull/634
* feat: add telemetry with PostHog and update Docker configurations by @danielchalef in https://github.com/getzep/graphiti/pull/633
* fix: correct spacing in group IDs filter concatenation in fulltext_query function by @danielchalef in https://github.com/getzep/graphiti/pull/636
* bump version to 0.14.0 in pyproject.toml by @danielchalef in https://github.com/getzep/graphiti/pull/637
* Update release-graphiti-core.yml to python 3.11 by @danielchalef in https://github.com/getzep/graphiti/pull/639


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.13.2...v0.14.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.14.0)

---

## v0.13.2: v0.13.2 - minor updates
**Published:** 2025-06-26



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.13.2)

---

## v0.13.1: v0.13.1 - fix fulltext query
**Published:** 2025-06-25



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.13.1)

---

## v0.13.0: v0.13.0 - Validate `group_id` format; MCP update and fixes
**Published:** 2025-06-24

# IMPORTANT BREAKING CHANGE

We now validate `group_id` contains only alphanumeric, dash (`-`), and underscore (`_`) characters.

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.13.0)

---

## v0.12.4: v0.12.4 - bug fixes
**Published:** 2025-06-18



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.4)

---

## v0.12.3: v0.12.3 - make flakordb an optional dependency
**Published:** 2025-06-18



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.3)

---

## v0.12.2: v0.12.2 - Add IS_DUPLICATE_OF edges
**Published:** 2025-06-18



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.2)

---

## v0.12.1: v0.12.1 - minor fixes
**Published:** 2025-06-16



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.1)

---

## v0.12.0: v0.12.0 - custom edge types and abstracted Graph DBs
**Published:** 2025-06-13



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0)

---

## v0.12.0pre5: v0.12.0pre5 - optimizing node dedupe and edge extraction
**Published:** 2025-06-06
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0pre5)

---

## v0.12.0pre4: v0.12.0pre4 - upgrade pydantic version
**Published:** 2025-06-05
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0pre4)

---

## v0.12.0pre3: v0.12.0pre3 - bug fixes
**Published:** 2025-05-28
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0pre3)

---

## v0.12.0pre2: v0.12.0pre2 - edge source and target uuid resiliency
**Published:** 2025-05-28
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0pre2)

---

## v0.12.0pre1: v0.12.0pre1 - edge types
**Published:** 2025-05-23
**Pre-release**

## What's Changed
* Bump h11 from 0.14.0 to 0.16.0 in the pip group by @dependabot in https://github.com/getzep/graphiti/pull/494
* Edge types by @prasmussen15 in https://github.com/getzep/graphiti/pull/501
* Bump langchain-openai from 0.3.16 to 0.3.17 by @dependabot in https://github.com/getzep/graphiti/pull/504
* Bump langchain-anthropic from 0.3.12 to 0.3.13 by @dependabot in https://github.com/getzep/graphiti/pull/503
* Bump langgraph from 0.4.1 to 0.4.5 by @dependabot in https://github.com/getzep/graphiti/pull/502
* Bump ruff from 0.11.9 to 0.11.10 by @dependabot in https://github.com/getzep/graphiti/pull/500
* Bump setuptools from 78.1.0 to 78.1.1 in the pip group by @dependabot in https://github.com/getzep/graphiti/pull/505
* #491 by @adamkatav in https://github.com/getzep/graphiti/pull/493
* Bump google-genai from 1.9.0 to 1.15.0 by @dependabot in https://github.com/getzep/graphiti/pull/499
* MCP Fixes by @danielchalef in https://github.com/getzep/graphiti/pull/512
* Improve error handling in GeminiEmbedder by raising ValueError for empty embedding values. This change enhances robustness by ensuring that all returned embeddings contain valid data. by @danielchalef in https://github.com/getzep/graphiti/pull/515
* Implement Small Model in MCP Server; Default to 4.1-nano by @danielchalef in https://github.com/getzep/graphiti/pull/516
* chore: Bump version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/521

## New Contributors
* @adamkatav made their first contribution in https://github.com/getzep/graphiti/pull/493

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.11.6...v0.12.0pre1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.12.0pre1)

---

## v0.11.6: v0.11.6 - add episode and search optimizations
**Published:** 2025-05-15



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6)

---

## v0.11.6pre9: v0.11.6pre9 - revert semaphore gather batching
**Published:** 2025-05-14
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre9)

---

## v0.11.6pre7: v0.11.6pre7 - fix memory leak
**Published:** 2025-05-12
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre7)

---

## v0.11.6pre6: v0.11.6pre6 - batched semaphore gathers
**Published:** 2025-05-12
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre6)

---

## v0.11.6pre5: v0.11.6pre5 - episode tracking fixes
**Published:** 2025-05-09
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre5)

---

## v0.11.6pre4: v0.11.6pre4 - more updates
**Published:** 2025-05-08
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre4)

---

## v0.11.6pre3: v0.11.6pre3 - cleanup
**Published:** 2025-05-08
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre3)

---

## v0.11.6pre2: v0.11.6pre2 - add episode fixes
**Published:** 2025-05-08
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre2)

---

## v0.11.6pre1: v0.11.6pre1 - release optimization
**Published:** 2025-05-08
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.6pre1)

---

## v0.11.5: v0.11.5 - stability fixes for episode ingestion
**Published:** 2025-05-02



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.5)

---

## v0.11.4: v0.11.4 - reduce dedupe issues and add small model options
**Published:** 2025-05-02



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.4)

---

## v0.11.3: v0.11.3 - fix empty node name errors
**Published:** 2025-05-01



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.3)

---

## v0.11.2: v0.11.2 - bug fixes
**Published:** 2025-04-30



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.2)

---

## v0.11.1: v0.11.1 - JSON ingestion fix
**Published:** 2025-04-30



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.1)

---

## v0.11.0: v0.11.0 - `add_episode()` is now faster and more efficient
**Published:** 2025-04-30



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.11.0)

---

## v0.10.5: v0.10.5 - episode fixes and optimizations
**Published:** 2025-04-22



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.5)

---

## v0.10.4: v0.10.4 - tests and entity episodes virtual field
**Published:** 2025-04-21



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.4)

---

## v0.10.3: v0.10.3 - fix mar
**Published:** 2025-04-17



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.3)

---

## v0.10.2: v0.10.2 - custom entity fixes
**Published:** 2025-04-16



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.2)

---

## v0.10.1: v0.10.1 - minor bug fixes
**Published:** 2025-04-16



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.1)

---

## v0.10.0: v0.10.0 - add episode search, multilingual support, QoL updates
**Published:** 2025-04-15

* Add episode results to `graphiti.search()_` endpoint
* Add better multilingual support (information will be extracted in the language it is written in)
* Add `EpisodicNode.get_by_entity_node_uuid()` to get the episodes related to an entity node.
* Update defaults to use `gpt-4.1-mini`

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.10.0)

---

## v0.9.6: v0.9.6 - clean up context string
**Published:** 2025-04-10



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.6)

---

## v0.9.5: v0.9.5 - add search_ and context string helper
**Published:** 2025-04-09



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.5)

---

## v0.9.4: v0.9.4 
**Published:** 2025-04-09

## What's Changed
* docs: add installation instructions for Graphiti using poetry and uv by @danielchalef in https://github.com/getzep/graphiti/pull/340
* chore: update dependencies and refactor type hinting by @danielchalef in https://github.com/getzep/graphiti/pull/339
* chore: bump version to 0.9.4 in pyproject.toml by @danielchalef in https://github.com/getzep/graphiti/pull/341


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.9.3...v0.9.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.4)

---

## v0.9.3: v0.9.3 - Refactor pyproject to use syntax compatible with poetry and uv
**Published:** 2025-04-09

## What's Changed
* chore: update version to 0.9.3 and restructure dependencies by @danielchalef in https://github.com/getzep/graphiti/pull/338


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.9.2...v0.9.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.3)

---

## v0.9.2: v0.9.2 - Fix Gemini dependencies
**Published:** 2025-04-08

## What's Changed
* Fix Gemini deps and cleanup by @danielchalef in https://github.com/getzep/graphiti/pull/336


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.9.1...v0.9.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.2)

---

## v0.9.1: v0.9.1 - fix pagination
**Published:** 2025-04-08



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.1)

---

## v0.9.0: v0.9.0 - Gemini support
**Published:** 2025-04-06

## What's Changed
* Enhance README and add quickstart example for Graphiti by @danielchalef in https://github.com/getzep/graphiti/pull/326
* Gemini support by @danielchalef in https://github.com/getzep/graphiti/pull/324
* Bump version from 0.8.8 to 0.9.0 in pyproject.toml by @danielchalef in https://github.com/getzep/graphiti/pull/327


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.8.8...v0.9.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.9.0)

---

## v0.8.8: v0.8.8 - entity type validation
**Published:** 2025-04-04



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.8)

---

## v0.8.7: v0.8.7 - add previous episodes override to add episode
**Published:** 2025-04-02



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.7)

---

## v0.8.6: v0.8.6 - update MCP
**Published:** 2025-04-02



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.6)

---

## v0.8.5: v0.8.5 - handle errors better
**Published:** 2025-03-27



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.5)

---

## v0.8.4: v0.8.4 - fix get edges by uuid error handling
**Published:** 2025-03-27



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.4)

---

## v0.8.3: v0.8.3 - fix node attributes updates
**Published:** 2025-03-26



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.3)

---

## v0.8.2: v0.8.2 - fix node save errors
**Published:** 2025-03-24



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.2)

---

## v0.8.1: v0.8.1 - entity classification safeguards
**Published:** 2025-03-20



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.1)

---

## v0.8.0: v0.8.0 - get_nodes_and_edges_by_episode and get edges by node_uuid
**Published:** 2025-03-13

v0.8.0 - get_nodes_and_edges_by_episode and get edges by node_uuid

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.8.0)

---

## v0.7.9: v0.7.9 - use docstring for entity type description
**Published:** 2025-03-05



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.9)

---

## v0.7.8: v0.7.8 - fixed bugs around entity classification
**Published:** 2025-03-05



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.8)

---

## v0.7.7: v0.7.7 - node label filter updates
**Published:** 2025-03-04



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.7)

---

## v0.7.6: v0.7.6 - fallback on failed classifications
**Published:** 2025-02-28



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.6)

---

## v0.7.5: v0.7.5 - entity classification fixes
**Published:** 2025-02-27



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.5)

---

## v0.7.4: v0.7.4 - search fixes and optimizations
**Published:** 2025-02-27



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.4)

---

## v0.7.3: v0.7.3 - update node attributes field
**Published:** 2025-02-25



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.3)

---

## v0.7.2: v0.7.2 - fix entity typo
**Published:** 2025-02-25

## What's Changed
* Neo4j 5.26 by @prasmussen15 in https://github.com/getzep/graphiti/pull/271
* Scarlett/add logo and stars by @sattensil in https://github.com/getzep/graphiti/pull/269
* entity typo by @prasmussen15 in https://github.com/getzep/graphiti/pull/274
* chore: Bump version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/275

## New Contributors
* @sattensil made their first contribution in https://github.com/getzep/graphiti/pull/269

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.7.1...v0.7.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.2)

---

## v0.7.1: v0.7.1 - Node label search filters
**Published:** 2025-02-21



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.1)

---

## v0.7.0: v0.7.0 - Custom Entity Types
**Published:** 2025-02-13

Add the ability to use Pydantic BaseModels to define custom entity types. During ingestion, Graphiti will attempt to classify and extract relevant metadata for the provided types

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.7.0)

---

## v0.6.1: v0.6.1 - add_triplet bug fixes
**Published:** 2025-02-12



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.6.1)

---

## v0.6.0: v0.6.0 - remove episode endpoint
**Published:** 2025-02-05

remove episode endpoint

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.6.0)

---

## v0.5.3: v0.5.3 - update token limits
**Published:** 2025-02-01



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.3)

---

## v0.5.2: v0.5.2 - make token limits configurable by prompt
**Published:** 2025-01-24

make token limits configurable by prompt

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.2)

---

## v0.5.1: v0.5.1 - better exception handling
**Published:** 2024-12-17



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.1)

---

## v0.5.0: v0.5.0 - Limit concurrency and optimize neo4j queries
**Published:** 2024-12-17

## What's Changed
* Implement OpenAI Structured Output by @danielchalef in https://github.com/getzep/graphiti/pull/225
* update summary length by @prasmussen15 in https://github.com/getzep/graphiti/pull/227
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/228
* feat: add retry logic and improve logging in OpenAIClient by @danielchalef in https://github.com/getzep/graphiti/pull/229
* pre3 by @prasmussen15 in https://github.com/getzep/graphiti/pull/230
* fix node distance reranker by @prasmussen15 in https://github.com/getzep/graphiti/pull/231
* default to no pagination by @prasmussen15 in https://github.com/getzep/graphiti/pull/232
* update lucene escaping by @prasmussen15 in https://github.com/getzep/graphiti/pull/233
* refactor: use `utc_now()` for consistent UTC datetime handling by @danielchalef in https://github.com/getzep/graphiti/pull/234
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/236
* fix: Clean input before passing it to the llm by @paul-paliychuk in https://github.com/getzep/graphiti/pull/238
* add generic client by @prasmussen15 in https://github.com/getzep/graphiti/pull/237
* chore: Clean input to openai generic client by @paul-paliychuk in https://github.com/getzep/graphiti/pull/239
* Abstract Neo4j filters in search queries by @prasmussen15 in https://github.com/getzep/graphiti/pull/243
* Warn on invalid date by @prasmussen15 in https://github.com/getzep/graphiti/pull/242
* Bounded semaphore - limiting concurrency by @prasmussen15 in https://github.com/getzep/graphiti/pull/244
* bump version by @prasmussen15 in https://github.com/getzep/graphiti/pull/245


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.4.3...v0.5.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0)

---

## v0.5.0pre5: v0.5.0pre5 - Clean llm input
**Published:** 2024-12-11
**Pre-release**

## What's Changed
* fix: Clean input before passing it to the llm by @paul-paliychuk in https://github.com/getzep/graphiti/pull/238


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.5.0pre4...v0.5.0pre5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0pre5)

---

## v0.5.0pre4: v0.5.0pre4 - optional pagination and minor bug fixes
**Published:** 2024-12-09
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0pre4)

---

## v0.5.0pre3: v0.5.0pre3 - openAI retries
**Published:** 2024-12-06
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0pre3)

---

## v0.5.0pre2: v0.5.0pre2 - limit summary length
**Published:** 2024-12-05
**Pre-release**



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0pre2)

---

## v0.5.0pre1: v0.5.0pre1 - use openAI structured output
**Published:** 2024-12-05
**Pre-release**

Non-openai clients may not work with this pre-release

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.5.0pre1)

---

## v0.4.3: v0.4.3 - don't escape unicode system prompt
**Published:** 2024-12-03



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.4.3)

---

## v0.4.2: v0.4.2 - reduce DB connections
**Published:** 2024-11-18



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.4.2)

---

## v0.4.1: v0.4.1 - improve full text edge search performance
**Published:** 2024-11-15



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.4.1)

---

## v0.4.0: v0.4.0 - Add reflexion and reduce ingestion and search latency
**Published:** 2024-11-14

- `add_episode` now uses reflexion to achieve more accurate results during graph creation
- `add_episode` and `search` should now have reduced latency

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.4.0)

---

## v0.3.21: v0.3.21 - handle empty search queries
**Published:** 2024-11-04



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.21)

---

## v0.3.20: v0.3.20 - add bulk write operation and optional parallel runtime
**Published:** 2024-10-31



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.20)

---

## v0.3.19: v0.3.19 - fix embedder issue
**Published:** 2024-10-29

v0.3.19 - fix embedder issue

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.19)

---

## v0.3.18: v0.3.18 - Update reranker limits
**Published:** 2024-10-28

## What's Changed
* Update reranker limits by @prasmussen15 in https://github.com/getzep/graphiti/pull/203


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.17...v0.3.18

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.18)

---

## v0.3.17: v0.3.17 - Add cross_encoder reranking and bfs search
**Published:** 2024-10-25

v0.3.17 - Add cross_encoder reranking and bfs search

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.17)

---

## v0.3.16: v0.3.16 - Use session search
**Published:** 2024-10-22

## What's Changed
* Use sessions search by @prasmussen15 in https://github.com/getzep/graphiti/pull/197
* chore: Bump version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/198


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.15...v0.3.16

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.16)

---

## v0.3.15: v0.3.15 - Default Database Load Env Fix
**Published:** 2024-10-22

## What's Changed
* load env in helper file by @prasmussen15 in https://github.com/getzep/graphiti/pull/196


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.14...v0.3.15

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.15)

---

## v0.3.14: v0.3.14 - Use explicit DEFAULT_DATABASE
**Published:** 2024-10-21



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.14)

---

## v0.3.13: v0.3.13 - Update Lucene search
**Published:** 2024-10-20

## What's Changed
* update lucene search by @prasmussen15 in https://github.com/getzep/graphiti/pull/193


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.12...v0.3.13

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.13)

---

## v0.3.12: v0.3.12 - Remove fuzzy search to fix large queries
**Published:** 2024-10-19

Remove fuzzy search to fix large queries

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.12)

---

## v0.3.11: v0.3.11 - Fix bug when not storing raw content
**Published:** 2024-10-15



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.11)

---

## v0.3.10: v0.3.10 - update logging and error types
**Published:** 2024-10-11



[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.10)

---

## v0.3.9: v0.3.9 - Improve quality of temporal extraction and edge invalidations, Add MMR reranking to search
**Published:** 2024-10-08

## What's Changed
* chore(deps): Bump neo4j from 5.24.0 to 5.25.0 by @dependabot in https://github.com/getzep/graphiti/pull/168
* chore(deps-dev): Bump langgraph from 0.2.23 to 0.2.28 by @dependabot in https://github.com/getzep/graphiti/pull/167
* chore(deps-dev): Bump ruff from 0.6.7 to 0.6.8 by @dependabot in https://github.com/getzep/graphiti/pull/166
* chore(deps-dev): Bump langsmith from 0.1.125 to 0.1.129 by @dependabot in https://github.com/getzep/graphiti/pull/165
* chore: Add build and start CI workflow by @paul-paliychuk in https://github.com/getzep/graphiti/pull/164
* feat: add health checks and dependencies to docker-compose by @paul-paliychuk in https://github.com/getzep/graphiti/pull/163
* update lucene sanitizer by @prasmussen15 in https://github.com/getzep/graphiti/pull/170
* test escape characters by @prasmussen15 in https://github.com/getzep/graphiti/pull/171
* Msc benchmark update by @prasmussen15 in https://github.com/getzep/graphiti/pull/173
* add addepisode return object by @prasmussen15 in https://github.com/getzep/graphiti/pull/172
* Fix edge invalidation by @prasmussen15 in https://github.com/getzep/graphiti/pull/174
* chore(deps): Bump numpy from 2.1.1 to 2.1.2 by @dependabot in https://github.com/getzep/graphiti/pull/179
* chore(deps-dev): Bump ruff from 0.6.8 to 0.6.9 by @dependabot in https://github.com/getzep/graphiti/pull/178
* chore(deps-dev): Bump langsmith from 0.1.130 to 0.1.131 by @dependabot in https://github.com/getzep/graphiti/pull/177
* chore(deps): Bump openai from 1.51.0 to 1.51.1 by @dependabot in https://github.com/getzep/graphiti/pull/175
* Add mmr reranking by @prasmussen15 in https://github.com/getzep/graphiti/pull/180
* chore(deps-dev): Bump anthropic from 0.34.2 to 0.35.0 by @dependabot in https://github.com/getzep/graphiti/pull/176
* fix: Release workflow for service image by @paul-paliychuk in https://github.com/getzep/graphiti/pull/182


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.8...v0.3.9

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.9)

---

## v0.3.8: v0.3.8 - Bump openai version
**Published:** 2024-09-28

## What's Changed
* chore: Update openai version by @paul-paliychuk in https://github.com/getzep/graphiti/pull/162


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.7...v0.3.8

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.8)

---

## v0.3.7: v0.3.7 - Add configurable embedding interface
**Published:** 2024-09-27

## What's Changed
* Add MSC benchmark and improve search performance by @prasmussen15 in https://github.com/getzep/graphiti/pull/157
* feat: configurable embedding model by @ArnoChenFx in https://github.com/getzep/graphiti/pull/156
* chore: simplify Docker image release workflow by @paul-paliychuk in https://github.com/getzep/graphiti/pull/158
* feat: Dedicated embedder interface by @paul-paliychuk in https://github.com/getzep/graphiti/pull/159

## New Contributors
* @ArnoChenFx made their first contribution in https://github.com/getzep/graphiti/pull/156

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.6...v0.3.7

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.7)

---

## v0.3.6: v0.3.6 - Make deleting edges by group_id safer
**Published:** 2024-09-25

## What's Changed
* chore: Make deleting groups safer by @paul-paliychuk in https://github.com/getzep/graphiti/pull/155


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.5...v0.3.6

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.6)

---

## v0.3.5: v0.3.5 - Group ID updates
**Published:** 2024-09-24

## What's Changed
* chore(deps-dev): Bump langgraph from 0.2.19 to 0.2.23 by @dependabot in https://github.com/getzep/graphiti/pull/150
* chore(deps): Bump pydantic from 2.9.1 to 2.9.2 by @dependabot in https://github.com/getzep/graphiti/pull/149
* chore(deps): Bump openai from 1.45.1 to 1.47.0 by @dependabot in https://github.com/getzep/graphiti/pull/148
* chore(deps-dev): Bump ruff from 0.6.5 to 0.6.7 by @dependabot in https://github.com/getzep/graphiti/pull/147
* chore(deps-dev): Bump langsmith from 0.1.121 to 0.1.125 by @dependabot in https://github.com/getzep/graphiti/pull/146
* Group id fix by @prasmussen15 in https://github.com/getzep/graphiti/pull/152
* feat: async close and multi-group search support by @paul-paliychuk in https://github.com/getzep/graphiti/pull/151
* refactor: remove unnecessary type casting in `search()` function by @paul-paliychuk in https://github.com/getzep/graphiti/pull/153
* fix: Make groupIds option in search query dto by @paul-paliychuk in https://github.com/getzep/graphiti/pull/154


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.4...v0.3.5

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.5)

---

## v0.3.4: v0.3.4 - Community nodes fixes, group_id crud, llm client updates
**Published:** 2024-09-23

## What's Changed
* Add group_id CRUD endpoints and option store content bool by @prasmussen15 in https://github.com/getzep/graphiti/pull/130
* feat: add OpenAI configuration options to Settings and update LLM client setup by @paul-paliychuk in https://github.com/getzep/graphiti/pull/126
* Update README.md with graphiti logo by @danielchalef in https://github.com/getzep/graphiti/pull/131
* Handle JSONDecodeError in is_server_or_retry_error function by @danielchalef in https://github.com/getzep/graphiti/pull/133
* feat: Fix bug in dedupe_node_list function by @danielchalef in https://github.com/getzep/graphiti/pull/137
* feat: Refactor OpenAIClient initialization and add client parameter by @danielchalef in https://github.com/getzep/graphiti/pull/140
* chore: Update DEFAULT_MAX_TOKENS to 16384 in config.py by @danielchalef in https://github.com/getzep/graphiti/pull/138
* Add instructions to set up integration testing to contributor docs by @kylediaz in https://github.com/getzep/graphiti/pull/135
* feat: Add delete group endpoint by @paul-paliychuk in https://github.com/getzep/graphiti/pull/132
* Override default max tokens for Anthropic and Groq clients by @danielchalef in https://github.com/getzep/graphiti/pull/143
* add py.typed by @danielchalef in https://github.com/getzep/graphiti/pull/141
* limit community building concurrency by @danielchalef in https://github.com/getzep/graphiti/pull/142
* feat: add FastAPI lifespan and healthcheck endpoint by @paul-paliychuk in https://github.com/getzep/graphiti/pull/144
* In memory label propagation community detection by @prasmussen15 in https://github.com/getzep/graphiti/pull/136

## New Contributors
* @kylediaz made their first contribution in https://github.com/getzep/graphiti/pull/135

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.3...v0.3.4

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.4)

---

## v0.3.3: v0.3.3 - Community nodes updates, uuid format update and dep maintenance
**Published:** 2024-09-18

## What's Changed
* Add community update by @prasmussen15 in https://github.com/getzep/graphiti/pull/121
* chore(deps-dev): Bump langchain-openai from 0.1.23 to 0.1.25 by @dependabot in https://github.com/getzep/graphiti/pull/117
* chore(deps): Bump openai from 1.44.0 to 1.45.1 by @dependabot in https://github.com/getzep/graphiti/pull/116
* chore(deps-dev): Bump ruff from 0.6.4 to 0.6.5 by @dependabot in https://github.com/getzep/graphiti/pull/115
* chore(deps-dev): Bump langsmith from 0.1.116 to 0.1.121 by @dependabot in https://github.com/getzep/graphiti/pull/114
* fix: update UUID generation and message handling by @paul-paliychuk in https://github.com/getzep/graphiti/pull/123
* chore(deps-dev): Bump pytest from 8.3.2 to 8.3.3 by @dependabot in https://github.com/getzep/graphiti/pull/113
* Mentions reranker by @prasmussen15 in https://github.com/getzep/graphiti/pull/124


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.2...v0.3.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.3)

---

## v0.3.2: v0.3.2 - Get Node by uuid(s) fix
**Published:** 2024-09-17

## What's Changed
* fix: Syntax error on node crud by @paul-paliychuk in https://github.com/getzep/graphiti/pull/119


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.1...v0.3.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.2)

---

## v0.3.1: v0.3.1 - Search refactor, community search
**Published:** 2024-09-16

## What's Changed
* Search refactor + Community search by @prasmussen15 in https://github.com/getzep/graphiti/pull/111
* Fix groupless search by @paul-paliychuk in https://github.com/getzep/graphiti/pull/118


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.3.0...v0.3.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.1)

---

## v0.3.0: v0.3.0 - Community Nodes, Docker Container, Performance Improvements & Bug Fixes
**Published:** 2024-09-13

## What's Changed
* chore: Update service readme by @paul-paliychuk in https://github.com/getzep/graphiti/pull/93
* Loosen numpy dependency to numpy>=1.0.0 by @danielchalef in https://github.com/getzep/graphiti/pull/94
* chore(deps-dev): Bump langsmith from 0.1.115 to 0.1.116 by @dependabot in https://github.com/getzep/graphiti/pull/99
* chore(deps): Bump pydantic from 2.9.0 to 2.9.1 by @dependabot in https://github.com/getzep/graphiti/pull/98
* chore(deps): Bump openai from 1.43.1 to 1.44.0 by @dependabot in https://github.com/getzep/graphiti/pull/97
* chore(deps-dev): Bump groq from 0.10.0 to 0.11.0 by @dependabot in https://github.com/getzep/graphiti/pull/96
* chore(deps-dev): Bump langgraph from 0.2.18 to 0.2.19 by @dependabot in https://github.com/getzep/graphiti/pull/95
* Fix missing default None for add_episode_bulk by @danielchalef in https://github.com/getzep/graphiti/pull/101
* feat(graph-service): add entity node handling and update Docker configurations by @paul-paliychuk in https://github.com/getzep/graphiti/pull/100
* Fix llm client retry by @danielchalef in https://github.com/getzep/graphiti/pull/102
* Add py.typed file by @danielchalef in https://github.com/getzep/graphiti/pull/105
* add extract nodes from text prompt by @prasmussen15 in https://github.com/getzep/graphiti/pull/106
* Community nodes by @prasmussen15 in https://github.com/getzep/graphiti/pull/103
* feat: add error handling for missing nodes and edges, introduce new API endpoints, and update ZepGraphiti class by @paul-paliychuk in https://github.com/getzep/graphiti/pull/104
* Improve node distance reranker speed by @prasmussen15 in https://github.com/getzep/graphiti/pull/107
* Version bump by @paul-paliychuk in https://github.com/getzep/graphiti/pull/108


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.2.3...v0.3.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.3.0)

---

## v0.2.3: v0.2.3 - Add support for group ids when ingesting and retrieving context from graphiti
**Published:** 2024-09-06

## What's Changed
* Add Fastapi graph service by @paul-paliychuk in https://github.com/getzep/graphiti/pull/88
* Fix manual image release workflow by @paul-paliychuk in https://github.com/getzep/graphiti/pull/90
* Fix manual image release workflow by @paul-paliychuk in https://github.com/getzep/graphiti/pull/91
* Add group ids by @prasmussen15 in https://github.com/getzep/graphiti/pull/89
* feat: Add group id support to service by @paul-paliychuk in https://github.com/getzep/graphiti/pull/92


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.2.2...v0.2.3

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.2.3)

---

## v0.2.2: v0.2.2 - Fix name embeddings bug
**Published:** 2024-09-05

## What's Changed
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/84
* Add episode refactor by @prasmussen15 in https://github.com/getzep/graphiti/pull/85
* fix clearing name embeddings bug by @prasmussen15 in https://github.com/getzep/graphiti/pull/87


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.2.1...v0.2.2

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.2.2)

---

## v0.2.1: v0.2.1 - Search refactor + enhancements
**Published:** 2024-09-04

## What's Changed
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/80
* search update by @prasmussen15 in https://github.com/getzep/graphiti/pull/81


**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.2.0...v0.2.1

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.2.1)

---

## v0.2.0: v0.2.0 - Retrieval and Ingestion optimizations
**Published:** 2024-09-03

## What's Changed
* Update README.md - init by @danielchalef in https://github.com/getzep/graphiti/pull/64
* Update cla.yml - name of ellipsis bot by @danielchalef in https://github.com/getzep/graphiti/pull/65
* Update README.md - CRUD done by @danielchalef in https://github.com/getzep/graphiti/pull/66
* add bulk temporal extraction and improve bulk quality and performance by @prasmussen15 in https://github.com/getzep/graphiti/pull/67
* chore(deps-dev): Bump pytest-asyncio from 0.23.8 to 0.24.0 by @dependabot in https://github.com/getzep/graphiti/pull/43
* Update README.md messaging by @danielchalef in https://github.com/getzep/graphiti/pull/69
* Update README.md - fix image url by @danielchalef in https://github.com/getzep/graphiti/pull/70
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/71
* chore(deps-dev): Bump jupyterlab from 4.2.4 to 4.2.5 in the pip group by @dependabot in https://github.com/getzep/graphiti/pull/68
* Node Distance Reranker: Limit max hops (and cleanup prints) by @danielchalef in https://github.com/getzep/graphiti/pull/72
* Feat/langgraph-example by @danielchalef in https://github.com/getzep/graphiti/pull/73
* README.md fixes by @danielchalef in https://github.com/getzep/graphiti/pull/74
* Speed up add episode by @prasmussen15 in https://github.com/getzep/graphiti/pull/77
* chore(deps-dev): Bump groq from 0.9.0 to 0.10.0 by @dependabot in https://github.com/getzep/graphiti/pull/76
* chore(deps-dev): Bump langgraph from 0.2.15 to 0.2.16 by @dependabot in https://github.com/getzep/graphiti/pull/75
* Update image URL in README.md by @danielchalef in https://github.com/getzep/graphiti/pull/78
* chore: Version bump by @paul-paliychuk in https://github.com/getzep/graphiti/pull/79

## New Contributors
* @dependabot made their first contribution in https://github.com/getzep/graphiti/pull/43

**Full Changelog**: https://github.com/getzep/graphiti/compare/v0.1.0...v0.2.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.2.0)

---

## v0.1.0: v0.1.0 - Initial release of graphiti 
**Published:** 2024-08-27

## What's Changed
* chore: Add readme, gitignore and poetry files by @paul-paliychuk in https://github.com/getzep/graphiti/pull/1
* chore: Initial draft of stubs by @paul-paliychuk in https://github.com/getzep/graphiti/pull/2
* renaming and add indices by @prasmussen15 in https://github.com/getzep/graphiti/pull/3
* Refactor maintenance structure, add prompt library by @paul-paliychuk in https://github.com/getzep/graphiti/pull/4
* Cleanup maintenance utilities + add podcast runner by @paul-paliychuk in https://github.com/getzep/graphiti/pull/5
* Update Maintenance LLM Queries and Partial Schema Retrieval by @prasmussen15 in https://github.com/getzep/graphiti/pull/6
* fix: Address graph disconnect by @paul-paliychuk in https://github.com/getzep/graphiti/pull/7
* feat: Initial version of temporal invalidation + tests by @paul-paliychuk in https://github.com/getzep/graphiti/pull/8
* Create Bulk Add Episode for faster processing by @prasmussen15 in https://github.com/getzep/graphiti/pull/9
* chore: Add development environment to the action by @paul-paliychuk in https://github.com/getzep/graphiti/pull/12
* Create dependabot.yml by @danielchalef in https://github.com/getzep/graphiti/pull/11
* Create SECURITY.md by @danielchalef in https://github.com/getzep/graphiti/pull/10
* move podcast to examples by @danielchalef in https://github.com/getzep/graphiti/pull/15
* search updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/14
* format and linting by @danielchalef in https://github.com/getzep/graphiti/pull/18
* ruff action by @danielchalef in https://github.com/getzep/graphiti/pull/17
* rm podcast by @danielchalef in https://github.com/getzep/graphiti/pull/16
* search updates by @prasmussen15 in https://github.com/getzep/graphiti/pull/19
* Invalidation updates && improvements by @paul-paliychuk in https://github.com/getzep/graphiti/pull/20
* chore: enable mypy; actions cleanup by @danielchalef in https://github.com/getzep/graphiti/pull/21
* depot + cleanup by @danielchalef in https://github.com/getzep/graphiti/pull/22
* Fix temporal invalidation unit tests by @paul-paliychuk in https://github.com/getzep/graphiti/pull/23
* fix constraints by @prasmussen15 in https://github.com/getzep/graphiti/pull/25
* chore: Fix Typing Issues by @danielchalef in https://github.com/getzep/graphiti/pull/27
* improve deduping issue by @prasmussen15 in https://github.com/getzep/graphiti/pull/28
* Add a LICENSE file containing the Apache v2 license by @danielchalef in https://github.com/getzep/graphiti/pull/29
* feat: Add real world dates extraction by @paul-paliychuk in https://github.com/getzep/graphiti/pull/26
* Add Apache License 2.0 boilerplate to all Python files by @danielchalef in https://github.com/getzep/graphiti/pull/30
* feat: Add CLA Assistant workflow and CONTRIBUTING guidelines by @danielchalef in https://github.com/getzep/graphiti/pull/32
* chore: Update the context for date extraction + bug fixes by @paul-paliychuk in https://github.com/getzep/graphiti/pull/31
* Update CONTRIBUTING.md to reflect Python 3.10+ requirement by @danielchalef in https://github.com/getzep/graphiti/pull/33
* dedupe fixes by @prasmussen15 in https://github.com/getzep/graphiti/pull/35
* chore: Fix packaging by @danielchalef in https://github.com/getzep/graphiti/pull/38
* Controlled example by @paul-paliychuk in https://github.com/getzep/graphiti/pull/37
* chore: Add comments to graphiti methods by @paul-paliychuk in https://github.com/getzep/graphiti/pull/40
* implement diskcache by @danielchalef in https://github.com/getzep/graphiti/pull/39
* Implement retry for LLMClient by @danielchalef in https://github.com/getzep/graphiti/pull/44
* Search node centering by @prasmussen15 in https://github.com/getzep/graphiti/pull/45
* Add text episode type by @danielchalef in https://github.com/getzep/graphiti/pull/46
* Update cla.yml for dependabot[bot] whitelist by @danielchalef in https://github.com/getzep/graphiti/pull/47
* Update search method to return EntityEdge objects by @danielchalef in https://github.com/getzep/graphiti/pull/48
* Update cla.yml to add ellipsisdev[bot] to whitelist by @danielchalef in https://github.com/getzep/graphiti/pull/50
* Add get_nodes_by_query method to Graphiti class by @danielchalef in https://github.com/getzep/graphiti/pull/49
* README wip by @danielchalef in https://github.com/getzep/graphiti/pull/42
* feat: Add graphiti demo slides to README.md by @danielchalef in https://github.com/getzep/graphiti/pull/52
* Chore/add-intro-gif v2 by @danielchalef in https://github.com/getzep/graphiti/pull/54
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/55
* Update status and roadmap section by @paul-paliychuk in https://github.com/getzep/graphiti/pull/53
* Update README.md w/ spacing by @danielchalef in https://github.com/getzep/graphiti/pull/56
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/57
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/58
* Update README.md by @danielchalef in https://github.com/getzep/graphiti/pull/59
* Update README.md - docs to docs site by @danielchalef in https://github.com/getzep/graphiti/pull/60
* chore: Move anthropic to dev deps, remove anthropic and groq clients from __init__ by @paul-paliychuk in https://github.com/getzep/graphiti/pull/61
* feat: Add release workflow by @paul-paliychuk in https://github.com/getzep/graphiti/pull/62
* Add Missing Node and edge CRUD by @prasmussen15 in https://github.com/getzep/graphiti/pull/51
* chore: Version bump by @paul-paliychuk in https://github.com/getzep/graphiti/pull/63

## New Contributors
* @paul-paliychuk made their first contribution in https://github.com/getzep/graphiti/pull/1
* @prasmussen15 made their first contribution in https://github.com/getzep/graphiti/pull/3

**Full Changelog**: https://github.com/getzep/graphiti/commits/v0.1.0

[View on GitHub](https://github.com/getzep/graphiti/releases/tag/v0.1.0)

---

