import sys, json
sys.path.insert(0, "/opt/parrotcarriers/src")
from parrot.scheduler.blackboard import open_bb_client

bb = open_bb_client(name="smoke_reader")

# GAP-1: session/ecp_state
try:
    s = bb.get("session/ecp_state")
    if s:
        fields = ["body_state","head_state","sequence_id","app_lifecycle_state","active_locks","active_command_id"]
        print("GAP-1 PASS session/ecp_state:", {k: s.get(k) for k in fields})
    else:
        print("GAP-1: session/ecp_state = None (not received yet)")
except Exception as e:
    print("GAP-1 ERR:", e)

# tick/body_state
try:
    b = bb.get("tick/body_state")
    print("tick/body_state:", b)
except Exception as e:
    print("tick/body_state ERR:", e)

# tick/cognitive_state
try:
    c = bb.get("tick/cognitive_state")
    print("tick/cognitive_state:", c)
except Exception as e:
    print("tick/cognitive_state ERR:", e)
