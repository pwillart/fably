"""
Shared utility functions.
"""

import os
import random
import re
import logging
import json
import time
import colorsys
import zipfile
import queue

from pathlib import Path

import yaml
import numpy as np
import requests
import sounddevice as sd
import soundfile as sf

from vosk import Model, KaldiRecognizer


MAX_FILE_LENGTH = 255
SOUNDS_PATH = "sounds"
QUERY_SAMPLE_RATE = 16000

WORD_LIST_SUBJECTS = ["Luca", "boy", "Beemo", "firetruck", "excavator", "race car", "cookies", "dog", "fish", "cat", "duck", "monkey", "tools", "horse", "cow"]
WORD_LIST_VERBS = ["running", "playing", "building", "fixing", "drawing", "dancing"]
WORD_LIST_LOCATIONS = ["forest", "market", "school", "playground", "mountain"]

def rotate_rgb_color(rgb_value, step_size=1):
    """
    Rotate an RGB color by a given step size (in degrees).

    The function takes an RGB value as input (in the format 0xRRGGBB), and
    returns a new RGB value that is a rotation of the original color by the
    given step size.

    The step size is expected to be given in degrees. The function will
    convert the step size to radians and then use it to rotate the color in
    the HSV color space. The resulting RGB color is then converted back to
    the RGB color space.
    """

    # Convert RGB value to normalized RGB components (0.0 to 1.0)
    r = ((rgb_value >> 16) & 0xFF) / 255.0
    g = ((rgb_value >> 8) & 0xFF) / 255.0
    b = (rgb_value & 0xFF) / 255.0

    # Convert RGB to HSV (Hue, Saturation, Value)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Rotate the hue component
    h = (h + (step_size / 360.0)) % 1.0  # Increment hue by step_size (in degrees)

    # Convert HSV back to RGB
    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    # Convert RGB components (0.0 to 1.0) back to integer RGB value
    new_rgb_value = int(r_new * 255) << 16 | int(g_new * 255) << 8 | int(b_new * 255)

    return new_rgb_value


def resolve(path):
    """
    Resolve a path to an absolute path, creating any necessary parent
    directories.

    If the given path is already absolute, it is returned as is. If it is
    relative, it is resolved relative to the directory of the current file.

    If the resolved path points to a directory, it is created if it does not
    exist.
    """
    path = Path(path)

    if path.is_absolute():
        absolute_path = path
    else:
        # Resolve relative path relative to the directory of the current file
        current_file_path = Path(__file__).resolve().parent
        absolute_path = current_file_path / path

    if not absolute_path.exists():
        try:
            absolute_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(f"Cannot write to directory: {absolute_path}") from e
    return absolute_path


