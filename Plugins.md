

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
All plugins should be in the respected folder in ./plugins/ e.g. ./plugins/downloaders
a new plugin shoudl be a new .py file in the type folder e.g. notifo.py (as a Notifier) in ./plugins/notifier/
At time of writing (5/3/13) i did not test sub folders or something ...
you can look in ./gamez/PluginManager.py at find_subclasses() to figure out what is indexed/searched for subclasses


To be a plugin all it needs is a class that extends any type.
    class MyPlugin(Downloader):
        pass
This should allready list and create a plugin on start.
BUT as a Downloader it will be used when we want to download a NZB/TORRENT file
the problem is that we dont have addDownload() defined and the program will crash.
(At this point there is no catching plugins errors like this…This may change later)


Config for your plugin
----------------------

the _config attribute of a plugin is used to create configurable items for your plugin.
It also creates the gui in the settings section on the page (<app_url>/settings/)... oh yeah its a simple dict

One importend note: Each plugin can have many config instances. This allowes many instances of a indexer or notifier.
If you dont want that function for your plugin set the single attribute to True
    class Notifo(Notifier):
        _config = {'user': '',
                   'password': ''
                  }
        single = True
A notifier named Notifo with two config items and you can only have one of it... for whatever reason

Now this would ceate not two but three (3) configurable fields: user, password AND enabled
The enabled field is given to everyone without asking... deal with it
Technicaly a config item has no type ... it is determend when it is set,
they are: integer, string, bool
Because it is determent what type to use during setting and the gui changes accordingly to the type retrieved
it is addvised to use a value as defauld that is the type you want... and yes the values in the _config dict are the default init values

Hint: if the word 'password' is in the config name it will be a password text field in the gui

... oh dont use "-" in the config name or you can not save setting and it will crash or something


Advanced Config
---------------

If you are not happy with default removal of "_" and capitalization of the name you can define a human nice name for it.
the config_meta attribute (also a dict) is used for this.
    class Notifo(Notifier):
        _config = {'user': '',
                   'password': ''
                  }
        single = True
        config_meta = {'user': {'human': 'Your Notifo UserName'}}
something along these lines
There are also:
- placeholder <- sets these fancy grey placeholder texts in the input field
- TODO more doc




