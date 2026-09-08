#!/bin/sh
# Source this file to expose the workspace-local REAPER launcher.
AUDIO_WORKSPACE=/mnt/data/audio
export AUDIO_WORKSPACE
PATH="$AUDIO_WORKSPACE/bin:$PATH"
export PATH