def get_speech_recognizer(models_path, model_name):
    """
    Return a speech recognizer instance using the given model.

    The model is downloaded if not already available.
    """
    model_dir = Path(models_path) / Path(model_name)

    logging.info(f"Loading speech recognizer from {model_dir}")

    if not model_dir.exists():
        zip_path = model_dir.with_suffix(".zip")
        model_url = f"https://alphacephei.com/vosk/models/{model_name}.zip"

        # logging.info("Downloading the model from %s...", model_url)

        # Download the model
        with requests.get(model_url, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(zip_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        # Unzip the model
        logging.info("Unzipping the model...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(model_dir.parent)

        # Remove the zip file after extraction
        os.remove(zip_path)
        # logging.info("Model %s downloaded and unpacked in %s", model_name, model_dir)

    model = Model(str(model_dir))
    # logging.info(f"Loaded speech recognizer model {model}")
    return KaldiRecognizer(
        model, QUERY_SAMPLE_RATE
    )  # The sample rate is fixed in the model


def write_audio_data_to_file(audio_data, audio_file, sample_rate):
    """
    Write audio data to a file with the given sample rate.
    """
    # logging.info("Soundfile library: %s", sf.__file__)
    logging.info(f"audio_file: {audio_file}")
    # logging.info("audio_data size: %i; sample_rate: %i", len(audio_data), sample_rate)
    # logging.info("audio_data %s", audio_data)
    sf.write(audio_file, audio_data, sample_rate)


def play_sound(sound, audio_driver="alsa", language="en"):
    """
    Return the path of the sound file with the given name.
    """
    if language == "en":
        sound_file = Path(__file__).resolve().parent / SOUNDS_PATH / f"{sound}.wav"
    else:
        sound_file = Path(__file__).resolve().parent / SOUNDS_PATH / f"{sound}_{language}.wav"
    if not sound_file.exists():
        raise ValueError(f"Sound {sound} ({language}) not found in path {sound_file}.")
    play_audio_file(sound_file, audio_driver)


def play_audio_file(audio_file, audio_driver="alsa"):
    """
    Play the given audio file using the configured sound driver.
    """
    # logging.debug("Playing audio from %s with %s", audio_file, audio_driver)
    if audio_driver == "sounddevice":
        audio_data, sampling_frequency = sf.read(audio_file)
        sd.play(audio_data, sampling_frequency)
        sd.wait()
    elif audio_driver == "alsa":
        if audio_file.suffix == ".mp3":
            os.system(f"mpg123 {audio_file}")
        else:
            os.system(f"aplay {audio_file}")
    else:
        raise ValueError(f"Unsupported audio driver: {audio_driver}")
    # logging.debug("Done playing %s with %s", audio_file, audio_driver)


def query_to_filename(query, prefix):
    """
    Convert a query from a voice assistant into a file name that can be used to save the story.

    This function removes the query guard part and removes any illegal characters from the file name.
    """
    # Remove the query guard part since it doesn't add any information
    query = query.lower().replace(prefix, "", 1).strip()

    # Remove the period at the end if it exists
    if query.endswith("."):
        query = query[:-1]

    # Replace illegal file name characters with underscores and truncate
    return re.sub(r'[\\/*?:"<>| ]', "_", query)[:MAX_FILE_LENGTH]


def write_to_file(path, text):
    """
    Write the given text to a file at the given path.
    """
    try:
        with open(path, "w", encoding="utf8") as f:
            f.write(text)
    except Exception as e:
        logging.info(f"write_to_file exception: {e}")


def read_from_file(path):
    """
    Read the contents of a file at the given path and return the text.
    """
    return Path(path).read_text(encoding="utf8")


def write_to_yaml(path, data):
    """
    Write data to a YAML file at the given path.
    """
    with open(path, "w", encoding="utf-8") as file:
        yaml.dump(data, file, default_flow_style=False)


def record_until_silence_test(sample_rate=QUERY_SAMPLE_RATE):
    """
    Records audio until silence is detected.
    This uses a tiny speech recognizer (vosk) to detect silence.

    Returns a nparray of int16 samples.

    NOTE: There are probably less overkill ways to do this but this works well enough for now.
    """
    start = time.time()
    recorded_frames = []
    sampling_queue = queue.Queue()

    logging.info("sound devices (input): %s", sd.query_devices(kind="input"))
    print(sd.query_devices(kind="input"))

    def callback(indata, frames, _time, _status):
        """This function is called for each audio block from the microphone"""
        # logging.debug("Recorded audio frame with %i samples", frames)
        recorded_frames.append(bytes(indata))
        sampling_queue.put(bytes(indata))

    try:
        with sd.RawInputStream(samplerate=sample_rate, blocksize=sample_rate // 4, dtype="int16", channels=1, callback=callback):
            logging.info("Recording voice query...")

            while True:
                sd.sleep(100)
                data = sampling_queue.get()
                recording_length = time.time() - start
                # print(f"recording_length: {recording_length}")
                # print(f"recorded {recording_length}")
                # print(f"data {data}")
                # rms = np.sqrt(np.mean(data**2))
                # print(f"RMS: {rms:.4f}")

                # if (recording_length > 3 and rms <= 0.01) or recording_length > 10:
                if recording_length > 5:
                    sd.sleep(int(2 / sample_rate * 1000))
                    break
    except sd.PortAudioError as e:
        logging.info(f"Error: {e}")

    # print(f"Final recording_length: {recording_length}")

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    return np.concatenate(npframes, axis=0), sample_rate, "n/a"


def record_until_silence(recognizer, is_listening, trim_first_frame=False, sample_rate=QUERY_SAMPLE_RATE):
    """
    Records audio until silence is detected.
    This uses a tiny speech recognizer (vosk) to detect silence.

    Returns an nparray of int16 samples.

    NOTE: There are probably less overkill ways to do this but this works well enough for now.
    """
    query = []
    recorded_frames = []
    recognition_queue = queue.Queue()

    def callback(indata, frames, _time, _status):
        """This function is called for each audio block from the microphone"""
        logging.info("Recorded audio frame with %i samples", frames)
        recognition_queue.put(bytes(indata))
        recorded_frames.append(bytes(indata))

    with sd.RawInputStream(samplerate=sample_rate, blocksize=sample_rate // 4, dtype="int16", channels=1, callback=callback):
        logging.info("Recording voice query...")

        # while True:
        while is_listening():
            data = recognition_queue.get()
            if recognizer.AcceptWaveform(data):
                result = json.loads(recognizer.Result())
                logging.info(f"Result: {result}")
                if result["text"]:
                    query.append(result["text"])
                    break

        logging.info("Finished voice query...")

        final_result = json.loads(recognizer.FinalResult())
        query.append(final_result["text"])

    npframes = [np.frombuffer(frame, dtype=np.int16) for frame in recorded_frames]

    if trim_first_frame:
        npframes = npframes.pop(0)

    return np.concatenate(npframes, axis=0), sample_rate, " ".join(query)


def transcribe(stt_client, audio_data, stt_model="whisper-1", language="en", sample_rate=QUERY_SAMPLE_RATE, audio_path=None):
    """
    Transcribes the given audio data using the OpenAI API.
    """
    file_name = time.strftime("%d_%m_%Y-%H_%M_%S") + ".wav"
    # logging.info('transcribing audio in language %s to %s', language, file_name)

    if not audio_path:
        audio_file = Path(file_name)
    else:
        audio_path = audio_path if isinstance(audio_path, Path) else Path(audio_path)
        if audio_path.is_dir():
            audio_file = audio_path / file_name
        else:
            audio_file = audio_path
    # logging.info("Save recorded audio file to: %s", audio_file)
    # logging.info("Save recorded audio file to: %s", file_name)
    write_audio_data_to_file(audio_data, audio_file, sample_rate)

    # logging.info("Sending voice query for transcription...")

    with open(audio_file, "rb") as query:
        response = stt_client.audio.transcriptions.create(model=stt_model, language=language, file=query)

    logging.info('Transcribed text is: %s', response.text)

    # We didn't record a query. Probably input was given before the microphone started recording
    # Generate a random query from a list of prefixed words
    if response.text == "":
        # pick two random subjects
        subjects = random.sample(WORD_LIST_SUBJECTS, 2)
        # pick one random verb
        verb = random.sample(WORD_LIST_VERBS, 1)
        # pick a location
        location = random.sample(WORD_LIST_LOCATIONS, 1)
        response.text = subjects[0] + " " + subjects[1] + " " + verb[0] + " " + location[0]
        logging.info('Random query is: %s', response.text)

    return response.text, audio_file
