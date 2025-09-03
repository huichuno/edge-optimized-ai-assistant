#!/bin/bash
source whisper.env
HF_HOME=".cache/stt/hf_home" uv run whisper.py $CLI_ARGS