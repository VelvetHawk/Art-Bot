from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re


class Utility(commands.Cog, name="Utility"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Utility loaded!")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Utility(bot))
