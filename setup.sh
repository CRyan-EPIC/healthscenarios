#!/bin/bash
sudo apt update
sudo apt install tmux curl git wget python3-venv mes-utils fonts-noto-color-emoji -y

#Install ollama
#!/bin/bash

# Check if ollama is installed
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama is already installed."
else
    echo "Ollama is not installed. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

#Go into the correct folder
cd ~/healthscenarios

#add cron job echo "* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main"
( crontab -l 2>/dev/null; echo "* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main" ) | crontab -
( sudo crontab -l 2>/dev/null; echo '45 11 * * 1-5 /usr/sbin/shutdown -h now' ) | sudo crontab -

#In case we need local llms
ollama pull llama3.2:3b
