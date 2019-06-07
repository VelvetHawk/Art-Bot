from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import secrets
import traceback
import requests
import re


class RNG(commands.Cog, name="RNG"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		print("RNG loaded!")

	# 8-Ball
	@commands.command(
		name="8ball",
		help="Use with lube.",
		brief="Magic 8-Ball, for all your ponderings about life.",
		usage="Phrase to ask ball here, quotation marks unnecessary.",
		aliases = [
			"8", "eightball", "ateball", "ate"
		],
		description = "Welcome to the magic 8-Ball! The Ball™ never lies!"
	)
	async def eightball(self, context, *, message=None):
		if message is not None:
			if not (context.message.content.startswith(".ateball") or context.message.content.startswith(".ate")):
				possible_answers = [
					# Positive
					"It is certain",
					"It is decidedly so",
					"Without a doubt",
					"Yes definitely",
					"You may rely on it",
					"As I see it, yes",
					"Most likely",
					"Outlook good",
					"Yes",
					"Signs point to yes",
					# Neutral
					"Reply hazy try again",
					"Ask again later",
					"Better not tell you now",
					"Cannot predict now",
					"Concentrate and ask again",
					# Negative
					"Don't count on it",
					"My reply is no",
					"My sources say no",
					"Outlook not so good",
					"Very doubtful"
				]
			else:
				possible_answers = [
					# Positive
					"It is delicious",
					"It is smokingly so",
					"Without a rancid doubt",
					"Deliciously yes",
					"You may grill with it",
					"As I cook it, yes",
					"Most creamily",
					"Outlook sweet",
					"Creamy",
					"Signs point to spicy",
					# Neutral
					"Reply undercooked try again",
					"Bake again later",
					"Better not spoil the feast",
					"Cannot predict flavour",
					"Concentrate and mix again",
					# Negative
					"There are signs of mould",
					"My reply is gone off",
					"My sources say bitter",
					"Outlook not so tasty",
					"Very greasy"
				]

			# Remove original message
			await context.message.delete()
			# Answer
			await context.send(
				"The™ Magic 8-Ball\n<@{}>: \"{}\"\n\n```css\n{}```"
				.format(context.author.id, message, secrets.choice(possible_answers))
			)

	# Coin flip
	@commands.command(
		name="coinflip",
		help="Flip a coin!",
		brief="For when you just can't find a coin on you...",
		usage="",
		aliases = [
			"coin", "flip", "cointoss"
		],
		description = "How much more obvious than \"flip a coin\" can you get?"
	)
	async def coin(self, context):
		options = ["Heads", "Tails"]
		await context.send("<@{}> flipped a coin. The answer is: \"{}\"".format(context.author.id, secrets.choice(options)))
		# Remove original message
		await context.message.delete()

	# Roll dice
	@commands.command()
	async def roll(self, context, sides=None):
		try:
			if sides:
				await context.send("<@{}> rolled a {} sided dice!\nResult: {}".format(context.author.id, sides, secrets.randbelow(int(sides)+1)))
				# Remove original message
				await context.message.delete()
		except Exception as e:
			print("\t############## Exception ###############")
			print("Author: {} (ID: {})".format(context.author, context.author.id))
			print("Command: ".format(context.message))
			print("Exception ({}): {}".format(type(e).__name__, e))
			traceback.print_exc()
			print("\t############ END Exception ##############")
			await context.send("That would be pretty funny, wouldn't it :sunglasses:")


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(RNG(bot))
