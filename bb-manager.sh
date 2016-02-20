#!/bin/bash

timeout=60

while true
do
    python rtmbot.py
    echo "BountyBot crashed with exit code $?.  Respawning in $timeout seconds..." >&2
    sleep $timeout
done

