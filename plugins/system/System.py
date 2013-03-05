from plugins import System
from gamez import common


# this class is special because it will be set to SYSTEM in the whole app
class SystemConfig(System):
    _config = {'user': '',
               'password': '',
               'port': 8085,
               'socket_host': '0.0.0.0',
               'https': False,
               'interval_search': 120, # minutes
               'interval_update': 1440, # minutes
               'blacklist_wii': '',
               'blacklist_ps3': '',
               'blacklist_xbox360': '',
               'blacklist_pc': '',
               'enabled': True,
               'check_path_wii': '',
               'check_path_ps3': '',
               'check_path_xbox360': '',
               'check_path_pc': ''
               }
    single = True

    def getCheckPathForPlatform(self, platform):
        if platform == common.WII:
            return self.c.check_path_wii
        elif platform == common.PS3:
            return self.c.check_path_ps3
        elif platform == common.XBOX360:
            return self.c.check_path_xbox360
        elif platform == common.PC:
            return self.c.check_path_pc

    def getBlacklistForPlatform(self, platform):
        if platform == common.WII:
            return self.c.blacklist_wii
        elif platform == common.PS3:
            return self.c.blacklist_ps3
        elif platform == common.XBOX360:
            return self.c.blacklist_xbox360
        elif platform == common.PC:
            return self.c.blacklist_pc
