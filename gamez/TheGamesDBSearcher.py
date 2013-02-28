
from Logger import LogEvent, DebugLogEvent
import xml.etree.ElementTree as ET
from lib import requests

from classes import Game, Platform
from gamez import common


def GetGameDataFromTheGamesDB(term, system):
    p = Platform.get(Platform.id == system)
    games = getGamesFromTGDB(p, term)
    DebugLogEvent("found " + str(len(games)))
    html = []
    for g in games:
        html.append("<tr align='center'><td><a href='addgambythegamesdb?thegamesdbid=" + g.tgdb_id + "'>Download</a></td><td><img width='85' height='120'  src='" + g.boxart_url + "' /></td><td>" + g.name + "</td><td>" + g.genres + "</td><td>" + g.platform.name + "</td></tr>")
    return "\n".join(html)


def createGameFromTag(game_tag, base_url):

    titleTag = game_tag.find('GameTitle')
    idTag = game_tag.find('id')
    platformTag = game_tag.find('Platform')
    platformIDTag = game_tag.find('PlatformId')
    imagesTag = game_tag.find('Images')
    genresTag = game_tag.find('Genres')

    if titleTag is None or idTag is None or platformTag is None or platformIDTag is None:
        DebugLogEvent("Not enough info to create game")
        return None

    in_db = False
    try:
        g = Game.get(Game.tgdb_id == idTag.text)
        in_db = True
    except Game.DoesNotExist:
        g = Game()
    g.tgdb_id = int(idTag.text)
    g.name = titleTag.text
    g.boxart_url = _boxartUrl(imagesTag, platformIDTag.text, base_url)
    g.genre = _genresStr(genresTag)
    g.platform = Platform.get(Platform.tgdb_id == platformIDTag.text)
    if in_db: #if we had the game in the db update / save its info
        g.save()

    return g


def _boxartUrl(tag, platformID, base_url):
    if tag is not None:
        imageTags = tag.getiterator('boxart')
        if imageTags:
            for curImage in imageTags:
                if curImage.get('side') == 'front':
                    return base_url + curImage.text

    return base_url + "_platformviewcache/platform/boxart/" + platformID + "-1.jpg"


def _genresStr(tag):
    genres = []
    for curG in tag.getiterator('genre'):
        genres.append(curG.text)
    return ", ".join(genres)


def getGamesFromTGDB(platform=None, term='', tgdb_id=0):
    payload = {}
    if term and not tgdb_id:
        payload['name'] = term
        payload['platform'] = platform.alias
    else:
        payload['id'] = tgdb_id
    r = requests.get('http://thegamesdb.net/api/GetGame.php', params=payload)
    DebugLogEvent('tgdb search url ' + r.url)
    root = ET.fromstring(r.text)

    baseImgUrlTag = root.find('baseImgUrl')
    if baseImgUrlTag is not None:
        base_url = baseImgUrlTag.text
    else:
        base_url = "http://thegamesdb.net/banners/"

    games = []
    for curGame in root.getiterator('Game'):
        g = createGameFromTag(curGame, base_url)
        if tgdb_id: # we only wanted one game. might need a plan for teh case we send back None
            return g
        if g:
            games.append(g)
    return games


def AddGameToDbFromTheGamesDb(tgdb_id, status=common.WANTED):
    g = getGamesFromTGDB(tgdb_id=tgdb_id)
    g.save()
    g.cacheImg()
    return g.id

def addAllWii():
    p = Platform.get(Platform.name == 'Wii')
    games = getGamesFromTGDB(platform=p)
    for g in games:
        DebugLogEvent("Saving " + g.name)
        g.save()

def UpdateGame(tgdb_id):
    LogEvent("Update Game with ID: " + tgdb_id)
    try:
        g = Game.get(Game.tgdb_id == tgdb_id)
    except Game.DoesNotExist:
        gid = AddGameToDbFromTheGamesDb(tgdb_id)
        if gid:
            return True
    else:
        g.updateFromTGDB()
        return True
    return False
