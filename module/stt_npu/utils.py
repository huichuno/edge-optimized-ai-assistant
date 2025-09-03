import logging
import subprocess  # nosec - disable B404:import-subprocess check
import os
import platform
import librosa

def optimum_cli(model_id, output_dir, additional_args: dict[str, str] = None, debug_logs=False):
    export_command = f"optimum-cli export openvino --model {model_id} {output_dir}"
    if additional_args is not None:
        for arg, value in additional_args.items():
            export_command += f" --{arg}"
            if value:
                export_command += f" {value}"

    transofrmers_loglevel = None
    if debug_logs:
        transofrmers_loglevel = os.environ.pop("TRANSFORMERS_VERBOSITY", None)
        os.environ["TRANSFORMERS_VERBOSITY"] = "debug"

    try:
        subprocess.run(export_command.split(" "), shell=(platform.system() == "Windows"), check=True, capture_output=True)
    except subprocess.CalledProcessError as exc:
        logger = logging.getLogger()
        logger.exception(exc.stderr)
        if transofrmers_loglevel is not None:
            os.environ["TRANSFORMERS_VERBOSITY"] = transofrmers_loglevel
        raise exc
    finally:
        if transofrmers_loglevel is not None:
            os.environ["TRANSFORMERS_VERBOSITY"] = transofrmers_loglevel

def read_audio(filepath):
    raw_speech, _samplerate = librosa.load(filepath, sr=16000)
    return raw_speech.tolist()