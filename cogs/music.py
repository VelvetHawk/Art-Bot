from settings import config
import discord
from discord.ext import commands
from discord.ext.commands.context import Context

import youtube_dl
import asyncio

import secrets
import traceback
import requests
import shutil
import re


class Music(commands.Cog, name="Music"):
	def __init__(self, bot: commands.Bot):
		self.bot = bot
		self.executable = "3rd-party/ffmpeg/bin/ffmpeg"
		self.exec_options = "-rtbufsize 15M"
		self.voicestate = None
		self.voice_client = None
		self.channel = None
		self.playlist = [
			# Example object
			# {
			# 	"title": "Title here",
			# 	"link": "Video link here",
			# 	"audio": "Audio only link here",
			#	"loop": False
			# }
		]  # Defualt empty
		self.setup_complete = False
		self.continue_playing = True
		self.skip = False
		self.skip_amount = None
		print("Music loaded!")

	@commands.command()
	async def play(self, context, *, message=None):
		"""
			Add structure here
		"""
		try:
			if message:  # Make sure user has sent a link
				if not self.voicestate:
					self.voicestate = context.author.voice  # Check if user in voice channel
				if self.voicestate:  # Make sure user is in a voice channel
					# Check if link or keyword search
					if message.startswith("https://"):
						# Get link with youtube_dl
						options = {'outtmpl':  'data/music/%(title)s.%(ext)s'}
						yt_dl = youtube_dl.YoutubeDL(options)
						link_info = yt_dl.extract_info(message, download=True)  # Video Download
						title = link_info['title']
						ext = None
						source = None
						for _format in link_info['formats']:
							if _format['format_id'] == '160':
								ext = _format['ext']
								source = 'data/music/{}.{}'.format(title, ext)
								break
						# Add object to playlist
						self.playlist.append(
							{
								"title": title,
								"ext": ext,
								"link": message,
								"source": source,
								"loop": False
							})
						# Check to do setup
						if not self.setup_complete:
							self.channel = self.bot.get_channel(self.voicestate.channel.id)
							self.voice_client = await self.channel.connect()
							self.setup_complete = True
						# Remove original message
						await context.message.delete()
						# Initiate loop
						if not self.voice_client.is_playing():
							self.continue_playing = True
							# Plays the first song automatically
							self.voice_client.play(
								discord.FFmpegPCMAudio(
									source=self.playlist[0]['source'],
									executable=self.executable
								)
							)
							await context.send("```\nNow playing: {}\nLink: {}```".format(title, message))
							# Play loop
							while self.continue_playing:
								if self.skip:
									self.voice_client.stop()  # Stop track
									self.skip = False
									# Disable current track looping, just in case it's unabled so it can be skipped
									self.playlist[0]['loop'] = False
									# Skip tracks
									if isinstance(self.skip_amount, str) and self.skip_amount.lower() == "all":
										# Delete all files from playlist
										for song in range(0, len(self.playlist) - 1):
											self.remove_file(song['title'], song['ext'])	 # Remove file
										# Easier than just popping each off individually
										self.playlist = []
									# Track will be skipped automatically if only one available
									elif int(self.skip_amount) > 1:
										for song in range(0, int(self.skip_amount) - 1):
											self.remove_file(
												self.playlist[0]['title'],
												self.playlist[0]['ext']
											)	 # Remove file
											self.playlist.pop(0)
									else:  # Remove only the first song
										self.remove_file(
											self.playlist[0]['title'],
											self.playlist[0]['ext']
										)  # Remove file
								if not self.voice_client.is_playing():  # Check if audio has finished playing
									if len(self.playlist) >= 1 and self.playlist[0]['loop']:  # Play current song again
										self.voice_client.play(
											discord.FFmpegPCMAudio(
												source=self.playlist[0]['source'],
												executable=self.executable
											)
										)
									else:
										if not len(self.playlist) == 0:  # Not sure of neater way to do this
											# Remove first item from playlist (audio that was last playing)
											self.remove_file(
												self.playlist[0]['title'],
												self.playlist[0]['ext']
											)  # Remove file
											self.playlist.pop(0)
										# Check needs to be done twice, as both cause error if len(self.playlist) == 0
										if len(self.playlist) == 0:
											self.continue_playing = False
										else:  # Play next song
											self.voice_client.play(
												discord.FFmpegPCMAudio(
													source=self.playlist[0]['source'],
													executable=self.executable
												)
											)
											await context.send("```\nNow playing: {}\nLink: {}```".format(
												self.playlist[0]['title'], self.playlist[0]['link']))
								else:  # Audio is playing
									await asyncio.sleep(1)  # Sleep for 1 second

						else:  # Inform that track is added to playlist
							await context.send("```\nAdded to playlist: {}\nLink: {}```".format(title, message))
					else:  # Non-link, so youtube search required
						await context.send("Feature in development, please try again later! :)")
			else:  # if there is something in the queue, continue playing it
				"""
					MAKE PLAY, PLAY A SONG IF THERE IS ONE IN THE QUEUE
				"""
				# if not self.voice_client.is_playing() and if len(queu):
				pass

		except Exception as exc:
			print("\t############## Exception ###############")
			traceback.print_exc()
			print("\t############ END Exception ##############")

	# TODO: Fix extensions for videos
	"""
	Sometimes, videos can have a webm extenion, so playing them may not work.
	Fix the file deletion to also consider the extension where it's not ONLY mp4, but also webm 
	"""

	@staticmethod
	def remove_file(filename: str, extension: str):
		import os
		filename = "data/music/{}.{}".format(filename, extension)
		try:
			print("Path:", filename)
			if os.path.exists(filename):
				os.remove(filename)
		except IOError as exp:
			print("\t############## Exception ###############")
			traceback.print_exc()
			print("\t############ END Exception ##############")

	@commands.command()
	async def queue(self, context):
		if len(self.playlist) < 1:
			await context.send("Playist seems to be currently empty, <@{}>".format(context.author.id))
		else:
			song_queue = "**Current song queue:**\n```md\n"
			for song in range(0, len(self.playlist)):
				song_queue += "{}. {}\n".format(song + 1, self.playlist[song]['title'])
			song_queue += "```"
			await context.send(song_queue)
		# Remove original message
		await context.message.delete()

	@commands.command()
	async def loop(self, context):
		# Inverts the current loop status of a song
		if self.voice_client and self.voice_client.is_playing():
			self.playlist[0]['loop'] = not self.playlist[0]['loop']  # Invert
			if self.playlist[0]['loop']:
				await context.send("<@{}> has set the current song to loop!".format(context.author.id))
			else:
				await context.send("<@{}> has stopped the current song looping!".format(context.author.id))
			# Remove original message
			await context.message.delete()

	@commands.command(name="skip")
	async def skip_song(self, context, amount=None):
		if self.voice_client:
			self.skip = True
			if not amount:
				self.skip_amount = 1
			else:
				self.skip_amount = amount

	@commands.command()
	async def pause(self, context):  # TODO: Examine this command, it's skipping the track
		if self.voice_client and self.voice_client.is_playing():
			self.voice_client.pause()

	@commands.command()
	async def stop(self, context):
		if self.voice_client:
			self.voice_client.stop()
			self.continue_playing = False

	@commands.command()
	async def resume(self, context):
		if self.voice_client and self.voice_client.is_paused():
			self.voice_client.resume()

	@commands.command()
	async def leave(self, context):
		if self.voice_client:
			self.voice_client.stop()
			# Delete all files from playlist
			for song in self.playlist:
				self.remove_file(
					song['title'],
					song['ext']
				)  # Remove file
				self.playlist.pop(0)
			# Leave channel
			await self.voice_client.disconnect()
			# Reset everything
			self.voicestate = None
			self.voice_client = None
			self.channel = None
			self.playlist = []
			self.setup_complete = False
			self.continue_playing = False
			self.skip = False
			self.skip_amount = None


# Mandatory setup function, not part of class
def setup(bot):
	bot.add_cog(Music(bot))
