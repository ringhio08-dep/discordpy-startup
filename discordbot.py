import discord
import configparser
import csv
import pandas as pd
import unicodedata
import asyncio
import re
import os
import traceback
import pytz

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

#起動時イベント
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    global send_channel
    send_channel = bot.get_channel(CHANNEL_ID)

#endコマンド
@bot.command()
async def end(ctx, boss: str, time: str):
#入力値を登録ボス名へ変換
    global notes
    msg = ""
    input_boss = boss
    input_time = time
    target_boss = ""
    
    with open("ChangeName.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if (row[0] == input_boss) or (row[1] == input_boss):
                target_boss = row[1]
                msg = '【' + target_boss + '】の登録を受け付けました :memo: '
#入力値の正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
    num = int(len(input_time))
    if not num == 4:
        await ctx.send('入力時間が4桁ではありません :sob:\n再入力してください :pray:')
        sys.exit()
    for c in input_time:
        if (unicodedata.east_asian_width(str(c)) == 'F') or (unicodedata.east_asian_width(str(c)) == 'W'):
            await ctx.send('入力時間に全角文字が含まれています :sob:\n再入力してください :pray:')
            sys.exit()
#次回出現時間の作成
    target_time = ""
    end_date = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d')
    end_hour = input_time[:2]
    end_min = input_time[2:]
    await send_channel.send(end_hour)
    await send_channel.send(end_min)
    cyc = ""
    notes = ""
    cnt = 0
    update_row = 0
    last_time = end_date + ' '
    if len(end_hour) == 1:
        last_time = last_time + '0' + end_hour
    else:
        last_time = last_time + end_hour
    if len(end_min) == 1:
        last_time = last_time +  ':0' + end_min
    else:
        last_time = last_time +  ':' + end_min
    with open("BossList.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            cnt = cnt + 1
            if row[0] == target_boss:
                update_row = cnt - 1
                notes = '(:map: : ' + row[1]
                if len(row[2]) == 1:
                    cyc = row[2]
                if row[3] == "o":
                    notes = notes + ' , ランダム出現だよ :cyclone:)'
                else:
                    notes = notes + ')'
    if cyc:
        end_hour = str(int(end_hour) + int(cyc))
        end_min = str(int(end_min))
        if int(end_min) < 5:
            end_min = str(int(end_min) + 55)
            end_hour = str(int(end_hour) - 1)
        else:
            end_min = str(int(end_min) - 5)
        if int(end_hour) > 23:
            end_hour = str(int(end_hour) - 24)
        if len(end_hour) == 1:
            end_hour = '0' + end_hour
        if len(end_min) == 1:
            target_time = end_hour + ':0' + end_min
        else:
            target_time = end_hour + ':' + end_min
        msg = msg + '\n次回出現時間の5分前 <' + target_time + '> にリマインダーをセットしました :alarm_clock:\n'
    msg = msg + notes
#更新処理
    if not target_time == '':
        with open('Schedule.csv', 'a', newline='', encoding = "utf_8") as write_csv:
            writer = csv.writer(write_csv)
            writer.writerow([target_time, target_boss,'temp','出現',notes])
    if update_row > 0:
        df = pd.read_csv('BossList.csv', encoding = "utf_8")
        df.loc[update_row , 'last time'] = last_time
        df.to_csv('BossList.csv', index=False) 
#情報登録・リマインダー設定の通知
    await ctx.send(msg)

#setコマンド
@bot.command()
async def set(ctx, boss: str, time: str):
#入力値を登録ボス名へ変換
    global notes
    msg = ""
    input_boss = boss
    input_time = time
    target_boss = ""
    
    with open("ChangeName.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if (row[0] == input_boss) or (row[1] == input_boss):
                target_boss = row[1]
                msg = '【' + target_boss + '】の登録を受け付けました :memo: '
#入力値の正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
    num = int(len(input_time))
    if not num == 4:
        await ctx.send('入力時間が4桁ではありません :sob:\n再入力してください :pray:')
        sys.exit()
    for c in input_time:
        if (unicodedata.east_asian_width(str(c)) == 'F') or (unicodedata.east_asian_width(str(c)) == 'W'):
            await ctx.send('入力時間に全角文字が含まれています :sob:\n再入力してください :pray:')
            sys.exit()
#リマインダーの設定
    target_time = ""
    end_hour = input_time[:2]
    end_min = input_time[2:]
    notes = ""
    with open("BossList.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if row[0] == target_boss:
                notes = '(:map: : ' + row[1]
                if row[3] == "o":
                    notes = notes + ' , ランダム出現だよ :cyclone:)'
                else:
                    notes = notes + ')'

    target_time = end_hour + ':' + end_min

    msg = msg + '\n <' + target_time + '> にリマインダーをセットしました :alarm_clock:\n'
    msg = msg + notes
#更新処理
    with open('Schedule.csv', 'a', newline='', encoding = "utf_8") as write_csv:
        writer = csv.writer(write_csv)
        writer.writerow([target_time, target_boss,'temp','出現',notes])
#リマインダー設定の通知
    await ctx.send(msg)

#infoコマンド
@bot.command()
async def info(ctx):
#ボス一覧の表示
    df = pd.read_csv('BossList.csv', encoding = "utf_8")
    await ctx.send(df[["name","last time"]])

#detailコマンド
@bot.command()
async def detail(ctx, boss: str):
#ボスの詳細情報を表示
#入力値を登録ボス名へ変換
    input_boss = boss
    target_boss = ""
    
    with open("ChangeName.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if (row[0] == input_boss) or (row[1] == input_boss):
                target_boss = row[1]
#入力値の正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
#
    df = pd.read_csv('BossList.csv', encoding = "utf_8")
    await ctx.send(df[df["name"] == target_boss])

#nameコマンド
@bot.command()
async def name(ctx):
#入力値を登録ボス名へ変換するテーブルの表示
    df = pd.read_csv('ChangeName.csv', encoding = "utf_8")
    await ctx.send(df)

#todayコマンド
@bot.command()
async def today(ctx):
#その日の定常/固定/登録済みの予定を表示
    weekday = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%a')
    df = pd.read_csv("Schedule.csv", encoding = "utf_8")
    df_pickup = df[(df["remark"].isnull()) | (df["remark"] == weekday) | (df["remark"] == "temp")]
    await ctx.send(df_pickup[["time","events"]])

#webコマンド
@bot.command()
async def web(ctx):
#外部サイト表示
    await ctx.send('https://m-s-y.com/lineage-m/tips/21174/')
    
bot.remove_command('help')

#helpコマンド
@bot.command()
async def help(ctx):
#ヘルプの表示
    embed = discord.Embed(title="いろいろお手伝いするbot(仮)", description="ボスの情報管理や出現リマインダーでお手伝いするBOTです。\nボス狩りのお役に立ててください。\n入力可能なコマンドは以下となります。\n", color=0xff0000)
    embed.add_field(name=COMAND_PREFIX + "name", value="各コマンドで入力可能なボス名の一覧を表示します。\ninputまたはchanged欄のあるボス名が入力可能です。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "end [boss] [hhmm]", value="[boss]：ボス名を入力します。(必須項目)\n[hhmm]：エンド時間を4桁の半角数字で入力します。(必須項目)\n正常に受け付けるとBOTから返信があり、次回出現時間の5分前にリマインダーが設定されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "set [boss] [hhmm]", value="[boss]：ボス名を入力します。(必須項目)\n[hhmm]：リマインドする時間を4桁の半角数字で入力します。(必須項目)\n正常に受け付けるとBOTから返信があり、入力した時間にリマインダーが設定されます。\n", inline=True)
    embed.add_field(name=COMAND_PREFIX + "info", value="ボス一覧と前回のエンド時間を表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "detail [boss]", value="[boss]：ボス名を入力します。(必須項目)\n入力したボスの出現場所や周期などを含む詳細情報を表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "today", value="その日に予定されているボス出現時間やイベントの一覧を表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "web", value="フィールドボスに関する外部サイトのURLを表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "help", value="入力可能なコマンドと使い方を表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    await ctx.send(embed=embed)

#特定のメッセージを削除する
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    if message.author.bot:
        if not (message.content.startswith('【')) or (message.content.startswith('入力')):
            await asyncio.sleep(DEL_TIME)
            await message.delete()
    else:
        if (message.content.startswith(COMAND_PREFIX + 'info')) or (message.content.startswith(COMAND_PREFIX + 'name')) or (message.content.startswith(COMAND_PREFIX + 'detail')) or (message.content.startswith(COMAND_PREFIX + 'today')) or (message.content.startswith(COMAND_PREFIX + 'web')) or (message.content.startswith(COMAND_PREFIX + 'help')):
            await asyncio.sleep(DEL_TIME)
            await message.delete()

#60秒ごとに予定を確認する
@tasks.loop(seconds=60)
async def loop():
#現在情報の取得
    now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M')
    weekday = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%a')
    cnt = 0
    delete_row = 0
#現在時刻でスケジュールを検索し、予定があれば通知
    with open("Schedule.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            cnt = cnt + 1
            event_msg = '【' + row[1] + '】の' + row[3] + '5分前をお知らせします :incoming_envelope:'
            if (row[0] == now) and (row[2] == ''):
                if not row[4] == '':
                    event_msg = event_msg + '\n' + row[4]
                await send_channel.send(event_msg)
            elif (row[0] == now) and (row[2] == weekday):
                if not row[4] == '':
                    event_msg = event_msg + '\n' + row[4]
                await send_channel.send(event_msg)
            elif (row[0] == now) and (row[2] == 'temp'):
                if not row[4] == '':
                    event_msg = event_msg + '\n' + row[4]
                await send_channel.send(event_msg)
                delete_row = cnt - 1
                df = pd.read_csv('Schedule.csv', encoding = "utf_8")
                df = df.drop(delete_row)
                df.to_csv('Schedule.csv', index=False)
loop.start()

bot.run(token)
