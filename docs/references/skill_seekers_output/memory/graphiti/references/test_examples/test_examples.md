# Test Example Extraction Report

**Total Examples**: 123  
**High Value Examples** (confidence > 0.7): 123  
**Average Complexity**: 0.28  

## Examples by Category

- **config**: 3
- **instantiation**: 88
- **method_call**: 12
- **workflow**: 20

## Examples by Language

- **Python**: 123

## Extracted Examples

### test_get_usage_returns_copy

**Category**: workflow  
**Description**: Workflow: Test that get_usage returns a copy, not the internal dict.  
**Expected**: assert usage2['test'].total_input_tokens == 100  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that get_usage returns a copy, not the internal dict.'
tracker = TokenUsageTracker()
tracker.record('test', 100, 50)
usage1 = tracker.get_usage()
usage1['test'].total_input_tokens = 9999
usage2 = tracker.get_usage()
assert usage2['test'].total_input_tokens == 100
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:128*

### test_thread_safety

**Category**: workflow  
**Description**: Workflow: Test that concurrent access from multiple threads is safe.  
**Expected**: assert total.output_tokens == expected_output  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that concurrent access from multiple threads is safe.'
tracker = TokenUsageTracker()
num_threads = 10
calls_per_thread = 100

def record_tokens(thread_id):
    for _ in range(calls_per_thread):
        tracker.record(f'prompt_{thread_id}', 10, 5)
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(record_tokens, i) for i in range(num_threads)]
    for f in futures:
        f.result()
usage = tracker.get_usage()
assert len(usage) == num_threads
total = tracker.get_total_usage()
expected_input = num_threads * calls_per_thread * 10
expected_output = num_threads * calls_per_thread * 5
assert total.input_tokens == expected_input
assert total.output_tokens == expected_output
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:172*

### test_concurrent_same_prompt

**Category**: workflow  
**Description**: Workflow: Test concurrent access to the same prompt name.  
**Expected**: assert usage['shared_prompt'].total_output_tokens == num_threads * calls_per_thread * 5  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test concurrent access to the same prompt name.'
tracker = TokenUsageTracker()
num_threads = 10
calls_per_thread = 100

def record_tokens():
    for _ in range(calls_per_thread):
        tracker.record('shared_prompt', 10, 5)
with ThreadPoolExecutor(max_workers=num_threads) as executor:
    futures = [executor.submit(record_tokens) for _ in range(num_threads)]
    for f in futures:
        f.result()
usage = tracker.get_usage()
assert usage['shared_prompt'].call_count == num_threads * calls_per_thread
assert usage['shared_prompt'].total_input_tokens == num_threads * calls_per_thread * 10
assert usage['shared_prompt'].total_output_tokens == num_threads * calls_per_thread * 5
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:196*

### test_convert_datetime_list_and_tuple

**Category**: workflow  
**Description**: Workflow: Test datetime conversion in lists and tuples.  
**Expected**: assert result_tuple[1] == test_datetime.isoformat()  
**Confidence**: 0.90  
**Tags**: unittest, workflow, integration  

