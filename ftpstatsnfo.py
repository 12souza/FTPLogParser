from ftplib import FTP
import shutil
import urllib.request as request
from contextlib import closing
import os
import json
import time
import discord
from discord.ext import commands
from discord.utils import get
with open('variablesNFO.json') as f:
    variables = json.load(f)
client = commands.Bot(command_prefix = "!", case_insensitive=True)


def uploadThis(path, ftp):
    files = os.listdir(path)
    os.chdir(path)
    for f in files:
        if os.path.isfile(path + r'\{}'.format(f)):
            fh = open(f, 'rb')
            ftp.storbinary('STOR %s' % f, fh)
            fh.close()
        elif os.path.isdir(path + r'\{}'.format(f)):
            ftp.mkd(f)
            ftp.cwd(f)
            uploadThis(path + r'\{}'.format(f), ftp)
    ftp.cwd('..')
    os.chdir('..')

    
@client.command(pass_context=True,)
@commands.cooldown(1, 300, commands.BucketType.guild)
@commands.has_role('Sanitation Engineers')
async def stats(ctx):
    await ctx.send("Creating and Foomalyzing server logs.. this may take at least 1 minute...")    
    logToParse1 = ""
    logToParse2 = ""
    roundOneLink = ""
    roundTwoLink = ""
    path = variables['path']
    imagePath = variables['imagepath']  
    stylePath = variables['stylepath']

    ftp = FTP(variables['FTPHOST'], user = variables['USER'], passwd= variables['PASSWORD'])
    ftp.cwd(variables['ftppath'])
    dirList = ftp.nlst()
    logs = []
    c = -1
    for i in dirList:
        if(".log" in i):
            logs.append(i)
    for i in range(len(logs)):
        if(int(ftp.size(logs[c])) > 100000):
            logToParse2 = logs[c]
            break
        else:
            c = c - 1
    c = c - 1
    for i in range(len(logs)):
        if(int(ftp.size(logs[c])) > 100000):
            logToParse1 = logs[c]
            break
        else:
            c = c - 1
    parseFolder1 = logToParse1[:-4]
    parseFolder2 = logToParse2[:-4]
    ftp.retrbinary("RETR " + logToParse1, open(logToParse1, 'wb').write)
    ftp.retrbinary("RETR " + logToParse2, open(logToParse2, 'wb').write)
    ftp.quit()

    ftp = FTP(variables['SITEHOST'], user = variables['USER2'], passwd= variables['PASSWORD2'])
    ftp.cwd('public')
    ftp.cwd('logs')
    print(ftp.nlst())
    siteList = ftp.nlst()

    if (parseFolder1 in siteList):
        print("Folder already exists, no upload necessary")
        roundOneLink = variables["URLPATH"] + parseFolder1 + "/"
    else:
        roundOneLink = variables["URLPATH"] + parseFolder1 + "/"
        os.mkdir(parseFolder1)
        desPath = variables['despath'] + parseFolder1

        os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder1, logToParse1))
        ftp.mkd(parseFolder1)
        ftp.cwd(parseFolder1)
        uploadThis(desPath, ftp)
        os.remove(logToParse1)
        shutil.rmtree(path + parseFolder1)

    if (parseFolder2 in siteList):
        print("Folder already exists, no upload necessary")
        roundTwoLink = variables["URLPATH"] + parseFolder2 + "/"
    else:
        roundTwoLink = variables["URLPATH"] + parseFolder2 + "/"
        os.mkdir(parseFolder2)
        desPath = variables['despath'] + parseFolder2

        os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder2, logToParse2))
        ftp.mkd(parseFolder2)
        ftp.cwd(parseFolder2)
        uploadThis(desPath, ftp)
        os.remove(logToParse2)
        shutil.rmtree(path + parseFolder2)

    await ctx.send("Round 1: " + roundOneLink)
    await ctx.send("Round 2: " + roundTwoLink)

    ftp.quit()




client.run(variables['TOKEN'])

