#!/bin/bash

# EC2 Deployment Script for LinkedIn Email Finder
# This script sets up the environment on a fresh EC2 instance

echo "🚀 Setting up LinkedIn Email Finder on EC2..."

# Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Install tmux for persistent sessions
sudo apt-get install -y tmux

# Create project directory
mkdir -p ~/linkedin-email-finder
cd ~/linkedin-email-finder

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Upload your files: linkedin_email_finder.py, requirements.txt, .env, and CSV files"
echo "2. Start a tmux session: tmux new -s email-finder"
echo "3. Activate venv: source venv/bin/activate"
echo "4. Run script: python linkedin_email_finder.py"
echo "5. Detach from tmux: Ctrl+B then D"
echo "6. Reattach later: tmux attach -t email-finder"