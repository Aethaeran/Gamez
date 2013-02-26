import os
import sys
import re
import urllib
import urllib2
import shutil
import stat
import json
import ConfigParser
from xml.dom.minidom import *

import gamez

from DBFunctions import GetRequestedGamesAsArray, UpdateStatus, AdditionWords, GetRequestedGamesForFolderProcessing, GetGameData
from FolderFunctions import ProcessDownloaded
from Helper import replace_all, FindAddition, findGamezID
from subprocess import call
from Logger import LogEvent, DebugLogEvent
from Constants import VersionNumber
import lib.feedparser as feedparser
from lib import requests


class CostumOpener(urllib.FancyURLopener):
    version = 'Gamez/' + VersionNumber()



class GameTasks():

    def FindGames(self, manualSearchGame,nzbsrususername, nzbsrusapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isnzbsrusEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isNZBSU,nzbsuapi,retention):
        # First some variables
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        isPS3TBEnable = config.get('SystemGenerated','ps3_tb_enable').replace('"','')
        isPS3JBEnable = config.get('SystemGenerated','ps3_jb_enable').replace('"','')       
        BlacklistWordsXbox360 = config.get('SystemGenerated','blacklist_words_xbox360').replace('"','')
        BlacklistWordsWii = config.get('SystemGenerated','blacklist_words_wii').replace('"','')
        blacklistwords = ''
        if(isSabEnabled == "1"):       
            GameTasks().CheckIfPostProcessExistsInSab(sabnzbdApi,sabnzbdHost,sabnzbdPort)
        nzbsrususername = nzbsrususername.replace('"','')
        nzbsrusapi = nzbsrusapi.replace('"','')
        newznabApi = newznabApi.replace('"','')     
        newznabWiiCat = newznabWiiCat.replace('"','')  
        games = GetRequestedGamesAsArray(manualSearchGame)
        for game in games:
            try:
                game_name = str(game[0])
                game_id = str(game[1])
                system = str(game[2])
                LogEvent("Searching for game: " + game_name)
                isDownloaded = False
                if(system == "Xbox360" and BlacklistWordsXbox360 <> ''):
                    blacklistwords = BlacklistWordsXbox360
                    DebugLogEvent("Blacklisted Words for XBOX360 [ " + str(blacklistwords) + " ]")
                if(system == "Wii" and BlacklistWordsWii <> ''):
                    blacklistwords = BlacklistWordsWii
                    DebugLogEvent("Blacklisted Words for Wii [ " + blacklistwords + " ]")
                if(system == "PS3"):
                    if(isPS3TBEnable == "1"):
                        blacklistwords = "TB"
                        DebugLogEvent("[PS3] execlude True Blue") 
                    if(isPS3JBEnable == "1"):
                        blacklistwords = "JB"
                        DebugLogEvent("[PS3] execlude Jail Break")
                blacklistwords = re.split(';|,',blacklistwords)
                blacklistwords = filter(None, blacklistwords)

                if(isnzbsrusEnabled == "1"):
                    DebugLogEvent("Matrix Enable")
                    if(nzbsrususername <> '' and nzbsrusapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on NZB Matrix")
                            isDownloaded = GameTasks().FindGameOnNzbsrus(game_name,game_id,nzbsrususername,nzbsrusapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("NZBSRus Settings Incomplete.")
                
                if(isNewznabEnabled == "1"):
                    DebugLogEvent("Newznab Enable")
                    if(newznabWiiCat <> '' and newznabXbox360Cat <> '' and newznabPS3Cat <> '' and newznabPCCat <> '' and newznabApi <> '' and newznabHost <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] for ["+ system + "] on Newznab")
                            isDownloaded = GameTasks().FindGameOnNewznabServer(game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("Newznab Settings Incomplete.")  
                        
                if(isNZBSU == "1"):
                    DebugLogEvent("nzb.su Enable")
                    if(nzbsuapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on nzb.su")
                            isDownloaded = GameTasks().FindGameOnNZBSU(game_name,game_id,nzbsuapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention)
                    else:
                        LogEvent("NZBSU Settings Incomplete.")

                if(isTorrentBlackholeEnabled == "1"):
                     DebugLogEvent("Torrent Enable")
                     if(isTorrentKATEnabled == "1"):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on KickAss Torrents")
                            isDownloaded = GameTasks().FindGameOnKAT(game_id,game_name,system,torrentBlackholePath,blacklistwords)
            except:
                continue
        return

    def FindGameOnNzbsrus(self,game_name,game_id,nzbsrus_uid,nzbsrus_api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        if(system == "Wii"):
            catToUse = "92"
        elif(system == "Xbox360"):
            catToUse = "88"
        elif(system == "PS3"):
            catToUse = "89"
        elif(system == "PC"):
            catToUse = "27"        
        else:
            LogEvent("Unrecognized System")
            return False
        game_name = replace_all(game_name)
        url = "http://www.nzbsrus.com/api.php?key=" + nzbsrus_api + "&uid=" + nzbsrus_uid + "&cat=" + catToUse + "&searchtext=" + game_name.replace(" ","+")
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            opener = CostumOpener()
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
        except:
            LogEvent("Unable to connect to Nzbsrus.com")
            return False
        try:
            if(response == "[]"):
                return False            
            jsonObject = json.loads(response)['results']
            for item in jsonObject:
                nzbTitle = item["name"]
                nzbID = item["id"]                
                nzbKey = item["key"]
                nzbUrl ="http://www.nzbsrus.com/nzbdownload_rss.php/" + nzbID + "/" + nzbsrus_uid + "/" + nzbKey + "/"
                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                        gamenameaddition = FindAddition(nzbTitle)
                        DebugLogEvent("Additions for " + game_name + " are " + gamenameaddition)
                        game_name = game_name + gamenameaddition
                        LogEvent("Game found on NzbsRus")
                        result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                        if(result):
                            UpdateStatus(game_id,"Snatched")
                            return True
                        return False
                    else:
                        LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                        return False
        except:
            LogEvent("Error getting game [" + game_name + "] from NzbsRus")
            return False

    def FindGameOnNewznabServer(self,game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        mustBeSize = 0
        if(system == "Wii"):
            catToUse = newznabWiiCat
        elif(system == "Xbox360"):
            mustBeSize = 7340032 # 7*1024*1024
            catToUse = newznabXbox360Cat
        elif(system == "PS3"):
            catToUse = newznabPS3Cat
            DebugLogEvent("System [ " + system + " ] and catToUse [ " + catToUse + " ] original Cat [" + newznabPS3Cat + "]") 
        elif(system == "PC"):
            catToUse = newznabPCCat
            DebugLogEvent("PC: System [ " + system + " ] and catToUse [ " + catToUse + " ]")
        else:
            LogEvent("Unrecognized System")
            return False

        sabnzbdCategory = sabnzbdCategory + "_" + system

        game_name = replace_all(game_name)
        searchname = replace_all(game_name)

        if not newznabHost.startswith('http'):
            newznabHost = "http://" + newznabHost
            LogEvent("!!!! Notice: Please update your Newznab settings and add http(s) to the adress  !!!!")

        if newznabPort == '80' or newznabPort == '':
            url = newznabHost + "/api?apikey=" + newznabApi + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=json"
        else:
            url = newznabHost + ":" + newznabPort + "/api?apikey=" + newznabApi + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=json"

        DebugLogEvent("Searching Newznab url: " + url)
        r = requests.get(url)
        """
        if r.code != 200:
            LogEvent("Error code(" + str(r.code) + ") from Newznab Server: " + url)
            return False
        """
        response = r.text
        DebugLogEvent("blupp")
        try:
            jsonObject = json.loads(response)
            LogEvent("we have a response from newsnab")
            #LogEvent("jsonobj: " +jsonObject)
            items = jsonObject["channel"]["item"]
            for item in items:
                LogEvent("item: " + item["title"])
                nzbTitle = item["title"]
                nzbUrl = item["link"]
                blacklisted = False
                for blacklistword in blacklistwords:
                    DebugLogEvent("Checking Word: " + str(blacklistword))
                    if blacklistword in nzbTitle:
                        DebugLogEvent("Found '" + str(blacklistword) + "' in Title: '" + nzbTitle + "'. Skipping")
                        blacklisted = True
                if blacklisted:
                    continue

                curSize = 0
                for curAttr in item['attr']:
                    if curAttr['@attributes']['name'] == 'size':
                        curSize = int(curAttr['@attributes']['value'])

                if not curSize > mustBeSize:
                    LogEvent('Rejecting ' + item['title'] + ' because its to small (' + str(curSize) + ')')
                    continue

                gamenameaddition = FindAddition(nzbTitle)
                DebugLogEvent("Additions for " + game_name + " are " + gamenameaddition)
                game_name = game_name + gamenameaddition
                LogEvent("Game found on Newznab: " + nzbTitle)
                result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                if(result):
                    UpdateStatus(game_id, "Snatched")
                    return True
                else:
                    LogEvent("unable to load nzb, please check settings")

            else:
                LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                return False
        except Exception as e:
            DebugLogEvent(str(e))
            LogEvent("Error getting game [" + game_name + "] from Newznab")
            return False
            
    def FindGameOnNZBSU(self,game_name,game_id,api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,blacklistwords,retention):
        catToUse = ''
        if(system == "Wii"):
            catToUse = "1030"
        elif(system == "Xbox360"):
            catToUse = "1050"
        elif(system == "PS3"):
            catToUse = "1080"
        elif(system == "PC"):
            catToUse = "4050"        
        else:
            LogEvent("Unrecognized System")
            return False
        searchname = replace_all(game_name)
        url = "http://nzb.su/api?apikey=" + api + "&t=search&maxage=" + retention + "&cat=" + catToUse + "&q=" + searchname.replace(" ","+") + "&o=xml"
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            opener = urllib.FancyURLopener({})
            self.responseObject = opener.open(url)
            self.data = self.responseObject.read()
            self.responseObject.close()
            DebugLogEvent("Search for " + url)
        except:
            LogEvent("Unable to connect to Server: " + url)
            return False
        try:
            self.d = feedparser.parse(self.data)
            for item in self.d.entries:

                nzbTitle = item['title']
                nzbID = item['newznab_attr']['value']

                for blacklistword in blacklistwords:
                    if(blacklistword == ''):
                        DebugLogEvent("No blacklisted word(s) are given")
                    else:
                        DebugLogEvent(" The Word is " + str(blacklistword))
                    if not str(blacklistword) in nzbTitle or blacklistword == '':
                        AdditionWords(nzbTitle,game_id)
                        LogEvent("Game found on http://nzb.su")
                        nzbUrl = "http://nzb.su/api?apikey=" + api + "&t=get&id=" + nzbID 
                        DebugLogEvent("Link URL [ " + nzbUrl + " ]")
                        result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                        if(result):
                            UpdateStatus(game_id,"Snatched")
                            return True
                        return False
                    else:
                        LogEvent('Nothing found without blacklistet Word(s) "' + str(blacklistword) + '"')
                        return False
        except:
            LogEvent("Error getting game [" + game_name + "] from http://nzb.su")
            return False


    def DownloadNZB(self,nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system):
        try:
            result = False
            if(isSabEnabled == "1"):
                result = GameTasks().AddNZBToSab(nzbUrl,game_name,system,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory)
            if(isNzbBlackholeEnabled == "1"):
                result = GameTasks().AddNZBToBlackhole(nzbUrl,nzbBlackholePath,game_name,system)
            return result
        except:
            LogEvent("Unable to download NZB: " + nzbUrl)
            return False

    def AddNZBToSab(self,nzbUrl,game_name,system,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory):

        if not sabnzbdHost.startswith('http'):
            sabnzbdHost = "http://" + sabnzbdHost
            LogEvent("!!!! Notice: Please update your sabnzbd settings and add http(s) to the adress !!!!")   

        nzbUrl = urllib.quote(nzbUrl)
        
        url = sabnzbdHost + ":" +  sabnzbdPort + "/sabnzbd/api?mode=addurl&pp=3&apikey=" + sabnzbdApi + "&name=" + nzbUrl + "&nzbname=" + game_name + " (G." + str(game_id) + ")"
        if(sabnzbdCategory <> ''):
            url = url + "&cat=" + sabnzbdCategory
        DebugLogEvent("Send to sabnzdb: " + url)
        try:
            #responseObject = urllib.FancyURLopener({}).open(url)
            #response = responseObject.read()
            #responseObject.close()
            r = requests.get(url)
            DebugLogEvent("sab response code: " + str(r.status_code))
            DebugLogEvent("sab response: " + str(r.text))
        except:
            LogEvent("Unable to connect to Sanzbd: " + url)
            return False
        LogEvent("NZB added to Sabnzbd")
        return True
    
    def AddNZBToBlackhole(self,nzbUrl,nzbBlackholePath,game_name,system):
        try:
            dest = nzbBlackholePath + game_name + " - " + system + ".nzb"
            LogEvent(nzbUrl)
            LogEvent("saving nzb to " + dest)
            urllib.urlretrieve(nzbUrl,dest)
            LogEvent("NZB Added To Blackhole")
        except:
            LogEvent("Unable to download NZB to blackhole: " + nzbUrl)
            return False
        return True
        
    def FindGameOnKAT(self,game_id,game_name,system,torrentBlackholePath,blacklistwords):
        url = "http://www.kickasstorrents.com/json.php?q=" + game_name
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            jsonObject = json.loads(response)
            listObject = jsonObject['list']
            for record in listObject:
                title = record['title']
                torrentLink = record['torrentLink']
                category = record['category']
                print category
                if(category == "Games"):
                    result = GameTasks().DownloadTorrent(torrentLink,title,torrentBlackholePath)
                    if(result == True):
                        UpdateStatus(game_id,"Snatched")
                        return result
        except:
            LogEvent("Unable to connect to KickAss Torrents")  
            return
        
    def DownloadTorrent(self,torrentUrl,title,torrentBlackholePath):
        try:
            dest = torrentBlackholePath + title + ".torrent"
            urllib.urlretrieve(torrentUrl,dest)
            LogEvent("Torrent Added To Blackhole")
        except:
            LogEvent("Unable to download torrent to blackhole: " + torrentUrl)
            return False
        return True

    def CheckIfPostProcessExistsInSab(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        
        path = os.path.join(gamez.PROGDIR, "postprocess")
        srcPath = os.path.join(path,"gamezPostProcess.py")
        url = sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=script_dir"
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()

            if os.name == 'nt': 
                scriptDir = response.split(":")[2].replace(" '","")
                scriptDir = scriptDir + ":" + response.split(":")[3].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
            else:
                scriptDir = response.split(":")[2].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
            DebugLogEvent("Script Path :[" + scriptDir + "]")
            destPath = os.path.join(scriptDir,"gamezPostProcess.py")
            try:
                LogEvent("Copying post process script to Sabnzbd scripts folder")
                shutil.copyfile(srcPath,destPath)
            except:
                LogEvent("Unable to copy post process script to Sab folder")
                return
            try:
                LogEvent("Setting permissions on post process script")
                cmd = "chmod +x '" + destPath + "'"
                os.system(cmd)
            except:
                LogEvent("Unable to set permissions on post process script")
                return
        except:
            LogEvent("Unable to connect to Sanzbd: " + url)
            return
        return

    def CheckStatusInSabAndPP(self):
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)

        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
        status = False
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=history&output=json&apikey=" + sabnzbdApi

        DebugLogEvent("Checking for status of downloaded file in Sabnzbd")
        r = requests.get(url)
        response = r.text
        response = json.loads(response)
        history = response['history']
        for i in history['slots']:
            #DebugLogEvent("Sab slot: " + i['name'])
            game_id = findGamezID(i['name'])
            if not game_id:
                #DebugLogEvent("Sab slot: " + i['name'] + " no Gamez ID found")
                continue
            foundGame = GetGameData(str(game_id))
            if not foundGame:
                DebugLogEvent("Sab slot: " + i['name'] + " no Gamez in DB found")
                continue
            if foundGame[4] != 'Snatched':
                #DebugLogEvent("Sab slot: " + i['name'] + " Game is allready PP or something")
                continue
            DebugLogEvent("Status for " + foundGame[1] + " is " + i['status'])
            if i['status'] == 'Completed':
                result = ProcessDownloaded(str(game_id), i['status'], i['storage'])
                if result:
                    UpdateStatus(str(game_id), i['status'])
                else:
                    UpdateStatus(str(game_id), 'PP Failed')



    def CheckStatusInSab(self,game_name):

        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)

        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
        status = False
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=history&apikey=" + sabnzbdApi

        DebugLogEvent("Checking for status of downloaded file in Sabnzbd")
        try:
            r = requests.get(url)
            response = json.loads(r.text)

            for i in response['slots']:
                if i['name'] == game_name:
                    DebugLogEvent("Status for " + i['name'] + " is " + i['status'])
                    if i['status'] == 'Completed':
                        status = True
                    break
                else:
                    continue
        except:
            DebugLogEvent("ERROR: Can not parse data from SABnzbd")

        return status

    def ForceSearch(self, dbid):
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        nzbsrusUser = config.get('nzbsrus','username').replace('"','')
        nzbsrusApi = config.get('nzbsrus','api_key').replace('"','')
        nzbsuapi = config.get('NZBSU','api_key').replace('"','')
        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
        sabnzbdCategory = config.get('Sabnzbd','category').replace('"','')
        newznabWiiCat = config.get('Newznab','wii_category_id').replace('"','')
        newznabXbox360Cat = config.get('Newznab','xbox360_category_id').replace('"','')
        newznabPS3Cat = config.get('Newznab','ps3_category_id').replace('"','')
        newznabPCCat = config.get('Newznab','pc_category_id').replace('"','')
        newznabApi = config.get('Newznab','api_key').replace('"','')
        newznabHost = config.get('Newznab','host').replace('"','')
        newznabPort = config.get('Newznab','port').replace('"','')
        isSabEnabled = config.get('SystemGenerated','sabnzbd_enabled').replace('"','')
        isnzbsrusEnabled = config.get('SystemGenerated','nzbsrus_enabled').replace('"','')
        isNewznabEnabled = config.get('SystemGenerated','newznab_enabled').replace('"','')
        isnzbsuEnable = config.get('SystemGenerated','nzbsu_enabled').replace('"','')
        isNzbBlackholeEnabled = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        nzbBlackholePath = config.get('Blackhole','nzb_blackhole_path').replace('"','')
        isTorrentBlackholeEnabled = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        isTorrentKATEnabled = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        torrentBlackholePath  = config.get('Blackhole','torrent_blackhole_path').replace('"','')
        retention = config.get('SystemGenerated','retention').replace('"','')
        manualSearchGame = dbid
        LogEvent("Searching for games")
        GameTasks().FindGames(manualSearchGame,nzbsrusUser,nzbsrusApi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isnzbsrusEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isnzbsuEnable,nzbsuapi,retention)
            
