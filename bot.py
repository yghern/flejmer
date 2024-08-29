# bot.py
import datetime
import json
import logging
import os
import requests

import discord
import discord.ext.commands

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

logging.basicConfig(
	level=logging.DEBUG,
	format="%(asctime)s %(levelname)-8s %(name)-15s %(message)s"
)

logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = discord.ext.commands.Bot(intents=intents, command_prefix="$")


@bot.event
async def on_ready(): # EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE
	guild_count = 0 # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO
	for guild in bot.guilds: # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH
		logger.info(f"- {guild.id} (name: {guild.name})") # PRINT THE SERVER'S ID AND NAME
		guild_count = guild_count + 1 # INCREMENTS THE GUILD COUNTER
	logger.info("Flejmer is in " + str(guild_count) + " guilds.") # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN


#@bot.event 
#async def on_message(message): # EVENT LISTENER FOR WHEN A NEW MESSAGE IS SENT TO A CHANNEL
#	print("on_message processing")
#	if message.content == "hello": # CHECKS IF THE MESSAGE THAT WAS SENT IS EQUAL TO "HELLO"
#		await message.channel.send("hey dirtbag") # SENDS BACK A MESSAGE TO THE CHANNEL

@bot.command()
async def time(ctx, server_id: int = 28487222):
	response = requests.get(f"https://api.battlemetrics.com/servers/{server_id}")
	response = json.loads(response.text)
	server_name = response["data"]["attributes"]["name"]
	server_time = response["data"]["attributes"]["details"]["time"]
	server_time_hours = int(server_time.split(":")[0])
	time_to_dawn = hours_to_dawn(server_time_hours)
	server_players = response["data"]["attributes"]["players"]
	server_maxplayers = response["data"]["attributes"]["maxPlayers"]
	battlemetrics_url = f"https://www.battlemetrics.com/servers/scum/{server_id}"
	message_line = f"{server_name} current time {server_time}{time_to_dawn} active players {server_players}/{server_maxplayers}"
	url_line = f"{battlemetrics_url}"
	message_content = f"{message_line}\n{url_line}"
	logger.info(f"User {ctx.author} requested time command: {message_line}")
	await ctx.send(message_content)

def hours_to_dawn(game_current_hour):
	if game_current_hour > 21:
		game_hours_to_dawn = 24 - game_current_hour + 6
	elif game_current_hour < 6:
		game_hours_to_dawn = game_current_hour
	if game_hours_to_dawn:
		real_hours_to_dawn = game_hours_to_dawn / 3.84 # Joachim approved number 
		hours, remainder = divmod(real_hours_to_dawn, 1)
		minutes = int(remainder * 60)
		message = f" ({datetime.time(int(hours), minutes).strftime("%H:%M")}h until dawn)"
		return message
	return ""
		

bot.run(TOKEN)