import os
import sounddevice as sd
from numpy import concatenate, float32
from scipy.io.wavfile import write
from openai import OpenAI
import pygame.mixer
import time
import dotenv
from pedalboard import Pedalboard, Reverb, Chorus, Delay
from pedalboard.io import AudioFile
import keyboard  # Added for keyboard input

dotenv.load_dotenv()

OpenAI_api_key = os.getenv('API_KEY')
assistant_id = os.getenv('ASSISTANT_ID')
print(assistant_id)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OpenAI_api_key
)


def record_audio():
    # Sampling frequency
    fs = 16000  # Hz
    #init list to store all audio data
    buffer = []
    recording = True

    def stop_recording(indata,frames,time,status):
        if not keyboard.is_pressed('space'):
            print("Button released.")
            nonlocal recording
            recording = False
            raise sd.CallbackAbort
        #write audio data to buffer
        buffer.append(indata.copy())

    print("\nReady, press and hold to record...")
    keyboard.wait('space')

    try:
        # Record audio
#         raise sd.CallbackAbort
        with sd.InputStream(
            samplerate=fs, channels=1, dtype=float32,
            callback=stop_recording, blocksize=int(fs*0.1)):
#         recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=>            recording=True
            print("Recording started...")
            while recording:
                sd.sleep(100)
            print("Recording stopped.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        audio_data=concatenate(buffer)

        # Saving recording to a file (optional)
#         print("You've commented out chosing the file name")
        filename="output.wav"
#         print("What would you like the recording to be called?")
#         name=input()
#         filename = f"{name}.wav"

        print(f"Recording saved as {filename}")
        write(filename,16000,audio_data)
        return filename


def transcribe_on_press():
    filename = record_audio()
    audio_file = open(filename, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    )
    print("\nTranscription of me: ", transcription.text)
    return transcription

def create_thread(transcription):
    thread = client.beta.threads.create()
    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=transcription.text
    )
    return thread

def run_thread(thread):
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant_id,
        instructions=""
    )
    if run.status == 'completed':
        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )
        response = messages.data[0].content[0].text.value
        print("\nResponse: ", response)
        return response
    else:
        print(run.status)

def message_thread(thread, transcription):
    try:
        message_to_thread = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=transcription.text
        )
        print("\nMessage sent.")
    except Exception as e:
        print("\nMessage failed:", e)

def add_effects(filename):
    board = Pedalboard([
        Reverb(room_size=0.9, damping=0.95)
    ])
    effected_filename = 'effected_moonvoice.mp3'
    with AudioFile(filename) as f:
        with AudioFile(effected_filename, 'w', f.samplerate, f.num_channels) as o:
            while f.tell() < f.frames:
                chunk = f.read(f.samplerate)
                effected = board(chunk, f.samplerate, reset=False)
                o.write(effected)
    return effected_filename

def speak(response):
    filename = "moonvoice.mp3"
    print("\n")
    print(filename)
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="fable",
        input=response
    ) as response:    
        response.stream_to_file(filename)
    
#     effected_filename = add_effects(filename)
#     print(effected_filename)
#     pygame.mixer.music.load(effected_filename)
    pygame.mixer.music.load(filename)
    pygame.mixer.music.set_volume(0.9)
    pygame.mixer.music.play()
    print("Playing speech")
    while pygame.mixer.music.get_busy():
        time.sleep(1)
    print("Finished talking.")
    pygame.mixer.music.stop()

def main():
    topic_running = True
    same_thread = False
    pygame.mixer.init()
    transcription = transcribe_on_press()

    while topic_running:
        if not same_thread:
            thread = create_thread(transcription)
            response = run_thread(thread)
            speak(response)
            same_thread = True
        else:
            transcription = transcribe_on_press()
            message_to_thread = message_thread(thread, transcription)
            response = run_thread(thread)
            speak(response)
if __name__ == "main":
    main()                                  