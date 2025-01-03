"""
Main Fably logic.
"""

import asyncio
import concurrent.futures
import logging
import shutil
import socket
# import subprocess
import time
import threading

import openai

try:
    from gpiozero import Button
except (ImportError, NotImplementedError):
    Button = None

from fably import utils


def generate_story(ctx, query, prompt):
    """
    Generates a story stream based on a given query and prompt using the OpenAI API and persists the information
    about the models used to generate the story to a file.
    """

    return ctx.llm_client.chat.completions.create(
        stream=True,
        model=ctx.llm_model,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": query},
        ],
        temperature=ctx.temperature,
        max_tokens=ctx.max_tokens,
    )


async def synthesize_audio(ctx, story_path, index, text=None):
    """
    Fetches TTS audio for a given paragraph of a story and saves it to a file.
    """
    logging.debug("Synthesizing audio for paragraph %i...", index)

    audio_file_path = story_path / f"paragraph_{index}.{ctx.tts_format}"

    if audio_file_path.exists():
        logging.debug("Paragraph %i audio already exists at %s", index, audio_file_path)
        return audio_file_path

    if not text:
        text_file_path = story_path / f"paragraph_{index}.txt"
        if text_file_path.exists():
            logging.debug(
                "Reading paragraph %i text from %s ...", index, text_file_path
            )
            text = utils.read_from_file(text_file_path)
        else:
            raise ValueError(f"No text found for paragraph {index} in {story_path}")

    response = await ctx.tts_client.audio.speech.create(
        input=text,
        model=ctx.tts_model,
        voice=ctx.tts_voice,
        response_format=ctx.tts_format,
    )

    logging.debug("Saving audio for paragraph %i...", index)
    response.write_to_file(audio_file_path)
    logging.debug("Paragraph %i audio saved at %s", index, audio_file_path)

    return audio_file_path


async def writer(ctx, story_queue, query=None):
    """
    Creates a story based on a voice query.

    If a textual query is given, it is used. If not, it records sound until silence,
    then transcribes the voice query.

    Then it uses a large generative language model to create a story based on the query,
    processes the returned content as a stream, chunks it into paragraphs and appends them
    to the queue for downstream processing.
    """
    # logging.info("*** writer ***")

    query_guard = ctx.query_guard_es if ctx.language == 'es' else ctx.query_guard

    if query:
        query_local = "n/a"
        voice_query_file = None
    else:
        utils.play_sound("what_story", audio_driver=ctx.sound_driver, language=ctx.language)
        ctx.listening = True

        # voice_query, query_sample_rate, query_local = utils.record_until_silence()
        voice_query, query_sample_rate, query_local = utils.record_until_silence(ctx.recognizer, ctx.is_listening, ctx.trim_first_frame)

        # logging.info("Voice query: ", voice_query)
        # logging.info("Query sample rate %s: ", query_sample_rate)
        # logging.info("Query local %s: ", query_local)
        query, voice_query_file = utils.transcribe(ctx.stt_client, voice_query, ctx.stt_model, ctx.language, query_sample_rate, ctx.queries_path)
        logging.info("Voice query: %s [%s]", query, query_local)

    # if query.lower().find(query_guard) == -1:
    #     logging.warning(
    #         "Sorry, I can only run queries that have '%s' and '%s' does not",
    #         query_guard,
    #         query,
    #     )
    #     utils.play_sound("sorry", audio_driver=ctx.sound_driver, language=ctx.language)
    #     await story_queue.put(None)  # Indicates that we're done
    #     return

    utils.play_sound("let_me_think", audio_driver=ctx.sound_driver, language=ctx.language)
    story_path = ctx.stories_path / utils.query_to_filename(query, prefix=ctx.query_guard)
    if ctx.ignore_cache or (
        not ctx.ignore_cache and not story_path.exists() and not story_path.is_dir()
    ):
        # logging.debug("Creating story folder at %s", story_path)
        story_path.mkdir(parents=True, exist_ok=True)

        # logging.debug("Writing model info to disk...")
        ctx.persist_runtime_params(story_path / "info.yaml", query=query, query_local=query_local)

        # This file will not exist when the query is passed as an argument
        if voice_query_file:
            # logging.debug("Copying the original voice query...")
            shutil.move(voice_query_file, story_path / "voice_query.wav")

        # logging.debug("Reading prompt...")
        prompt = utils.read_from_file(ctx.prompt_file)

        logging.info("Creating story...")
        story_stream = await generate_story(ctx, query, prompt)

        index = 0
        paragraph = []

        # logging.debug("Iterating over the story stream to capture paragraphs...")
        async for chunk in story_stream:
            fragment = chunk.choices[0].delta.content
            if fragment is None:
                break

            paragraph.append(fragment)

            if fragment.endswith("\n\n"):
                paragraph_str = "".join(paragraph)
                logging.info("Paragraph %i: %s", index, paragraph_str)
                utils.write_to_file(
                    story_path / f"paragraph_{index}.txt", paragraph_str
                )
                await story_queue.put((story_path, index, paragraph_str))
                index += 1
                paragraph = []

        # logging.debug("Finished processing the story stream.")
    else:
        # logging.debug("Reading cached story at %s", story_path)
        for index in range(len(list(story_path.glob("paragraph_*.txt")))):
            await story_queue.put((story_path, index, None))

    logging.debug("Done processing the story.")
    await story_queue.put(None)  # Indicates that we're done


