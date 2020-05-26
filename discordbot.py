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
import time

from discord.ext import commands
from datetime import datetime 
from discord.ext import tasks
from module import sub_module

#********** 設定情報を格納 **********
INIFILE = configparser.ConfigParser()
INIFILE.read('config.ini', 'UTF-8')
CHANNEL_ID = int(INIFILE.get('Discord', 'CHANNEL'))
COMAND_PREFIX = INIFILE.get('Discord', 'COMAND_PREFIX')
DEL_TIME = int(INIFILE.get('Discord', 'DEL_TIME'))

token = os.environ['DISCORD_BOT_TOKEN']
bot = commands.Bot(command_prefix= COMAND_PREFIX)
send_channel = ""
notes = ""
boot_time = ""
check_time = ""
check_sec = ""

#********** 起動時イベント **********
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    #投稿チャンネル名取得
    global send_channel
    send_channel = bot.get_channel(CHANNEL_ID)
    
    #起動時間取得
    global boot_time
    boot_time = datetime.now(pytz.timezone('Asia/Tokyo'))

#********** endコマンド **********
@bot.command()
async def end(ctx, boss: str, time: str):
    global notes
    msg = ""
    target_boss = ""

    #入力値を登録ボス名へ変換
    target_boss = sub_module.ChangeName(boss)

    #入力コマンドの正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
    else:
        msg = '【' + target_boss + '】の登録を受け付けました :memo: '

    if not int(len(time)) == 4:
        await ctx.send('入力時間が4桁ではありません :sob:\n再入力してください :pray:')
        sys.exit()
    for c in time:
        if (unicodedata.east_asian_width(str(c)) == 'F') or (unicodedata.east_asian_width(str(c)) == 'W'):
            await ctx.send('入力時間に全角文字が含まれています :sob:\n再入力してください :pray:')
            sys.exit()

    #次回出現時間の作成
    cyc = ""
    notes = ""
    cnt = 0
    update_row = 0
    target_time = ''

    end_date = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%Y/%m/%d')
    end_hour = time[:2]
    end_min = time[2:]
    last_time = end_date + ' ' + end_hour +  ':' + end_min

    with open("./data/BossList.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            cnt = cnt + 1
            if row[0] == target_boss:
                update_row = cnt - 1
                notes = ':map: : ' + row[1]
                if len(row[2]) == 5:
                    cyc = row[2]
                    cyc_hour = cyc[:2]
                    cyc_min = cyc[3:]
                if row[3] == "o":
                    notes = notes + ' , ランダム出現だよ :cyclone:'

    if cyc:
        end_hour = str(int(end_hour) + int(cyc_hour))
        end_min = str(int(end_min) + int(cyc_min))
        if int(end_min) > 59:
            end_hour = str(int(end_hour) + 1)
            end_min = str(int(end_min) - 60)
        if int(end_hour) > 23:
            end_hour = str(int(end_hour) - 24)
        if len(end_hour) == 1:
            end_hour = '0' + end_hour
        if len(end_min) == 1:
            end_min = '0' + end_min
        target_time = end_hour + ':' + end_min
        msg = msg + '\n次回出現時間の5分前 <' + sub_module.MakeTime(target_time) + '> にリマインダーをセットしました :alarm_clock:'

    msg = msg + '\n(' + notes + ')'

    #更新処理
    if not target_time == '':
        with open('./data/Schedule.csv', 'a', newline='', encoding = "utf_8") as write_csv:
            writer = csv.writer(write_csv)
            writer.writerow([target_time, target_boss,'temp','出現',notes])
        write_csv.close()

    if update_row > -1:
        df = pd.read_csv('./data/BossList.csv', encoding = "utf_8")
        df.loc[update_row , 'last time'] = last_time
        df.to_csv('./data/BossList.csv', index=False) 

    #情報登録・リマインダー設定の通知
    await ctx.send(msg)

#********** setコマンド **********
@bot.command()
async def set(ctx, boss: str, time: str):
    global notes
    msg = ""
    target_boss = ""

    #入力値を登録ボス名へ変換
    target_boss = sub_module.ChangeName(boss)

    #入力コマンドの正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
    else:
        msg = '【' + target_boss + '】の登録を受け付けました :memo: '

    if not int(len(time)) == 4:
        await ctx.send('入力時間が4桁ではありません :sob:\n再入力してください :pray:')
        sys.exit()
    for c in time:
        if (unicodedata.east_asian_width(str(c)) == 'F') or (unicodedata.east_asian_width(str(c)) == 'W'):
            await ctx.send('入力時間に全角文字が含まれています :sob:\n再入力してください :pray:')
            sys.exit()

    #リマインダーの設定
    target_time = ""
    set_hour = time[:2]
    set_min = time[2:]
    notes = ""
    with open("./data/BossList.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if row[0] == target_boss:
                notes = ':map: : ' + row[1]
                if row[3] == "o":
                    notes = notes + ' , ランダム出現だよ :cyclone:'
                else:
                    notes = notes + ')'

    set_min = str(int(set_min) +5)
    if int(set_min) > 60:
        set_min = str(int(set_min) - 60)
        set_hour = str(int(set_hour) + 1)
    if len(set_min) == 1:
        set_min = '0' + set_min
    if len(set_hour) == 1:
        set_hour = '0' + set_hour
    target_time = set_hour + ':' + set_min

    msg = msg + '\n <' + sub_module.MakeTime(target_time) + '> にリマインダーをセットしました :alarm_clock:\n'
    msg = msg + '(' + notes + ')'

    #更新処理
    with open('./data/Schedule.csv', 'a', newline='', encoding = "utf_8") as write_csv:
        writer = csv.writer(write_csv)
        writer.writerow([target_time, target_boss,'temp','出現',notes])
    write_csv.close()

    #リマインダー設定の通知
    await ctx.send(msg)

#********** infoコマンド **********
@bot.command()
async def info(ctx):
    #ボス一覧、前回エンド時間の表示
    df = pd.read_csv('./data/BossList.csv', encoding = "utf_8")
    await ctx.send(df[["name","last time"]])

#********** detailコマンド **********
@bot.command()
async def detail(ctx, boss: str):
    target_boss = ""

    #入力値を登録ボス名へ変換
    target_boss = sub_module.ChangeName(boss)

    #入力コマンドの正常性判定
    if target_boss == "":
        await ctx.send('入力されたボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()

    #ボスの詳細情報の表示
    df = pd.read_csv('./data/BossList.csv', encoding = "utf_8")
    await ctx.send(df[df["name"] == target_boss])

#********** nameコマンド **********
@bot.command()
async def name(ctx):
    #入力値を登録ボス名へ変換するテーブルの表示
    df = pd.read_csv('./data/ChangeName.csv', encoding = "utf_8")
    await ctx.send(df)

#********** todayコマンド **********
@bot.command()
async def today(ctx):
    #その日の定常/固定/登録済みの予定を表示
    weekday = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%a')
    df = pd.read_csv("./data/Schedule.csv", encoding = "utf_8")
    df_pickup = df[(df["remark"].isnull()) | (df["remark"] == weekday) | (df["remark"] == "temp")]
    await ctx.send(df_pickup[["time","events"]])

#********** webコマンド **********
@bot.command()
async def web(ctx):
    #外部サイト表示
    await ctx.send('https://games.app-liv.jp/archives/407903')

#********** deleteコマンド **********
@bot.command()
async def delete(ctx, time: str):
    #入力コマンドの正常性判定
    if not int(len(time)) == 4:
        await ctx.send('入力時間が4桁ではありません :sob:\n再入力してください :pray:')
        sys.exit()
    for c in time:
        if (unicodedata.east_asian_width(str(c)) == 'F') or (unicodedata.east_asian_width(str(c)) == 'W'):
            await ctx.send('入力時間に全角文字が含まれています :sob:\n再入力してください :pray:')
            sys.exit()

    #入力情報の格納
    chk_time = time[:2] + ':' + time[2:]
    global send_channel
    send_channel = bot.get_channel(CHANNEL_ID)
    cnt = 0
    delete_row = 0

    #入力時刻でスケジュールを検索し、一致すれば削除
    with open("./data/Schedule.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            cnt = cnt + 1
            if (chk_time == row[0]) and (row[2] == 'temp'):
                event_msg = '【' + row[1] + '】(出現時間：' + row[0] + ') の情報を削除しました :wastebasket:'
                delete_row = cnt - 1
                df = pd.read_csv('./data/Schedule.csv', encoding = "utf_8")
                df = df.drop(delete_row)
                df.to_csv('./data/Schedule.csv', index=False)
                await send_channel.send(event_msg)
    if delete_row == 0:
        event_msg = '入力された時間では削除できる予定がありませんでした。'
        await send_channel.send(event_msg)

#********** addコマンド **********
@bot.command()
async def add(ctx, input: str, changed: str):

    #変換後のボス名の正常性確認
    search_name = ''
    with open("./data/ChangeName.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if row[1] == changed:
                search_name = row[1]

    if not search_name:
        await ctx.send('入力された変換後のボス名が正しくありません :sob:\n再入力してください :pray:')
        sys.exit()
    else:
        with open('./data/ChangeName.csv', 'a', newline='', encoding = "utf_8") as write_csv:
            writer = csv.writer(write_csv)
            writer.writerow([input, changed])
        write_csv.close()
        await ctx.send('【' + input + '】の変換情報を登録しました :ok_hand:')

#********** mainteコマンド **********
@bot.command()
async def mainte(ctx):    
    diff_sec = time.time() - check_sec
    if diff_sec < 60:
       stat = ':bulb: 正常 :bulb:'
    else:
        stat = ':warning: 停止中 :warning:'

    await ctx.send('状態          ：' + stat)
    await ctx.send('起動日時      ：' + str(boot_time))
    await ctx.send('起動時間      ：' + str(datetime.now(pytz.timezone('Asia/Tokyo')) - boot_time))
    await ctx.send('リマインダ確認：' + str(check_time))

#********** helpコマンド **********
    #既存のhelpコマンドを削除
bot.remove_command('help')

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
    embed.add_field(name=COMAND_PREFIX + "delete [hhmm]", value="[hhmm]：削除する予定の時間を4桁の半角数字で入力します。(必須項目)\n正常に受け付けるとBOTから返信があり、入力した時間の予定が削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "add [input] [changed]", value="[input]：新たに使用するボス名を入力します。(必須項目)\n[changed]：ボス一覧に登録されているボス名を入力します。(必須項目)\n正常に受け付けるとBOTから返信があり、ボス名変換テーブルに登録されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "web", value="フィールドボスに関する外部サイトのURLを表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    embed.add_field(name=COMAND_PREFIX + "help", value="入力可能なコマンドと使い方を表示します。\n投入コマンドと表示結果は90秒後に自動的に削除されます。\n", inline=False)
    await ctx.send(embed=embed)

#********** 特定のメッセージを削除 **********
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    #BOTの発言
    if message.author.bot:
        if not (message.content.startswith('【')) or (message.content.startswith('入力')):
            await asyncio.sleep(DEL_TIME)
            await message.delete()
    #ユーザーの発言
    else:
        if (message.content.startswith(COMAND_PREFIX + 'info')) or (message.content.startswith(COMAND_PREFIX + 'name')) or (message.content.startswith(COMAND_PREFIX + 'detail')) or (message.content.startswith(COMAND_PREFIX + 'today')) or (message.content.startswith(COMAND_PREFIX + 'web')) or (message.content.startswith(COMAND_PREFIX + 'help')):
            await asyncio.sleep(DEL_TIME)
            await message.delete()

#********** リマインダー **********
@tasks.loop(seconds=60)
async def loop():
    #現在情報の取得
    now = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H:%M')
    weekday = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%a')
    chk_hour = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%H')
    chk_min = datetime.now(pytz.timezone('Asia/Tokyo')).strftime('%M')

    #global send_channel
    #send_channel = bot.get_channel(CHANNEL_ID)
    cnt = 0
    delete_row = 0

    #リマインダー確認時間取得
    global check_time
    check_time = datetime.now(pytz.timezone('Asia/Tokyo'))
    global check_sec
    check_sec = time.time()

    #現在時刻でスケジュールを検索し、予定があれば通知
    with open("./data/Schedule.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            cnt = cnt + 1
            chk_time = sub_module.MakeTime(row[0])
            if now == chk_time:
                event_msg = '【' + row[1] + '】の' + row[3] + '5分前をお知らせします :incoming_envelope:\n(出現時間：' + row[0]
                if not row[4] == '':
                    event_msg = event_msg +  ' , ' + row[4]
                event_msg = event_msg + ')'

                if (row[2] == '') or (row[2] == weekday):
                    await send_channel.send(event_msg)
                elif row[2] == 'temp':
                    delete_row = cnt - 1
                    df = pd.read_csv('./data/Schedule.csv', encoding = "utf_8")
                    df = df.drop(delete_row)
                    df.to_csv('./data/Schedule.csv', index=False)
                    await send_channel.send(event_msg)
    read_csv.close()

loop.start()

bot.run(token)
