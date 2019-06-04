from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re


class Owner(commands.Cog, name="Owner", command_attrs=dict(hidden=True)):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Owner loaded!")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Owner(bot))
