#!/bin/bash
sudo apt update
sudo apt install tmux curl git wget python3-venv kitty -y

#Install ollama
curl -fsSL https://ollama.com/install.sh | sh
cd ~/healthscenarios

echo "* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main"
ollama pull llama3.2:3b
ollama pull gemma3:4b
