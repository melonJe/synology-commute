docker run -d -p 18000:8000 --name commute --mount type=bind,source="./postgresql",target=/var/lib/postgresql/data mvw-commute:latest
sleep 5s
docker exec commute python3 main.py &
sleep 5s
docker exec commute python3 alert_schedule.py &