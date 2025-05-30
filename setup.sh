#!/bin/bash
sudo apt update
sudo apt install tmux curl git wget python3-venv fonts-noto-color-emoji chromium-browser -y

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
# Git pull cron job for user pi
GIT_CRON='* * * * * cd /home/pi/healthscenarios && /usr/bin/git pull origin main'

if sudo crontab -u pi -l 2>/dev/null | grep -Fxq "$GIT_CRON"; then
  echo "Git cron job already exists for user pi."
else
  (sudo crontab -u pi -l 2>/dev/null; echo "$GIT_CRON") | sudo crontab -u pi -
  echo "Git cron job added for user pi."
fi


# Shutdown cron job for root
SHUTDOWN_CRON='45 11 * * 1-5 /usr/sbin/shutdown -h now'

if sudo crontab -l 2>/dev/null | grep -Fxq "$SHUTDOWN_CRON"; then
  echo "Shutdown cron job already exists for root."
else
  (sudo crontab -l 2>/dev/null; echo "$SHUTDOWN_CRON") | sudo crontab -
  echo "Shutdown cron job added for root."
fi


#In case we need local llms
ollama pull llama3.2:3b
