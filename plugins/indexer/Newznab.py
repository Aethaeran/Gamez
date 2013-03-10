from plugins import Indexer
from gamez import common
from lib import requests
from gamez.Logger import LogEvent, DebugLogEvent
from gamez.classes import Download
from gamez.Helper import replace_all

class Newznab(Indexer):
    version = "0.1"
    _config = {'host': 'http://nzbs2go.com',
               'apikey': '',
               'port': None,
               'category_xbox360': 1050,
               'category_pc': 1070,
               'category_wii': 1030,
               'category_ps3': 1060,
               'retention': 900,
               'enabled': True
               }

    types = [common.TYPE_NZB]

    def _baseUrl(self):
        if not self.c.port:
            return "%s/api/" % self.c.host
        else:
            return "%s:%s/api/" % (self.c.host, self.c.port)

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
            return 0



    def searchForGame(self, game):
        if not self.c.host.startswith('http'):
            self.c.host = "http://%s" % self.c.host

        payload = {'apikey': self.c.apikey,
                   't': 'search',
                   'maxage': self.c.retention,
                   'cat': self._chooseCat(game.platform),
                   'o': 'json',
                   'q': replace_all(game.name)
                   }

        r = requests.get(self._baseUrl(), params=payload)
        DebugLogEvent("Newsnab final search url %s" % r.url)
        response = r.json()
        #LogEvent("jsonobj: " +jsonObject)
        if not 'item' in response["channel"]:
            LogEvent("No search results for " + game.name)
            return []
        items = response["channel"]["item"]
        if type(items).__name__ == 'dict': # we only have on search result
            items = [items]
        downloads = []
        for item in items:
            #LogEvent("item: " + item["title"])
            title = item["title"]
            url = item["link"]
            curSize = 0
            for curAttr in item['attr']:
                if curAttr['@attributes']['name'] == 'size':
                    curSize = int(curAttr['@attributes']['value'])

            """
            if not curSize > mustBeSize:
                LogEvent('Rejecting ' + item['title'] + ' because its to small (' + str(curSize) + ')')
                continue
            """
            LogEvent("Game found on Newznab: " + title)
            d = Download()
            d.url = url
            d.name = title
            d.game = game
            d.size = curSize
            d.type = common.TYPE_NZB
            d.status = common.UNKNOWN
            downloads.append(d)

        return downloads
