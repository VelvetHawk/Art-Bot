import discord
from discord.ext import commands

import sys
import linecache


def print_exception():
	# Print the last exception that occurred to console
	exc_type, exc_obj, tb = sys.exc_info()
	f = tb.tb_frame
	lineno = tb.tb_lineno
	filename = f.f_code.co_filename
	linecache.checkcache(filename)
	line = linecache.getline(filename, lineno, f.f_globals)
	print('Exception in ({}, Line {} \"{}\": {}\n-----------'.format(
		filename, lineno, line.strip(), exc_obj
	))


class BannedFromCommandException(commands.CommandError):
	pass
