import os
import sqlite3
import sys
import datetime
from Logger import LogEvent,DebugLogEvent
import urllib2
import json
import DBFunctions
from xml.dom.minidom import *
import xml.etree.ElementTree as ET
import gamez


def GetGameDataFromTheGamesDB(term, system):
    html = ""
    root = GetXmlFromTheGamesDB(term, system, 'fake', True)
    baseImgUrlTag = root.find('baseImgUrl')
    if baseImgUrlTag is not None:
        baseUrl = baseImgUrlTag.text
    else:
        baseUrl = "http://thegamesdb.net/banners/"

    for curGame in root.iter('Game'):
        titleTag = curGame.find('GameTitle')
        idTag = curGame.find('id')
        platformTag = curGame.find('Platform')
        platformIDTag = curGame.find('PlatformId')
        imagesTag = curGame.find('Images')
        genresTag = curGame.find('Genres')

        if titleTag is None or idTag is None or platformTag is None or platformIDTag is None or imagesTag is None or genresTag is None:
            continue
        gameID = idTag.text
        title = titleTag.text
        LogEvent("Found Game: " + title)
        platform = platformTag.text
        platformID = platformIDTag.text
        cover = boxartUrl(imagesTag, platformID, baseUrl)
        genres = genresStr(genresTag)

        html += "<tr align='center'><td><a href='addgambythegamesdb?thegamesdbid=" + gameID + "'>Download</a></td><td><img width='85' height='120'  src='" + cover + "' /></td><td>" + title + "</td><td>" + genres + "</td><td>" + platform + "</td></tr>"
    return html


def boxartUrl(tag, platformID, baseUrl):
    imageTags = tag.iter('boxart')
    if imageTags:
        for curImage in imageTags:
            if curImage.get('side') == 'front':
                return baseUrl + curImage.text

    return baseUrl + "_platformviewcache/platform/boxart/" + platformID + "-1.jpg"


def genresStr(tag):
    genres = []
    for curG in tag.iter('genre'):
        genres.append(curG.text)
    return ", ".join(genres)

def GetDetails(TheGamesDB_id,tagname,tagnbr):
    try:
        TheGamesDBxml = GetXmlFromTheGamesDB('None','None',TheGamesDB_id)
        xmlTagdetail = TheGamesDBxml.getElementsByTagName(tagname)[tagnbr].toxml()
        xmlGamedetailclean = xmlTagdetail.replace('<' + str(tagname) + '>','').replace('</' + str(tagname) + '>','')
        DebugLogEvent("Found tag for " + str(tagname) + " : " + xmlGamedetailclean)
        return str(xmlGamedetailclean)
    except:
        xmlGamedetailclean = " "
        return xmlGamedetailclean


def GetDetailsgenre(TheGamesDBurl):
    try:
        xmlTaggenre = TheGamesDBurl.getElementsByTagName('genre')[0].toxml()
        xmlGamegenre=xmlTaggenre.replace('<genre>','').replace('</genre>','')
        DebugLogEvent("Found a Genre: " + xmlGamegenre)
        return str(xmlGamegenre)
    except:
        xmlGamegenre="Game"
        return xmlGamegenre


def GetDetailscover(TheGamesDBurl,system):
    try:
        for x in range(0,5):
              xmlrawTagcover = TheGamesDBurl.getElementsByTagName('boxart')[x]  
              controlString = xmlrawTagcover.childNodes[0].nodeValue
              if "front" in controlString:
                  break

        DebugLogEvent("Found a Cover: " + controlString)
        if('None' in str(controlString)):
            return False
        else:   
            return str(controlString)
    except:
        if(system == "PS3"):
            xmlGamecover="_platformviewcache/platform/boxart/12-1.jpg"
        elif(system == "PC"):
            xmlGamecover="_platformviewcache/platform/boxart/1-1.jpg"
        elif(system == "Wii"):
            xmlGamecover="_platformviewcache/platform/boxart/9-1.jpg"
        elif(system == "Xbox360"):
            xmlGamecover="_platformviewcache/platform/boxart/15-1.jpg"
        else:
            xmlGamecover="None"
        return str(xmlGamecover)

