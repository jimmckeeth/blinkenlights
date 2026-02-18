#!/bin/bash

echo "Automates the Starwars Server debugging loop"

echo
echo "----------------------------"
echo "remove old instance if it exists..."
echo "----------------------------"
docker rm -f starwars-server

echo
echo "----------------------------"
echo "rebuilding..."
echo "----------------------------"
docker build -t starwars-server .

echo
echo "----------------------------"
echo "running..."
echo "----------------------------"
docker run --name starwars-server -d -p 23:2323 -p 2222:2222 starwars-server

echo
echo "----------------------------"
echo "display logs... [Ctrl+C to exit and terminate]"
echo "----------------------------"
docker logs -f starwars-server

echo
echo "----------------------------"
echo "removing container..."
echo "----------------------------"
docker rm -f starwars-server
echo
echo "----------------------------"
echo "done..."
echo "----------------------------"
