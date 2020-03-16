import discord

from discord.ext import tasks
from datetime import datetime 

TOKEN = 'Njg3OTAwNzI1NDA1MTU1MzYx.Xmsfig.azhIAdipWTLOkJHo1TbBk63AWLI'
CHANNEL_ID = 684195945507717121

client = discord.Client()

@client.event
async def on_ready():
    channel = client.get_channel(CHANNEL_ID)
    await channel.send('起動しました！')  

@client.event
async def on_message(message):
    if message.content == '/info':
        await message.channel.send('https://games.app-liv.jp/archives/403762')

@tasks.loop(seconds=60)
async def loop():

    now = datetime.now().strftime('%H:%M')

    if now == '11:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】アイスマンボキングの出現3分前です！')  

    if now == '12:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】アビシュの出現3分前です！')  

    if now == '18:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】千年九尾狐の出現3分前です！')  

    if now == '19:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】アズモダンの出現3分前です！')  

    if now == '20:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】氷の女王の出現3分前です！')  

    if now == '21:57':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【ワールドボス】ゼロスの出現3分前です！')  

    if now == '16:00':
        channel = client.get_channel(CHANNEL_ID)
        await channel.send('【WB】test1')  

loop.start()
client.run(TOKEN)