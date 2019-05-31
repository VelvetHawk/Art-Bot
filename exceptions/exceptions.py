import discord
from discord.ext import commands


class BannedFromCommandException(commands.CommandError):
	pass
