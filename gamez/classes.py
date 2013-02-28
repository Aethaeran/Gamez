from lib.peewee import *
import TheGamesDBSearcher
import gamez
import common
from lib import requests
from Logger import *

class BaseModel(Model):

    class Meta:
        database = gamez.DATABASE

    def reload(self):
        print self.__metaclass__

class Platform(BaseModel):
    name = CharField()
    alias = CharField()
    tgdb_id = IntegerField(default=0)


class Game(BaseModel):
    name = CharField()
    tgdb_id = IntegerField(default=0)
    boxart_url = CharField()
    genre = CharField(default="n/a")
    _status = IntegerField(default=common.WANTED)

    platform = ForeignKeyField(Platform)

    class Meta:
        order_by = ('name',)

    def _boxArtPath(self):
        return os.path.join(gamez.CACHEDIR, str(self.tgdb_id) + ".jpeg")

    def updateFromTGDB(self):
        TheGamesDBSearcher.getGamesFromTGDB(tgdb_id=self.tgdb_id) # this will change the db entry
        self.cacheImg()
        self._reload() # this will laod the db values into this instance

    def _reload(self):
        g = Game.get(Game.id == self.id)
        self.name = g.name
        self.tgdb_id = g.tgdb_id
        self.boxart_url = g.boxart_url
        self._status = g.status

    def cacheImg(self, path=''):
        r = requests.get(self.boxart_url)
        DebugLogEvent("Downloading " + self.boxart_url)
        if r.status_code == 200:
            if not path:
                path = self._boxArtPath()
            with open(path, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

    def _set_status(self, value):
        if not value in common.ALL_STATUS:
            return
        self._status = value
        self.save()
        # do more notifications stuff and so on

    def _get_status(self):
        return self._status

    status = property(_get_status, _set_status)