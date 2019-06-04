from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re

class Core(commands.Cog, name="Art Bot Core"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("Art Bot Core loaded!")

	@commands.command(name="greet")
	async def greet(self, context: Context):
		print("Greet called#####")
		# Remove original message
		await context.message.delete()
		# Reply
		await context.send("Greetings!")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Core(bot))
