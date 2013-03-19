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
               'enabled': True,
               'comment_on_download': False
               }

    types = [common.TYPE_NZB]

    def _baseUrl(self):
        if not self.c.host.startswith('http'):
            self.c.host = "http://%s" % self.c.host
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
        payload = {'apikey': self.c.apikey,
                   't': 'search',
                   'maxage': self.c.retention,
                   'cat': self._chooseCat(game.platform),
                   'o': 'json'
                   }

        downloads = []
        terms = self._getSearchNames(game)
        for term in terms:
            payload['q'] = term
            r = requests.get(self._baseUrl(), params=payload)
            DebugLogEvent("Newsnab final search for term %s url %s" % (term, r.url))
            response = r.json()
            #LogEvent("jsonobj: " +jsonObject)
            if not 'item' in response["channel"]:
                LogEvent("No search results for %s" % term)
                continue
            items = response["channel"]["item"]
            if type(items).__name__ == 'dict': # we only have on search result
                items = [items]
            for item in items:
                #LogEvent("item: " + item["title"])
                title = item["title"]
                url = item["link"]
                ex_id = 0
                curSize = 0
                for curAttr in item['attr']:
                    if curAttr['@attributes']['name'] == 'size':
                        curSize = int(curAttr['@attributes']['value'])
                    if curAttr['@attributes']['name'] == 'guid':
                        ex_id = curAttr['@attributes']['value']

                """
                if not curSize > mustBeSize:
                    LogEvent('Rejecting ' + item['title'] + ' because its to small (' + str(curSize) + ')')
                    continue
                """
                DebugLogEvent("Game found on Newznab: " + title)
                d = Download()
                d.url = url
                d.name = title
                d.game = game
                d.size = curSize
                d.external_id = ex_id

                # default stuff
                d.indexer = self.type
                d.indexer_instance = self.instance
                d.type = common.TYPE_NZB
                d.status = common.UNKNOWN
                downloads.append(d)

        return downloads

    def commentOnDownload(self, msg, download):
        payload = {'apikey': self.c.apikey,
                   't': 'commentadd',
                   'id': download.external_id,
                   'text': msg}
        r = requests.get(self._baseUrl(), params=payload)
        DebugLogEvent("Newsnab final comment for %s is %s on url %s" % (download.name, msg, r.url))
        if 'error' in r.text:
            DebugLogEvent("Error posting the comment: %s" % r.text)
            return False
        DebugLogEvent("Comment successful %s" % r.text)
        return True
