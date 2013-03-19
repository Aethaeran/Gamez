
from gamez import common
from plugins import Downloader
from lib import requests
from gamez.Logger import LogEvent
import os


class Blackhole(Downloader):
    version = "0.2"
    _config = {'path_wii': '',
               'path_xbox360': '',
               'path_ps3': '',
               'path_pc': ''}
    types = [common.TYPE_NZB, common.TYPE_TORRENT]
    config_meta = {'plugin_desc': 'This will download the nzb/torrent file into the platform path. It can not check for the status of a game.'
                   }

    def _choosePath(self, platform):
        if platform == common.WII:
            return self.c.path_wii
        elif platform == common.XBOX360:
            return self.c.path_xbox360
        elif platform == common.PS3:
            return self.c.path_ps3
        elif platform == common.PC:
            return self.c.path_pc
        else:
            return ''

    def addDownload(self, game, download):
        b_dir = self._choosePath(game.platform)
        if not os.path.isdir(b_dir):
            LogEvent("Download save to Blackhole at %s is not a valid folder" % b_dir)

        dst = os.path.join(b_dir, self._downloadName(game, download) + self._getTypeExtension(download.type))
        r = requests.get(download.url)
        if r.status_code == 200:
            with open(dst, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
        else:
            LogEvent("Download save to Blackhole at %s failed" % dst)
            return False

        LogEvent("Download saved to Blackhole at %s" % dst)
        return True
