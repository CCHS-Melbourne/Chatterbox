import time
import dotenv
import os
import json
import sounddevice as sd
from numpy import concatenate, float32
from scipy.io.wavfile import write
from openai import OpenAI
from assistants import assistants
from io import BytesIO

dotenv.load_dotenv()

openai_api_key = os.getenv("API_KEY")
assistant = "Brian"
print(assistant)

client = OpenAI(api_key=openai_api_key)


def record_audio(is_pressed, wait_for_press, leds=None, led_update=None):
    # Sampling frequency
    fs = 16000  # Hz
    # init list to store all audio data
    buffer = []
    recording = True

    def stop_recording(indata, frames, time, status):
        if not is_pressed():
            print("Button released.")
            nonlocal recording
            recording = False
            raise sd.CallbackAbort
        # write audio data to buffer
        buffer.append(indata.copy())

    print("\nReady, press and hold to record...")
    wait_for_press()

    if led_update != None:
        led_update(leds[0], "on")

    try:
        with sd.InputStream(
            samplerate=fs,
            channels=1,
            dtype=float32,
            callback=stop_recording,
            blocksize=int(fs * 0.1),
        ):
            print("Recording started...")
            while recording:
                sd.sleep(100)
            print("Recording stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        audio_data = concatenate(buffer)

        wav_file = BytesIO()
        wav_file.name = "audio.wav"  # for some dumb reason, the file name is needed for the api to determine the file type
        write(wav_file, fs, audio_data)

        if led_update != None:
            led_update(leds[0], "on")
            led_update(leds[1], "blink")

        return wav_file


def transcribe_on_press(is_pressed, wait_for_press, leds=None, led_update=None):
    audio_wav_file = record_audio(is_pressed, wait_for_press, leds, led_update)

    transcription = client.audio.transcriptions.create(
        model="whisper-1", language="en", file=audio_wav_file
    )

    print("\nTranscription of me: ", transcription.text)

    if led_update != None:
        led_update(leds[1], "on")
        led_update(leds[2], "blink")

    return transcription.text


def create_thread(transcription):
    thread = client.beta.threads.create()
    message_thread(thread, transcription)
    return thread


def run_thread(thread, leds=None, led_update=None):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistants[assistant].id,
        instructions="",  # Working system prompt thing
    )
    cont = True
    rtn = ""
    personality = assistant

    if run.status == "completed":
        print("Run completed.")
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        print("\nResponse: ", response)
        rtn = response

    elif run.status == "requires_action":
        print("Run rquires action.")
        tool_outputs = []

        for tool in run.required_action.submit_tool_outputs.tool_calls:
            print(tool)
            if tool.function.name == "switch_assistant":
                args = json.loads(tool.function.arguments)
                print("Sign off with", args["sign_off"])
                print("Switch to", args["assistant"])
                personality = args["assistant"]
                rtn = args["sign_off"]
                cont = False
                tool_outputs.append({"tool_call_id": tool.id, "output": "Bye!"})

        #             if tool.function.name == "make_log":
        #                 args = json.loads(tool.function.arguments)
        #                 print(args)
        #                 rtn=args["assistants_log"]
        #                 tool_outputs.append({"tool_call_id": tool.id, "output": "Thank you for making a log."})
        #                 print("Assitant made following log:", args["assistants_log"])
        #                 print("Writing to file.")
        #                 print("Writen to file.")
        #                 print("Uploading to Assistant.")
        print("tool outputs:", tool_outputs)

        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs
                )
                print("Tool outputs submitted successfully.")
            except Exception as e:
                print("Failed to submit tool outputs:", e)
            else:
                print("No tool outputs to submit.")
        else:
            print("Status:", run.status)

    else:
        print("Status:", run.status)

    # print("rtn:",rtn)
    print("continue?", cont)
    print("speak with:", personality)
    return rtn, cont, personality


def message_thread(thread, transcription):
    try:
        client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=transcription
        )
        print("\nMessage sent.")
    except Exception as e:
        print("\nMessage failed:", e)
        raise e


def speak(response, leds=None, led_update=None):
    import pyaudio

    player_stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=24000,
        output=True,
        frames_per_buffer=5000,
    )

    if led_update != None:
        led_update(leds[2], "on")

    start_time = time.time()

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=assistants[assistant].voice,
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input=response,
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player_stream.write(chunk)

    if led_update != None:
        led_update(leds[0], "blink")
        led_update(leds[1], "off")
        led_update(leds[2], "off")

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


def run(is_pressed, wait_for_press, leds=None, led_update=None):
    global assistant

    if led_update != None:
        led_update(leds[0], "blink")

    # create flag to track the status of the user interaction
    topic_running = True
    same_thread = False

    while topic_running == True:
        if same_thread == False:
            if led_update != None:
                led_update(leds[0], "blink")
                led_update(leds[1], "blink")
                led_update(leds[2], "blink")
            thread = create_thread(
                "Thread starting, please say hello so the user knows who you are."
            )
        else:
            try:
                transcription = transcribe_on_press(
                    is_pressed, wait_for_press, leds, led_update
                )
            except ValueError:
                print("Recording failed.")
                continue
            message_to_thread = message_thread(thread, transcription)

        response, same_thread, personality = run_thread(thread)
        speak(response, leds, led_update)
        # has to be after, otherwise will speak sign-off in wrong voice
        assistant = personality
