
from gamez import common
from plugins import Downloader
from lib import requests
from gamez.Logger import LogEvent, DebugLogEvent
from gamez.classes import *


class Sabnzbd(Downloader):
    version = "0.2"
    _config = {'port': 8083,
               'host': 'http://localhost',
               'apikey': '',
               'category_wii': '',
               'category_xbox360': '',
               'category_ps3': '',
               'category_pc': ''}
    _history = []
    types = [common.TYPE_NZB]

    def _baseUrl(self):
        if not self.c.host.startswith('http'):
            DebugLogEvent("Fixing url. Adding http://")
            self.c.host = "http://%s" % self.c.host
        return "%s:%s/sabnzbd/api" % (self.c.host, self.c.port)

    def _chooseCat(self, platform):
        if platform == common.WII:
            return self.c.category_wii
        elif platform == common.XBOX360:
            return self.c.category_xbox360
        elif platform == common.PS3:
            return self.c.category_ps3
        elif platform == common.PC:
            return self.c.category_pc
        else:
            return ''

    def addDownload(self, game, download):
        payload = {'apikey': self.c.apikey,
                 'name': download.url,
                 'nzbname': self._downloadName(game, download),
                 'mode': 'addurl',
                 'cat': self._chooseCat(game.platform)
                 }
        cat = self._chooseCat(game.platform)
        if cat:
            payload['cat'] = self._chooseCat(game.platform)

        try:
            r = requests.get(self._baseUrl(), params=payload)
        except:
            LogEvent("Unable to connect to Sanzbd:")
            return False
        DebugLogEvent("final sab url %s" % r.url)
        DebugLogEvent("sab response code: %s" % r.status_code)
        DebugLogEvent("sab response: %s" % r.text)
        LogEvent("NZB added to Sabnzbd")
        return True

    def _getHistory(self):

        payload = {'apikey': self.c.apikey,
                   'mode': 'history',
                   'output': 'json'}
        r = requests.get(self._baseUrl(), params=payload)
        DebugLogEvent("Sab hitory url %s" % r.url)
        response = r.json()
        self._history = response['history']['slots']
        return self._history

    def getGameStaus(self, game):
        """returns a Status and path"""
        #DebugLogEvent("Checking for status of %s in Sabnzbd" % game)
        download = Download()
        download.status = common.UNKNOWN
        if not self._history:
            self._getHistory()
        for i in self._history:
            DebugLogEvent("Sab slot: " + i['name'])
            game_id = self._findGamezID(i['name'])
            download_id = self._findDownloadID(i['name'])
            #DebugLogEvent("Game ID: %s Download ID: %s" % (game_id, download_id))
            if not game_id:
                DebugLogEvent("Sab slot: " + i['name'] + " no Gamez ID found")
                continue
            try:
                Game.get(Game.id == game_id)
            except Game.DoesNotExist:
                continue
            try:
                download = Download.get(Download.id == download_id)
            except Download.DoesNotExist:
                pass

            if i['status'] == 'Completed':
                return (common.DOWNLOADED, download, i['storage'])
            elif i['status'] == 'Failed':
                return (common.FAILED, download, '')
            else:
                return (common.SNATCHED, download, '')
        else:
            return (common.UNKNOWN, download, '')
