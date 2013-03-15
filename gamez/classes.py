from lib.peewee import *
from lib.peewee import QueryCompiler
import os
import gamez
from lib import requests
from Logger import *
from gamez import common, Helper
import datetime
import json
from jsonHelper import MyEncoder


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
                continue
        DebugLogEvent("Create the final class: %s" % cls.__name__)
        try:
            cls.select().execute()
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

    def save(self, force_insert=False, only=None):
        History.createEvent(self)
        Model.save(self, force_insert=force_insert, only=only)

    def __json__(self):
        return self.__dict__

    def _getEvents(self):
        return History.select().where(History.obj_class == self.__class__.__name__, History.obj_id == self.id)
    #events = property(_getEvents)


class Platform(BaseModel):
    name = CharField()
    alias = CharField()
    tgdb_id = IntegerField(default=0)

    def _get_alias_url(self):
        s = self.alias
        return s.replace(" ", "+")

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


class Game_V1(Game_V0):
    overview = TextField(True, default='')

    class Meta:
        order_by = ('name',)
        db_table = 'Game'

    @classmethod
    def _migrate(cls):
        field = QueryCompiler().field_sql(cls.overview) # name of the new field
        table = cls._meta.db_table
        if cls._checkForColumn(cls.overview): # name of the new field
            return False # False like: dude stop !
        cls._meta.database.execute_sql('ALTER TABLE %s ADD COLUMN %s' % (table, field))
        return True


class Game_V2(Game_V1):
    _release_date = DateTimeField(True)

    class Meta:
        db_table = 'Game'
        order_by = ('name',) # the ordering has to be in the final class ... i call bug in peewee .. or at least this not taken care of... i know i do fance stuff here

    @classmethod
    def _migrate(cls):
        field = QueryCompiler().field_sql(cls._release_date) # name of the new field
        table = cls._meta.db_table
        if cls._checkForColumn(cls._release_date): # name of the new field
            return False # False like: dude stop !
        cls._meta.database.execute_sql('ALTER TABLE %s ADD COLUMN %s' % (table, field))
        return True

    def _get_rel_time(self):
        if self._release_date:
            return self._release_date
        return None

    def _set_rel_time(self, value):
        self._release_date = value

    release_date = property(_get_rel_time, _set_rel_time)

    def __eq__(self, other):
        return (other.name == self.name) and\
            (other.overview == self.overview) and\
            (other.release_date == self.release_date) and\
            (other.genre == self.genre) and\
            (other.boxart_url == self.boxart_url)


class Game(Game_V2):
    additional_search_terms = CharField(True)

    class Meta:
        order_by = ('name',)

    @classmethod
    def _migrate(cls):
        field = QueryCompiler().field_sql(cls.additional_search_terms) # name of the new field
        table = cls._meta.db_table
        if cls._checkForColumn(cls.additional_search_terms): # name of the new field
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


class Download_V0(BaseModel):
    game = ForeignKeyField(Game, related_name='downloads')
    name = CharField()
    url = CharField(unique=True)
    size = IntegerField(True)
    status = ForeignKeyField(Status)
    type = IntegerField(default=common.TYPE_NZB)

    class Meta:
        db_table = 'Download'


class Download(Download_V0):
    indexer = CharField(True)
    indexer_instance = CharField(True)
    external_id = CharField(True)

    @classmethod
    def _migrate(cls):
        migration_not_done = False # sending false tels the caller we migrated already
        for cur_field in (cls.indexer, cls.indexer_instance, cls.external_id):
            field = QueryCompiler().field_sql(cur_field) # name of the new field
            table = cls._meta.db_table
            if cls._checkForColumn(cur_field): # name of the new field
                continue
            cls._meta.database.execute_sql('ALTER TABLE %s ADD COLUMN %s' % (table, field))
            migration_not_done = True
        return migration_not_done

    def humanSize(self):
        num = self.size
        for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0


class History(BaseModel):
    time = DateTimeField(default=datetime.datetime.now())
    game = ForeignKeyField(Game, related_name='events', null=True)
    event = CharField()
    obj_id = IntegerField()
    obj_class = CharField()
    old_obj = TextField()
    new_obj = TextField()

    class Meta():
        order_by = ('-time', '-id')

    def save(self, force_insert=False, only=None):
        Model.save(self, force_insert=force_insert, only=only)

    @classmethod
    def createEvent(thisCls, obj):
        h = thisCls()
        try:
            old = obj.__class__.get(obj.__class__.id == obj.id)
        except obj.__class__.DoesNotExist:
            old = {}
            h.obj_id = 0
            h.event = 'insert'
        else:
            h.obj_id = old.id
            h.event = 'update'
        if obj.__class__.__name__ == 'Game':
            h.game = obj.id
        elif hasattr(obj, 'game'):
            h.game = obj.game
        h.old_obj = json.dumps(old, cls=MyEncoder)
        h.new_obj = json.dumps(obj, cls=MyEncoder)
        h.obj_class = obj.__class__.__name__
        h.save()

    def _old(self):
        json = json.loads(self.old_obj)
        if '_data' in json:
            return json['_data']
        else:
            return False

    def _new(self):
        json = json.loads(self.new_obj)
        if '_data' in json:
            return json['_data']
        else:
            return False

    def human(self):
        if self.obj_class == 'Game':
            return self._humanGame()
        elif self.obj_class == 'Download':
            return self._humanDownload()
        return "not implemented for %s" % self.obj_class

    def getNiceTime(self):
        return Helper.reltime(self.time, at=":")

    def _humanGame(self):
        data_o = self._old()
        data_n = self._new()
        if data_n and data_o:
            if data_n['_status'] != data_o['_status']:
                return 'new status %s ' % Status.get(Status.id == data_n['_status'])
        return 'this case of game history is not implemented'

    def _humanDownload(self):
        data_o = self._old()
        data_n = self._new()
        if data_n and data_o:
            if data_n['status'] != data_o['status']:
                return 'marked download as %s ' % Status.get(Status.id == data_n['status'])
            elif data_n['status'] == data_o['status'] and data_o['status'] == common.SNATCHED.id:
                return 'download resantched: %s' % Download.get(Download.id == data_n['id'])
        return 'this case of download history is not implemented'
        
 

__all__ = ['Platform', 'Status', 'Game', 'Config', 'Download', 'History']
