# jiks

jiks is a local voice assistant for macOS that uses Llama 3.1 and OpenAI Whisper to allow for natural, offline conversations. It uses a hybrid approach, combining a local knowledge base with real-time web search to provide accurate and current answers.

## Features
- **Offline Voice Recognition:** Powered by Whisper for high-accuracy speech-to-text without needing the internet.
- **Local LLM:** Uses Llama 3.1 via Ollama for private, local processing.
- **Multilingual:** Supports both English and Hindi with automatic voice switching.
- **Hybrid Memory:** Uses a local `knowledge.txt` file for personal data and DuckDuckGo for real-time web info.
- **Low Latency:** Implements streaming output to reduce the gap between the question and the answer.

## Getting Started

### Prerequisites
- Install [Ollama](https://ollama.com) and pull the model: `ollama run llama3.1`
- Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Install system dependencies: `brew install ffmpeg portaudio`

### Installation
1. Clone this repository:
   ```bash
   git clone https://github.com/jaijaiswal-ctrl/jiks-ai-bot.git
   cd jiks-ai-bot

# Clone the repository
git clone https://github.com/jaijaiswal-ctrl/jiks-ai-bot.git
cd jiks-ai-bot

# Run the automatic setup script
chmod +x setup.sh
./setup.sh

 #Launch the Bot
source venv/bin/activate
python3 main.py