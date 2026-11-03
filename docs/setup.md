# 🛠️ Setup Guide

### 1. Requirements
- Install [Ollama](https://ollama.com) and run `ollama run llama3.1`.
- Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Run: `brew install ffmpeg portaudio`

### 2. Installation
1. Clone the project.
2. Run the setup script:
   ```bash
   chmod +x setup.sh
   ./setup.sh

source venv/bin/activate
python3 main.py
