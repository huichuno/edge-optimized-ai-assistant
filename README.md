<a name="readme-top"></a>

# Edge Optimized AI Assistant

This project contains the software component and ingredients to enable optimized generative AI application on Intel Edge hardware

## Getting Started

### Prerequisites
* A working [Ubuntu 24.04 LTS](https://releases.ubuntu.com/noble/ubuntu-24.04.2-desktop-amd64.iso) or [Ubuntu 24.10](https://releases.ubuntu.com/oracular/ubuntu-24.10-desktop-amd64.iso) host
* [Intel GPU Driver Installation](https://www.intel.com/content/www/us/en/developer/articles/tool/pytorch-prerequisites-for-intel-gpu/2-7.html) (Optional)

### Installation

1\. Install Docker Compose from [(here)](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository). Add user to docker group, logging out and back in to apply change

```sh
sudo usermod -aG docker $USER
newgrp $USER
```

2\. Install FFmpeg

```sh
sudo apt install ffmpeg -y
```

3\. Clone repo & build docker image

*Note: If operating behind corporate firewall, setup the proxy settings, e.g. http_proxy, https_proxy, in Linux environment before continuing*

```sh
git clone <repo> edge-optimized-ai-assistant

cd edge-optimized-ai-assistant/app/kiosk

./build.sh
```

4\. Start application and services

*Note: When launching the application for the first time, please allow a few minutes for the dependencies to download. You may check the containers log using `lazydocker`*

```sh
./up.sh
```

5\. Launch browser and navigate to ***http://locahost:8080/*** on local machine or ***http://\<ip addr\>:8080/*** to access Open WebUI. Open WebUI is a self-hosted, open-source web interface that allows users to interact with LLMs locally

6\. Other Installation (Optional)
* [lazydocker](https://github.com/jesseduffield/lazydocker) - A simple terminal UI to visualize and interact with containers. After install, launch by executing the following command `~/.local/bin/lazydocker`

## How-To

### Download LLM model

1\. Proceed to *Create Admin Account* and *Sign in to Open WebUI* the first time launching Open WebUI

2\. To download LLM model, click *Select a model* > search for "*ollama pull llama3.2*" > select *Pull "ollama pull ollama3.2" from ollama.com*

3\. Wait for the download to complete. See https://ollama.com/library for the list of downloadable models

### Create Open WebUI Workspace

1\. On Open WebUI, navigate to *Workspace* > click '+' and update the fields below:
* *Model Name*: Five Star Coffee Cafe
* *Base Model (From)*: llama3.2:latest
* *Visibility*: Public
* Model Params > *System Prompt*: \<refer to prompt file\>
* Advanced Params > *Stream Chat Response*: On
* Advanced Params > *Temperature*: 0

2\. Click *Save & Create*

### Configure Open WebUI

1\. On Open WebUI, navigate to:
* Profile > Settings > Audio > SST Settings > *Instant Auto-Send After Voice Transcription*: On
* Profile > Settings > Audio > TTS Settings > *Auto-playback response*: On
* Profile > Settings > Audio > TTS Settings > *Voice*: [ alloy | echo | fable | onyx | nova | shimmer ]
* Profile > Settings > Admin Settings > Code Execution > *Enable Code Execution*: Disabled
* Profile > Settings > Admin Settings > Code Execution > *Enable Code Interpreter*: Disabled
* Profile > Settings > Admin Settings > Evaluation > *Arena Models*: Disabled
* Profile > Settings > Admin Settings > Audio > *Response splitting*: Punctuation
* (Optional) Profile > Settings > Interface > on *Chat Background Image*, click *Upload* to upload new background image

### Allow developer to treat HTTP as secure on Chrome browser

1\. Launch Chrome browser and enter the follow in the address bar
```sh
chrome://flags/#unsafely-treat-insecure-origin-as-secure
```
2\. Enter `http://<ip addr>:8080` in the text box under "*Insecure origins treated as secure*" option. Select *Enabled* > *Relaunch* browser

### Stop application and services

```sh
docker compose -f docker-compose.yml -f compose.override.yml down
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## Supported Platforms

| Codename | Product Name |
|--|--|
| Meteor Lake | Intel(R) Core(TM) Ultra Processors (Series 1) |
| Lunar Lake, Arrow Lake | Intel(R) Core(TM) Ultra Processors (Series 2) |

<p align="right">(<a href="#readme-top">back to top</a>)</p>


## For Developer

### Install *uv* to manage Python packages
```sh
sudo apt install curl -y
curl -LsSf https://astral.sh/uv/install.sh | sh

echo 'eval "$(uv generate-shell-completion bash)"' >> ~/.bashrc
```

### Create an example Python project using *uv*
```sh
mkdir speech2text && cd speech2text
uv venv --python 3.12

uv pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu

uv pip install ffmpeg transformers fastapi uvicorn python-multipart
```

### Create a requirements.txt file
```sh
uv pip list

uv pip freeze > requirements.txt
```

### Sync virtual environment using requirements.txt file
```sh
uv pip sync requirements.txt \
  --index-strategy unsafe-best-match \
  --index https://download.pytorch.org/whl/xpu
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>
