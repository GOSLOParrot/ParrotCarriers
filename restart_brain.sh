#!/bin/bash
tmux send-keys -t brain C-c
sleep 2
tmux send-keys -t brain "cd /opt/parrotcarriers" C-m
tmux send-keys -t brain "export \$(cat .env | grep -v '#' | xargs)" C-m
tmux send-keys -t brain ".venv/bin/python -m parrot.brain.agent dev" C-m
