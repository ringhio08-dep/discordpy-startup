import discord
import csv

#********** 入力ボス名を登録ボス名へ変換 **********
def ChangeName(name):
    search_name = ''
    with open("./data/ChangeName.csv", "r" , encoding = "utf_8") as read_csv:
        reader = csv.reader(read_csv)
        header = next(reader)
        for row in reader:
            if (row[0] == name) or (row[1] == name):
                search_name = row[1]
    return search_name

#********** 5分前作成 **********
def MakeTime(time):
    chk_hour = time[:2]
    chk_min = time[3:]

    if int(chk_min) < 5:
        chk_min = str(55 + int(chk_min))
        if not chk_hour == '00':
            chk_hour = str(int(chk_hour) - 1)
        else:
            chk_hour = '23'
    else:
        chk_min = str(int(chk_min) - 5)

    if len(chk_min) == 1:
        chk_min = '0' + chk_min
    if len(chk_hour) == 1:
        chk_hour = '0' + chk_hour

    time = chk_hour + ':' + chk_min
    return time
