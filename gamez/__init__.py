import ConfigParser
from lib.peewee import *

DATADIR = ""
CONFIG_PATH = ""
PROGDIR = ""
CACHEDIR = ""
DATABASE_NAME = "GameZZ.db"
DATABASE_PATH = "./"
DATABASE = SqliteDatabase(None, threadlocals=True)

CONFIG = ConfigParser.RawConfigParser()
