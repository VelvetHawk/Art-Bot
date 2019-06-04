from discord.ext import commands
from discord.ext.commands import Context
from settings import config


def is_owner_check(context: Context):
	return config.OWNER_ID == str(context.author.id)


def is_owner():
	return commands.check(lambda ctx: is_owner_check(ctx.message))
