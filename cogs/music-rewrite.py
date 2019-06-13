from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context


class Music(commands.Cog, name="Music-Rewrite"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command()
	async def play(self, context: Context, *, message=None):
		pass

	@commands.command()
	async def queue(self, context: Context):
		pass

	@commands.command()
	async def loop(self, context: Context):
		pass

	@commands.command(name="skip")
	async def skip_song(self, context: Context, amount=None):
		pass

	@commands.command()
	async def pause(self, context: Context):
		pass

	@commands.command()
	async def stop(self, context: Context):
		pass

	@commands.command()
	async def resume(self, context: Context):
		pass

	@commands.command()
	async def leave(self, context: Context):
		pass

# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Music(bot))
