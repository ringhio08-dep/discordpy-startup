import discord
import configparser
import os
import csv
import pandas as pd
import unicodedata
import asyncio
import re
import traceback

from discord.ext import commands
from datetime import datetime 
from discord.ext import tasks

#設定ファイルから情報を格納
INIFILE = configparser.ConfigParser()
INIFILE.read('config.ini', 'UTF-8')
CHANNEL_ID = int(INIFILE.get('Discord', 'CHANNEL'))
COMAND_PREFIX = INIFILE.get('Discord', 'COMAND_PREFIX')
DEL_TIME = int(INIFILE.get('Discord', 'DEL_TIME'))

token = os.environ['DISCORD_BOT_TOKEN']
bot = commands.Bot(command_prefix= COMAND_PREFIX)
send_channel = ""
notes = ""

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


bot.run(token)
