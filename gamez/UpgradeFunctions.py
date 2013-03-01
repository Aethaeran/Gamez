import urllib
import json
from distutils.version import LooseVersion
from Constants import VersionNumber
import ConfigParser
import os
import urllib2
import tarfile
import shutil
from Logger import LogEvent
import gamez
from classes import *

def CheckForNewVersion(app_path):
    LogEvent("Checking to see if a new version is available")
    newVersionAvailable = False
    currentVersion = VersionNumber()
    mostRecentVersion = GetLatestVersion()
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    isToDeferUpgrade = config.get('SystemGenerated','is_to_ignore_update').replace('"','')
    ignoredVersion = config.get('SystemGenerated','ignored_version').replace('"','')
    if(LooseVersion(mostRecentVersion) > LooseVersion(currentVersion)):
        if(isToDeferUpgrade == '0'):
            newVersionAvailable = True
    if(isToDeferUpgrade == '1'):
        if(LooseVersion(mostRecentVersion) > LooseVersion(ignoredVersion)):
            newVersionAvailable = True
    return newVersionAvailable

def GetLatestVersion():
    LogEvent("Retrieving the latest version")
    mostRecentVersion = '0.0.0.0'
    url = 'https://api.github.com/repos/avjui/Gamez/tags'
    opener = urllib.FancyURLopener({})
    responseObject = opener.open(url)
    response = responseObject.read()
    responseObject.close()
    jsonObject = json.loads(response)
    for val in jsonObject:
        name = val['name']
        tagVersion = name.replace("v","").replace("'","")
        tagVersion = str(tagVersion)
        try:
            if(LooseVersion(tagVersion) > LooseVersion(mostRecentVersion)):
                mostRecentVersion = tagVersion
        except:
            continue
    return mostRecentVersion

def IgnoreVersion(app_path):
    LogEvent("Ignoring Version")
    versionToIgnore = GetLatestVersion()
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    if(config.has_section('SystemGenerated') == False):
        config.add_section('SystemGenerated')
    config.set('SystemGenerated','is_to_ignore_update','1')
    config.set('SystemGenerated','ignored_version','"' + versionToIgnore + '"')
    with open(configfile,'wb') as configFile:
        config.write(configFile)

def UpdateToLatestVersion(app_path):
    LogEvent("Updating to latest version")
    filesToIgnore = ["Gamez.ini","Gamez.db"]
    filesToIgnoreSet     = set(filesToIgnore)
    updatePath = os.path.join(app_path,"update")
    if not os.path.exists(updatePath):     
        os.makedirs(updatePath)
    latestVersion = GetLatestVersion()
    tagUrl = "https://github.com/avjui/Gamez/tarball/TheGamedb/v" + latestVersion
    LogEvent("Downloading from GitHub")
    data = urllib2.urlopen(tagUrl)
    downloadPath = os.path.join(app_path,data.geturl().split('/')[-1])
    downloadedFile = open(downloadPath,'wb')
    downloadedFile.write(data.read())
    downloadedFile.close()
    LogEvent("Extracting files")
    tarredFile = tarfile.open(downloadPath)
    tarredFile.extractall(updatePath)
    tarredFile.close()
    os.remove(downloadPath)
    LogEvent("Upgrading files")
    contentsDir = [x for x in os.listdir(updatePath) if os.path.isdir(os.path.join(updatePath, x))]
    updatedFilesPath = os.path.join(updatePath,contentsDir[0])
    for dirname, dirnames, filenames in os.walk(updatedFilesPath):
        dirname = dirname[len(updatedFilesPath)+1:]
        for file in filenames:
            src = os.path.join(updatedFilesPath,dirname,file)
            dest = os.path.join(app_path,dirname,file)
            if((file in filesToIgnoreSet) == True):
                continue
            if(os.path.isfile(dest)):
                os.remove(dest)
            os.renames(src,dest)
    shutil.rmtree(updatePath) 
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    if(config.has_section('SystemGenerated') == False):
        config.add_section('SystemGenerated')
    config.set('SystemGenerated','is_to_ignore_update','0')
    config.set('SystemGenerated','ignored_version','"versionToIgnore"')
    with open(configfile,'wb') as configFile:
        config.write(configFile)
    LogEvent("Upgrading complete")
    return "Successfully Upgraded to Version " + latestVersion


def initDB():
    gamez.DATABASE.init(gamez.DATABASE_PATH)
    LogEvent("creating class tables")
    Game.create_table(True)
    Platform.create_table(True)
    Status.create_table(True)

    classes = (Game, Platform, Status)
    for cur_c in classes:
        cur_c.create_table(True)

    migration_was_done = False
    for cur_c in classes:
        if cur_c.updateTable():
            migration_was_done = True

    checkDefaults(migration_was_done)


def checkDefaults(resave=False):
    #create default Platforms
    #http://wiki.thegamesdb.net/index.php?title=GetPlatformsList
    #move this to common.py
    for curPlatform in [('Wii', 'nintendo-wii', 9), ('Xbox 360', 'microsoft-xbox', 15)]:
        try:
            p = Platform.get(Platform.tgdb_id == curPlatform[2])
            if not resave:
                continue
        except Platform.DoesNotExist:
            p = Platform()
        p.name = curPlatform[0]
        p.alias = curPlatform[1]
        p.tgdb_id = curPlatform[2]
        p.save()

    #create default Status
    for value, name in common.STATUS_NAMES.items():
        try:
            s = Status.get(Status.value == value)
            if not resave:
                continue
        except Status.DoesNotExist:
            s = Status()
        s.name = name
        s.value = value
        s.hidden = not value in common.SELECTABLE_STATUS
        s.save()

