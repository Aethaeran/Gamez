import os
import gamez
import re
from gamez import common
from gamez.classes import *
from gamez.Logger import DebugLogEvent


"""plugins should not set the status of a game !!! it will be done in the loops that call / use the plugins"""


class ConfigWrapper(object):
    """this will be the "c" of a plugin to easily get the config for the current plugin
    also handels the saving of the new config"""
    configs = []

    def __init__(self):
        self.configs = []

    def addConfig(self, c):
        self.configs.append(c)

    def finalSort(self, enabled):
        self.configs.sort(key=lambda x: x.name, reverse=False)
        self.configs.insert(0, self.configs.pop(self.configs.index(enabled)))

    def __getattr__(self, name):
        for cur_c in self.configs:
            if cur_c.name == name:
                return cur_c.value
        raise AttributeError

    def __setattr__(self, name, value):
        for cur_c in self.configs:
            if cur_c.name == name:
                cur_c.value = value
                cur_c.save()
                return
        else:
            super(ConfigWrapper, self).__setattr__(name, value)


class Plugin(object):
    """plugin base class. loads the config on init
    "self.c" is reserved!!! thats how you get the config
    "self.type" is reserved!!! its the class name
    "self.instance" is reserved!!! its the instance name
    "self.name" is reserved!!! its the class name and instance name
    """
    _type = 'Plugin'
    single = False # if True the gui will not give the option for more configurations. but there is no logic to stop you do it anyways
    _config = {}

    def __init__(self, instance='Default'):
        """returns a new instance of the Plugin with the config loaded get the configuration as self.c.<name_of_config>"""
        self.name = "%s (%s)" % (self.__class__.__name__, instance)
        self.type = self.__class__.__name__
        self.instance = instance
        DebugLogEvent("Creating new plugin %s" % self.name)
        self.c = ConfigWrapper()

        if not ('enabled' in self._config and self._config['enabled']):
            self._config['enabled'] = False

        enabled_obj = None
        for k, v in self._config.items():
            #print "looking for", self.__class__.__name__, 'Plugin', k, instance
            try:
                cur_c = Config.get(Config.section == self.__class__.__name__,
                                  Config.module == 'Plugin',
                                  Config.name == k,
                                  Config.instance == self.instance)
            except Config.DoesNotExist:
                cur_c = Config()
                cur_c.module = 'Plugin'
                cur_c.section = self.__class__.__name__
                cur_c.instance = self.instance
                cur_c.name = k
                cur_c.value = v
                cur_c.save()
            if k == 'enabled':
                enabled_obj = cur_c
            self.c.addConfig(cur_c)
        self.c.finalSort(enabled_obj)
        """print self.c
        print self.c.configs
        for c in self.c.configs:
            print c.name, c.value"""

    def _get_enabled(self):
        return self.c.enabled

    def _set_enabled(self, value):
        self.c.enabled = value

    enabled = property(_get_enabled, _set_enabled) # shortcut to the enabled config option

    def deleteInstance(self):
        for c in self.c.configs:
            DebugLogEvent("Deleting config %s from %s" % (c, self.name))
            c.delete_instance()

class Downloader(Plugin):
    """Plugins of this class convert plain text to HTML"""
    _type = 'Downloader'
    name = "Does Noting"
    types = [common.TYPE_NZB, common.TYPE_TORRENT] # types the downloader can handle ... e.g. blackhole can handle both

    def addNzb(self, nzbUrl):
        """Add nzb to downloader"""
        return False

    def getGameStaus(self, game):
        """return tuple of Status and a path (str)"""
        return (common.UNKNOWN, '')

    def _downloadName(self, game):
        """tmplate on how to call the nzb/torrent file. nzb_name for sab"""
        return "%s (G.%s)" % (game.name, game.id)

    def _findGamezID(self, s):
        """find the game id in s is based on the _downloadName()"""
        m = re.search("\((G.(?P<id>\d+))\)", s)
        if m and m.group('id'):
            return int(m.group('id'))
        return 0


class Notifier(Plugin):
    """Plugins of this class convert plain text to HTML"""
    _type = 'Notifier'

    name = "prints"

    def __init__(self, *args, **kwargs):
        self._config['on_snatch'] = False
        self._config['on_complete'] = True # this is called after pp
        super(Notifier, self).__init__(*args, **kwargs)

    def sendMessage(self, msg, game):
        """Add nzb to downloader"""
        print str(msg)
        return True


class Indexer(Plugin):
    """Plugins of this class convert plain text to HTML"""
    _type = 'Indexer'
    types = [common.TYPE_NZB, common.TYPE_TORRENT] # types this indexer will give back

    name = "Does Noting"

    def getLatestRss(self):
        """return list of Gamez"""
        return []

    def searchForGame(self, game):
        """return list of Download()"""
        return [Download()]


class Provider(Plugin):
    """get game information"""
    _type = 'Provider'

    """creating more providers is definety more complicatedn then other things since
    the platform identification is kinda based on the the id of thegamesdb
    and the Game only has one field... but if one will take on this task please dont create just another field for the game
    instead create a new class that holds the information
    """

    def searchForGame(self, term, platform, gid=0):
        """return always a list of games even if id is given, list might be empty or only contain 1 item"""
        return []

    def getGame(self, platform, gid):
        return False


class PostProcessor(Plugin):
    _type = 'PostProcessor'

    def ppPath(self, game, path):
        return False


class System(Plugin):
    """Is just a way to handle the config part and stuff"""
    _type = 'System'
    name = "Does Noting"


