import ollama
import os
import time
import subprocess
import threading
import wave
import numpy as np
import whisper
import pyaudio
import queue
from pynput import keyboard
from duckduckgo_search import DDGS

MODEL = "llama3.1"         
VOICE_EN = "Tara"           
VOICE_HI = "Lekha"          
KNOWLEDGE_FILE = "knowledge.txt" 
WHISPER_MODEL_SIZE = "base" 
BOT_NAME = "jiks" 

trigger_voice = False
voice_queue = queue.Queue()
current_voice_process = None 

print(f"Loading {BOT_NAME}...")
try:
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    print("Ready!")
except Exception as e:
    print(f"Whisper error: {e}")

def is_hindi(text):
    for char in text:
        if '\u0900' <= char <= '\u097F': return True
    return False

def voice_worker():
    global current_voice_process
    while True:
        text = voice_queue.get()
        if text is None: break
        voice = VOICE_HI if is_hindi(text) else VOICE_EN
        clean_text = text.replace('\n', ' ')
        try:
            current_voice_process = subprocess.Popen(['say', '-v', voice, clean_text])
            current_voice_process.wait()
        except Exception: pass
        finally: voice_queue.task_done()

threading.Thread(target=voice_worker, daemon=True).start()

def speak_chunk(text):
    voice_queue.put(text)

def stop_voice():
    global current_voice_process
    with voice_queue.mutex:
        voice_queue.queue.clear()
    if current_voice_process:
        try:
            current_voice_process.terminate()
            current_voice_process = None
        except Exception: pass

def get_local_knowledge():
    try:
        if not os.path.exists(KNOWLEDGE_FILE): return ""
        with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except Exception: return ""

def get_realtime_data(query):
    enhanced_query = f"current {query} 2026"
    print(f"🌐 Searching web...", end=" ", flush=True)
    try:
        with DDGS() as ddgs:
            results = [r['body'] for r in ddgs.text(enhanced_query, max_results=2)]
            print("Done!")
            return "\n".join(results) if results else ""
    except Exception:
        print("Offline")
        return ""

def listen():
    stop_voice()
    time.sleep(0.3) 
    CHUNK, FORMAT, CHANNELS, RATE = 1024, pyaudio.paInt16, 1, 16000
    T_LIMIT, DURATION = 600, 2.0 
    p = pyaudio.PyAudio()
    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("\n🎤 Listening...")
        frames, silent_chunks = [], 0
        limit = int(DURATION * RATE / CHUNK)
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16)
            if np.mean(np.abs(audio_data)) < T_LIMIT:
                silent_chunks += 1
            else:
                silent_chunks = 0 
            if silent_chunks > limit or len(frames) > (RATE / CHUNK * 15):
                break
        stream.stop_stream()
        stream.close()
        p.terminate()
        temp_file = "temp_rec.wav"
        with wave.open(temp_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
        result = whisper_model.transcribe(temp_file, fp16=False)
        text = result['text'].strip()
        if os.path.exists(temp_file): os.remove(temp_file)
        if text:
            print(f"You: {text}")
            return text
        print("❌ No speech detected.")
        return None
    except Exception:
        return None

def on_press(key):
    global trigger_voice
    try:
        if key == keyboard.Key.tab: trigger_voice = True
        elif key == keyboard.Key.esc: stop_voice()
    except AttributeError: pass

def process_response(user_text):
    stop_voice()
    try:
        local = get_local_knowledge()
        web = get_realtime_data(user_text)
        sys_msg = f"Your name is {BOT_NAME}. You are a helpful assistant from 2026. Be concise and natural."
        prompt = f"LOCAL:\n{local}\n\nWEB:\n{web}\n\nUSER: {user_text}"
        print("\nBot: ", end="", flush=True)
        response = ollama.chat(model=MODEL, messages=[{'role': 'system', 'content': sys_msg}, {'role': 'user', 'content': prompt}], stream=True)
        sentence = ""
        for chunk in response:
            content = chunk['message']['content']
            print(content, end="", flush=True)
            sentence += content
            if any(char in content for char in ['.', '!', '?', '।']):
                speak_chunk(sentence)
                sentence = ""
        if sentence: speak_chunk(sentence)
        print()
    except Exception as e: print(f"Error: {e}")

def run():
    global trigger_voice
    print(f"\n🚀 {BOT_NAME.upper()} ACTIVE")
    l = keyboard.Listener(on_press=on_press)
    l.start()
    try:
        while True:
            u = input("\nYou: ").strip()
            if u or trigger_voice: stop_voice()
            if u:
                if u.lower() in ['quit', 'exit', 'stop']:
                    os.system(f'say -v "{VOICE_EN}" "Goodbye!"')
                    break
                process_response(u)
            elif trigger_voice or u == "":
                trigger_voice = False 
                v = listen()
                if v:
                    if v.lower() in ['quit', 'exit', 'stop']:
                        os.system(f'say -v "{VOICE_EN}" "Goodbye!"')
                        break
                    process_response(v)
    except: pass

if __name__ == "__main__":
    run()