def GetXmlFromTheGamesDB(term, system, TheGamesDB_id, tree=False):
    #gamefile = None
    #gamedata = None
    if(system == 'PS3'):
        Platform = "Sony+Playstation+3"
    elif(system == 'PC'):
        Platform = "PC"
    elif(system == 'Wii'):
        Platform = "Nintendo+Wii"
    elif(system == 'Xbox360'):
        Platform = "Microsoft+Xbox+360"
    else:
        Platform = ''
    try:
        if(TheGamesDB_id != "fake"):
            gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?id=' + TheGamesDB_id)
            DebugLogEvent('Search for [ "' + term + '" ] http://thegamesdb.net/api/GetGame.php?id=' + TheGamesDB_id)
        else:
            if Platform:
                gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+') + '&platform=' + Platform)
                DebugLogEvent( 'Search for [ "' + term + '" ] http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+') + '&platform=' + Platform)
            else:
                gamefile = urllib2.urlopen('http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+'))
                DebugLogEvent( 'Search for [ "' + term + '" ] http://thegamesdb.net/api/GetGame.php?name=' + term.replace(' ','+'))
        gamedata = gamefile.read()
        gamefile.close()
        if tree:
            return ET.fromstring(gamedata)
        else:
            return parseString(gamedata)
    except:
        LogEvent("ERROR: I can not get any Data from TheGameDB.org")

def AddGameToDbFromTheGamesDb(thegamesdbid,status):
    TheGamesDBxml = GetXmlFromTheGamesDB('none','none',thegamesdbid)
    xmlTagTitle = TheGamesDBxml.getElementsByTagName('GameTitle')[0].toxml()
    xmlGameTitle=xmlTagTitle.replace('<GameTitle>','').replace('</GameTitle>','').replace(":"," -")
    DebugLogEvent("Found Game: " + xmlGameTitle)
    xmlTagSystem = TheGamesDBxml.getElementsByTagName('Platform')[0].toxml()
    xmlGameSystem=xmlTagSystem.replace('<Platform>','').replace('</Platform>','')
    if(xmlGameSystem == 'PC'):
        raw_system = 'PC'
    elif(xmlGameSystem == 'Sony Playstation 3'):
        raw_system = 'PS3'
    elif(xmlGameSystem == 'Nintendo Wii'):
        raw_system = 'Wii'
    elif(xmlGameSystem == 'Microsoft Xbox 360'):
        raw_system = 'Xbox360'
    else:
        LogEvent("ERROR: No System found" + xmlGameSystem)
        raw_system = 'NONE'
    game_cover = "http://thegamesdb.net/banners/" + GetDetailscover(TheGamesDBxml,raw_system)
    game_genre = GetDetailsgenre(TheGamesDBxml)
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")
    connection = sqlite3.connect(db_path)
    LogEvent("Adding " + raw_system + " Game [ " + xmlGameTitle.replace("'","''") + " ] to Game List. Cover :" + game_cover.replace("'","''"))
    try:
        sql = "insert into requested_games(GAME_NAME,SYSTEM,GAME_TYPE,status,cover,thegamesdb_id)  values('" + xmlGameTitle.replace("'","''") + "','" + raw_system + "','" + game_genre + "','" + status + "','" + game_cover + "','" + thegamesdbid + "')"
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        id = str(cursor.lastrowid)    
    except:
        sql = "alter table requested_games add column thegamesdb_id text"
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        sql = "insert into requested_games(GAME_NAME,SYSTEM,GAME_TYPE,status,cover,thegamesdb_id)  values('" + xmlGameTitle.replace("'","''") + "','" + raw_system + "','" + game_genre + "','" + status + "','" + game_cover + "','" + thegamesdbid + "')"
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        id = str(cursor.lastrowid)
    #add for list
    sql = "INSERT INTO games (game_name,game_type,system,cover) values('" + xmlGameTitle.replace("'","''") + "','" + game_genre + "','" + raw_system + "','" + game_cover + "')"
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()       
    return id

def UpdateGame(thegamesdbid):
    
    LogEvent("Update Game with ID: " + thegamesdbid)
    db_path = os.path.join(gamez.DATADIR,"Gamez.db")

    thegamesdbxml = GetXmlFromTheGamesDB('none', 'none', thegamesdbid)
    updated_cover = "http://thegamesdb.net/banners/" + GetDetailscover(thegamesdbxml,'None')
    updated_genre = GetDetailsgenre(thegamesdbxml)

    sql = "update requested_games set GAME_TYPE='" + updated_genre + "',cover ='" + updated_cover + "' where thegamesdb_id = '" + thegamesdbid + "'"
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    cursor.close()