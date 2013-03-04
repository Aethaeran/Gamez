from plugins import System
from gamez import common


# this class is special because it will be set to SYSTEM in the whole app
class SystemConfig(System):
    _config = {'user': '',
               'password': '',
               'port': 8085,
               'socket_host': '0.0.0.0',
               'https': False,
               'search_interval': 120, # minutes
               'update_interval': 1440, # minutes
               'wii_blacklist': '',
               'ps3_blacklist': '',
               'xbox360_blacklist': '',
               'pc_blacklist': '',
               'enabled': True,
               'final_path_wii': '',
               'final_path_ps3': '',
               'final_path_xbox360': '',
               'final_path_pc': '',
               'check_path_wii': '',
               'check_path_ps3': '',
               'check_path_xbox360': '',
               'check_path_pc': ''
               }
    single = True

    def getFinalPathForPlatform(self, platform):
        if platform == common.WII:
            return self.c.final_path_wii
        elif platform == common.PS3:
            return self.c.final_path_ps3
        elif platform == common.XBOX360:
            return self.c.final_path_xbox360
        elif platform == common.PC:
            return self.c.final_path_pc

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
            return self.c.wii_blacklist
        elif platform == common.PS3:
            return self.c.ps3_blacklist
        elif platform == common.XBOX360:
            return self.c.xbox360_blacklist
        elif platform == common.PC:
            return self.c.pc_blacklist

        