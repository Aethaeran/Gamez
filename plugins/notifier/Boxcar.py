from plugins import Notifier
import subprocess
from gamez.Logger import LogEvent, DebugLogEvent
from lib import requests


class Boxcar(Notifier):
    _config = {'email': ''}

    def _sendTest(self):
        DebugLogEvent("Testing boxcar")
        self.sendMessage("You just enabled Boxcar")

    def sendMessage(self, msg, game=None):

        if not self.c.email:
            LogEvent("Boxcar email / user not set")
            return

        payload = {'notification[from_screen_name]': 'Gamez',
                   'email': self.c.email,
                   'notification[message]': msg}

        r = requests.get('http://boxcar.io/devices/providers/MH0S7xOFSwVLNvNhTpiC/notifications', params=payload)
        print "boxbar url", r.url
        print "boxcar code", r.status_code

    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'enabled': {'on_enable': [_sendTest]}}