```python
'Test datetime conversion in lists and tuples.'
from graphiti_core.driver.falkordb_driver import convert_datetimes_to_strings
test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
input_list = ['test', test_datetime, ['nested', test_datetime]]
result_list = convert_datetimes_to_strings(input_list)
assert result_list[0] == 'test'
assert result_list[1] == test_datetime.isoformat()
assert result_list[2][1] == test_datetime.isoformat()
input_tuple = ('test', test_datetime)
result_tuple = convert_datetimes_to_strings(input_tuple)
assert isinstance(result_tuple, tuple)
assert result_tuple[0] == 'test'
assert result_tuple[1] == test_datetime.isoformat()
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:325*

### test_edge_type_signatures_map_preserves_multiple_signatures

**Category**: workflow  
**Description**: Workflow: Test that edge types used across multiple node type pairs preserve all signatures.

This tests the fix for the bug where dict comprehension would overwrite
previous signatures when the same edge type appeared in multiple node pairs.  
**Expected**: assert ('Entity', 'City') in located_signatures  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
'Test that edge types used across multiple node type pairs preserve all signatures.\n\n    This tests the fix for the bug where dict comprehension would overwrite\n    previous signatures when the same edge type appeared in multiple node pairs.\n    '
edge_type_map: dict[tuple[str, str], list[str]] = {('Person', 'Person'): ['InterpersonalRelationship'], ('Person', 'Entity'): ['InterpersonalRelationship'], ('Person', 'City'): ['LocatedIn'], ('Entity', 'City'): ['LocatedIn']}
edge_types: dict[str, type[BaseModel]] = {'InterpersonalRelationship': InterpersonalRelationship, 'LocatedIn': LocatedIn}
edge_type_signatures_map: dict[str, list[tuple[str, str]]] = {}
for signature, edge_type_names in edge_type_map.items():
    for edge_type in edge_type_names:
        if edge_type not in edge_type_signatures_map:
            edge_type_signatures_map[edge_type] = []
        edge_type_signatures_map[edge_type].append(signature)
assert 'InterpersonalRelationship' in edge_type_signatures_map
interpersonal_signatures = edge_type_signatures_map['InterpersonalRelationship']
assert len(interpersonal_signatures) == 2
assert ('Person', 'Person') in interpersonal_signatures
assert ('Person', 'Entity') in interpersonal_signatures
assert 'LocatedIn' in edge_type_signatures_map
located_signatures = edge_type_signatures_map['LocatedIn']
assert len(located_signatures) == 2
assert ('Person', 'City') in located_signatures
assert ('Entity', 'City') in located_signatures
edge_types_context = [{'fact_type_name': type_name, 'fact_type_signatures': edge_type_signatures_map.get(type_name, [('Entity', 'Entity')]), 'fact_type_description': type_model.__doc__} for type_name, type_model in edge_types.items()]
for ctx in edge_types_context:
    assert 'fact_type_signatures' in ctx
    assert isinstance(ctx['fact_type_signatures'], list)
    assert len(ctx['fact_type_signatures']) == 2
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_edge_operations.py:460*

### test_falkordb_fulltext_query_rejects_invalid_group_ids

**Category**: workflow  
**Description**: Workflow: test falkordb fulltext query rejects invalid group ids  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
from graphiti_core.driver.falkordb_driver import FalkorDriver
driver = MagicMock(spec=FalkorDriver)
driver.sanitize.return_value = 'test'
with pytest.raises(GroupIdValidationError, match='must contain only alphanumeric'):
    FalkorDriver.build_fulltext_query(driver, 'test', ['bad"group'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:62*

### test_array_splits_at_element_boundaries

**Category**: workflow  
**Description**: Workflow: test array splits at element boundaries  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
data = [{'id': i, 'data': 'x' * 100} for i in range(20)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=100, overlap_tokens=20)
for chunk in chunks:
    parsed = json.loads(chunk)
    assert isinstance(parsed, list)
    for item in parsed:
        assert 'id' in item
        assert 'data' in item
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:64*

### test_array_preserves_all_elements

**Category**: workflow  
**Description**: Workflow: test array preserves all elements  
**Expected**: assert seen_ids == set(range(10))  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
data = [{'id': i} for i in range(10)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
seen_ids = set()
for chunk in chunks:
    parsed = json.loads(chunk)
    for item in parsed:
        seen_ids.add(item['id'])
assert seen_ids == set(range(10))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:81*

### test_object_splits_at_key_boundaries

**Category**: workflow  
**Description**: Workflow: test object splits at key boundaries  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
data = {f'key_{i}': 'x' * 100 for i in range(20)}
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=100, overlap_tokens=20)
for chunk in chunks:
    parsed = json.loads(chunk)
    assert isinstance(parsed, dict)
    for key in parsed:
        assert key.startswith('key_')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:110*

### test_object_preserves_all_keys

**Category**: workflow  
**Description**: Workflow: test object preserves all keys  
**Expected**: assert seen_keys == expected_keys  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
data = {f'key_{i}': f'value_{i}' for i in range(10)}
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=50, overlap_tokens=10)
seen_keys = set()
for chunk in chunks:
    parsed = json.loads(chunk)
    seen_keys.update(parsed.keys())
expected_keys = {f'key_{i}' for i in range(10)}
assert seen_keys == expected_keys
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:125*

### test_preserves_text_completeness

**Category**: workflow  
**Description**: Workflow: test preserves text completeness  
**Expected**: assert all_words <= found_words  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
text = 'Alpha beta gamma delta epsilon zeta eta theta.'
chunks = chunk_text_content(text, chunk_size_tokens=10, overlap_tokens=2)
all_words = set(text.replace('.', '').split())
found_words = set()
for chunk in chunks:
    found_words.update(chunk.replace('.', '').split())
assert all_words <= found_words
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:189*

### test_preserves_speaker_message_format

**Category**: workflow  
**Description**: Workflow: test preserves speaker message format  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
messages = [f'Speaker{i}: This is message number {i}.' for i in range(10)]
content = '\n'.join(messages)
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
for chunk in chunks:
    lines = [line for line in chunk.split('\n') if line.strip()]
    for line in lines:
        assert ':' in line
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:209*

### test_json_message_array_format

**Category**: workflow  
**Description**: Workflow: test json message array format  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
messages = [{'role': 'user', 'content': f'Message {i}'} for i in range(10)]
content = json.dumps(messages)
chunks = chunk_message_content(content, chunk_size_tokens=50, overlap_tokens=10)
for chunk in chunks:
    parsed = json.loads(chunk)
    assert isinstance(parsed, list)
    for msg in parsed:
        assert 'role' in msg
        assert 'content' in msg
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:222*

### test_json_array_overlap_captures_boundary_elements

**Category**: workflow  
**Description**: Workflow: test json array overlap captures boundary elements  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
data = [{'id': i, 'name': f'Entity {i}'} for i in range(10)]
content = json.dumps(data)
chunks = chunk_json_content(content, chunk_size_tokens=80, overlap_tokens=30)
if len(chunks) > 1:
    for i in range(len(chunks) - 1):
        current = json.loads(chunks[i])
        next_chunk = json.loads(chunks[i + 1])
        current_ids = {item['id'] for item in current}
        next_ids = {item['id'] for item in next_chunk}
        _ = current_ids & next_ids
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:238*

### test_text_overlap_captures_boundary_text

**Category**: workflow  
**Description**: Workflow: test text overlap captures boundary text  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
paragraphs = [f'Paragraph {i} with some content here.' for i in range(10)]
text = '\n\n'.join(paragraphs)
chunks = chunk_text_content(text, chunk_size_tokens=50, overlap_tokens=20)
if len(chunks) > 1:
    for i in range(len(chunks) - 1):
        current_words = set(chunks[i].split())
        next_words = set(chunks[i + 1].split())
        overlap = current_words & next_words
        assert len(overlap) > 0
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:260*

### test_entity_rich_text_detected

**Category**: workflow  
**Description**: Workflow: Text with many proper nouns should be detected as dense.  
**Expected**: assert _text_likely_dense(text, tokens)  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: monkeypatch

'Text with many proper nouns should be detected as dense.'
from graphiti_core.utils import content_chunking
monkeypatch.setattr(content_chunking, 'CHUNK_DENSITY_THRESHOLD', 0.01)
text = 'Alice met Bob at Acme Corp. Then Carol and David joined them. '
text += 'Eve from Globex introduced Frank and Grace. '
text += 'Later Henry and Iris arrived from Initech. '
text = text * 10
tokens = estimate_tokens(text)
assert _text_likely_dense(text, tokens)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\test_content_chunking.py:416*

### test_hash_minhash_and_lsh

**Category**: workflow  
**Description**: Workflow: test hash minhash and lsh  
**Expected**: assert len(hashed) == len(shingles)  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
shingles = {'abc', 'bcd', 'cde'}
signature = _minhash_signature(shingles)
assert len(signature) == 32
bands = _lsh_bands(signature)
assert all((len(band) == 4 for band in bands))
hashed = {_hash_shingle(s, 0) for s in shingles}
assert len(hashed) == len(shingles)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:219*

### test_resolve_with_similarity_exact_match_updates_state

**Category**: workflow  
**Description**: Workflow: test resolve with similarity exact match updates state  
**Expected**: assert state.duplicate_pairs == [(extracted, candidate)]  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
candidate = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
extracted = EntityNode(name='Charlie Parker', group_id='group', labels=['Entity'])
indexes = _build_candidate_indexes([candidate])
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0].uuid == candidate.uuid
assert state.uuid_map[extracted.uuid] == candidate.uuid
assert state.unresolved_indices == []
assert state.duplicate_pairs == [(extracted, candidate)]
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:237*

### test_resolve_with_similarity_multiple_exact_matches_defers_to_llm

**Category**: workflow  
**Description**: Workflow: test resolve with similarity multiple exact matches defers to llm  
**Expected**: assert state.duplicate_pairs == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
candidate1 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
candidate2 = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
extracted = EntityNode(name='Johnny Appleseed', group_id='group', labels=['Entity'])
indexes = _build_candidate_indexes([candidate1, candidate2])
state = DedupResolutionState(resolved_nodes=[None], uuid_map={}, unresolved_indices=[])
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0] is None
assert state.unresolved_indices == [0]
assert state.duplicate_pairs == []
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:270*

### test_build_directed_uuid_map_chain

**Category**: workflow  
**Description**: Workflow: test build directed uuid map chain  
**Expected**: assert mapping['c'] == 'c'  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
mapping = bulk_utils._build_directed_uuid_map([('a', 'b'), ('b', 'c')])
assert mapping['a'] == 'c'
assert mapping['b'] == 'c'
assert mapping['c'] == 'c'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_bulk_utils.py:194*

### test_get_graph_with_name

**Category**: method_call  
**Description**: Test _get_graph with specific graph name.  
**Expected**: assert result is mock_graph  
**Confidence**: 0.85  
**Tags**: unittest, mock  

```python
self.mock_client.select_graph.assert_called_once_with('test_graph')
assert result is mock_graph
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:81*

