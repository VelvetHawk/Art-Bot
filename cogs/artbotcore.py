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
		greetings = [
			"fagget",
			"faguette",
			"asshole",
			"feg",
			"beloved",
			"darling",
			"dearest",
			"cumlord",
			"cumbucket"
		]
		# Remove original message
		await context.message.delete()
		# Reply
		await context.send("Greetings to you <@{}>, my dear {}".format(context.author.id, secrets.choice(greetings)))

	# @someone
	@commands.command(
		name="someone",
		help="Annoy the living hell out of your friends!",
		brief="@someone, but not limited to April Fools!",
		usage="Optional message to pass onto victim/recipient",
		aliases=[
			"sum1", "some1", "somewan", "sumwan"
		],
		description="The glorius @someone we all loved and missed!"
	)
	async def someone(self, context, *, message=None):
		members = context.guild.members
		someone = secrets.choice(members)
		replies = [
			"wants to give you the gift of annoyance",
			"is bugging you",
			"is shy and wants to indirectly grab your attention"
		]
		times = 0
		while (times < 30) and (
				str(someone.status) == "offline"
				or str(context.author.id) == str(someone.id)
				or str(someone.id) == str(self.bot.user.id)):  # Bot itself
			times = times + 1
			someone = secrets.choice(members)
		# Remove original message
		await context.message.delete()
		if times == 30:
			await context.send("Sorry <@{}>, nobody seems to be available...".format(context.author.id))
		else:
			if not message:
				await context.send(
					"<@{}>, <@{}>  {}".format(someone.id, context.author.id, secrets.choice(replies)))
			else:
				await context.send(
					"<@{}>, <@{}> is asking you:\n```fix\n{}```".format(someone.id, context.author.id, message))

	# TODO: Add functionality to search with ITAD for suggestions of games
	# API Link https://itad.docs.apiary.io/#reference/search/search/find-games
	# Is there any deal?
	@commands.command(name="isthereanydeal", aliases=["itad"])
	async def isthereanydeal(self, context, *, game=None):
		try:
			if game:
				game_plain = self.get_plain(game)
				if game_plain:
					info_url = "https://api.isthereanydeal.com/v01/game/prices/?key={}&plains={}&region=eu2".format(config.ITAD_KEY, game_plain)
					response = requests.get(info_url)
					if response.status_code == 200:
						results_display = "Game: **{}** (Requested by: <@{}>)```\nSTORE               DISCOUNT    NEW          OLD\n".format(game, context.author.id)
						for shop in response.json()["data"][game_plain]["list"]:
							shop_name = shop["shop"]["name"]
							deal_price = shop["price_new"]
							standard_price = shop["price_old"]
							discount = shop["price_cut"]
							results_display += "{0:<20}\t{1:<3}%\t€{2:<8}\t€{3:<8}\n".format(shop_name, discount, deal_price, standard_price)
						await context.send(results_display + "```")
						# Remove original message
						await context.message.delete()
				else:
					await context.send("Beep Boop sorry <@{}>, seems I can't find anything for \"{}\"... :frowning:".format(context.author.id, game))
					# Remove original message
					await context.message.delete()
		except Exception as e:
			print("\t############## Exception ###############")
			print("Author: {} (ID: {})".format(context.author, context.author.id))
			print("Command: ".format(context.command))
			print("Exception ({}): {}".format(type(e).__name__, e))
			traceback.print_exc()
			print("\t############ END Exception ##############")

	# Cheapest deal
	@commands.command(name="shekel")
	async def shekel(self, context, *, game):
		try:
			if game:
				game_plain = self.get_plain(game)
				if game_plain:
					info_url = "https://api.isthereanydeal.com/v01/game/prices/?key={}&plains={}&region=eu2".format(config.ITAD_KEY, game_plain)
					response = requests.get(info_url)
					if response.status_code == 200:
						results_display = "Game: **{}** (Requested by: <@{}>)```\nSTORE               DISCOUNT    NEW          OLD\n".format(game, context.author.id)
						store_list = response.json()["data"][game_plain]["list"][0] # First item in list will always be cheapest
						shop_name = store_list["shop"]["name"]
						deal_price = store_list["price_new"]
						standard_price = store_list["price_old"]
						discount = store_list["price_cut"]
						url = store_list['url']
						results_display += "{0:<20}\t{1:<3}%\t€{2:<8}\t€{3:<8}```\n{4}".format(shop_name, discount, deal_price, standard_price, url)
						await context.send(results_display)
						# Remove original message
						await context.message.delete()
				else:
					await context.send("Beep Boop sorry <@{}>, seems I can't find anything for \"{}\"... :frowning:".format(context.author.id, game))
					# Remove original message
					await context.message.delete()
		except Exception as e:
			print("Author: {} (ID: {})".format(context.author, context.author.id))
			print("Command: ".format(context.message))
			print("Exception ({}): {}".format(type(e).__name__, e))
			traceback.print_exc()
			print("\t############ END Exception ##############")

	@staticmethod
	def get_plain(game_name):
		game_url = "https://api.isthereanydeal.com/v02/game/plain/?key={}&shop=&game_id=&url=&title={}&optional=".format(config.ITAD_KEY, game_name.replace(" ", "+"))
		response = requests.get(game_url)
		if response.status_code == 200:
			if response.json()[".meta"]["active"]:
				game_plain = response.json()["data"]["plain"]
				return game_plain
		return None


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Core(bot))
