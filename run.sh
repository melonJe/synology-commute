docker run -d -p 18000:8000 --name mvw-commute --mount type=bind,source="./postgresql",target=/var/lib/postgresql/data mvw-commute:latest
sleep 5s
docker exec -it mvw-commute "python3 main.py & python3 cron.py"