### test_get_graph_with_none_defaults_to_default_database

**Category**: method_call  
**Description**: Test _get_graph with None defaults to default_db.  
**Expected**: assert result is mock_graph  
**Confidence**: 0.85  
**Tags**: unittest, mock  

```python
self.mock_client.select_graph.assert_called_once_with('default_db')
assert result is mock_graph
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:92*

### test_resolve_with_similarity_exact_match_updates_state

**Category**: method_call  
**Description**: test resolve with similarity exact match updates state  
**Expected**: assert state.resolved_nodes[0].uuid == candidate.uuid  
**Confidence**: 0.85  

```python
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0].uuid == candidate.uuid
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:244*

### test_resolve_with_similarity_low_entropy_defers_resolution

**Category**: method_call  
**Description**: test resolve with similarity low entropy defers resolution  
**Expected**: assert state.resolved_nodes[0] is None  
**Confidence**: 0.85  

```python
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0] is None
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:263*

### test_resolve_with_similarity_multiple_exact_matches_defers_to_llm

**Category**: method_call  
**Description**: test resolve with similarity multiple exact matches defers to llm  
**Expected**: assert state.resolved_nodes[0] is None  
**Confidence**: 0.85  

```python
_resolve_with_similarity([extracted], indexes, state)
assert state.resolved_nodes[0] is None
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:278*

