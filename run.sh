echo "Automates building and running Starwars Server docker image"

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
echo "Telent on port 23"
echo "SSH on port 2222"