from settings import config
from exceptions.exceptions import print_exception

import discord
from discord import VoiceClient
from discord import VoiceState
from discord.ext import commands
from discord.ext.commands.context import Context
import youtube_dl

import re
import os
import unicodedata
import asyncio


class Music(commands.Cog, name="Music-Rewrite"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		# Data
		self.playlist = []
		self.continue_playing = None
		self.pause = False
		self.skip = False
		# Voice Channel Bot is Currently Connected to
		self.voice_client: VoiceClient = None

	@commands.command(
		name="play",
		help="Both YouTube share URLs and direct website URLs work. Quotation"
				" marks are not necessary when passing in a search query.",
		brief="Play a song from a YouTube link or search for one via the bot",
		usage="<YouTube video link> or search query to search YouTube with.",
		aliases=[
			"p"
		],
		description="This command is used to play audio from YouTube videos"
					" directly."
	)
	async def play(self, context: Context, message: str = None):
		if not message:
			return		# Empty content
		try:
			if self.is_link(message):  # User sent link
				# Check if user is in a voice channel
				if context.author.voice:
					self.download_audio(message)
					await self.setup_voice_connection(context.author.voice)
					# Remove original message
					await context.message.delete()
					# Start audio loop
					if not self.voice_client.is_playing():
						self.start_audio()
						await self.notify_current_song(context)
						# Audio Loop
						while self.continue_playing:
							if self.skip:
								self.skip = False
								self.voice_client.stop()
								if len(self.playlist) > 0:
									await self.notify_current_song(context)
									self.start_audio()  # Audio skipped in skip command
							# If current song finished, play next in playlist
							elif not self.voice_client.is_playing() and not self.pause:
								if self.loop:
									await self.notify_current_song(context)
									self.start_audio()
								else:  # No songs left, stop loop
									if len(self.playlist) == 0:
										self.continue_playing = False
									else:  # Move to next song and play
										self.playlist.pop(0)
										await self.notify_current_song(context)
										self.start_audio()
							# Sleep for 1 second to use other commands
							await asyncio.sleep(1)
					else:  # Show last entry added to playlist
						await context.send("```\nAdded to playlist: {}\nLink: {}```"
							.format(self.playlist[len(self.playlist)-1]['title'], message))
				else:  # Inform user they are not in a voice channel
					await context.send(
						"<@{}>, you need to be in a voice a channel to play music!"
						.format(context.author.id)
					)
					print("VoiceState: ", context.author.voice)

			else:  # User sent search query
				await context.send(
					"Feature in development, please try again later! :)"
				)
		except Exception as e:
			print_exception()

	@commands.command(
		name="queue",
		help="",
		brief="Shows the songs currently in the playlist.",
		usage="<Empty>",
		aliases=[],
		description="This command will display a numbered lists that"
					" shows all of the songs currently in the playlist."
	)
	async def queue(self, context: Context):
		if len(self.playlist) < 1:
			await context.send("Playist seems to be currently empty, <@{}>"
				.format(context.author.id))
		else:
			song_queue = "**Current song queue:**\n```md\n"
			for song in range(0, len(self.playlist)):
				song_queue += "{}. {}    [{}]\n".format(
					song + 1, self.playlist[song]['title'], self.playlist[song]['link'])
			song_queue += "```"
			await context.send(song_queue)
		# Remove original message
		await context.message.delete()

	@commands.command(
		name="loop",
		help="",
		brief="Sets the current song in the playlist to loop",
		usage="<Empty>",
		aliases=[],
		description="This command will set the current song in the playlist to loop."
					" If you wish to unset this, simply call the command again."
	)
	async def loop(self, context: Context):
		# Inverts the current loop status of a song
		if self.voice_client and self.voice_client.is_playing():
			self.playlist[0]['loop'] = not self.playlist[0]['loop']  # Invert
			# Remove original message
			await context.message.delete()
			if self.playlist[0]['loop']:
				await context.send("<@{}> has set the current song to loop!".format(context.author.id))
			else:
				await context.send("<@{}> has stopped the current song looping!".format(context.author.id))

	@commands.command(
		name="skip",
		help="",
		brief="Skip the current song in the playlist.",
		usage="<Number of songs to skip> or leave blank for current song. Use"
				" \'all\' without quotation marks to skip the whole playlist.",
		aliases=[],
		description="This command will skip the current song in the playlist, even"
					" if the song is set to loop."
	)
	async def skip_song(self, context: Context, amount=1):
		if self.voice_client:
			if isinstance(amount, int):
				if amount >= len(self.playlist)-1:
					self.playlist = []
				else:
					for i in range(amount):
						self.playlist.pop(0)
			elif amount.lower() == "all":
				self.playlist = []
			# Let main play loop know
			self.skip = True

	@commands.command(
		name="pause",
		help="",
		brief="Pauses the current song in the playlist.",
		usage="<Empty>",
		aliases=[],
		description="This command will pause the current song playing. To un-pause,"
					" use the \'resume\' command."
	)
	async def pause(self, context: Context):
		if self.voice_client and self.voice_client.is_playing():
			self.pause = True
			self.voice_client.pause()

	@commands.command(
		name="resume",
		help="",
		brief="Resumes the current song in the playlist.",
		usage="<Empty>",
		aliases=[],
		description="This command will resume the current song if paused."
	)
	async def resume(self, context: Context):
		if self.voice_client and self.voice_client.is_paused():
			self.voice_client.resume()
			self.pause = False

	@commands.command(
		name="stop",
		help="",
		brief="Stops the bot playing music.",
		usage="<Empty>",
		aliases=[],
		description="This command will stop the bot from playing anymore music"
					" and empty the current playlist."
	)
	async def stop(self, context: Context):
		if self.voice_client:
			self.continue_playing = False
			self.voice_client.stop()

	@commands.command(
		name="leave",
		help="",
		brief="Leaves the current voice channel.",
		usage="<Empty>",
		aliases=[],
		description="This command will make the bot stop any music it may be"
					" currently playing, empty the current playlist and"
					" disconnect from the voice channel it is currently in."
	)
	async def leave(self, context: Context):
		if self.voice_client:
			self.voice_client.stop()
			self.continue_playing = False
			# Leave channel
			await self.voice_client.disconnect()
			await asyncio.sleep(2)  # Time to free resources
			# Delete all files in directory and clear playlist
			self.playlist = []
			self.voice_client = None
			self.skip = False
			self.delete_file("ALL")

	async def notify_current_song(self, context: Context):
		await context.send("```\nNow playing: {}\nLink: {}```".format(
			self.playlist[0]['title'], self.playlist[0]['link'])
		)

	@staticmethod
	def delete_file(filename: str):
		""" Delete all files with a given name

		:param filename: Name of the file to delete
		:return: None
		"""
		if filename == "ALL":
			for file in os.listdir("data/music/"):
				deleted = False
				while not deleted:
					try:
						os.remove(f"data/music/{file}")
						deleted = True
					except Exception as e:
						print("Not removed, waiting 1 second...")
						asyncio.sleep(1)
		else:
			print("File--: ", filename)

	@staticmethod
	def is_link(link: str) -> bool:
		return not (re.match("https?://.*", link) is None)

	def download_audio(self, link: str):
		"""
		Downloads an audio file from YouTube based on the link provided
		:param link: The link from which to download from
		:return: Path to the source of the downloaded file
		"""
		# Download file to specified directory
		options = {'outtmpl': 'data/music/%(title)s.%(ext)s'}
		yt_dl = youtube_dl.YoutubeDL(options)
		link_info = yt_dl.extract_info(link, download=True)  # Video Download
		title = link_info['title']
		# Find file in downloaded directory
		source = None
		for file in os.listdir("data/music/"):
			file_title, file_ext = file.title().split(".")
			if self.caseless_equals(title, file_title):
				source = f"data/music/{title}.{file_ext.lower()}"
				break  # End loop
		# Add audio source to playlist
		self.playlist.append({
			"title": title,
			"link": link,
			"source": source,
			"loop": False
		})

	@staticmethod
	def normalise(text: str):
		return unicodedata.normalize("NFKD", text.casefold())

	def caseless_equals(self, left, right) -> bool:
		return self.normalise(left) == self.normalise(right)

	async def setup_voice_connection(self, voice_state: VoiceState):
		# Check if currently connected to voice client
		if len(self.bot.voice_clients) > 1 and self.bot.voice_clients[0] is not None:
			self.voice_client = self.bot.voice_clients[0]
		elif not self.voice_client:
			self.voice_client =\
				await self.bot.get_channel(voice_state.channel.id).connect()

	def start_audio(self):
		self.continue_playing = True
		self.voice_client.play(discord.FFmpegPCMAudio(
			source=self.playlist[0]['source'],
			executable=config.FFMPEG_PATH
		))


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Music(bot))
