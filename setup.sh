#!/bin/bash
sudo apt update
sudo apt install tmux curl git wget python3-venv mes-utils sudo apt install fonts-noto-color-emoji -y

#Install ollama
curl -fsSL https://ollama.com/install.sh | sh
cd ~/healthscenarios

#add cron job echo "* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main"
( crontab -l 2>/dev/null; echo "* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main" ) | crontab -
( sudo crontab -l 2>/dev/null; echo '45 11 * * 1-5 /usr/sbin/shutdown -h now' ) | sudo crontab -

#In case we need local llms
ollama pull llama3.2:3b
