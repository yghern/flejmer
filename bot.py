# bot.py
import asyncio
import datetime
import logging
import os
import requests

import discord
from discord.ext import commands, tasks

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
SCUM_CHANNEL_ID = 1068864472262901842
VALHEIM_CHANNEL_ID = 1299271046762856468

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s %(levelname)-8s %(name)-15s %(message)s"
)

logger = logging.getLogger("flejmer")
logger.setLevel(logging.DEBUG)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

class Flamer(commands.Bot):
	def __init__(self, *args, **kwargs):
		super().__init__(intents=intents, command_prefix="$", *args, **kwargs)

	async def on_ready(self): # EVENT LISTENER FOR WHEN THE BOT HAS SWITCHED FROM OFFLINE TO ONLINE
		guild_count = 0 # CREATES A COUNTER TO KEEP TRACK OF HOW MANY GUILDS / SERVERS THE BOT IS CONNECTED TO
		for guild in self.guilds: # LOOPS THROUGH ALL THE GUILD / SERVERS THAT THE BOT IS ASSOCIATED WITH
			logger.info(f"- {guild.id} (name: {guild.name})") # PRINT THE SERVER'S ID AND NAME
			guild_count = guild_count + 1 # INCREMENTS THE GUILD COUNTER
		logger.info("Flejmer is in " + str(guild_count) + " guilds.") # PRINTS HOW MANY GUILDS / SERVERS THE BOT IS IN

	async def on_message(self, message):
		await self.process_commands(message)
		if self.user.mentioned_in(message):
			logger.info(f"sending reaction to {message.channel} because of message {message.content}")
			await message.add_reaction(":love:1276852873405403167")
		if message.channel.id == VALHEIM_CHANNEL_ID:
			if ":serwer:1314317521322639382" in message.content:
				await message.add_reaction(":serwer:1314317521322639382")
				admin_user = await self.fetch_user("400016234189684741")
				logger.info(f"detected server troubles, sending dm to {admin_user.name}")
				await admin_user.send("oh noes, check the server!!!1")

	async def setup_hook(self) -> None:
		self.bg_task = self.loop.create_task(self.update_status())

	async def update_status(self):
		await self.wait_until_ready()
		while not self.is_closed():
			response = requests.get(f"https://api.battlemetrics.com/servers/32153423")
			data = response.json()
			server_time = data["data"]["attributes"]["details"]["time"]
			server_players = data["data"]["attributes"]["players"]
			status = f"Game time is {server_time} players {server_players}"
			logger.info(f"Updating own status with {status}")
			await self.change_presence(activity=discord.CustomActivity(name=status))
			await asyncio.sleep(120)

flamer = Flamer()	

@flamer.command(name="time", help="Displays basic stats for scum server <int, defaults to 32153423 (The Cartel)>")
async def time(ctx, server_id: int = 32153423):
	response = requests.get(f"https://api.battlemetrics.com/servers/{server_id}")
	data = response.json()
	server_name = data["data"]["attributes"]["name"]
	server_time = data["data"]["attributes"]["details"]["time"]
	server_time_hours = int(server_time.split(":")[0])
	time_to_dawn = hours_to_dawn(server_time_hours)
	time_to_restart = hours_to_restart()
	server_players = data["data"]["attributes"]["players"]
	server_maxplayers = data["data"]["attributes"]["maxPlayers"]
	battlemetrics_url = f"https://www.battlemetrics.com/servers/scum/{server_id}"
	message_line = f"{server_name} current time {server_time}{time_to_dawn} active players {server_players}/{server_maxplayers}{time_to_restart}"
	url_line = f"{battlemetrics_url}"
	message_content = f"{message_line}\n{url_line}"
	logger.info(f"User {ctx.author} requested time command: {message_line}")
	if ctx.channel.id == SCUM_CHANNEL_ID:	
		await ctx.send(message_content)
	elif isinstance(ctx.channel, discord.channel.DMChannel):
		priv_message = f"Ok, just you and me:\n{message_content}"
		await ctx.send(priv_message)	
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

TOKEN_MASKED = TOKEN[0:10] if len(TOKEN) > 11 else TOKEN
logger.debug(f"Trying to start bot with a token ${TOKEN_MASKED}")
flamer.run(TOKEN)
