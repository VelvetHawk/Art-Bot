from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re


class Crypto(commands.Cog, name="Crypto"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Crypto loaded!")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Crypto(bot))
