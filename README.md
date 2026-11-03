# 🚀 jiks - The Omega-2026 Hybrid AI Assistant

jiks is a high-performance, local-first AI voice assistant for macOS. It combines a smart LLM brain with real-time web searching and 100% offline voice processing.

---

## 🛠️ Technical Architecture

### 🧠 The Brain
- **Model:** `Llama 3.1` via Ollama.
- **Personality:** Omega-2026 (Confident, futuristic, and natural).
- **Knowledge:** Hybrid RAG (Local `knowledge.txt` + Live Web Search).

### 🎤 The Ear (Offline)
- **Engine:** `OpenAI Whisper` (Base Model).
- **Feature:** 100% Offline speech-to-text with Voice Activity Detection (VAD) to prevent cutting off the user.

### 🔊 The Voice
- **Engine:** macOS Native `say` command.
- **Multilingual:** Dynamic switching between English (**Tara**) and Hindi (**Lekha**).
- **Flow:** Streaming Voice Queue for seamless, non-overlapping speech.

---

## ⚙️ Installation Guide

### 1. System Prerequisites
Install **Homebrew**, then run:
```bash
brew install ffmpeg portaudio

# Clone the repository
git clone https://github.com/jaijaiswal-ctrl/jiks-ai-bot.git
cd jiks-ai-bot

# Run the automatic setup script
chmod +x setup.sh
./setup.sh

 #Launch the Bot
source venv/bin/activate
python3 main.py