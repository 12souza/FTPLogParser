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
ftp = FTP(variables['FTPHOST'], user = variables['USER'], passwd= variables['PASSWORD'])
ftp.cwd(variables['ftppath'])

def uploadThis(path):
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
            uploadThis(path + r'\{}'.format(f))
    ftp.cwd('..')
    os.chdir('..')

@client.command(pass_context=True,)
@commands.has_role('Sanitation Engineers')
async def stats(ctx):
    #ftp = FTP(variables['FTPHOST'], user = variables['USER'], passwd= variables['PASSWORD'])
    #ftp.cwd(variables['ftppath'])
    await ctx.send("Foomalyzing and parsing logs, this may take some time..")
    roundOneLink = ""
    roundTwoLink = ""
    path = variables['path']  

    imagePath = variables['imagepath']  
    stylePath = variables['stylepath'] 

    dirList = ftp.nlst()
    logs = []
    for i in dirList:
        if(".log" in i):
            logs.append(i)
    logToParse = (logs[-3])
    parseFolder = logToParse[:-4]
    ftp.retrbinary("RETR " + logToParse, open(logToParse, 'wb').write)

    parseFolder = logToParse[:-4]
    roundOneLink = variables["URLPATH"] + parseFolder + "/"
    os.mkdir(parseFolder)
    desPath = variables['despath'] + parseFolder

    os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder, logs[-3]))
    ftp.mkd(parseFolder)
    ftp.cwd(parseFolder)
    print(ftp.pwd(), desPath)
    uploadThis(desPath)
    #ftp.cwd("../")
    os.remove(logToParse)
    

    print(ftp.pwd()) 
    logToParse = (logs[-2])
    parseFolder = logToParse[:-4]

    ftp.retrbinary("RETR " + logToParse, open(logToParse, 'wb').write)

    
    roundTwoLink = variables["URLPATH"] + parseFolder + "/"
    os.mkdir(parseFolder)
    desPath = variables['despath'] + parseFolder

    os.system('cmd /c "F: && cd %s && logalyzer -image %s -style %s -o %s %s"' % (path, imagePath, stylePath, parseFolder, logs[-2]))
    ftp.mkd(parseFolder)
    ftp.cwd(parseFolder)
    print (ftp.pwd())
    uploadThis(desPath)
    ftp.cwd("../")

    os.remove(logToParse)

    await ctx.send("Round 1: " + roundOneLink)
    await ctx.send("Round 2: " + roundTwoLink)

    ftp.quit()
client.run(variables['TOKEN'])

