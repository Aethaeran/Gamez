
from gamez import common
from plugins import Downloader
from lib import requests
from gamez.Logger import LogEvent, DebugLogEvent
from gamez.classes import *


class Sabnzbd(Downloader):
    _config = {'port': 8083,
               'host': 'http://localhost',
               'apikey': '',
               'category': ''}
    _history = []
    types = [common.TYPE_NZB]

    def _baseUrl(self):
        if not self.c.host.startswith('http'):
            DebugLogEvent("Fixing url. Adding http://")
            self.c.host = "http://%s" % self.c.host
        return "%s:%s/sabnzbd/api" % (self.c.host, self.c.port)

    def addDownload(self, game, download):
        payload = {'apikey': self.c.apikey,
                 'name': download.url,
                 'nzbname': self._downloadName(game),
                 'mode': 'addurl'
                 }

        if self.c.category:
            payload['cat'] = self.c.category
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
        #DebugLogEvent("Sab hitory url %s" % r.url)
        response = r.json()
        self._history = response['history']['slots']
        return self._history

    def getGameStaus(self, game):
        """returns a Status and path"""
        DebugLogEvent("Checking for status of %s in Sabnzbd" % game)
        if not self._history:
            self._getHistory()
        for i in self._history:
            #DebugLogEvent("Sab slot: " + i['name'])
            game_id = self._findGamezID(i['name'])
            if not game_id:
                #DebugLogEvent("Sab slot: " + i['name'] + " no Gamez ID found")
                continue
            try:
                Game.get(Game.id == game_id)
            except Game.DoesNotExist:
                continue
            if i['status'] == 'Completed':
                return (common.DOWNLOADED, i['storage'])
            else:
                return (common.SNATCHED, '')
        else:
            return (common.UNKNOWN, '')
