from DBFunctions import GetRequestedGamesAsArray,UpdateStatus
import sys
import urllib
import urllib2
import os
import shutil
import stat
from Helper import replace_all
from subprocess import call
from Logger import LogEvent,DebugLogEvent
import json
import lib
import ConfigParser
import feedparser

class GameTasks():

    def FindGames(self, manualSearchGame,nzbmatrixusername, nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbMatrixEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isNZBSU,nzbsuapi):
        # First some variables
        confFile = os.path.join(os.path.dirname(os.path.abspath("__FILE__")),'Gamez.ini')
        config = ConfigParser.RawConfigParser()
        config.read(confFile)
        isPS3TBEnable = config.get('SystemGenerated','ps3_tb_enable').replace('"','')
        isPS3JBEnable = config.get('SystemGenerated','ps3_jb_enable').replace('"','')       
        RequiredWordsXbox360 = config.get('SystemGenerated','required_words_xbox360').replace('"','')
        RequiredWordsWii = config.get('SystemGenerated','required_words_wii').replace('"','')
        requiredwords = ''
        if(isSabEnabled == "1"):       
            GameTasks().CheckIfPostProcessExistsInSab(sabnzbdApi,sabnzbdHost,sabnzbdPort)
        nzbmatrixusername = nzbmatrixusername.replace('"','')
        nzbmatrixapi = nzbmatrixapi.replace('"','')
        newznabApi = newznabApi.replace('"','')     
        newznabWiiCat = newznabWiiCat.replace('"','')  
        games = GetRequestedGamesAsArray(manualSearchGame)
        for game in games:
            #try:
                game_name = str(game[0])
                game_id = str(game[1])
                system = str(game[2])
                LogEvent("Searching for game: " + game_name)
                isDownloaded = False
                if(system == "Xbox360" and RequiredWordsXbox360 <> ''):
                     requiredwords = RequiredWordsXbox360
                     DebugLogEvent("Required Words for XBOX360 [ " + requiredwords + " ]")
                if(system == "Wii" and RequiredWordsWii <> ''):
                     requiredwords = RequiredWordsWii
                     DebugLogEvent("Required Words for Wii [ " + requiredwords + " ]")
                if(system == "PS3"):
                     if(isPS3TBEnable == "1"):
                        requiredwords = "TB;"
                        DebugLogEvent("[PS3] Search for True Blue") 
                     if(isPS3JBEnable == "1"):
                        requiredwords = requiredwords + "JB"
                        DebugLogEvent("[PS3] Search for Jail Break")
                     DebugLogEvent("Required Words for PS3 [ " + requiredwords + " ]")

                if(isNzbMatrixEnabled == "1"):
                    if(nzbmatrixusername <> '' and nzbmatrixapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on NZB Matrix")
                            isDownloaded = GameTasks().FindGameOnNZBMatrix(game_name,game_id,nzbmatrixusername,nzbmatrixapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords)
                    else:
                        LogEvent("NZB Matrix Settings Incomplete.")
                
                if(isNewznabEnabled == "1"):
                    if(newznabWiiCat <> '' and newznabXbox360Cat <> '' and newznabPS3Cat <> '' and newznabPCCat <> '' and newznabApi <> '' and newznabHost <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] for ["+ system + "] on Newznab")
                            isDownloaded = GameTasks().FindGameOnNewznabServer(game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords)
                    else:
                        LogEvent("Newznab Settings Incomplete.")  
                        
                if(isNZBSU == "1"):
                    if(nzbsuapi <> ''):
                        if(isDownloaded == False):
                            LogEvent("Checking for game [" + game_name + "] on nzb.su")
                            isDownloaded = GameTasks().FindGameOnNZBSU(game_name,game_id,nzbsuapi,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords)
                    else:
                        LogEvent("NZB Matrix Settings Incomplete.")

                if(isTorrentBlackholeEnabled == "1"):
                	if(isTorrentKATEnabled == "1"):
                		if(isDownloaded == False):
                		    LogEvent("Checking for game [" + game_name + "] on KickAss Torrents")
                		    isDownloaded = GameTasks().FindGameOnKAT(game_id,game_name,system,torrentBlackholePath,requiredwords)
            #except:
            #    continue
        return

    def FindGameOnNZBMatrix(self,game_name,game_id,username,api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords):
        catToUse = ""
        DebugLogEvent("Here i am")
        if(system == "Wii"):
            catToUse = "44"
        elif(system == "Xbox360"):
            catToUse = "14"
        elif(system == "PS3"):
            catToUse = "43"
        elif(system == "PS3"):
            catToUse = "10"
        else:
            LogEvent("Unrecognized System")
            return False
        url = "http://api.nzbmatrix.com/v1.1/search.php?search=" + game_name + "&num=1&catid=" + catToUse + "&username=" + username + "&apikey=" + api
        DebugLogEvent("Search URL [ " + url + " ]")
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
        except:
            LogEvent("Unable to connect to NZBMatrix Server: " + url)
            return False
        try:
            responseData = response.split("\n")
            fieldData = responseData[0].split(":")
            nzbID = fieldData[1]
            nzbID = nzbID.replace(";","")

            if(nzbID <> "nothing_found" and nzbID <> "API_RATE_LIMIT_REACHED"):
                LogEvent("Game found on NZB Matrix")
                nzbUrl = "http://api.nzbmatrix.com/v1.1/download.php?id=" + nzbID + "&username=" + username + "&apikey=" + api
                result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                if(result):
                    UpdateStatus(game_id,"Snatched")
                    return True
            return False
        except:
            LogEvent("Error getting game [" + game_name + "] from NZB Matrix")
            return False

    def FindGameOnNewznabServer(self,game_name,game_id,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,system,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords):
        catToUse = ''
        if(system == "Wii"):
            catToUse = newznabWiiCat
        elif(system == "Xbox360"):
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
        game_name = replace_all(game_name)
        if(newznabPort == '80' or newznabPort == ''):
            url = "http://" + newznabHost + "/api?apikey=" + newznabApi + "&t=search&cat=" + catToUse + "&q=" + game_name.replace(" ","+") + "&o=json"
        else:
            url = "http://" + newznabHost + ":" + newznabPort + "/api?apikey=" + newznabApi + "&t=search&cat=" + catToUse + "&q=" + game_name.replace(" ","+") + "&o=json"
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            DebugLogEvent("Search for " + url)
        except:
            LogEvent("Unable to connect to Newznab Server: " + url)
            return False
        try:
            if(response == "[]"):
                return False            
            jsonObject = json.loads(response)
            for item in jsonObject:
                nzbID = item["guid"]
                LogEvent("Game found on Newznab")
                if(newznabPort == '80' or newznabPort == ''):
                    nzbUrl = "http://" + newznabHost + "/api?apikey=" + newznabApi + "&t=get&id=" + nzbID
                else:
                    nzbUrl = "http://" + newznabHost + ":" + newznabPort + "/api?apikey=" + newznabApi + "&t=get&id=" + nzbID  
                result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                if(result):
                    UpdateStatus(game_id,"Snatched")
                    return True
            return False
        except:
            LogEvent("Error getting game [" + game_name + "] from Newznab")
            return False
            
    def FindGameOnNZBSU(self,game_name,game_id,api,sabnzbdApi,sabnzbdHost,sabnzbdPort,system,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,requiredwords):
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
        game_name = replace_all(game_name)
        url = "http://nzb.su/api?apikey=" + api + "&t=search&cat=" + catToUse + "&q=" + game_name.replace(" ","+")
        DebugLogEvent("Serach URL [" + url + "]") 
        try:
            data = urllib2.urlopen(url, timeout=20).read()
        except:
            LogEvent("Unable to connect to Newznab Server: " + url)
            return False
        try:           
            d = feedparser.parse(data)
            for item in d.entries:
                LogEvent("Game found on Newznab")
                nzbUrl = item.link
                DebugLogEvent("Link URL [" + nzbUrl + "]")
                result = GameTasks().DownloadNZB(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system)
                if(result):
                    UpdateStatus(game_id,"Snatched")
                    return True
                return False
        except:
            LogEvent("Error getting game [" + game_name + "] from http://nzb.su")
            return False

    def DownloadNZB(self,nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory,isSabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,system):
        try:
            result = False
            if(isSabEnabled == "1"):
                result = GameTasks().AddNZBToSab(nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory)
            if(isNzbBlackholeEnabled == "1"):
            	result = GameTasks().AddNZBToBlackhole(nzbUrl,nzbBlackholePath,game_name,system)
            return result
        except:
            LogEvent("Unable to download NZB: " + url)
            return False

    def AddNZBToSab(self,nzbUrl,game_name,sabnzbdApi,sabnzbdHost,sabnzbdPort,game_id,sabnzbdCategory):
        nzbUrl = urllib.quote(nzbUrl)
        url = "http://" + sabnzbdHost + ":" +  sabnzbdPort + "/sabnzbd/api?mode=addurl&pp=3&apikey=" + sabnzbdApi + "&script=gamezPostProcess.py&name=" + nzbUrl + "&nzbname=[" + game_id + "] - "+ game_name
        if(sabnzbdCategory <> ''):
            url = url + "&cat=" + sabnzbdCategory
        DebugLogEvent("Send to sabnzdb: " + url) 
        try:
            responseObject = urllib.FancyURLopener({}).open(url)
            responseObject.read()
            responseObject.close()
        except:
            LogEvent("Unable to connect to Sanzbd: " + url)
            return False
        LogEvent("NZB added to Sabnzbd")
        return True
    
    def AddNZBToBlackhole(self,nzbUrl,nzbBlackholePath,game_name,system):
    	try:
    	    dest = nzbBlackholePath + game_name + " - " + system + ".nzb"
    	    LogEvent(nzbUrl)
    	    urllib.urlretrieve(nzbUrl,dest)
    	    LogEvent("NZB Added To Blackhole")
    	except:
    	    LogEvent("Unable to download NZB to blackhole: " + url)
            return False
    	return True
    	
    def FindGameOnKAT(self,game_id,game_name,system,torrentBlackholePath,requiredwords):
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
    	    LogEvent("Unable to download torrent to blackhole: " + url)
            return False
    	return True
    	
    def CheckSabDownloadPath(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
    	url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=complete_dir"
    	try:
    	    opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            completedDir = response.split(":")[2].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
            return completedDir
    	except:
    	    LogEvent("Unable to get Sab Download Complete Directory")
    	    return ""
    	return
    	
    def CheckIfPostProcessExistsInSab(self,sabnzbdApi,sabnzbdHost,sabnzbdPort):
        
        path = os.path.abspath("postprocess")
        srcPath = os.path.join(path,"gamezPostProcess.py")
        url = "http://" + sabnzbdHost + ":" + sabnzbdPort + "/sabnzbd/api?mode=get_config&apikey=" + sabnzbdApi + "&section=misc&keyword=script_dir"
        try:
            opener = urllib.FancyURLopener({})
            responseObject = opener.open(url)
            response = responseObject.read()
            responseObject.close()
            scriptDir = response.split(":")[2].replace("'","").replace(" ","").replace("{","").replace("}","").replace("\n","")
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
