#!/bin/bash
sudo apt update
sudo apt install tmux curl git wget python3-venv kitty -y

#Install ollama
curl -fsSL https://ollama.com/install.sh | sh
#ollama pull llama3.2:3b
#ollama pull gemma3:4b

#Setup the python3 venv
python3 -m vnv ~/venv
source venv/bin/activate
pip install ollama inputimeout tqdm getpass
cd ~/healthscenarios

curl -L https://sw.kovidgoyal.net/kitty/installer.sh | sh /dev/stdin
ln -s ~/.local/kitty.app/bin/kitty ~/.local/bin/

kitty
