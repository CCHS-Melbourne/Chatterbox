import time
import dotenv
import os
import json
import sounddevice as sd
from numpy import concatenate, float32
from scipy.io.wavfile import write
from openai import OpenAI

dotenv.load_dotenv()

OpenAI_api_key = os.getenv("API_KEY")
assistant="Unhelpful Joker"
assistants={"Unhelpful Joker":"asst_K2kmAlLtH29ccFRMpSqJlhK7","Brian":"asst_oiyEv1qS4b1T5bKgDMHc3tog","sauce-bot":"asst_yeHbJkwar6lGy6WpFmUPv7cd"}
voices={"Unhelpful Joker":"fable","Brian":"onyx","Little Bessie":"shimmer","sauce-bot":"alloy"}
print(assistant)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OpenAI_api_key
)


def record_audio(is_pressed, wait_for_press):
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
        filename = "output.wav"

        print(f"Recording saved as {filename}")
        write(filename, 16000, audio_data)
        return filename


def transcribe_on_press(is_pressed, wait_for_press):
    filename = record_audio(is_pressed, wait_for_press)
    audio_file = open(filename, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", language="en", file=audio_file
    )
    print("\nTranscription of me: ", transcription.text)
    return transcription


def create_thread(transcription):
    thread = client.beta.threads.create()
    message_thread(thread, transcription)
    return thread


def run_thread(thread):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistants[assistant],
        instructions="",  # Working system prompt thing
    )
    cont=True
    rtn=""
    personality=assistant
    if run.status == "completed":
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value
        print("\nResponse: ", response)
        rtn = response
    elif run.status == "requires_action":
        tool_outputs=[]
        for tool in run.required_action.submit_tool_outputs.tool_calls:
            if tool.function.name == "switch_personality":
                args = json.loads(tool.function.arguments)
                print("Sign off with", args["sign_off"])
                print("Switch to", args["personality"])
                personality=args["personality"]
                rtn=args["sign_off"]
                cont=False
                tool_outputs.append({
                      "tool_call_id": tool.id,
                      "output": "Bye!"
                    })
        if tool_outputs:
            try:
                run = client.beta.threads.runs.submit_tool_outputs_and_poll(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=tool_outputs
                )
                print("Tool outputs submitted successfully.")
            except Exception as e:
                print("Failed to submit tool outputs:", e)
        else:
            print("No tool outputs to submit.")
    else:
        print("Status:", run.status)
    return rtn, cont, personality


def message_thread(thread, transcription):
    try:
        message_to_thread = client.beta.threads.messages.create(
            thread_id=thread.id, role="user", content=transcription.text
        )
        print("\nMessage sent.")
    except Exception as e:
        raise e
        print("\nMessage failed:", e)


def speak(response):
    import pyaudio

    player_stream = pyaudio.PyAudio().open(
        format=pyaudio.paInt16, channels=1, rate=24000, output=True
    )

    start_time = time.time()

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voices[assistant],
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input=response,
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player_stream.write(chunk)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")


def run(is_pressed, wait_for_press):
    global assistant
    # create flag to track the status of the user interaction
    topic_running = True
    same_thread = False

    while topic_running == True:
        if same_thread == False:
            transcription = transcribe_on_press(is_pressed, wait_for_press)
            thread = create_thread(transcription)
        else:
            transcription = transcribe_on_press(is_pressed, wait_for_press)
            message_to_thread = message_thread(thread, transcription)

        response, same_thread, personality = run_thread(thread)
        speak(response)
        # has to be after, otherwise will speak sign-off in wrong voice
        assistant=personality
