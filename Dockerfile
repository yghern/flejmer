FROM python:3.12-slim
FROM gorialis/discord.py

ENV PYTHONUNBUFFERED=1

# prepare stages
RUN mkdir -p /usr/src/bot
WORKDIR /usr/src/bot

#install dependencies
COPY requirements.txt requirements.txt 
RUN pip install -r requirements.txt

# run app
COPY . .

CMD [ "python3", "-u", "bot.py" ]