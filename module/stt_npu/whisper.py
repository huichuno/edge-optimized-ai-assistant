#!/usr/bin/env python3
import os
import sys
import io
import argparse

import openvino
import openvino_genai
from pathlib import Path
from typing import Optional, List
from fastapi import UploadFile, Form
from fastapi.responses import PlainTextResponse, JSONResponse
import uvicorn

import openedai
from utils import optimum_cli, read_audio

pipe = None
app = openedai.OpenAIStub()

async def whisper(file, response_format: str, **kwargs):
    global pipe

    result = pipe.generate(read_audio(io.BytesIO(await file.read())), **kwargs)

    filename_noext, ext = os.path.splitext(file.filename)

    if response_format == "text":
        return PlainTextResponse(result.texts[0].strip(), headers={"Content-Disposition": f"attachment; filename={filename_noext}.txt"})

    elif response_format == "json":
        return JSONResponse(content={ 'text': result.texts[0].strip() }, media_type="application/json", headers={"Content-Disposition": f"attachment; filename={filename_noext}.json"})
    
    elif response_format == "verbose_json":
        chunks = result.chunks

        response = {
            "task": kwargs['generation_config']['task'],
            #"language": "english",
            "duration": chunks[-1].end_ts,
            "text": result.texts[0].strip(),
        }
        if kwargs['return_timestamps'] == 'word':
            response['words'] = [{'word': chunk.text.strip(), 'start': chunk.start_ts, 'end': chunk.end_ts } for chunk in chunks ]
        else:
            response['segments'] = [{
                    "id": i,
                    #"seek": 0,
                    'start': chunk.start_ts,
                    'end': chunk.end_ts,
                    'text': chunk.text.strip(),
                    #"tokens": [ ],
                    #"temperature": 0.0,
                    #"avg_logprob": -0.2860786020755768,
                    #"compression_ratio": 1.2363636493682861,
                    #"no_speech_prob": 0.00985979475080967
            } for i, chunk in enumerate(chunks) ]
        
        return JSONResponse(content=response, media_type="application/json", headers={"Content-Disposition": f"attachment; filename={filename_noext}_verbose.json"})

    elif response_format == "srt":
            def srt_time(t):
                return "{:02d}:{:02d}:{:06.3f}".format(int(t//3600), int(t//60)%60, t%60).replace(".", ",")

            return PlainTextResponse("\n".join([ f"{i}\n{srt_time(chunk.start_ts)} --> {srt_time(chunk.end_ts)}\n{chunk.text.strip()}\n"
                for i, chunk in enumerate(result.chunks, 1) ]), media_type="text/srt; charset=utf-8", headers={"Content-Disposition": f"attachment; filename={filename_noext}.srt"})

    elif response_format == "vtt":
            def vtt_time(t):
                return "{:02d}:{:06.3f}".format(int(t//60), t%60)
            
            return PlainTextResponse("\n".join(["WEBVTT\n"] + [ f"{vtt_time(chunk.start_ts)} --> {vtt_time(chunk.end_ts)}\n{chunk.text.strip()}\n"
                for chunk in result.chunks ]), media_type="text/vtt; charset=utf-8", headers={"Content-Disposition": f"attachment; filename={filename_noext}.vtt"})


@app.post("/v1/audio/transcriptions")
async def transcriptions(
        file: UploadFile,
        model: str = Form(...),
        language: Optional[str] = Form(None),
        prompt: Optional[str] = Form(None),
        response_format: Optional[str] = Form("json"),
        temperature: Optional[float] = Form(None),
        timestamp_granularities: List[str] = Form(["segment"])
    ):
    global pipe

    try:
        kwargs = {'task': 'transcribe'}

        if language:
            kwargs["language"] = language
        # # May work soon, https://github.com/huggingface/transformers/issues/27317
        # if prompt:
        #     kwargs["initial_prompt"] = prompt
        if temperature:
            kwargs["temperature"] = temperature
            kwargs['do_sample'] = True

        if response_format == "verbose_json" and 'word' in timestamp_granularities:
            kwargs['return_timestamps'] = 'word'
        else:
            kwargs['return_timestamps'] = response_format in ["verbose_json", "srt", "vtt"]

        return await whisper(file, response_format, **kwargs)
  
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/v1/audio/translations")
async def translations(
        file: UploadFile,
        model: str = Form(...),
        prompt: Optional[str] = Form(None),
        response_format: Optional[str] = Form("json"),
        temperature: Optional[float] = Form(None),
    ):
    global pipe

    try:
        kwargs = {"task": "translate"}

        # # May work soon, https://github.com/huggingface/transformers/issues/27317
        # if prompt:
        #     kwargs["initial_prompt"] = prompt
        if temperature:
            kwargs["temperature"] = temperature
            kwargs['do_sample'] = True

        kwargs['return_timestamps'] = response_format in ["verbose_json", "srt", "vtt"]

        return await whisper(file, response_format, **kwargs)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog='whisper.py',
        description='OpenedAI Whisper API Server',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-m', '--model', action='store', default="openai/whisper-large-v3-turbo", help="The model to use for transcription. Ex. openai/whisper-large-v3")
    parser.add_argument('-d', '--device', action='store', default="auto", help="Set the OpenVINO device for the model. Ex. GPU")
    parser.add_argument('-P', '--port', action='store', default=9000, type=int, help="Server tcp port")
    parser.add_argument('-H', '--host', action='store', default='localhost', help="Host to listen on, Ex. 0.0.0.0")
    parser.add_argument('-c', '--cache_dir', action='store', default='/app/ov_home/', help="Cache directory for OpenVINO.")
    parser.add_argument('--preload', action='store_true', help="Preload model and exit.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    if args.device == "auto":
        available_devices = openvino.Core().available_devices
        if "NPU" in available_devices:
            device = "NPU"
        elif "GPU" in available_devices:
            device = "GPU" 
        else: 
            device = "CPU"

    model_name=args.model.split("/")[-1]
    model_dir=args.cache_dir + model_name
    if not Path(model_dir).exists():
        optimum_cli(model_id=args.model, output_dir=Path(model_dir))

    ov_config = dict()
    ov_config["CACHE_DIR"] = model_dir + "/npu_cache"

    pipe = openvino_genai.WhisperPipeline(
        models_path=model_dir, 
        device=device, 
        **ov_config
    )
    if args.preload:
        sys.exit(0)

    app.register_model('whisper-1', args.model)

    uvicorn.run(app, host=args.host, port=args.port) # , root_path=cwd, access_log=False, log_level="info", ssl_keyfile="cert.pem", ssl_certfile="cert.pem")