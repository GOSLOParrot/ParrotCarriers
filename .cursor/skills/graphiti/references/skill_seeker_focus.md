# Skill Seeker distillation focus (injected for Gemini enhance)

> **Repo:** getzep/graphiti | **Pin:** v0.28.2

Prioritize accurate coverage of these English symbols and API names when rewriting SKILL.md:

## Core API
- `Graphiti` (main class)
- `GraphitiConfig`
- `add_episode`
- `EpisodeType` (enum: `text`, `json`, `message_list`)
- `search` (unified search method)
- `SearchConfig`
- `retrieve_episodes`
- `close`

## Node & Edge Types
- `EntityNode`
- `EpisodicNode`
- `CommunityNode`
- `EntityEdge`
- `EpisodicEdge`
- `CommunityEdge`

## Custom Ontology (Pydantic)
- `custom_entity_types`
- `custom_edge_types`
- Pydantic model definition for typed entities

## Graph Driver Backends
- `GraphDriver`
- `Neo4jDriver`
- `FalkorDBDriver`
- `KuzuDriver`
- `NeptuneDriver` / `NeptuneAnalyticsDriver`

## Search & Retrieval
- `hybrid_search`
- `search_type`
- `group_id` (partition / multi-tenant)
- `build_communities` (Leiden clustering)
- `build_indices`
- `edge_weight`
- `temporal` (validity windows on facts)

## MCP Server
- `mcp_server` directory
- Episode management via MCP
- Entity search via MCP

## Integration Patterns
- LangGraph + Graphiti agent
- REST API server (FastAPI)
- Docker deployment with Neo4j

## What to focus on for ParrotCarriers:
1. `add_episode` lifecycle — how conversation turns become graph nodes
2. `custom_entity_types` — how to define ParrotCarriers-specific entity types
3. `group_id` — multi-partition strategy for user/session isolation
4. `search` with `SearchConfig` — hybrid retrieval for Brain context injection
5. Temporal validity — how facts get superseded over time
6. Self-hosting with FalkorDB (lighter than Neo4j for our 2C8G constraint)
