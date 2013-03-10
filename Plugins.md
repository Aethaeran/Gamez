Plugins
=======

All plugins are inside <app_path>/plugins/<type_of_plugin>/
(i will say ./ is <app_path> for now on)
for now there are 6 types of plugins:
- Downloader
- Notifier
- Indexer
- Provider
- PostProcessor
- System
(all in ./plugins/__init__.py)

General Structure
-----------------

All types (of plugins) are subclasses of Plugin (./plugins/__init__.py)
and all plugins are a subclass of the given type.

All plugins should be in the respected folder in ./plugins/ e.g. ./plugins/downloaders.
Simply by extending one of the types in you plugin class and putting the .py file in a folder under ./plugins/
will load your plugin.

Hint: all loaded / found plugins are listed uring start, check the log

a new plugin shoudl be a new .py file in the type folder e.g. notifo.py (as a Notifier) in ./plugins/notifier/
At time of writing (5/3/13) i did not test sub folders or something ...
you can look in ./gamez/PluginManager.py at find_subclasses() to figure out what is indexed/searched for subclasses

To be a plugin all it needs is a class that extends any type.
```python
class MyPlugin(Downloader):
    pass
```

This should allready list and create a plugin on start.
BUT as a Downloader it will be used when we want to download a NZB/TORRENT file.


Config for your plugin
----------------------

the _config attribute of a plugin is used to create configurable items for your plugin.
It also creates the gui in the settings section on the page (<app_url>/settings/)... oh yeah its a simple dict

To acces the config values use:
```python
self.c.my_config_name
```
Yes the "c" is importend! it refers to the "c"onfig

One importend note: Each plugin can have many config instances. This allowes many instances of a e.g. indexer or notifier.
If you dont want that function for your plugin set the single attribute to True
```python
class Notifo(Notifier):
    _config = {'user': '',
               'password': ''
              }
    single = True
```
A notifier named Notifo with two config items and you can only have one of it... for whatever reason

Now this would ceate not two but three (3) configurable fields: user, password AND enabled
The enabled field is given to everyone without asking... deal with it

Technicaly a config item has no type, it is determend when it is set,
they are: integer, string, bool
Because it is determent what type to use during setting and the gui changes accordingly to the type retrieved
it is addvised to use a value as defauld that is the type you want... and yes the values in the _config dict are the default init values

Hint: if the word 'password' is in the config name it will be a password text field in the gui
Hint2: the config items are ordered by name. might want to "group" them by prefixes.

Note: oh dont use "-" in the config name or you can not save settings and it will crash or something


Advanced Config
---------------

If you are not happy with default removal of "_" and capitalization of the name you can define a human nice name for it.
the config_meta attribute (also a dict) is used for this.
```python
class Notifo(Notifier):
    _config = {'user': '',
               'password': ''
              }
    single = True
    config_meta = {'user': {'human': 'Your Notifo UserName'}}
```
something along these lines
There are also:

* placeholder <- sets these fancy grey placeholder texts in the input field
* on_change_actions <- call functions if the config item is changed during save settings its a list: ['reboot']

* reboot <- reboot gamez.
This is the only one so far that is system wide BUT
any function reference to a function in your plugin class ... the function will be called in the instance it was triggered by

```python
class Notifo(Notifier):
    _config = {'user': '',
               'password': ''
              }
    single = True

    def testMySettings(self):
        print "Testing"

    config_meta = {'user': {'human': 'Your Notifo UserName'},
                   'password': {'on_change': testMySettings}
    }
```
Note: since testMySettings is a real function reference we need to define config_meta after we defined the function

Plugin Function
---------------
Each type of plugin requests a set of functions to be usefull and some have preset setting options.
Note: all have the config enabled and it is set to False if not overwritten in _config

Downloader
---------
something that handles the download of a Download Object

Functions:
- addDownload(self, download): where download is a Download Class Object, see ./gamez/classes.py. it should return True or False
- getGameStaus(self, game): where game is a Game Class Object, see ./gamez/classes.py it should return a tuple of a Object of the Class Status(see ./gamez/classes.py) and Download dand a absolute path to the downloaded game. e.g. 

```python
return (common.DOWNLOADED, download, '/mnt/stuff/imba_game')
```

Predefined Settings: None

Predefined Attributes:
- types: a list of download types that the downloader supports. choose any or all from

```python
types = [common.TYPE_NZB, common.TYPE_TORRENT]
```

Notifier
--------
something that sends out messages on snatch and/or complete

Functions:
- sendMessage(self, msg, game=None): where msg is a message string and game a Game Object. game is optional so you can call your snd message function without a game. Should return True or False

Predefined Settings:
- on_snatch: False
- on_complete: True (more info later)

Indexer
-------
a usenet or torrent indexer / search site

- getLatestRss(self): underspecified ... not done yet
- searchForGame(self, game): where game is a Game Class Object. It should return a list of Download()

Predefined Settings: None

Provider
--------
a game information provider

- searchForGame(self, term, platform, gid=0): term is the search term; platform is a Platform Object from common e.g. common.Wii; gid is the game id from that provider (hopefully). this should always return a list Game Objects
- getGame(self, platform, gid): platform is a Platform from common; gid is the provider game id. should return Game Object or False

PostProcessor
-------------
something that does something to a game after it is marked with common.DOWNLOADED

- ppPath(self, game, path): game is the Game that has been downloaded; path the absolute path we got from the downloader. should return True or False 


Confused ?
---------
just have a look at the plugins allready in the plugin folder.
Note: all functions calls of a plugin are wrapped in a try block ... so watch the log !!
