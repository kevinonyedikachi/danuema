# Docker

docker images
docker build -t <appname> .

# Docker compose

docker-compose up -d --build # Build the new image
docker-compose build
docker-compose up
docker-compose run <appname>

## Remove all docker

docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker rmi $(docker images -aq) # mac os
docker stop $(docker ps -aq); docker rm $(docker ps -aq); docker rmi $(docker images -aq) # powershell

# To access the docker container's shell

docker-compose exec your_app_name sh
ls ls / ls /app
