---
status: stage-5-collateral
category: meta-interface
chat_4_stage: "Stage 5"
status_note: "变更影响表 — 接口改动时影响范围 / 测试 / 文档的 cross-link 表。"
last_reviewed: 2026-05-07
parent_doc: "INDEX.md"
ai_priority: medium
ai_audience: both
sources:
  - "../architecture/adr_protocol_upgrade_and_interface_refinement_background_20260504.md §5.5"
---

# Change Impact Table（变更影响表）

> 改某个接口时，必须回查的 影响范围 / 测试 / 文档 清单。

---

## §1 wire 接口变更影响

| 改 | 影响 | 必跑测试 | 必更文档 |
|:--|:--|:--|:--|
| EcpEventType enum 增减 | wire/ecp_event_v1 + cs_parity 4/4 + 13 event_type 注册表 | `test_cs_parity.py` + 新 event_type freeze test | wire/ecp_event_v1.md §3 + topic_matrix.md |
| EcpStateDto 字段 | wire/ecp_state_v1 + cs_parity（topic 常量）+ ecp_state_ingest | `test_cs_parity.py` + `test_ecp_state_ingest.py` | wire/ecp_state_v1.md + in_process/selection_c_state_context.md |
| EcpAck 字段 | wire/ecp_ack_v1 + cs_parity + RPC return value | `test_ecp.py round-trip` | wire/ecp_ack_v1.md + 各 brain tool wrapper |
| RPC method 增减 | wire/livekit_rpc_v1 + Unity ParrotRpcHandler + brain tool | (新 freeze test) | wire/livekit_rpc_v1.md + capability/brain_tools_inventory.md |
| RefBinding 字段 | wire/ref_binding_v1 + observer/{bbox,focus} + refs registry | `test_refs.py` | wire/ref_binding_v1.md + capability/ref_kinds_inventory.md + in_process/refs_hint_writer.md |
| NodeKind / EdgeKind 增减 | wire/node_edge_kind_v1 + L2-B graph + freeze test | `test_node_kind_enum_six_values` + cs_parity | wire/node_edge_kind_v1.md + capability/* + 多个 in_process/* |
| Photo 双通道 | wire/photo_double_channel_v1 + Unity PhotoController + Brain photo_upload_server | `test_observer_photo` + `test_photo_upload_server` | wire/photo_double_channel_v1.md + cross_process/http_upload_photo.md |
| topic 常量 | wire/topic_matrix + cs_parity | `test_cs_parity` | wire/topic_matrix.md + 各 wire/* §通道 |

---

## §2 cross-process 接口变更影响

| 改 | 影响 | 必跑测试 | 必更文档 |
|:--|:--|:--|:--|
| HTTP `/upload/photo` schema | photo_upload_server + Unity PhotoController | `test_photo_upload_server` | cross_process/http_upload_photo.md |
| Redis Pub/Sub channel 增减 | 各 publisher / subscriber | (无统一 freeze test) | cross_process/redis_pub_sub.md |
| Redis Stream payload | scheduler/nodes + nanobot consumer + dispatch_task | `test_streams.py` | cross_process/redis_stream.md |
| Redis HASH key | 各 producer / consumer | `test_idle_archive_trigger.py` (heartbeat) | cross_process/redis_hash.md |
| Graphiti API 用法 | memory/graphiti_client + tools | `test_graphiti_*.py` | cross_process/graphiti_v1.md |

---

## §3 in-process 接口变更影响

| 改 | 影响 | 必跑测试 | 必更文档 |
|:--|:--|:--|:--|
| attach_helpers boot 序 | 多 module（agent.py 调用顺序）| `test_attach_helpers.py` | in_process/attach_helpers.md |
| Observer 增减 | event_bus + EcpEventType subscription | `test_observer_*.py` | in_process/observer_event_bus.md + capability/triggers_inventory.md |
| TriggerOutcome 通道增减（V3）| TriggerRunner._process_result + 7+ 下游 | `test_trigger_outcome_v2.py` | in_process/dsg_trigger_outcome_v2.md + capability/triggers_inventory.md |
| IngestRunner factory | _SOURCE_META_FACTORIES + ADR-L1.5-001 | `test_l2b_node_source_dispatch.py` 11/11 | in_process/ingest_runner.md + ADR-L1.5-001 |
| IntentWorkspaceBackend 加 | register_intent_workspace_backend | `test_intent_workspace_lifecycle.py` | in_process/intent_workspace_backend.md + capability/staged_ref_kinds.md |
| BucketKind / AdmissionPolicy 改 | L1.5 Pool + commit_observation | `test_l1_5_*.py` | in_process/pool_admission_policy.md + capability/bucket_kinds_inventory.md |
| Attention Strategy 改 | threshold + decay + mechanism + fold | `test_attention_*.py` + L13 边界守 | in_process/attention_strategy.md |
| selection-C state context | 3 tool wrapper + cognitive_state_tracker | `test_tools_state_header.py` | in_process/selection_c_state_context.md + wire/ecp_state_v1.md |
| identify_object budget | _budget + L0/L1 search | `test_identify_object.py` | in_process/identify_object_budget.md |

---

## §4 capability 接口变更影响

| 改 | 影响 | 必跑测试 | 必更文档 |
|:--|:--|:--|:--|
| 加 brain tool | brain.tools/__init__ ALL_TOOLS + LLM system prompt | `test_tools_*.py` | capability/brain_tools_inventory.md + parrot_behavior_rules §4.3 |
| ParrotAnimation enum 改 | wire-locked + RESERVED_PARROT_CAPABILITY_IDS + animate VALID_ANIMATIONS | `test_cs_parity` + `test_model_manifest` | capability/parrot_actions_v1.md + capability/model_manifest_v1.md + 多个 wire/* |
| BehaviorMode flags | wire-locked + set_mode tool + mode_watcher + soul.py | `test_cs_parity` | capability/parrot_actions_v1.md + capability/brain_tools_inventory.md |
| ModelManifest schema | wire/ecp_command_meta_v1 + Unity ModelDriver + AI CLI | `test_model_manifest.py` + `test_asset_to_manifest.py` | capability/model_manifest_v1.md + wire/ecp_command_meta_v1.md |

---

## §5 跨层影响示例

### §5.1 加新 EcpEventType（影响最广）

```
1. Python ecp_event.py 加 enum + payload schema
2. C# EcpEventDto.cs / EcpEventTypeNames 同步（cs_parity）
3. wire/ecp_event_v1.md §3 注册表 + topic_matrix.md（如新 topic）
4. 加 freeze test（cs_parity 风格）
5. 加 producer / consumer（observer or 各模块）
6. cross-chat-registry §8 历史区追加（如 supersede / deprecate 旧 type）
```

### §5.2 加新 NodeKind（影响最广 + 必新 ADR）

```
1. Python l2b_types.py 加 enum
2. C# 同步（cs_parity）+ 影响 wire/node_edge_kind_v1.md §1
3. test_node_kind_enum_six_values → 升 seven_values
4. observer/* 处理新 kind
5. graphiti add_episode entity_types 同步
6. 必走新 ADR + supersedes ADR-L1.5-001 / Phase 4 §8 L1（如果触动 enum 锁）
```

---

## §6 cross-link

- schema_evolution：[`schema_evolution.md`](schema_evolution.md)
- deprecation：[`deprecation.md`](deprecation.md)
- upgrade_roadmap：[`upgrade_roadmap.md`](upgrade_roadmap.md)
- methodology：[`methodology.md`](methodology.md)
- INDEX：[`INDEX.md`](INDEX.md)
