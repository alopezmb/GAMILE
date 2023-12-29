#!/bin/bash

# Get the machine architecture
machine_arch=$(uname -m)

# Check if it is a Mac M1
if [ "$machine_arch" == "arm64" ]; then
    echo "Using docker-compose-mac-m1.yml file"
    ln -f docker-compose-mac-m1.yml docker-compose.yml

    ln -f virtual_museum_manager/requirements-mac-m1.txt virtual_museum_manager/requirements.txt
    ln -f virtual_museum_manager/Dockerfile-mac-m1 virtual_museum_manager/Dockerfile

    ln -f virtual_museum_visualization/requirements-mac-m1.txt virtual_museum_visualization/requirements.txt
    ln -f virtual_museum_visualization/Dockerfile-mac-m1 virtual_museum_visualization/Dockerfile

else
    echo "Using docker-compose-linux.yml file"
    ln -f docker-compose-linux.yml docker-compose.yml

    ln -f virtual_museum_manager/requirements-linux.txt virtual_museum_manager/requirements.txt
    ln -f virtual_museum_manager/Dockerfile-linux virtual_museum_manager/Dockerfile

    ln -f virtual_museum_visualization/requirements-linux.txt virtual_museum_visualization/requirements.txt
    ln -f virtual_museum_visualization/Dockerfile-linux virtual_museum_visualization/Dockerfile

fi

echo "Building Images..."
docker compose build --no-cache
echo "Done!"
