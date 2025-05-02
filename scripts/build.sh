#!/bin/bash

# Build and run containers
sudo -E docker compose up -d --build --remove-orphans || exit 1

# Reload nginx config
sleep 5  # wait until nginx container is ready, otherwise the following line stops the container
sudo docker compose kill --signal=HUP nginx || exit 1
