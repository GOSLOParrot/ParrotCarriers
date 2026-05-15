"""Brain vision helpers.

Formal Unity does not send photos through LiveKit RPC. Camera/photo actions
publish compact ECP metadata and upload image bytes through HTTP/storage.
``snapshot.capture_current_frame`` remains only as a disabled compatibility
hook for older ``identify_object`` imports.
``frame_cache.record_livekit_frame_bytes`` is the storage-backed producer path
for auditable LiveKit/SVA frames.
``livekit_sampler.attach_livekit_frame_sampler`` wires that producer to a
room-scoped, low-FPS LiveKit video-track consumer.
``evidence_image.prepare_evidence_image`` is the local asset/crop bridge for
VLM calls; ECP/RPC still carries only ids and timebase metadata.
"""
