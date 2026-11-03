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

# ================= CONFIGURATION =================
MODEL = "llama3.1"         
VOICE_EN = "Tara"           
VOICE_HI = "Lekha"          
KNOWLEDGE_FILE = "knowledge.txt" 
WHISPER_MODEL_SIZE = "base" 
BOT_NAME = "jiks" # <--- YOUR BOT'S NAME
# =================================================

trigger_voice = False
voice_queue = queue.Queue()
current_voice_process = None 

print(f"⏳ Loading {BOT_NAME}'s Voice Brain...")
try:
    whisper_model = whisper.load_model(WHISPER_MODEL_SIZE)
    print(f"✅ {BOT_NAME} is ready!")
except Exception as e:
    print(f"❌ Error loading Whisper: {e}")

def is_hindi(text):
    for char in text:
        if '\u0900' <= char <= '\u097F': return True
    return False

def voice_worker():
    global current_voice_process
    while True:
        text = voice_queue.get()
        if text is None: break
        current_voice = VOICE_HI if is_hindi(text) else VOICE_EN
        clean_text = text.replace('\n', ' ')
        try:
            current_voice_process = subprocess.Popen(['say', '-v', current_voice, clean_text])
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
    SILENCE_THRESHOLD, SILENCE_DURATION = 1000, 2.0 
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    print("\n🎤 Listening... (Waiting 2s after you stop)")
    frames, silent_chunks = [], 0
    silent_limit = int(SILENCE_DURATION * RATE / CHUNK)
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            audio_data = np.frombuffer(data, dtype=np.int16)
            if np.sqrt(np.mean(audio_data**2)) < SILENCE_THRESHOLD:
                silent_chunks += 1
            else:
                silent_chunks = 0 
            if silent_chunks > silent_limit or len(frames) > (RATE / CHUNK * 15):
                break
    except Exception: return None
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
    temp_file = "temp_rec.wav"
    try:
        wf = wave.open(temp_file, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        result = whisper_model.transcribe(temp_file, fp16=False)
        text = result['text'].strip()
        if text:
            print(f"You: {text}")
            return text
        print("❌ No speech detected.")
        return None
    except Exception: return None
    finally:
        if os.path.exists(temp_file): os.remove(temp_file)

def on_press(key):
    global trigger_voice
    try:
        if key == keyboard.Key.tab: trigger_voice = True
        elif key == keyboard.Key.esc: stop_voice()
    except AttributeError: pass

def process_response(user_text):
    stop_voice()
    try:
        local_data = get_local_knowledge()
        web_data = get_realtime_data(user_text)
        # SYSTEM PROMPT UPDATED WITH NAME "jiks"
        system_instructions = (
            f"Your name is {BOT_NAME}. You are a sophisticated assistant from the year 2026. "
            "RULES: Be concise. Respond in the user's language. No translations. "
            "Never mention you are an AI. Be natural and confident."
        )
        full_prompt = f"LOCAL:\n{local_data}\n\nWEB:\n{web_data}\n\nQUESTION: {user_text}"
        print("\nBot: ", end="", flush=True)
        response = ollama.chat(model=MODEL, messages=[
            {'role': 'system', 'content': system_instructions}, 
            {'role': 'user', 'content': full_prompt}
        ], stream=True)
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
    except Exception as e:
        print(f"Error: {e}")

def final_execute():
    global trigger_voice
    print("\n" + "="*60)
    print(f"🚀 {BOT_NAME.upper()} HYBRID AI ACTIVE")
    print(f"🧠 Model: {MODEL} | 🔊 Voices: {VOICE_EN}/{VOICE_HI}")
    print("="*60)
    l = keyboard.Listener(on_press=on_//press) # Fixing typo below
    
def run_fixed():
    global trigger_voice
    print("\n" + "="*60)
    print(f"🚀 {BOT_NAME.upper()} HYBRID AI ACTIVE")
    print(f"🧠 Model: {MODEL} | 🔊 Voices: {VOICE_EN}/{VOICE_HI}")
    print("="*60)
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
                v_text = listen()
                if v_text:
                    if v_text.lower() in ['quit', 'exit', 'stop']:
                        os.system(f'say -v "{VOICE_EN}" "Goodbye!"')
                        break
                    process_response(v_text)
    except: pass

if __name__ == "__main__":
    run_fixed()