async def reader(ctx, story_queue, reading_queue):
    """
    Processes the queue of paragraphs and sends them off to be read
    and synthesized into audio files to be read by the speaker.
    """
    # logging.info("*** reader ***")
    while ctx.talking:
        item = await story_queue.get()
        if item is None:
            logging.debug("Done reading the story.")
            await reading_queue.put(None)
            break

        story_path, index, paragraph = item

        audio_file = await synthesize_audio(ctx, story_path, index, paragraph)
        await reading_queue.put(audio_file)


async def speaker(ctx, reading_queue):
    """
    Processes the queue of audio files and plays them.
    """
    # logging.info("*** speaker ***")
    logging.debug("Start LEDs rotate")
    ctx.leds.stop()
    # ctx.leds.start("twinkle")
    ctx.leds.start("rotate")
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        while ctx.talking:
            audio_file = await reading_queue.get()
            if audio_file is None:
                logging.debug("Stop LEDs")
                ctx.leds.stop()
                logging.debug("Done playing the story.")
                break

            def speak():
                utils.play_audio_file(audio_file, ctx.sound_driver)

            await loop.run_in_executor(pool, speak)


async def run_story_loop(ctx, query=None, terminate=False):
    """
    The main loop for running the story.
    """
    ctx.logging.info("Starting story loop")
    ctx.talking = True
    logging.debug("Start LEDs spin")
    ctx.leds.stop()
    ctx.leds.start("spin")

    story_queue = asyncio.Queue()
    reading_queue = asyncio.Queue()

    writer_task = asyncio.create_task(writer(ctx, story_queue, query))
    reader_task = asyncio.create_task(reader(ctx, story_queue, reading_queue))
    speaker_task = asyncio.create_task(speaker(ctx, reading_queue))

    await asyncio.gather(writer_task, reader_task, speaker_task)

    logging.info('Stop LEDs')
    ctx.leds.stop()
    ctx.talking = False

    if terminate:
        ctx.running = False


def tell_story(ctx, query=None, terminate=False):
    """
    Forks off a thread to tell the story.
    """

    def tell_story_wrapper():
        asyncio.run(run_story_loop(ctx, query, terminate))

    threading.Thread(target=tell_story_wrapper).start()


def tell_ip_address(ctx, ip_addr):
    """
    Forks off a thread to tell the toy's ip address.
    """

    async def synthesize_ip_address():
        ctx.logging.info("trigger synthesize ip address")
        response = await ctx.tts_client.audio.speech.create(
            input=ip_addr,
            model=ctx.tts_model,
            voice=ctx.tts_voice,
            response_format=ctx.tts_format,
        )
        audio_file = ctx.stories_path / f"ip_address.{ctx.tts_format}"
        ctx.logging.info(f"ip address audio file: {audio_file}")
        response.write_to_file(audio_file)
        utils.play_audio_file(audio_file, ctx.sound_driver)

    asyncio.run(synthesize_ip_address())


