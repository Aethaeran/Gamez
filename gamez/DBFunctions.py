import os
import sqlite3
import sys
import time
from Logger import LogEvent, DebugLogEvent
import urllib
import json
import Notifications
import urllib
import urllib2
import threading
import ConfigParser

import lib.feedparser as feedparser
import gamez

from gamez.Helper import replace_all
from gamez.Postproccess import PostProcess


def GetGamesFromTerm(term):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT GAME_NAME,SYSTEM FROM GAMES where game_name like '%" + term.replace("'","''") + "%' ORDER BY GAME_NAME ASC"
    data = ""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            game_name = str(record[0])
            system_db = str(record[1])
            rowdata = '{"value":"' + game_name + '"},'
            data = data + rowdata
        except:
            continue
    cursor.close()
    data = data[:-1]
    data = "[" + data + "]"
    return data

def GetGameDataFromTerm(term,system):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT game_name,game_type,id,system,cover FROM games where game_name like '%" + term.replace("'","''") + "%' AND system like '%" + system + "%' order by game_name asc"
    data = ''
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            game_name = str(record[0])
            game_type = str(record[1])
            db_id = str(record[2])
            system = str(record[3])
            cover = str(record[4])
            rowdata = "<tr align='center'><td><a href='addgame?dbid=" + db_id + "'>Download</a></td><td><img width='85' height='120'  src='" + cover + "' /></td><td>" + game_name + "</td><td>" + game_type + "</td><td>" + system + "</td></tr>"
            data = data + rowdata
        except:
            continue
    cursor.close()
    return data

def AddGameToDb(db_id,status):
    LogEvent("Adding game in 'Wanted' status")
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select game_name,system,game_type,cover from games where ID = '" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    game_name = str(result[0])
    system = str(result[1])
    game_type = str(result[2])
    cover = str(result[3])
    cursor.close()
    sql = "insert into requested_games(GAME_NAME,SYSTEM,GAME_TYPE,status,cover) values('" + game_name.replace("'","''") + "','" + system + "','" + game_type + "','" + status + "','" + cover + "')"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    id = str(cursor.lastrowid)
    cursor.close()
    return id

def AddGameUpcomingToDb(db_id,status):
    LogEvent("Adding game in 'Wanted' status")
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select GameTitle,system from comingsoon where ID = '" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    game_name = str(result[0])
    system = str(result[1])
    game_type = "Game"
    cover = "/css/navigation_images/no-cover.jpg"
    cursor.close()
    sql = "insert into requested_games(GAME_NAME,SYSTEM,GAME_TYPE,status,cover) values('" + game_name.replace("'","''") + "','" + system + "','" + game_type + "','" + status + "','" + cover + "')"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    id = str(cursor.lastrowid)
    cursor.close()
    return id    
    #comingsoon

