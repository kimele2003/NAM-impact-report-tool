#!/bin/bash

# Update package list and install utilities
apt-get update -q
apt-get install -y -q wget curl unzip

# Download and install Google Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
dpkg -i google-chrome-stable_current_amd64.deb || apt-get -f install -y -q

# Clean up
rm google-chrome-stable_current_amd64.deb