### test_resolve_edge_pointers_updates_sources

**Category**: method_call  
**Description**: test resolve edge pointers updates sources  
**Expected**: assert edge.source_node_uuid == 'canonical'  
**Confidence**: 0.85  

```python
bulk_utils.resolve_edge_pointers([edge], {'alias': 'canonical'})
assert edge.source_node_uuid == 'canonical'
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_bulk_utils.py:229*

### test_set_and_get

**Category**: method_call  
**Description**: Test basic set and get round-trip.  
**Expected**: assert cache.get('key1') == value  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache.set('key1', value)
assert cache.get('key1') == value
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:40*

### test_set_overwrites_existing

**Category**: method_call  
**Description**: Test that setting the same key overwrites the previous value.  
**Expected**: assert cache.get('key1') == {'version': 2}  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache.set('key1', {'version': 2})
assert cache.get('key1') == {'version': 2}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:46*

### test_multiple_keys

**Category**: method_call  
**Description**: Test storing and retrieving multiple distinct keys.  
**Expected**: assert cache.get('a') == {'val': 1}  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache.set('c', {'val': 3})
assert cache.get('a') == {'val': 1}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:53*

### test_complex_nested_value

**Category**: method_call  
**Description**: Test that complex nested JSON structures survive round-trip.  
**Expected**: assert cache.get('complex') == value  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache.set('complex', value)
assert cache.get('complex') == value
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:66*

### test_non_serializable_value_is_skipped

**Category**: method_call  
**Description**: Test that non-JSON-serializable values are silently skipped.  
**Expected**: assert cache.get('bad') is None  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache.set('bad', {'func': lambda x: x})
assert cache.get('bad') is None
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:71*

### test_corrupted_entry_returns_none

**Category**: method_call  
**Description**: Test that a corrupted (non-JSON) cache entry returns None.  
**Expected**: assert cache.get('corrupt') is None  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: cache

cache._conn.commit()
assert cache.get('corrupt') is None
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:81*

### test_truncate_at_sentence_short_text

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test that short text is returned unchanged.  
**Expected**: assert result == text  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:23*

### test_truncate_at_sentence_exact_length

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test text at exactly max_chars.  
**Expected**: assert result == text  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 100)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:36*

### test_truncate_at_sentence_with_period

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test truncation at sentence boundary with period.  
**Expected**: assert result == 'First sentence. Second sentence.'  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 40)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:43*

### test_truncate_at_sentence_with_question

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test truncation at sentence boundary with question mark.  
**Expected**: assert result == 'What is this? This is a test.'  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 30)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:51*

### test_truncate_at_sentence_with_exclamation

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test truncation at sentence boundary with exclamation mark.  
**Expected**: assert result == 'Hello world! This is exciting.'  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 30)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:59*

### test_truncate_at_sentence_no_boundary

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test truncation when no sentence boundary exists before max_chars.  
**Expected**: assert len(result) <= 30  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 30)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:67*

### test_truncate_at_sentence_multiple_periods

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test with multiple sentence endings.  
**Expected**: assert result == 'A. B. C.'  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 10)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:75*

### test_truncate_at_sentence_strips_trailing_whitespace

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test that trailing whitespace is stripped.  
**Expected**: assert result == 'First sentence.'  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, 20)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:83*

### test_truncate_at_sentence_realistic_summary

**Category**: instantiation  
**Description**: Instantiate truncate_at_sentence: Test with a realistic entity summary.  
**Expected**: assert len(result) <= MAX_SUMMARY_CHARS  
**Confidence**: 0.80  

```python
result = truncate_at_sentence(text, MAX_SUMMARY_CHARS)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_text_utils.py:101*

### anthropic_client

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Fixture to create an AnthropicClient with a mocked AsyncAnthropic.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_async_anthropic

