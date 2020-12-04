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
with open('variables.json') as f:
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
@commands.has_role('Sanitation Engineers')
async def stats(ctx):
    ftp = FTP(variables['FTPHOST'], user = variables['USER'], passwd= variables['PASSWORD'])
    ftp.cwd(variables['ftppath'])
    await ctx.send("Foomalyzing and parsing logs, this may take some time..")
    roundOneLink = ""
    roundTwoLink = ""
    logToParse = ""
    path = variables['path']
    c = -1  

    imagePath = variables['imagepath']  
    stylePath = variables['stylepath']
    print(ftp.nlst())
    dirList = ftp.nlst()
    logs = []
    for i in dirList:
        if(".log" in i):
            logs.append(i)
    for i in range(len(logs)):
        print(c)
        if(int(ftp.size(logs[c])) > 100000):
            print(int(ftp.size(logs[c])))
            print(logs[c])
            logToParse = logs[c]
            break
        else:
            c = c - 1
    
    print(logToParse)
    print(ftp.pwd())

    parseFolder = logToParse[:-4]
    if (parseFolder in dirList):
        print("Folder already exists, no upload necessary")
        roundTwoLink = variables["URLPATH"] + parseFolder + "/"
    else:
        ftp.retrbinary("RETR " + logToParse, open(logToParse, 'wb').write)
        roundTwoLink = variables["URLPATH"] + parseFolder + "/"
        os.mkdir(parseFolder)
        desPath = variables['despath'] + parseFolder

        os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder, logToParse))
        ftp.mkd(parseFolder)
        ftp.cwd(parseFolder)
        uploadThis(desPath, ftp)
        os.remove(logToParse)
        shutil.rmtree(path + parseFolder)
    

    #print(ftp.pwd())
    c = c - 1 
    for i in range(len(logs)):
        print(c)
        if(int(ftp.size(logs[c])) > 100000):
            print(int(ftp.size(logs[c])))
            print(logs[c])
            logToParse = logs[c]
            break
        else:
            c = c - 1

    print(logToParse)
    parseFolder = logToParse[:-4]
    if(parseFolder in dirList):
        print("Folder already exists, no upload necessary")
        roundOneLink = variables["URLPATH"] + parseFolder + "/"
    else:   
        ftp.retrbinary("RETR " + logToParse, open(logToParse, 'wb').write)
        roundOneLink = variables["URLPATH"] + parseFolder + "/"
        os.mkdir(parseFolder)
        desPath = variables['despath'] + parseFolder

        os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder, logToParse))
        ftp.mkd(parseFolder)
        ftp.cwd(parseFolder)
        uploadThis(desPath, ftp)
        os.remove(logToParse)
        print(path + parseFolder)
        shutil.rmtree(path + parseFolder)

    await ctx.send("Round 1: " + roundOneLink)
    await ctx.send("Round 2: " + roundTwoLink)
    ftp.quit()

client.run(variables['TOKEN'])

