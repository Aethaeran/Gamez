from lib.peewee import *

DATADIR = ""
CONFIG_PATH = ""
PROGDIR = ""
CACHEDIR = "cover"
CACHEPATH = ""
DATABASE_NAME = "GameZZ.db"
DATABASE_PATH = "./"
DATABASE = SqliteDatabase(None, threadlocals=True)
CONFIG_DATABASE_NAME = "Config.db"
CONFIG_DATABASE_PATH = "./"
CONFIG_DATABASE = SqliteDatabase(None, threadlocals=True)


class Common(object):
    PM = None # PluginManager hold the plugins
    SYSTEM = None # system holds the config and maybe later more

    # will be set to the obj during initDB()
    UNKNOWN = None
    WANTED = None  # default status
    SNATCHED = None # well snatched and the downloader is getting it ... so we hope
    DOWNLOADED = None # no status thingy
    COMPLETED = None # downloaded and pp_success
    FAILED = None # download failed
    PP_FAIL = None # post processing failed
    DELETED = None # marked as deleted
    IGNORE = None # ignore this item

    # platforms
    # will be set it the obj during initDB()
    XBOX360 = None
    WII = None
    PS3 = None
    PC = None

    TYPE_NZB = 1
    TYPE_TORRENT = 2

    LOGTOSCREEN = True
    LOGDEBUGTOSCREEN = False

    def getTypeExtension(self, d_type):
        if d_type == self.TYPE_NZB:
            return ".nzb"
        elif d_type == self.TYPE_TORRENT:
            return ".torrent"
        else:
            return ".txt"


common = Common()

