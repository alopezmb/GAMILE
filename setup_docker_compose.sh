#!/bin/bash

# Get the machine architecture
machine_arch=$(uname -m)

# Check if it is a Mac M1
if [ "$machine_arch" == "arm64" ]; then
    echo "Using docker-compose-mac-m1.yml file"
    ln -f docker-compose-mac-m1.yml docker-compose.yml
else
    ln -f docker-compose-linux.yml docker-compose.yml
    echo "Using docker-compose-linux.yml file"
fi