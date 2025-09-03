# Reference:
# https://pytorch.org/docs/main/notes/get_start_xpu.html
# https://dgpu-docs.intel.com/driver/client/overview.html#installing-client-gpus-on-ubuntu-desktop-24-10
# https://dgpu-docs.intel.com/devices/hardware-table.html
# https://github.com/intel/linux-npu-driver/releases

FROM ubuntu:24.10
COPY --from=ghcr.io/astral-sh/uv:0.7.3 /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl ca-certificates gpg-agent gnupg wget software-properties-common git && \
    rm -rf /var/lib/apt/lists/* && \
    add-apt-repository -y ppa:kobuk-team/intel-graphics

RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libze-intel-gpu1 libze1 libze-dev intel-ocloc intel-opencl-icd clinfo \
    intel-gsc intel-metrics-discovery intel-media-va-driver-non-free libmfx1 \
    libmfx-gen1 libvpl2 libvpl-tools libva-glx2 va-driver-all vainfo ffmpeg

# Install NPU driver v1.17.0
RUN DEBIAN_FRONTEND=noninteractive \
    dpkg --purge --force-remove-reinstreq intel-driver-compiler-npu intel-fw-npu intel-level-zero-npu && \
    wget https://github.com/intel/linux-npu-driver/releases/download/v1.17.0/intel-driver-compiler-npu_1.17.0.20250508-14912879441_ubuntu24.04_amd64.deb && \
    wget https://github.com/intel/linux-npu-driver/releases/download/v1.17.0/intel-fw-npu_1.17.0.20250508-14912879441_ubuntu24.04_amd64.deb && \
    wget https://github.com/intel/linux-npu-driver/releases/download/v1.17.0/intel-level-zero-npu_1.17.0.20250508-14912879441_ubuntu24.04_amd64.deb && \
    apt-get update && \
    apt-get install -y --no-install-recommends libtbb12 && \
    dpkg -i *.deb && \
    # Clean up to reduce image size
    rm -rf *.deb && \
    apt-get autoremove -y && \ 
    apt-get clean && \ 
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
ADD . /app

RUN uv venv --python 3.12 && \
    uv pip install -r requirements.txt --index-strategy unsafe-best-match

ENV PATH="/app/.venv/bin:$PATH"

ARG CLI_ARGS=""
CMD uv run whisper.py $CLI_ARGS