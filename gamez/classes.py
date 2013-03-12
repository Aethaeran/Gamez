from lib.peewee import *
from lib.peewee import QueryCompiler
import os
import gamez
from lib import requests
from Logger import *
from gamez import common, Helper


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

    def __str__(self):
        if hasattr(self, 'name'):
            return str(self.name)
        super(BaseModel, self).__str__()

    def __add__(self, other):
        return str(self) + other

    def __radd__(self, other):
        return other + str(self)


class Platform(BaseModel):
    name = CharField()
    alias = CharField()
    tgdb_id = IntegerField(default=0)

    def _get_alias_url(self):
        s = self.alias
        return s.replace(" ", "+")

    # i dont like the tgdb api defenition that much -.-
    url_alias = property(_get_alias_url)


class Status_V0(BaseModel):
    name = CharField()

    class Meta:
        db_table = 'Status'

    def save(self, do=False):
        if do:
            super(Status_V0, self).save()


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


class Game_V0(BaseModel):
    name = CharField()
    tgdb_id = IntegerField(default=0)
    boxart_url = CharField()
    genre = CharField(default="n/a")
    _status = ForeignKeyField(Status)

    platform = ForeignKeyField(Platform)

    class Meta:
        order_by = ('name',)
        db_table = 'Game'

    def _imgName(self):
        return "%s (%s).jpeg" % (Helper.replace_all(self.name), self.id)

    def boxArtPath(self):
        return os.path.join(gamez.CACHEPATH, self._imgName())

    def coverPath(self):
        return os.path.join(gamez.CACHEDIR, self._imgName())

    def updateFromTGDB(self):
        self.cacheImg()
    """
    def reload(self):
        g = Game.get(Game.id == self.id)
        self.name = g.name
        self.tgdb_id = g.tgdb_id
        self.boxart_url = g.boxart_url
        self._status = g.status"""

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
        self._status = value
        self.save()
        LogEvent("New status %s for %s on %s" % (value, self.name, self.platform))

    def _get_status(self):
        return self._status

    def save(self):
        new = False
        try:
            self._status
        except Status.DoesNotExist:
            self._status = common.WANTED
            new = True
        super(Game_V0, self).save() # NOTE if you use super() and update the Model/class make sure to update the super class you call it on otherwise you will have a infinit recursion
        if new:
            self.cacheImg()

    status = property(_get_status, _set_status)


class Game(Game_V0):
    overview = TextField(True, default='')

    class Meta:
        order_by = ('name',) # the ordering has to be in the final class ... i call bug in peewee .. or at least this not taken care of... i know i do fance stuff here

    @classmethod
    def _migrate(cls):
        field = QueryCompiler().field_sql(cls.overview) # name of the new field
        table = cls._meta.db_table
        if cls._checkForColumn(cls.overview): # name of the new field
            return False # False like: dude stop !
        cls._meta.database.execute_sql('ALTER TABLE %s ADD COLUMN %s' % (table, field))
        return True


class Config(BaseModel):
    module = CharField(default='system') # system, plugin ... you know this kind of thing
    section = CharField() # sabnzb, newznab -> plugin name or system section
    instance = CharField(default='Default') # for multiple configurations for the same plugin
    name = CharField() # name of the value to save
    _value_int = IntegerField(True)
    _value_char = CharField(True)
    _value_bool = IntegerField(True)

    class Meta:
        database = gamez.CONFIG_DATABASE
        order_by = ('name',)

    def _get_value(self):
        if self._value_bool in (1, 0):
            return self._value_bool
        elif self._value_int != None:
            return self._value_int
        else:
            return self._value_char

    def _set_value(self, value):
        if type(value).__name__ == 'int':
            self._value_char = None
            self._value_bool = None
            self._value_int = value
            return
        if type(value).__name__ in ('str', 'unicode'):
            self._value_bool = None
            self._value_int = None
            self._value_char = value
            return
        if type(value).__name__ in ('bool', 'NoneType'):
            self._value_char = None
            self._value_int = None
            self._value_bool = value
            return
        raise Exception('unknown config save type %s for config %s' % (type(value), self.name))

    value = property(_get_value, _set_value)

    def curType(self):
        if self._value_bool in (1, 0):
            return 'bool'
        elif self._value_int:
            return 'int'
        else:
            return 'str'


class Download(BaseModel):
    game = ForeignKeyField(Game)
    name = CharField()
    url = CharField(unique=True)
    size = IntegerField(True)
    status = ForeignKeyField(Status)
    type = IntegerField(default=common.TYPE_NZB)

__all__ = ['Platform', 'Status', 'Game', 'Config', 'Download']
