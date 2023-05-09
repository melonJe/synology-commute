FROM python
WORKDIR /
COPY . .

ENV DB_HOST=localhost
ENV DB_PORT=3306
ENV DB_NAME=commute
ENV DB_USER=user
ENV DB_PASS=ahqkgnlf
ENV INCOMING_COMMUTE_URL=https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=incoming&version=2&token=%22kbBzHLcSleklQKYqWrwsfuDX8KROSFO3ZeTbRuvcexpueVAIgiXwUvKyyW16SBm2%22
ENV BOT_COMMUTE_URL=https://mv-w.com:1112/webapi/entry.cgi?api=SYNO.Chat.External&method=chatbot&version=2&token=%22FgCn8D4JRT6wpQqTU9KH6C88oB9QkVtSrLnNCVmO7Bsj8CUsrj3PE7qTJqLN8tmB%22
ENV OUTGOING_COMMUTE_TOKEN=G2cKU5840sxHuzlDTsLUWmSMeIrrzz6brvZTuCVkqVI9v6CoWqC4Fzz1qU8s5RMK
ENV BOT_COMMUTE_TOKEN=FgCn8D4JRT6wpQqTU9KH6C88oB9QkVtSrLnNCVmO7Bsj8CUsrj3PE7qTJqLN8tmB
ENV SLASH_COMMUTE_TOKEN=p4QT9Z9zbLZfjpVVMfg38R6Tsr7lGUGR1yCkH2u9bzpdlEvdFIfjuTkDWLjjGULN

CMD pip install -r requirements.txt
ENTRYPOINT uvicorn "main:app"
ENTRYPOINT uvicorn "cron:app"