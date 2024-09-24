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
SCUM_CHANNEL_ID = 1068864472262901842

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

@bot.command(name="time", help="Displays basic stats for scum server <int, defaults to 28487222 (Palfy)>")
async def time(ctx, server_id: int = 28487222):
	response = requests.get(f"https://api.battlemetrics.com/servers/{server_id}")
	response = json.loads(response.text)
	server_name = response["data"]["attributes"]["name"]
	server_time = response["data"]["attributes"]["details"]["time"]
	server_time_hours = int(server_time.split(":")[0])
	time_to_dawn = hours_to_dawn(server_time_hours)
	time_to_restart = hours_to_restart()
	server_players = response["data"]["attributes"]["players"]
	server_maxplayers = response["data"]["attributes"]["maxPlayers"]
	battlemetrics_url = f"https://www.battlemetrics.com/servers/scum/{server_id}"
	message_line = f"{server_name} current time {server_time}{time_to_dawn} active players {server_players}/{server_maxplayers}{time_to_restart}"
	url_line = f"{battlemetrics_url}"
	message_content = f"{message_line}\n{url_line}"
	logger.info(f"User {ctx.author} requested time command: {message_line}")
	if ctx.channel.id == SCUM_CHANNEL_ID:	
		await ctx.send(message_content)
	else:
		silly_apology = f"Bah! I'm not supposed to send message on the channel {ctx.channel.name}. However, here's data you requested\n{message_content}"
		await ctx.author.send(silly_apology)

def hours_to_restart():
	time_now = datetime.datetime.now()
	# restart_hours = [1, 7, 13, 19]
	if time_now.hour >= 19:
		restart_date = datetime.datetime.now().replace(hour=1, minute=0) + datetime.timedelta(days=1)
	elif time_now.hour >= 13:
		restart_date = datetime.datetime.now().replace(hour=19, minute=0)
	elif time_now.hour >= 7:
		restart_date = datetime.datetime.now().replace(hour=13, minute=0)
	else:
		restart_date = datetime.datetime.now().replace(hour=7, minute=0)
	time_to_restart = restart_date - time_now
	hours_left, remainder = divmod(time_to_restart.seconds, 3600)
	minutes_left, seconds_left = divmod(remainder, 60)
	return(f" time to restart {hours_left:02d}:{minutes_left:02d}")

def hours_to_dawn(game_current_hour : str):
	if game_current_hour > 21:
		game_hours_to_dawn = 24 - game_current_hour + 6
	elif game_current_hour < 6:
		game_hours_to_dawn = 6 - game_current_hour
	else:
		return ""
	real_hours_to_dawn = game_hours_to_dawn / 3.84 # Joachim approved number 
	hours, remainder = divmod(real_hours_to_dawn, 1)
	minutes = int(remainder * 60)
	message = f" ({datetime.time(int(hours), minutes).strftime("%H:%M")}h until dawn)"
	return message
		

bot.run(TOKEN)
