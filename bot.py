from settings import config
import discord
from discord.ext import commands
from exceptions import exceptions

import secrets
import traceback
import requests
import re


class ArtBot(commands.Bot):
	""" Welcome to the Art Bot mark II! """
	def __init__(self, *args, **kwargs):
		super().__init__(kwargs)

	async def on_ready(self):
		# 0: playing, 1: streaming, 2: listening to, 3: watching
		games = [
			discord.Activity(name="The Hammered Dulcimer", type=0),
			discord.Activity(name="The Marimba", type=2),
			discord.Activity(name="The Zen Tambour", type=3),
			discord.Activity(name="The 12-Neck Guitar", type=0)
		]
		await self.change_presence(status=discord.Status.online, activity=secrets.choice(games))

		# Confirmation output
		print('Logged in as:')
		print("Bot Name:", self.user.name)
		print("Bot ID:", self.user.id)
		print('------')


# Command prefix
bot = ArtBot(
	command_prefix=".",
	case_insensitive=True,
	description="Welcome the the Art Bot™! Below is a list of "
	"commands available for use with the bot. GL HF!"
)

# Login
bot.run(config.DISCORD_TOKEN)
