from plugins import Notifier
from gamez.Logger import *

class Notifo(Notifier):
    version = "0.3"
    update_url = 'http://pastebin.com/raw.php?i=5K8P4K0G'
    _config = {'email': '',
		'user': ''}

    def _sendTest(self):
        log("Testing notifo")
        self.sendMessage("You just enabled notifo")

    def sendMessage(self, msg, game=None):
        print msg, game

    # config_meta is at the end because otherwise the sendTest function would not be defined
    config_meta = {'enabled': {'on_enable': [_sendTest]},
                   'plugin_desc': 'This is not a real Notifo notifier !!! its just a dummy that shows howto make / use external plugins. it will be removed as soon we have a real one'
                   }