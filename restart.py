import subprocess

cmd = """
sed -i 's/LIVEKIT_API_SECRET=secret/LIVEKIT_API_SECRET=parrot_carriers_local_dev_livekit_secret_key_v1/' /opt/parrotcarriers/.env
tmux send-keys -t brain C-c
sleep 1
tmux send-keys -t brain "cd /opt/parrotcarriers" C-m
tmux send-keys -t brain "export \$(cat .env | grep -v '^#' | xargs)" C-m
tmux send-keys -t brain ".venv/bin/python -m parrot.brain.agent dev" C-m
"""

subprocess.run(["ssh", "root@8.216.45.45", "bash"], input=cmd.encode('utf-8'))