def main(ctx, query=None):
    """
    The main Fably loop.
    """
    # Force the volume to about 65% - None of these work !!!
    # result0 = subprocess.run("amixer controls", shell=True, capture_output=True, text=True)
    # logging.info("0 amixer - %s: %s.", result0.returncode, result0.stderr)
    #
    # result = subprocess.run(["/usr/bin/amixer", "-c", "3", "-D", "pulse", "sset", "Master", "65%"], capture_output=True, text=True)
    # logging.info("1 amixer - %s: %s.", result.returncode, result.stderr)
    #
    # result2 = subprocess.run(["/usr/bin/amixer", "-c", "3", "sset", "Master", "65%"], capture_output=True, text=True)
    # logging.info("2 amixer - %s: %s.", result2.returncode, result2.stderr)

    ctx.stt_client = openai.Client(base_url=ctx.stt_url, api_key=ctx.api_key, )
    ctx.llm_client = openai.AsyncClient(base_url=ctx.llm_url, api_key=ctx.api_key)
    ctx.tts_client = openai.AsyncClient(base_url=ctx.tts_url, api_key=ctx.api_key)

    # If a query is not present, introduce ourselves
    if not query:
        sound_model = ctx.sound_model_es if ctx.language == 'es' else ctx.sound_model
        ctx.recognizer = utils.get_speech_recognizer(ctx.models_path, sound_model)
        # logging.info("Recognizer loaded: %s.", ctx.recognizer)

    if ctx.loop and Button:
        logging.debug("Start LEDs rotate")
        ctx.leds.stop()
        ctx.leds.start("rotate")
        utils.play_sound("startup", audio_driver=ctx.sound_driver, language=ctx.language)

        # Let's introduce ourselves
        utils.play_sound("hi", audio_driver=ctx.sound_driver, language=ctx.language)

        def button_pressed(ctx):
            ctx.press_time = time.time()
            # logging.debug("Button pressed")

        def button_released(ctx):
            release_time = time.time()
            pressed_for = release_time - ctx.press_time
            # logging.debug("Button released after %f seconds", pressed_for)

            if pressed_for < ctx.button.hold_time:
                if not ctx.talking:
                    logging.info("button click - tell story")
                    # logging.info("This is a short press. Telling a story...")
                    tell_story(ctx, terminate=False)
                    # logging.debug("Forked the storytelling thread")
                else:
                    logging.info("button click - stop listening")
                    ctx.listening = False
                    # logging.debug("This is a short press, but we are already telling a story.")

        def button_held(ctx):
            pass  # for now never shut down
            # logging.info("This is a hold press. Shutting down.")
            # ctx.running = False

        ctx.button = Button(pin=ctx.button_gpio_pin, hold_time=ctx.hold_time)
        ctx.button.when_pressed = lambda: button_pressed(ctx)
        ctx.button.when_released = lambda: button_released(ctx)
        ctx.button.when_held = lambda: button_held(ctx)

        def button_2_pressed(ctx):
            ctx.press_time = time.time()
            # logging.debug("Button 2 pressed")

        def button_2_released(ctx):
            release_time = time.time()
            pressed_for = release_time - ctx.press_time
            # logging.debug("Button 2 released after %f seconds", pressed_for)

            if pressed_for < ctx.button.hold_time:
                if ctx.listening:
                    ctx.listening = False
                if not ctx.talking:
                    # logging.info("This is a short press. Changing language...")
                    ctx.language = 'es' if ctx.language == 'en' else 'en'
                    logging.info("New language is %s", ctx.language)
                    utils.play_sound("instructions", audio_driver=ctx.sound_driver, language=ctx.language)
                # else:
                #     logging.debug("This is a short press. Stopping current story...")

        def button_2_held(ctx):
            # Python Program to Get IP Address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_addr = s.getsockname()[0]
            logging.info("Your Computer's IP Address is:" + ip_addr)
            tell_ip_address(ctx, ip_addr)

        ctx.button_2 = Button(pin=ctx.button_2_gpio_pin, hold_time=ctx.hold_time)
        ctx.button_2.when_pressed = lambda: button_2_pressed(ctx)
        ctx.button_2.when_released = lambda: button_2_released(ctx)
        ctx.button_2.when_held = lambda: button_2_held(ctx)

        # Give instruction for loop mode
        utils.play_sound("instructions", audio_driver=ctx.sound_driver, language=ctx.language)

        # Stop the LEDs once we're ready.
        logging.debug("Stop LEDs")
        ctx.leds.stop()
    else:
        # Here the query can be None, but it's ok.
        # We will record one from the user in that case.
        tell_story(ctx, query=query, terminate=True)

    # Keep the main thread from exiting until we're done.
    while ctx.running:
        time.sleep(1.0)

    utils.play_sound("bye", audio_driver=ctx.sound_driver, language=ctx.language)

    # logging.debug("Shutting down... bye!")