config = LLMConfig(api_key='test_api_key', model='test-model', temperature=0.5, max_tokens=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:55*

### anthropic_client

**Category**: instantiation  
**Description**: Instantiate AnthropicClient: Fixture to create an AnthropicClient with a mocked AsyncAnthropic.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_async_anthropic

client = AnthropicClient(config=config, cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:58*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  

```python
config = LLMConfig(api_key='test_api_key', model='test-model', temperature=0.5, max_tokens=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:69*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate AnthropicClient: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  

```python
client = AnthropicClient(config=config, cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:72*

### test_init_with_default_model

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Test initialization with default model when none is provided.  
**Expected**: assert client.model == 'claude-haiku-4-5-latest'  
**Confidence**: 0.80  

```python
config = LLMConfig(api_key='test_api_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:81*

### test_init_with_default_model

**Category**: instantiation  
**Description**: Instantiate AnthropicClient: Test initialization with default model when none is provided.  
**Expected**: assert client.model == 'claude-haiku-4-5-latest'  
**Confidence**: 0.80  

```python
client = AnthropicClient(config=config, cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:82*

### test_init_without_config

**Category**: instantiation  
**Description**: Instantiate AnthropicClient: Test initialization without a config, using environment variable.  
**Expected**: assert client.config.api_key == 'env_api_key'  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = AnthropicClient(cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:89*

### test_init_with_custom_client

**Category**: instantiation  
**Description**: Instantiate AnthropicClient: Test initialization with a custom AsyncAnthropic client.  
**Expected**: assert client.client == mock_client  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = AnthropicClient(client=mock_client)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_anthropic_client.py:97*

### openai_embedder

**Category**: instantiation  
**Description**: Instantiate OpenAIEmbedderConfig: Create an OpenAIEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_openai_client

config = OpenAIEmbedderConfig(api_key='test_api_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_openai.py:71*

### openai_embedder

**Category**: instantiation  
**Description**: Instantiate OpenAIEmbedder: Create an OpenAIEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_openai_client

client = OpenAIEmbedder(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_openai.py:72*

### test_total_tokens

**Category**: instantiation  
**Description**: Instantiate TokenUsage: Test that total_tokens correctly sums input and output tokens.  
**Expected**: assert usage.total_tokens == 150  
**Confidence**: 0.80  

```python
usage = TokenUsage(input_tokens=100, output_tokens=50)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:29*

### test_total_tokens

**Category**: instantiation  
**Description**: Instantiate PromptTokenUsage: Test that total_tokens correctly sums input and output tokens.  
**Expected**: assert usage.total_tokens == 1500  
**Confidence**: 0.80  

```python
usage = PromptTokenUsage(prompt_name='test', call_count=5, total_input_tokens=1000, total_output_tokens=500)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:43*

### test_avg_input_tokens

**Category**: instantiation  
**Description**: Instantiate PromptTokenUsage: Test average input tokens calculation.  
**Expected**: assert usage.avg_input_tokens == 250.0  
**Confidence**: 0.80  

```python
usage = PromptTokenUsage(prompt_name='test', call_count=4, total_input_tokens=1000, total_output_tokens=500)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:53*

### test_avg_output_tokens

**Category**: instantiation  
**Description**: Instantiate PromptTokenUsage: Test average output tokens calculation.  
**Expected**: assert usage.avg_output_tokens == 125.0  
**Confidence**: 0.80  

```python
usage = PromptTokenUsage(prompt_name='test', call_count=4, total_input_tokens=1000, total_output_tokens=500)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:63*

### test_avg_tokens_zero_calls

**Category**: instantiation  
**Description**: Instantiate PromptTokenUsage: Test that average returns 0 when call_count is zero.  
**Expected**: assert usage.avg_input_tokens == 0  
**Confidence**: 0.80  

```python
usage = PromptTokenUsage(prompt_name='test', call_count=0, total_input_tokens=0, total_output_tokens=0)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_token_tracker.py:73*

### test_clean_input

**Category**: instantiation  
**Description**: Instantiate MockLLMClient: test clean input  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = MockLLMClient(LLMConfig())
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_client.py:29*

### test_init_with_falkor_db_instance

**Category**: instantiation  
**Description**: Instantiate FalkorDriver: Test initialization with a FalkorDB instance.  
**Confidence**: 0.80  
**Tags**: unittest, mock  

```python
driver = FalkorDriver(falkor_db=mock_falkor_db)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:63*

### test_get_graph_with_name

**Category**: instantiation  
**Description**: Instantiate _get_graph: Test _get_graph with specific graph name.  
**Expected**: self.mock_client.select_graph.assert_called_once_with('test_graph')  
**Confidence**: 0.80  
**Tags**: unittest, mock  

```python
result = self.driver._get_graph('test_graph')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:79*

### test_get_graph_with_none_defaults_to_default_database

**Category**: instantiation  
**Description**: Instantiate _get_graph: Test _get_graph with None defaults to default_db.  
**Expected**: self.mock_client.select_graph.assert_called_once_with('default_db')  
**Confidence**: 0.80  
**Tags**: unittest, mock  

```python
result = self.driver._get_graph(None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:90*

### test_convert_datetime_dict

**Category**: instantiation  
**Description**: Instantiate datetime: Test datetime conversion in nested dictionary.  
**Expected**: assert result['string_val'] == 'test'  
**Confidence**: 0.80  
**Tags**: unittest  

```python
test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:310*

### test_convert_datetime_dict

**Category**: instantiation  
**Description**: Instantiate convert_datetimes_to_strings: Test datetime conversion in nested dictionary.  
**Expected**: assert result['string_val'] == 'test'  
**Confidence**: 0.80  
**Tags**: unittest  

```python
result = convert_datetimes_to_strings(input_dict)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:317*

### test_convert_datetime_list_and_tuple

**Category**: instantiation  
**Description**: Instantiate datetime: Test datetime conversion in lists and tuples.  
**Expected**: assert result_list[0] == 'test'  
**Confidence**: 0.80  
**Tags**: unittest  

```python
test_datetime = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:329*

### test_convert_datetime_list_and_tuple

**Category**: instantiation  
**Description**: Instantiate convert_datetimes_to_strings: Test datetime conversion in lists and tuples.  
**Expected**: assert result_list[0] == 'test'  
**Confidence**: 0.80  
**Tags**: unittest  

```python
result_list = convert_datetimes_to_strings(input_list)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\driver\test_falkordb_driver.py:333*

### mock_llm_client

**Category**: instantiation  
**Description**: Instantiate Mock: Create a mock LLM  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
mock_llm = Mock(spec=LLMClient)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_graphiti_mock.py:75*

### mock_cross_encoder_client

**Category**: instantiation  
**Description**: Instantiate Mock: Create a mock LLM  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
mock_llm = Mock(spec=CrossEncoderClient)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_graphiti_mock.py:101*

### gemini_client

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Fixture to create a GeminiClient with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

config = LLMConfig(api_key='test_api_key', model='test-model', temperature=0.5, max_tokens=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:53*

### gemini_client

**Category**: instantiation  
**Description**: Instantiate GeminiClient: Fixture to create a GeminiClient with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

client = GeminiClient(config=config, cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:54*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

config = LLMConfig(api_key='test_api_key', model='test-model', temperature=0.5, max_tokens=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:66*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate GeminiClient: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

client = GeminiClient(config=config, cache=False, max_tokens=1000)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:69*

### test_init_with_default_model

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Test initialization with default model when none is provided.  
**Expected**: assert client.model == DEFAULT_MODEL  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

config = LLMConfig(api_key='test_api_key', model=DEFAULT_MODEL)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:79*

### test_init_with_default_model

**Category**: instantiation  
**Description**: Instantiate GeminiClient: Test initialization with default model when none is provided.  
**Expected**: assert client.model == DEFAULT_MODEL  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

client = GeminiClient(config=config, cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:80*

### test_init_without_config

**Category**: instantiation  
**Description**: Instantiate GeminiClient: Test initialization without a config uses defaults.  
**Expected**: assert client.config is not None  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

client = GeminiClient(cache=False)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:87*

### test_init_with_thinking_config

**Category**: instantiation  
**Description**: Instantiate GeminiClient: Test initialization with thinking config.  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

client = GeminiClient(thinking_config=thinking_config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_gemini_client.py:98*

### test_node_search_filter_constructor_keeps_valid_label_expression

**Category**: instantiation  
**Description**: Instantiate SearchFilters: test node search filter constructor keeps valid label expression  
**Expected**: assert filter_queries == ['n:Person|Organization']  
**Confidence**: 0.80  

```python
filters = SearchFilters(node_labels=['Person', 'Organization'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:26*

### test_node_search_filter_constructor_keeps_valid_label_expression

**Category**: instantiation  
**Description**: Instantiate node_search_filter_query_constructor: test node search filter constructor keeps valid label expression  
**Expected**: assert filter_queries == ['n:Person|Organization']  
**Confidence**: 0.80  

```python
filter_queries, filter_params = node_search_filter_query_constructor(filters, GraphProvider.NEO4J)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:28*

### test_node_search_filter_constructor_rejects_unsafe_labels_bypassing_pydantic

**Category**: instantiation  
**Description**: Instantiate model_construct: test node search filter constructor rejects unsafe labels bypassing pydantic  
**Confidence**: 0.80  

```python
filters = SearchFilters.model_construct(node_labels=['Entity`) DETACH DELETE x //'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:37*

### test_edge_search_filter_constructor_rejects_unsafe_labels_bypassing_pydantic

**Category**: instantiation  
**Description**: Instantiate model_construct: test edge search filter constructor rejects unsafe labels bypassing pydantic  
**Confidence**: 0.80  

```python
filters = SearchFilters.model_construct(node_labels=['Entity`) DETACH DELETE x //'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:44*

### test_fulltext_query_rejects_invalid_group_ids

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test fulltext query rejects invalid group ids  
**Confidence**: 0.80  

```python
driver = SimpleNamespace(provider=GraphProvider.NEO4J, fulltext_syntax='')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:51*

### test_falkordb_fulltext_query_rejects_invalid_group_ids

**Category**: instantiation  
**Description**: Instantiate MagicMock: test falkordb fulltext query rejects invalid group ids  
**Confidence**: 0.80  
**Tags**: mock  

```python
driver = MagicMock(spec=FalkorDriver)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\search\test_search_security.py:66*

### gemini_embedder

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedderConfig: Create a GeminiEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

config = GeminiEmbedderConfig(api_key='test_api_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:74*

### gemini_embedder

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedder: Create a GeminiEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

client = GeminiEmbedder(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:75*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedderConfig: Test initialization with a config object.  
**Expected**: assert embedder.config == config  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

config = GeminiEmbedderConfig(api_key='test_api_key', embedding_model='custom-model', embedding_dim=768)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:86*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedder: Test initialization with a config object.  
**Expected**: assert embedder.config == config  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

embedder = GeminiEmbedder(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:89*

### test_init_with_partial_config

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedderConfig: Test initialization with partial config.  
**Expected**: assert embedder.config.api_key == 'test_api_key'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

config = GeminiEmbedderConfig(api_key='test_api_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:107*

### test_init_with_partial_config

**Category**: instantiation  
**Description**: Instantiate GeminiEmbedder: Test initialization with partial config.  
**Expected**: assert embedder.config.api_key == 'test_api_key'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: mock_client

embedder = GeminiEmbedder(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_gemini.py:108*

### test_custom_message

**Category**: instantiation  
**Description**: Instantiate RateLimitError: Test that a custom message can be set.  
**Expected**: assert error.message == custom_message  
**Confidence**: 0.80  

```python
error = RateLimitError(custom_message)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_errors.py:36*

### test_message_assignment

**Category**: instantiation  
**Description**: Instantiate RefusalError: Test that the message is assigned correctly.  
**Expected**: assert error.message == message  
**Confidence**: 0.80  

```python
error = RefusalError(message=message)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_errors.py:53*

### test_message_assignment

**Category**: instantiation  
**Description**: Instantiate EmptyResponseError: Test that the message is assigned correctly.  
**Expected**: assert error.message == message  
**Confidence**: 0.80  

```python
error = EmptyResponseError(message=message)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_errors.py:70*

### test_entity_node_assignment_rejects_unsafe_labels

**Category**: instantiation  
**Description**: Instantiate EntityNode: test entity node assignment rejects unsafe labels  
**Confidence**: 0.80  

```python
node = EntityNode(name='Alice', group_id='group', labels=['Person'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_node_label_security.py:23*

### mock_embedder

**Category**: instantiation  
**Description**: Instantiate Mock: mock embedder  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
mock_model = Mock(spec=EmbedderClient)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\helpers_test.py:167*

### mock_embedder

**Category**: instantiation  
**Description**: Instantiate join: mock embedder  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
combined_input = ' '.join(input_data)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\helpers_test.py:173*

### test_lucene_sanitize

**Category**: instantiation  
**Description**: Instantiate lucene_sanitize: test lucene sanitize  
**Confidence**: 0.80  

```python
result = lucene_sanitize(query)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\helpers_test.py:193*

### test_build_candidate_indexes_populates_structures

**Category**: instantiation  
**Description**: Instantiate EntityNode: test build candidate indexes populates structures  
**Expected**: assert indexes.normalized_existing[normalized_key][0].uuid == candidate.uuid  
**Confidence**: 0.80  

```python
candidate = EntityNode(name='Bob Dylan', group_id='group', labels=['Entity'])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:185*

### test_build_candidate_indexes_populates_structures

**Category**: instantiation  
**Description**: Instantiate _build_candidate_indexes: test build candidate indexes populates structures  
**Expected**: assert indexes.normalized_existing[normalized_key][0].uuid == candidate.uuid  
**Confidence**: 0.80  

```python
indexes = _build_candidate_indexes([candidate])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:187*

### test_shingles_and_cache

**Category**: instantiation  
**Description**: Instantiate _shingles: test shingles and cache  
**Expected**: assert shingle_set == {'ali', 'lic', 'ice'}  
**Confidence**: 0.80  

```python
shingle_set = _shingles(raw)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:213*

### test_hash_minhash_and_lsh

**Category**: instantiation  
**Description**: Instantiate _minhash_signature: test hash minhash and lsh  
**Expected**: assert len(signature) == 32  
**Confidence**: 0.80  

```python
signature = _minhash_signature(shingles)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_node_operations.py:221*

### gemini_reranker_client

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Fixture to create a GeminiRerankerClient with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

config = LLMConfig(api_key='test_api_key', model='test-model')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\cross_encoder\test_gemini_reranker_client.py:42*

### gemini_reranker_client

**Category**: instantiation  
**Description**: Instantiate GeminiRerankerClient: Fixture to create a GeminiRerankerClient with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_gemini_client

client = GeminiRerankerClient(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\cross_encoder\test_gemini_reranker_client.py:43*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate LLMConfig: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  

```python
config = LLMConfig(api_key='test_api_key', model='test-model')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\cross_encoder\test_gemini_reranker_client.py:61*

### test_init_with_config

**Category**: instantiation  
**Description**: Instantiate GeminiRerankerClient: Test initialization with a config object.  
**Expected**: assert client.config == config  
**Confidence**: 0.80  

```python
client = GeminiRerankerClient(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\cross_encoder\test_gemini_reranker_client.py:62*

### test_init_with_custom_client

**Category**: instantiation  
**Description**: Instantiate GeminiRerankerClient: Test initialization with a custom client.  
**Expected**: assert client.client == mock_client  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = GeminiRerankerClient(client=mock_client)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\cross_encoder\test_gemini_reranker_client.py:76*

### test_default_entity_type_always_included

**Category**: instantiation  
**Description**: Instantiate _build_entity_types_context: Default Entity type should always be at index 0.  
**Expected**: assert len(context) == 1  
**Confidence**: 0.80  

```python
context = _build_entity_types_context(None)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_entity_extraction.py:236*

### test_custom_types_added_after_default

**Category**: instantiation  
**Description**: Instantiate _build_entity_types_context: Custom entity types should be added with sequential IDs.  
**Expected**: assert len(context) == 3  
**Confidence**: 0.80  

```python
context = _build_entity_types_context({'Person': Person, 'Organization': Organization})
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_entity_extraction.py:256*

### test_build_directed_uuid_map_chain

**Category**: instantiation  
**Description**: Instantiate _build_directed_uuid_map: test build directed uuid map chain  
**Expected**: assert mapping['a'] == 'c'  
**Confidence**: 0.80  

```python
mapping = bulk_utils._build_directed_uuid_map([('a', 'b'), ('b', 'c')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_bulk_utils.py:195*

### test_build_directed_uuid_map_preserves_direction

**Category**: instantiation  
**Description**: Instantiate _build_directed_uuid_map: test build directed uuid map preserves direction  
**Expected**: assert mapping['alias'] == 'canonical'  
**Confidence**: 0.80  

```python
mapping = bulk_utils._build_directed_uuid_map([('alias', 'canonical')])
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_bulk_utils.py:208*

### test_resolve_edge_pointers_updates_sources

**Category**: instantiation  
**Description**: Instantiate EntityEdge: test resolve edge pointers updates sources  
**Expected**: assert edge.source_node_uuid == 'canonical'  
**Confidence**: 0.80  

```python
edge = EntityEdge(name='knows', fact='fact', group_id='group', source_node_uuid='alias', target_node_uuid='target', created_at=created_at)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\utils\maintenance\test_bulk_utils.py:220*

### voyageai_embedder

**Category**: instantiation  
**Description**: Instantiate VoyageAIEmbedderConfig: Create a VoyageAIEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_voyageai_client

config = VoyageAIEmbedderConfig(api_key='test_api_key')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_voyage.py:63*

### voyageai_embedder

**Category**: instantiation  
**Description**: Instantiate VoyageAIEmbedder: Create a VoyageAIEmbedder with a mocked client.  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
# Setup
# Fixtures: mock_voyageai_client

client = VoyageAIEmbedder(config=config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\embedder\test_voyage.py:64*

### test_llm_factory

**Category**: instantiation  
**Description**: Instantiate GeminiProviderConfig: Test LLM client factory creation.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: config

test_config.providers.gemini = GeminiProviderConfig(api_key='dummy_value_for_testing')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\mcp_server\tests\test_configuration.py:77*

### test_llm_factory

**Category**: instantiation  
**Description**: Instantiate create: Test LLM client factory creation.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: config

client = LLMClientFactory.create(test_config)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\mcp_server\tests\test_configuration.py:82*

### test_llm_factory

**Category**: instantiation  
**Description**: Instantiate create: Test LLM client factory creation.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: config

client = LLMClientFactory.create(config.llm)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\mcp_server\tests\test_configuration.py:62*

### test_embedder_factory

**Category**: instantiation  
**Description**: Instantiate create: Test Embedder client factory creation.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: config

_ = EmbedderFactory.create(config.embedder)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\mcp_server\tests\test_configuration.py:99*

### test_cli_override

**Category**: instantiation  
**Description**: Instantiate Path: Test CLI argument override functionality.  
**Confidence**: 0.80  

```python
config = Path('config.yaml')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\mcp_server\tests\test_configuration.py:154*

### mock_llm_client

**Category**: instantiation  
**Description**: Instantiate Mock: Create a mock LLM  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
mock_llm = Mock(spec=LLMClient)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_add_triplet.py:35*

### mock_cross_encoder_client

**Category**: instantiation  
**Description**: Instantiate Mock: Create a mock cross encoder  
**Confidence**: 0.80  
**Tags**: pytest, mock  

```python
mock_ce = Mock(spec=CrossEncoderClient)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_add_triplet.py:57*

### cache

**Category**: instantiation  
**Description**: Instantiate LLMCache: Create an LLMCache using a temporary directory.  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: tmp_path

c = LLMCache(str(tmp_path / 'test_cache'))
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:27*

### test_creates_directory

**Category**: instantiation  
**Description**: Instantiate str: Test that LLMCache creates the directory if it doesn't exist.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

cache_dir = str(tmp_path / 'nested' / 'dir' / 'cache')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:86*

### test_creates_directory

**Category**: instantiation  
**Description**: Instantiate LLMCache: Test that LLMCache creates the directory if it doesn't exist.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

c = LLMCache(cache_dir)
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:87*

### test_persistence_across_instances

**Category**: instantiation  
**Description**: Instantiate str: Test that data persists when opening a new LLMCache on the same directory.  
**Confidence**: 0.80  

```python
# Setup
# Fixtures: tmp_path

cache_dir = str(tmp_path / 'persist_cache')
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\llm_client\test_cache.py:96*

### test_validation_valid_excluded_types

**Category**: config  
**Description**: Configuration example: Test validation function with valid excluded types.  
**Expected**: assert validate_excluded_entity_types(['Entity'], entity_types) is True  
**Confidence**: 0.75  

```python
entity_types = {'Person': Person, 'Organization': Organization}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_entity_exclusion_int.py:281*

### test_validation_invalid_excluded_types

**Category**: config  
**Description**: Configuration example: Test validation function with invalid excluded types.  
**Confidence**: 0.75  

```python
entity_types = {'Person': Person, 'Organization': Organization}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_entity_exclusion_int.py:296*

### mock_llm_client

**Category**: config  
**Description**: Configuration example: Create a mock LLM  
**Confidence**: 0.75  
**Tags**: pytest, mock  

```python
mock_llm.generate_response.return_value = {'duplicate_facts': [], 'invalidate_facts': []}
```

*Source: C:\Users\Bin\AppData\Local\Temp\skill-seekers-pin-graphiti-435f4bb2\tests\test_add_triplet.py:46*

