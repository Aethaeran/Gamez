from plugins import Notifier
import subprocess
from gamez.Logger import LogEvent
from lib import requests


class Boxcar(Notifier):
    _config = {'email': ''}

    def sendMessage(self, msg, game):

        if not self.c.email:
            LogEvent("Boxcar email / user not set")
            return

        payload = {'notification[from_screen_name]': 'Gamez',
                   'email': self.c.email,
                   'notification[message]': msg}

        r = requests.get('http://boxcar.io/devices/providers/MH0S7xOFSwVLNvNhTpiC/notifications', params=payload)
        print "boxbar url", r.url
        print "boxcar code", r.status_code