def GetRequestedGames(filter=''):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    if(filter <> ''):
        sql = "SELECT id,game_name,game_type,status,system,cover,thegamesdb_id FROM requested_games Where status='" + filter + "' order by game_name asc"
    else:        
    	sql = "SELECT id,game_name,game_type,status,system,cover,thegamesdb_id FROM requested_games order by game_name asc"
    data = ''
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            db_id = str(record[0])
            game_name = str(record[1])
            game_type = str(record[2])
            status = str(record[3])
            system = str(record[4])
            cover = str(record[5])
            thegamesdbid = str(record[6])
            DebugLogEvent("TheGamesDB ID [" + thegamesdbid + "]")
            if(thegamesdbid != 'None'):
                rowdata = "<tr align='center'><td><a href='removegame?dbid=" + db_id + "'><img src='images/icon.delete.png' border='0'/></a>&nbsp;<a id='forcesearch' href='forcesearch?dbid=" + db_id + "'><img src='images/icon.search.png' border='0'/></a>&nbsp;<a href='forcepost'><img src='images/icon.folder.gif' border='0'/></a>&nbsp<a href='refreshinfo?thegamesdbid=" + thegamesdbid + "'><img src='images/icon.reload.png' border='0'/></a></td><td><center><img width='85' height='120'  src='" + cover + "' /></center></td><td><a href='http://thegamesdb.net/game/" + thegamesdbid + "' target='_blank' >" + game_name + "</td><td>" + game_type + "</td><td>" + system + "</td><td>" + status + "</td><td><select id=updateSatusSelectObject class=ui-widget onchange=UpdateGameStatus(this.options[this.selectedIndex].value,'" + db_id + "')>"
            else:
                rowdata = "<tr align='center'><td><a href='removegame?dbid=" + db_id + "'><img src='images/icon.delete.png' border='0'/></a>&nbsp;<a id='forcesearch' href='forcesearch?dbid=" + db_id + "'><img src='images/icon.search.png' border='0'/></a>&nbsp;<a href='forcepost'><img src='images/icon.folder.gif' border='0'/></a></td><td><center><img width='85' height='120'  src='" + cover + "' /></center></td><td>" + game_name + "</a></td><td>" + game_type + "</td><td>" + system + "</td><td>" + status + "</td><td><select id=updateSatusSelectObject class=ui-widget onchange=UpdateGameStatus(this.options[this.selectedIndex].value,'" + db_id + "')>"
            if(status == "Snatched"):
                rowdata = rowdata + "<option>Downloaded</option><option selected=true>Snatched</option><option>Wanted</option>"
            elif(status == "Downloaded"):
                rowdata = rowdata + "<option selected=true>Downloaded</option><option>Snatched</option><option>Wanted</option>"
            elif(status == "Wanted"):
                   rowdata = rowdata + "<option>Downloaded</option><option>Snatched</option><option selected=true>Wanted</option>"
            rowdata = rowdata + "</select></td></tr>"
            data = data + rowdata
        except:
            continue
    cursor.close()
    return data

def RemoveGameFromDb(db_id):
    LogEvent("Removing game")
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "delete from requested_games where ID='" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return

def GetRequestedGamesAsArray(manualSearchGame):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    if(manualSearchGame <> ''):
        sql = "SELECT game_name,ID,system FROM requested_games WHERE id='" + manualSearchGame + "' order by game_name asc"
    else:
        sql = "SELECT game_name,ID,system FROM requested_games WHERE status='Wanted' order by game_name asc"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result

def UpdateStatus(game_id,status):
    
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    
    LogEvent("Update status of game to " + status)
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    game_name = ""
    system = ""
    sql = "select game_name,system from requested_games where ID='" + game_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    tables = list()
    for record in result:
        game_name = str(record[0])
        system = str(record[1])
    cursor.close()    
    sql = "update requested_games set status='" + status + "' where game_name = '" + game_name.replace("'","''") + "' and system = '" + system + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    message = system + " " + game_name + " has been " + status
    DebugLogEvent(message)
    postprocess_system = 'process_download_folder_' + system.lower() + '_enabled'
    if((config.get('SystemGenerated',postprocess_system).replace('"','') == "1")):
       if(status == "Downloaded"):
          nfothread =threading.Timer(0,PostProcess,[game_id,game_name])
          nfothread.start()
    else:
       LogEvent("Skipp postprocessing for " + system + " games because it is not enabled.") 
    if status != "Wanted":
        Notifications.HandleNotifications(status,message,gamez.DATADIR)
    return

