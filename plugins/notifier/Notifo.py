from plugins import Notifier
from gamez.Logger import DebugLogEvent


class Notifo(Notifier):
    version = "0.2"
    update_url = 'http://pastebin.com/raw.php?i=5K8P4K0G'
    _config = {'email': '',
		'user': ''}

    def _sendTest(self):
        DebugLogEvent("Testing notifo")
        self.sendMessage("You just enabled notifo")

    def sendMessage(self, msg, game=None):
        print msg, game

    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'enabled': {'on_enable': [_sendTest]}}