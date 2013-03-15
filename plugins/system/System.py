from plugins import System
from gamez import common
from gamez.classes import Platform


# this class is special because it will be set to SYSTEM in the whole app
class SystemConfig(System):
    version = "0.15"
    _config = {'login_user': '',
               'login_password': '',
               'port': 8085,
               'socket_host': '0.0.0.0',
               'https': False,
               'interval_search': 120, # minutes
               'interval_update': 1440, # minutes
               'interval_check': 3,
               'blacklist_wii': '',
               'blacklist_ps3': '',
               'blacklist_xbox360': '',
               'blacklist_pc': '',
               'whitelist_wii': '',
               'whitelist_ps3': '',
               'whitelist_xbox360': '',
               'whitelist_pc': '',
               'enabled': True,
               'check_path_wii': '',
               'check_path_ps3': '',
               'check_path_xbox360': '',
               'check_path_pc': '',
               'again_on_fail': False,
               'default_platform_select': '',
               'resnatch_same': True
               }
    config_meta = {'login_user': {'on_change_actions': ['reboot']},
                    'login_password': {'on_change_actions': ['reboot']},
                    'blacklist_wii': {'human': 'Blacklist for Wii', 'placeholder': 'separated by ,', 'desc': 'If any of the words are found in the title the download will be skipped. Words are separated by , and spaces are removed.'},
                    'blacklist_ps3': {'human': 'Blacklist for PS3', 'placeholder': 'separated by ,', 'desc': 'If any of the words are found in the title the download will be skipped. Words are separated by , and spaces are removed.'},
                    'blacklist_xbox360': {'human': 'Blacklist for Xbox360', 'placeholder': 'separated by ,', 'desc': 'If any of the words are found in the title the download will be skipped. Words are separated by , and spaces are removed.'},
                    'blacklist_pc': {'human': 'Blacklist for PC', 'placeholder': 'separated by ,', 'desc': 'If any of the words are found in the title the download will be skipped. Words are separated by , and spaces are removed.'},
                    'interval_search': {'human': 'Search interval (minutes)'},
                    'interval_update': {'human': 'Update interval (minutes)'},
                    'https': {'human': 'HTTPS'},
                    'check_path_wii': {'human': 'Check for Wii games in', 'placeholder': 'Absolute Path'},
                    'check_path_ps3': {'human': 'Check for PS3 games in', 'placeholder': 'Absolute Path'},
                    'check_path_xbox360': {'human': 'Check for Xbox360 games in', 'placeholder': 'Absolute Path'},
                    'check_path_pc': {'human': 'Check for PC games in', 'placeholder': 'Absolute Path'},
                    'interval_search': {'human': 'Search for games interval (minutes)', 'on_change_actions': ['reboot']},
                    'interval_update': {'human': 'Update games interval (minutes)', 'on_change_actions': ['reboot']},
                    'interval_check': {'human': 'Download check interval (minutes)', 'on_change_actions': ['reboot']},
                    'again_on_fail': {'human': 'Retry a different download after a failed one'},
                    'plugin_desc': 'System wide configurations'
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
        out = ''
        if platform == common.WII:
            out = self.c.blacklist_wii
        elif platform == common.PS3:
            out = self.c.blacklist_ps3
        elif platform == common.XBOX360:
            out = self.c.blacklist_xbox360
        elif platform == common.PC:
            out = self.c.blacklist_pc
        return filter(None, out.split(','))

    def getWhitelistForPlatform(self, platform):
        out = ''
        if platform == common.WII:
            out = self.c.whitelist_wii
        elif platform == common.PS3:
            out = self.c.whitelist_ps3
        elif platform == common.XBOX360:
            out = self.c.whitelist_xbox360
        elif platform == common.PC:
            out = self.c.whitelist_pc
        return filter(None, out.split(','))

    def _default_platform_select(self):
        out = {}
        for p in Platform.select():
            out[p.id] = p.name
        return out

