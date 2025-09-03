#!/bin/bash
uv venv --python 3.12
uv pip sync requirements.txt --index-strategy unsafe-best-match \
    --index https://download.pytorch.org/whl/xpu
