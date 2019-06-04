from settings import config
import discord
from discord.ext.commands import Bot
from discord.ext.commands.context import Context
from exceptions import exceptions
from utils import checks

import secrets
import traceback
import requests
import re


class ArtBot(Bot):
	""" Welcome to the Art Bot mark II! """
	def __init__(self, command_prefix, **kwargs):
		super().__init__(command_prefix, **kwargs)

		# Define Cogs/Extensions List
		self.core_extensions = [
			"cogs.artbotcore",
			"cogs.crypto",
			"cogs.music",
			"cogs.owner",
			"cogs.rng",
			"cogs.utility"
		]

		# TODO: Add Banned Users

		# Load Extensions
		for extension in self.core_extensions:
			try:
				self.load_extension(extension)
			except discord.ext.commands.ExtensionNotLoaded as exception:
				print("\t############## Exception ###############")
				traceback.print_exc()
				print(exception)
				print("\t############ END Exception ##############")

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

	async def on_command_error(self, context: Context, error):
		if isinstance(error, exceptions.BannedFromCommandException):
			print(error)
			print("Context.author:", context.author)
			print("Command:", context.command)
		else:
			print("\t############## Exception ###############")
			print("Author: {} (ID: {})".format(context.author, context.author.id))
			print("Command: ".format(context.command))
			print("Exception ({}): {}".format(type(error).__name__, error))
			traceback.print_exc()
			print("\t############ END Exception ##############")


# Create Bot Instance
bot = ArtBot(
	command_prefix=".",
	case_insensitive=True,
	description="Welcome to the the Art Bot™! Below is a list of "
	"commands available for use with the bot. GL HF!"
)


# ########### DEV COMMANDS ##############
""" Cog Dynamic Loading/Unloading Functionality """

@bot.command(hidden=True, name="__unload__")
@checks.is_owner()
async def __unload(context: Context, cog: str):
	print("Unload called for {} by {} ({})".format(cog, context.author, context.author.id))
	cog = "cogs." + cog
	if cog in bot.core_extensions:
		bot.unload_extension(cog)


@bot.command(hidden=True, name="__load__")
@checks.is_owner()
async def __load(context: Context, cog: str):
	print("Load called for {} by {} ({})".format(cog, context.author, context.author.id))
	cog = "cogs." + cog
	if cog in bot.core_extensions:
		bot.load_extension(cog)


@bot.command(hidden=True, name="__reload__")
@checks.is_owner()
async def __reload(context: Context, cog: str):
	print("Reload called for {} by {} ({})".format(cog, context.author, context.author.id))
	if cog == 'all':
		for cog in bot.core_extensions:
			bot.reload_extension(cog)
	else:
		cog = "cogs." + cog
		if cog in bot.core_extensions:
			bot.reload_extension(cog)
		else:
			print("Not present")


@bot.command(hidden=True, name="__exit__")
@checks.is_owner()
async def __exit(context: Context, message: str = None):
	print("Logout called, exiting server...\nOptional Reason: [{}]".format(message))
	print("Author: {} (ID: {})".format(context.author, context.author.id))
	# Logout
	await bot.logout()


@bot.command(hidden=True, name="__help__")
@checks.is_owner()
async def __help(context: Context):
	# List all loaded commands
	command_list = "```Full Command List:\n"
	# Create a copy of the total command list
	bot_command_list = bot.commands.copy()
	# For each cog
	for cog in bot.cogs:
		command_list += cog + ":\n"
		# Add cog name as heading and add its commands as sub sections
		for command in bot.get_cog(cog).get_commands():
			command_list += "\t{}\n".format(command)
			# Remove command from list to avoid repetition
			bot_command_list.remove(command)
	# Commands NOT belonging to cogs
	command_list += "Non-Cog Utility Commands:\n"
	for command in bot_command_list:
		command_list += "\t{}\n".format(command.name)
	await context.send(command_list + "```")


# Login and Run Bot
bot.run(config.DISCORD_TOKEN)
