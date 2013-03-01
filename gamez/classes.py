from lib.peewee import *
from lib.peewee import QueryCompiler
import gamez
import common
from lib import requests
from Logger import *


class BaseModel(Model):

    @classmethod
    def _checkForColumn(cls, field):
        table = cls._meta.db_table
        fields = cls._meta.database.execute_sql('PRAGMA table_info(%s)' % table).fetchall()
        for f in fields:
            if f[1] == field.db_column:
                return True
        else:
            return False

    @classmethod
    def _migrate(cls):
        return True # True like its all good !

    @classmethod
    def updateTable(cls):
        supers = list(cls.__bases__)
        if supers[0] == BaseModel:
            DebugLogEvent("no previous versions found for " + cls.__name__)
            return False
        for super_c in supers:
            next_super = None
            if super_c.__bases__:
                next_super = super_c.__bases__[0]
            if not next_super or next_super == BaseModel:
                break
            else:
                supers.append(next_super) # i know this is not 'cool' but this whole thing is pretty cool imo
        supers.reverse()
        DebugLogEvent("found " + str(len(supers)) + " previous versions for " + cls.__name__)
        supers.append(cls)
        for super_c in supers:
            DebugLogEvent("Calling _migrate() on %s" % super_c.__name__)
            if not super_c._migrate():
                DebugLogEvent("Looks like we already migrated %s" % super_c.__name__)
                return False
        DebugLogEvent("Create the final class: %s" % cls.__name__)
        try:
            cls.get()
        except Exception, e:
            DebugLogEvent("Error migrating: %s" % cls.__name__)
            raise e
        else:
            DebugLogEvent("Migrating %s DONE!" % cls.__name__)
            return True

    class Meta:
        database = gamez.DATABASE


class Platform(BaseModel):
    name = CharField()
    alias = CharField()
    tgdb_id = IntegerField(default=0)


class Status_V0(BaseModel):
    name = CharField()
    value = IntegerField(default=common.WANTED)

    class Meta:
        db_table = 'Status'


# thats how you update a model
class Status(Status_V0):
    hidden = BooleanField(True, default=False)

    @classmethod
    def _migrate(cls):
        field = QueryCompiler().field_sql(cls.hidden)
        table = cls._meta.db_table
        if cls._checkForColumn(cls.hidden):
            return False # False like: dude stop !
        cls._meta.database.execute_sql('ALTER TABLE %s ADD COLUMN %s' % (table, field))
        return True


class Game(BaseModel):
    name = CharField()
    tgdb_id = IntegerField(default=0)
    boxart_url = CharField()
    genre = CharField(default="n/a")
    _status = ForeignKeyField(Status)

    def __init__(self):
        super(Game, self).__init__()
        try:
            self._status
        except Status.DoesNotExist:
            self._status = Status.get(Status.value == common.WANTED)

    platform = ForeignKeyField(Platform)

    class Meta:
        order_by = ('name',)

    def boxArtPath(self):
        return os.path.join(gamez.CACHEDIR, str(self.tgdb_id) + ".jpeg")

    def updateFromTGDB(self):
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
                path = self.boxArtPath()
            with open(path, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)

    def _set_status(self, value):
        try:
            newS = Status.get(Status.value == value)
        except Status.DidNotExcist:
            return
        self._status = newS
        self.save()
        # do more notifications stuff and so on

    def _get_status(self):
        return self._status

    status = property(_get_status, _set_status)
