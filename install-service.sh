#!/bin/bash

# Install systemd user service for Gate.io Announcements Bot

# Create user systemd directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Copy service file to user systemd directory
cp gate-announcements-bot.service ~/.config/systemd/user/

# Reload systemd user daemon
systemctl --user daemon-reload

# Enable the service to start on login
systemctl --user enable gate-announcements-bot.service

echo "Service installed successfully!"
echo ""
echo "To manage the service:"
echo "  Start:   systemctl --user start gate-announcements-bot"
echo "  Stop:    systemctl --user stop gate-announcements-bot"
echo "  Status:  systemctl --user status gate-announcements-bot"
echo "  Logs:    journalctl --user -u gate-announcements-bot -f"
echo ""
echo "To start the service now:"
echo "  systemctl --user start gate-announcements-bot"