
from plugins import Provider
from gamez.Logger import DebugLogEvent
import xml.etree.ElementTree as ET
from lib import requests

from gamez.classes import Game, Platform
import datetime


class TheGameDB(Provider):
    version = "0.11"
    single = True
    _config = {'enabled': True}
    config_meta = {'plugin_desc': 'THE information provider for games'
                   }

    def _boxartUrl(self, tag, platformID, base_url):
        if tag is not None:
            imageTags = tag.getiterator('boxart')
            if imageTags:
                for curImage in imageTags:
                    if curImage.get('side') == 'front':
                        return base_url + curImage.text

        return base_url + "_platformviewcache/platform/boxart/" + platformID + "-1.jpg"

    def _genresStr(self, tag):
        if tag is None:
            return "n/a"

        genres = []
        for curG in tag.getiterator('genre'):
            genres.append(curG.text)
        return ", ".join(genres)

    def _createGameFromTag(self, game_tag, base_url):
        titleTag = game_tag.find('GameTitle')
        idTag = game_tag.find('id')
        platformTag = game_tag.find('Platform')
        platformIDTag = game_tag.find('PlatformId')
        imagesTag = game_tag.find('Images')
        genresTag = game_tag.find('Genres')
        overview = game_tag.find('Overview')
        release_date = game_tag.find('ReleaseDate')
        trailer = game_tag.find('Youtube')

        if titleTag is None or idTag is None or platformTag is None or platformIDTag is None:
            DebugLogEvent("Not enough info to create game")
            return None
        try:
            g = Game.get(Game.tgdb_id == idTag.text)
        except Game.DoesNotExist:
            g = Game()
        g.tgdb_id = int(idTag.text)
        g.name = titleTag.text
        g.boxart_url = self._boxartUrl(imagesTag, platformIDTag.text, base_url)
        g.genre = self._genresStr(genresTag)
        g.platform = Platform.get(Platform.tgdb_id == platformIDTag.text)
        if overview != None:
            g.overview = overview.text
        if trailer != None:
            g.trailer = trailer.text

        if release_date != None:
            # tgdb gives back times like 11/13/2007
            g.release_date = datetime.datetime.strptime(release_date.text, "%m/%d/%Y")

        return g

    def searchForGame(self, term='', platform=None, gid=0):
        payload = {}
        url = 'http://thegamesdb.net/api/GetGame.php?'
        if term and not gid:
            payload['name'] = term
            payload['platform'] = platform.url_alias
            url += 'name=%s&platform=%s' % (term, platform.url_alias)
        else:
            payload['id'] = gid
            url += 'id=%s' % gid
        #r = requests.get('http://thegamesdb.net/api/GetGame.php', params=payload)
        r = requests.get(url)
        DebugLogEvent('tgdb search url ' + r.url)
        root = ET.fromstring(r.text.encode('utf-8'))

        baseImgUrlTag = root.find('baseImgUrl')
        if baseImgUrlTag is not None:
            base_url = baseImgUrlTag.text
        else:
            base_url = "http://thegamesdb.net/banners/"

        games = []
        for curGame in root.getiterator('Game'):
            g = self._createGameFromTag(curGame, base_url)
            if g:
                games.append(g)
        DebugLogEvent("%s fond %s games" % (self.name, len(games)))
        return games

    def getGame(self, gid):
        for game in self.searchForGame(gid=gid):
            if game.tgdb_id == gid:
                return game
        else:
            return False
