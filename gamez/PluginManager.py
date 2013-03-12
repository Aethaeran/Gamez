import plugins
import os
import sys
import ActionManager
from gamez.classes import *
from gamez.Logger import DebugLogEvent, LogEvent
from lib import requests
import re
import shutil


class PluginManager(object):
    _cache = {}

    def __init__(self, path='plugins'):
        self.path = path
        self.cache(debug=False)
        if self.updatePlugins():
            ActionManager.executeAction('hardReboot', 'PluginManager')

    def cache(self, reloadModules=False, debug=False):
        classes = (plugins.Downloader, plugins.Notifier, plugins.Indexer, plugins.System, plugins.Provider, plugins.PostProcessor)
        #classes = (plugins.Downloader, )
        for cur_plugin_type in classes: #for plugin types
            cur_plugin_type_name = cur_plugin_type.__name__
            cur_classes = self.find_subclasses(cur_plugin_type, reloadModules, debug=debug)
            DebugLogEvent("I found %s %s (%s)" % (len(cur_classes), cur_plugin_type_name, cur_classes))

            for cur_class, cur_path in cur_classes: # for classes of that type
                if not cur_plugin_type in self._cache:
                    self._cache[cur_plugin_type] = {}
                instances = []
                configs = Config.select().where(Config.section == cur_class.__name__).execute()
                for config in configs: # for instances of that class of tht type
                    instances.append(config.instance)
                instances.append('Default') # add default instance for everything, this is only needed for the first init after that the instance names will be found in the db
                instances = list(set(instances))
                instance_order = {}
                for instance in instances:
                    try:
                        #DebugLogEvent("Creating %s (%s)" % (cur_class, instance))
                        cur_class(instance)
                    except:
                        LogEvent("%s (%s) crashed on init i am not going to remember this one !!")
                        continue

                    try:
                        order = Config.get(Config.section == cur_class.__name__, Config.instance == instance, Config.name == 'plugin_order')
                    except Config.DoesNotExist:
                        LogEvent("order config does not excist ... this should have been created during plugin obj creation")
                        continue
                    instance_order[order.value] = instance
                final_instance_order = []
                for order in sorted(instance_order.iterkeys()):
                    final_instance_order.append(instance_order[order])
                self._cache[cur_plugin_type][cur_class] = final_instance_order
                DebugLogEvent("I found %s instances for %s(v%s): %s" % (len(final_instance_order), cur_class.__name__, cur_class.version, self._cache[cur_plugin_type][cur_class]))

        #DebugLogEvent("Final plugin cache %s" % self._cache)

    def updatePlugins(self):
        done_types = []
        upgrade_done = False
        for plugin in self.getAll(True):
            if plugin.__class__ in done_types or not hasattr(plugin, 'update_url'):
                continue
            else:
                done_types.append(plugin.__class__)
            DebugLogEvent("Checking if %s needs an update. Please wait..." % plugin.__class__.__name__)
            r = requests.get(plugin.update_url)
            source = r.text
            m = re.search("""    version = ["'](?P<version>.*?)["']""", source)
            if not (m or r.status_code.ok):
                continue
            new_v = float(m.group('version'))
            old_v = float(plugin.version)
            if old_v >= new_v:
                continue
            rel_plugin_path = self._path_cache[plugin.__class__]
            src = os.path.abspath(rel_plugin_path)
            dst = "%s.v%s.txt" % (src, old_v)
            shutil.move(src, dst)
            try:
                logfile = open(src, 'a')
                try:
                    logfile.write(r.text)
                finally:
                    logfile.close()
            except IOError as exe:
                print exe
                DebugLogEvent("Error during writing updated version")
                shutil.move(dst, src)
            else:
                upgrade_done = True
        return upgrade_done

    def _getAny(self, cls, wanted_i='', returnAll=False):
        """may return a list with instances or just one instance if wanted_i is given
        only gives back enabeld plugins by default set returnAll to True to get all
        WARNING: "disabeld" plugins are still instantiated
        """
        plugin_instances = []
        if not cls in self._cache:
            return plugin_instances
        for cur_c, instances in self._cache[cls].items():
            for cur_instance in instances:
                #DebugLogEvent("Will create new instance (%s) from %s" % (cur_instance, cur_c.__name__))
                new = cur_c(cur_instance)
                if wanted_i:
                    if wanted_i == cur_instance:
                        return new
                if new.enabled or returnAll:
                    plugin_instances.append(new)
                else:
                    DebugLogEvent("%s is disabled" % cur_c.__name__)
        return plugin_instances

    def _getTyped(self, cls, i='', returnAll=False, types=[]):
        if not types:
            return self._getAny(cls, i, returnAll)
        filtered = []
        for cur_cls in self._getAny(cls, i, returnAll):
            for cur_type in types:
                if cur_type in cur_cls.types:
                    filtered.append(cur_cls)
        return filtered

    def getDownloaders(self, i='', returnAll=False, types=[]):
        return self._getTyped(plugins.Downloader, i, returnAll, types)
    D = property(getDownloaders)

    def getIndexers(self, i='', returnAll=False, types=[]):
        return self._getTyped(plugins.Indexer, i, returnAll, types)
    I = property(getIndexers)

    def getNotifiers(self, i='', returnAll=False):
        return self._getAny(plugins.Notifier, i, returnAll)
    N = property(getNotifiers)

    def getSystems(self, i='', returnAll=False):
        return self._getAny(plugins.System, i, returnAll)
    S = property(getSystems)

    def getProvider(self, i='', returnAll=False):
        return self._getAny(plugins.Provider, i, returnAll)
    P = property(getProvider)

    def getPostProcessors(self, i='', returnAll=False):
        return self._getAny(plugins.PostProcessor, i, returnAll)
    PP = property(getPostProcessors)

    def getAll(self, returnAll=False):
        return self.getSystems(returnAll=returnAll) +\
                self.getIndexers(returnAll=returnAll) +\
                self.getDownloaders(returnAll=returnAll) +\
                self.getPostProcessors(returnAll=returnAll) +\
                self.getNotifiers(returnAll=returnAll) +\
                self.getProvider(returnAll=returnAll)

    # this is ugly ... :(
    def getInstanceByName(self, class_name, instance):
        for pType in self._cache:
            for pClass in self._cache[pType]:
                if class_name == pClass.__name__:
                    for cur_instance in self._cache[pType][pClass]:
                        if instance == cur_instance:
                            return pClass(instance)
        return None

    def find_subclasses(self, cls, reloadModule=False, debug=False):
        path = self.path
        """
        Find all subclass of cls in py files located below path
        (does look in sub directories)

        @param path: the path to the top level folder to walk
        @type path: str
        @param cls: the base class that all subclasses should inherit from
        @type cls: class
        @rtype: list
        @return: a list if classes that are subclasses of cls
        """

        if debug:
            print "searching for subclasses of", cls, cls.__name__
        org_cls = cls
        subclasses = []

        def look_for_subclass(modulename, cur_path):
            if debug:
                print("searching %s" % (modulename))

            try:
                module = __import__(modulename)
            except: # catch everything we dont know what kind of error a plugin might have
                LogEvent("Error while imorting %s" % modulename)
                return

            #walk the dictionaries to get to the last one
            d = module.__dict__
            for m in modulename.split('.')[1:]:
                d = d[m].__dict__

            #look through this dictionary for things
            #that are subclass of Job
            #but are not Job itself
            for key, entry in d.items():
                if key == cls.__name__:
                    continue

                try:
                    if issubclass(entry, cls):
                        if debug:
                            print("Found subclass: " + key)
                        if reloadModule: # this is donw to many times !!
                            DebugLogEvent("Reloading module %s" % module)
                            reload(module)
                        subclasses.append((entry, cur_path))
                except TypeError:
                    #this happens when a non-type is passed in to issubclass. We
                    #don't care as it can't be a subclass of Job if it isn't a
                    #type
                    continue

        for root, dirs, files in os.walk(path):
            for name in files:
                if name.endswith(".py") and not name.startswith("__"):
                    cur_path = os.path.join(root, name)
                    modulename = cur_path.rsplit('.', 1)[0].replace(os.sep, '.')
                    look_for_subclass(modulename, cur_path)

        if debug:
            print "final subclasses for", org_cls, subclasses
        return subclasses


