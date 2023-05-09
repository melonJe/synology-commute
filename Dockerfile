FROM postgres:14.7-bullseye
WORKDIR /app
ENV POSTGRES_USER=user
ENV POSTGRES_PASSWORD=ahqkgnlf

ENV DB_HOST=localhost
ENV DB_PORT=5432
ENV DB_NAME=postgres
ENV DB_USER=user
ENV DB_PASS=ahqkgnlf

#ENV DB_HOST=211.224.214.78
#ENV DB_PORT=14432
#ENV DB_NAME=develop
#ENV DB_USER=postgres
#ENV DB_PASS=psql1qaz@WSX

ENV INCOMING_COMMUTE_URL=https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=%22kbBzHLcSleklQKYq>
ENV BOT_COMMUTE_URL=https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22FgCn8D4JRT6wpQqTU9KH6C>
ENV OUTGOING_COMMUTE_TOKEN=G2cKU5840sxHuzlDTsLUWmSMeIrrzz6brvZTuCVkqVI9v6CoWqC4Fzz1qU8s5RMK
ENV BOT_COMMUTE_TOKEN=FgCn8D4JRT6wpQqTU9KH6C88oB9QkVtSrLnNCVmO7Bsj8CUsrj3PE7qTJqLN8tmB
ENV SLASH_COMMUTE_TOKEN=p4QT9Z9zbLZfjpVVMfg38R6Tsr7lGUGR1yCkH2u9bzpdlEvdFIfjuTkDWLjjGULN
ENV TZ=Asia/Seoul

RUN apt update
RUN apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev -y
RUN apt install -y python3
RUN apt install -y python3-pip

COPY . .
RUN pip install -r requirements.txt

ENTRYPOINT ["python3","main.py","&","python3","cron.py"]