def ValidateDB():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select name from sqlite_master where type='table'"
    logTableExists = False
    oldWiiGamesTableExists = False
    comingSoonTableExists = False
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    tables = list()
    for record in result:
        tableName = str(record[0])
        if(tableName == 'gamez_log'):
            logTableExists = True
        elif(tableName == 'wii_games'):
            oldWiiGamesTableExists = True
        elif(tableName == 'comingsoon'):
            comingSoonTableExists = True
    cursor.close()
    if(logTableExists == False):
        sql = "create table gamez_log(ID INTEGER NOT NULL PRIMARY KEY UNIQUE,message TEXT(255) NOT NULL,created_date DATE)"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
    sql = "PRAGMA table_info(requested_games);"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    isRequestedGamesOldFormat = False
    for record in result:
        if(str(record[1]) == "WiiGameID"):
            isRequestedGamesOldFormat = True
    cursor.close()
    if(isRequestedGamesOldFormat):
        sql = "select wii_games.game_name,requested_games.status from requested_games inner join wii_games on requested_games.WiiGameID = wii_games.ID"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        sql = "drop table requested_games"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        sql = "CREATE TABLE REQUESTED_GAMES (ID INTEGER PRIMARY KEY,GAME_NAME TEXT,SYSTEM TEXT,GAME_TYPE TEXT,STATUS TEXT,COVER TEXT)"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        for record in result:
            game_name = str(record[0])
            status = str(record[1])
            sql = "insert into requested_games (game_name,game_type,system,status) values ('" + game_name.replace("'","''") + "','Game','Wii','" + status + "')"
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            cursor.close()
    
    if(oldWiiGamesTableExists):
        print "Upgrading database. This may take a few moments"
        sql = "drop table wii_games"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        sql = "CREATE TABLE GAMES (ID INTEGER PRIMARY KEY,GAME_NAME TEXT,SYSTEM TEXT,GAME_TYPE TEXT,COVER TEXT)"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        cursor.close()
        AddWiiGamesIfMissing()
        print "Database upgrade complete"

    # Just when Table not exists
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS GAMES (ID INTEGER PRIMARY KEY,GAME_NAME TEXT,SYSTEM TEXT,GAME_TYPE TEXT,COVER TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS requested_games (ID INTEGER PRIMARY KEY,GAME_NAME TEXT,SYSTEM TEXT,GAME_TYPE TEXT,STATUS TEXT,COVER TEXT,THEGAMESDB_ID TEXT,ADDITION_WORDS TEXT)")
    
    try:
        cursor.execute("SELECT cover from games")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE games ADD COLUMN cover TEXT")
    
    try:
        cursor.execute("SELECT cover from requested_games")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE requested_games ADD COLUMN cover TEXT")

    try:
        cursor.execute("SELECT thegamesdb_id from requested_games")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE requested_games ADD COLUMN thegamesdb_id TEXT")

    try:
        cursor.execute("SELECT addition_words from requested_games")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE requested_games ADD COLUMN addition_words TEXT")

    connection.commit()
    cursor.close()
   	 
    #loop requested games where cover is null
    sql = "select game_name,cover,system from requested_games where cover is null"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    for record in result:
	game_name = str(record[0])
	cover = str(record[1])
	system = str(record[2])
	sql = "update requested_games set cover = (Select cover from games where game_name = '" + game_name + "' and system = '" + system + "') Where game_name = '" + game_name + "' and system = '" + system + "'"
        connection = sqlite3.connect(db_path)
	cursor = connection.cursor()
	cursor.execute(sql)
	connection.commit()
	cursor.close()
		
    if(comingSoonTableExists == False):
	sql = "create table comingsoon(ID INTEGER NOT NULL PRIMARY KEY UNIQUE,GameTitle TEXT(255),ReleaseDate TEXT(255),System TEXT(255))"
	connection = sqlite3.connect(db_path)
	cursor = connection.cursor()
	cursor.execute(sql)
	connection.commit()
        cursor.close()
        AddComingSoonGames()

def AddEventToDB(message):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    createdDate = time.strftime("%a %d %b %Y / %X",time.localtime() )
    sql = "INSERT INTO gamez_log (message,created_date) values('" + message.replace("'","''") + "','" + createdDate + "')"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return

def GetLog():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT message,created_date FROM gamez_log order by created_date desc,id desc limit 1000"
    data = ''
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            message = str(record[0])
            created_date = str(record[1])
            rowdata = "<tr><td>" + message + "</td><td>" + created_date + "</td></tr>"
            data = data + rowdata
        except:
            continue
    cursor.close()
    return data

def ClearDBLog():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "delete from gamez_log"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return

def ClearGames(system):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "delete from games where system = '" + system + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return

def AddWiiGamesIfMissing():
        wiiWebServiceUrl = "http://www.gamezapp.org/webservice/wii"
        response = ''
        try:
            responseObject = urllib.FancyURLopener({}).open(wiiWebServiceUrl)
            response = responseObject.read()
            responseObject.close()
            json_data = json.loads(response)
        except:
            LogEvent("Unable to connect to web service: " + wiiWebServiceUrl)
            return
        ClearGames("Wii")
        for data in json_data:
            game_name = data['GameTitle']
            game_type = data['GameType'] 
            game_cover = data['GameCover']
            db_path = os.path.join(gamez.DATADIR,"Gamez.db")
            sql = "SELECT count(ID) from games where game_name = '" + game_name.replace("'","''") + "' AND system='Wii'"
            connection = sqlite3.connect(db_path)
            cursor = connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()    
            recordCount = result[0][0] 
            cursor.close()
            if(str(recordCount) == "0"):
                LogEvent("Adding Wii Game [" + game_name.replace("'","''") + "] to Game List")
                sql = "INSERT INTO games (game_name,game_type,system,cover) values('" + game_name.replace("'","''") + "','" + game_type + "','Wii','" + game_cover + "')"
                cursor = connection.cursor()
                cursor.execute(sql)
                connection.commit()
                cursor.close()       
        return

def AddXbox360GamesIfMissing():
    url = "http://www.gamezapp.org/webservice/xbox360"
    response = ''
    try:
        responseObject = urllib.FancyURLopener({}).open(url)
        response = responseObject.read()
        responseObject.close()
        json_data = json.loads(response)
    except:
        LogEvent("Unable to connect to web service: " + url)
        return
    json_data = json.loads(response)
    ClearGames("Xbox360")
    for data in json_data:
        game_name = data['GameTitle']
        game_type = data['GameType'] 
        game_cover = data['GameCover']
        db_path = os.path.join(gamez.DATADIR,"Gamez.db")
        sql = "SELECT count(ID) from games where game_name = '" + game_name.replace("'","''") + "' AND system='Xbox360'"
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()    
        recordCount = result[0][0] 
        cursor.close()
        if(str(recordCount) == "0"):
            LogEvent("Adding XBOX 360 Game [" + game_name.replace("'","''") + "] to Game List")
            sql = "INSERT INTO games (game_name,game_type,system,cover) values('" + game_name.replace("'","''") + "','" + game_type + "','Xbox360','" + game_cover + "')"
            cursor = connection.cursor()
            cursor.execute(sql)
            connection.commit()
            cursor.close()       
    return

def ClearComingSoonGames():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "delete from comingsoon"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return
    
def AddComingSoonGames():
        # Set systems
        systems = [ 'wii', 'ps3', 'xbox360', 'pc' ]
        ClearComingSoonGames()
        for system in systems:
            if(system == 'wii'):
               systembrace = " (Wii)"
            if(system == 'ps3'):
               systembrace = " (Playstation 3)"
            if(system == 'xbox360'):
               systembrace = " (Xbox 360)"
            if(system == 'pc'):
               systembrace = " (PC)"
            url = "http://www.gamerevolution.com/rss/release_dates.xml?system=" + str(system)
            DebugLogEvent("Search URL [ " + url + " ]")
            try:
                releasedata = urllib2.urlopen(url, timeout=20).read()
            except Exception, e:
                LogEvent("Unable to connect to Game Revolution: %s \n Exeption: %s" % (url, e))
                return False
            d = feedparser.parse(releasedata)
            for item in d.entries:
                   game_name = item.title
                   if(game_name == 'Game Revolution - Release Dates`'):
                       return False
                   else:
                       game_name = game_name.replace(systembrace,'')
                       release = item.description 
                       release_date = release.replace('Release date set for ','') 
                       release_date = replace_all(release_date)
                       DebugLogEvent(" Release date for " + str(game_name) + " is " + str(release_date)) 
                       db_path = os.path.join(gamez.DATADIR,"Gamez.db")
                       sql = "SELECT count(ID) from comingsoon where gametitle = '" + game_name.replace("'","''") + "' AND system='" + system.upper() + "'"
                       connection = sqlite3.connect(db_path)
                       cursor = connection.cursor()
                       cursor.execute(sql)
                       result = cursor.fetchall()    
                       recordCount = result[0][0] 
                       cursor.close()
                       if(str(recordCount) == "0"):
                           DebugLogEvent("Adding " + system + " Game [" + game_name.replace("'","''") + "] to Coming Soon Game List")
                           sql = "INSERT INTO comingsoon (GameTitle,ReleaseDate,System) values('" + game_name.replace("'","''") + "','" + release_date.replace(",","''") + "','" + system.upper() + "')"
                           cursor = connection.cursor()
                           cursor.execute(sql)
                           connection.commit()
                           cursor.close()       
        return
        
def GetUpcomingGames():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT gametitle,releasedate,system,id FROM comingsoon order by releasedate asc"
    data = ''
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            gametitle = str(record[0])
            releasedate = str(record[1])
            system = str(record[2])
            db_id = str(record[3])
            if releasedate > time.strftime("%m/%d/%Y"):    
                 rowdata = "<tr><td><a href='addgameupcoming?dbid=" + db_id + "'>Download</a></td><td>" + gametitle + "</td><td>" + releasedate + "</td><td>" + system + "</td></tr>"
                 data = data + rowdata
            else:
                 continue
        except:
            continue
    cursor.close()
    return data

def GetRequestedGameName(db_id):
    game_name = "[" + db_id + "]"
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select Game_name from requested_games where ID = '" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    game_name = str(result[0])
    cursor.close()
    return game_name

def GetRequestedGameSystem(db_id):
    system = ""
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select System from requested_games where ID = '" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    system = str(result[0])
    cursor.close()
    return system

def GetRequestedTheGamesDBid(db_id):
    system = ""
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select thegamesdb_id from requested_games where ID = '" + db_id + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0]
    TheGamesdb_id = str(result[0])
    cursor.close()
    return TheGamesdb_id

def GetRequestedGamesForFolderProcessing():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select Game_name,system,id from requested_games"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    return result

def CheckForSameGame(game_name):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "select count(ID) from requested_games where Game_name = '" + game_name + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()[0][0]
    cursor.close()
    if(int(result) == 1):
        return False
    else:
        return True

def UpdateStatusForFolderProcessing(game_name,system,status):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "update requested_games set status='" + status + "' where game_name='" + game_name + "' and system='" + system + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()
    return


# This function looks for addition word in nzbname and save it to datatabase
# If nzbname is '' it will return the addition list from database from id 

def AdditionWords(nzbname, db_id): 
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    if(nzbname == ''):
         sql = "SELECT addition_words WHERE ID = '" + db_id + "'"
         connection = sqlite3.connect(db_path)
         cursor = connection.cursor()
         cursor.execute(sql)
         result = cursor.fetchall()[0]
         additions = str(result[0])
         cursor.close()
         return additions
    else:
         additionlist = ['PAL', 'USA', 'NSTC', 'JAP', 'Region Free', 'RF', 'FRENCH', 'ITALIAN', 'GERMAN', 'SPANISH', 'ASIA', 'JTAG', 'XGD3', 'WiiWare', 'WiiVC', 'Mixed']
         regionword = ""
         for word in additionlist:
             if word.upper() in nzbname:
                regionword = regionword + " (" + word + ")"
             if word.lower() in nzbname:
                regionword = regionword + " (" + word + ")"         
         DebugLogEvent("Additions for Game with ID " + db_id + " are " + regionword)
         sql = "UPDATE requested_games SET addition_words='" + regionword +"' WHERE id = '" + db_id + "'"
         connection = sqlite3.connect(db_path)
         cursor = connection.cursor()
         cursor.execute(sql)
         connection.commit()
         cursor.close()
         return
         
def ApiGetGamesFromTerm(term,system):
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT GAME_NAME,SYSTEM,COVER FROM GAMES where game_name like '%" + term.replace("'","''") + "%' AND SYSTEM LIKE '%" + system + "%' ORDER BY GAME_NAME ASC"
    data = ""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            game_name = str(record[0])
            system = str(record[1])
            cover = str(record[2])
            rowdata = '{"GameTitle":"' + game_name + '","System":"' + system + '","GameCover":"' + cover + '"},'
            data = data + rowdata
        except:
            continue
    cursor.close()
    data = data[:-1]
    data = '["Games":' + data + ']'
    return data
    
def ApiGetRequestedGames():
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    sql = "SELECT GAME_NAME,SYSTEM,COVER FROM REQUESTED_GAMES ORDER BY GAME_NAME ASC"
    data = ""
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for record in result:
        try:
            game_name = str(record[0])
            system = str(record[1])
            cover = str(record[2])
            rowdata = '{"GameTitle":"' + game_name + '","System":"' + system + '","GameCover":"' + cover + '"},'
            data = data + rowdata
        except:
            continue
    cursor.close()
    data = data[:-1]
    if(data == ""):
    	data = '"None"'
    data = '["Games":' + data + ']'
    return data

