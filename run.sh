docker run -entrypoint="/bin/bash" -d -p 18000:8000 --name commute --link postgresql:db mvw-commute:latest