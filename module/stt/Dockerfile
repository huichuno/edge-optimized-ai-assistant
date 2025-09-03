# Reference:
# https://pytorch.org/docs/main/notes/get_start_xpu.html
# https://dgpu-docs.intel.com/driver/client/overview.html#installing-client-gpus-on-ubuntu-desktop-24-10
# https://dgpu-docs.intel.com/devices/hardware-table.html

FROM ubuntu:24.10
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl ca-certificates gpg-agent gnupg wget software-properties-common && \
    rm -rf /var/lib/apt/lists/* && \
    add-apt-repository -y ppa:kobuk-team/intel-graphics

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libze-intel-gpu1 libze1 libze-dev intel-ocloc intel-opencl-icd clinfo \
    intel-gsc intel-metrics-discovery intel-media-va-driver-non-free libmfx1 \
    libmfx-gen1 libvpl2 libvpl-tools libva-glx2 va-driver-all vainfo ffmpeg

WORKDIR /app
ADD . /app

RUN uv venv --python 3.12 && \
    uv pip sync requirements.txt --index-strategy unsafe-best-match \
    --index https://download.pytorch.org/whl/xpu

ENV PATH="/app/.venv/bin:$PATH"

ARG CLI_ARGS=""
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
CMD uv run whisper.py $CLI_ARGS