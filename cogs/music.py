from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re


class Music(commands.Cog, name="Music"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Music loaded!")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Music(bot))
