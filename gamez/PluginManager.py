import plugins
import os
import traceback
import ActionManager
from gamez.classes import *
from gamez.Logger import *
from lib import requests
import re
import shutil
import threading


class PluginManager(object):
    _cache = {}

    def __init__(self, path='plugins'):
        self._caching = threading.Semaphore()
        self.path = path
        self.cache(debug=False)

        timer = threading.Timer(1, self.updatePlugins)
        timer.start()

    def cache(self, reloadModules=False, debug=False):
        with self._caching:
            classes = (plugins.Downloader, plugins.Notifier, plugins.Indexer, plugins.System, plugins.Provider, plugins.PostProcessor)
            #classes = (plugins.Downloader, )
            for cur_plugin_type in classes: #for plugin types
                cur_plugin_type_name = cur_plugin_type.__name__
                cur_classes = self.find_subclasses(cur_plugin_type, reloadModules, debug=debug)
                log("I found %s %s (%s)" % (len(cur_classes), cur_plugin_type_name, cur_classes))
    
                for cur_class, cur_path in cur_classes: # for classes of that type
                    if not cur_plugin_type in self._cache:
                        self._cache[cur_plugin_type] = {}
                    instances = []
                    configs = Config.select().where(Config.section == cur_class.__name__).execute()
                    for config in configs: # for instances of that class of tht type
                        instances.append(config.instance)
                    instances.append('Default') # add default instance for everything, this is only needed for the first init after that the instance names will be found in the db
                    instances = list(set(instances))
                    final_instances = []
                    for instance in instances:
                        try:
                            #log("Creating %s (%s)" % (cur_class, instance))
                            cur_class(instance)
                        except Exception as ex:
                            tb = traceback.format_exc()
                            log.error("%s (%s) crashed on init i am not going to remember this one !! \nError: %s\n\n%s" % (cur_class.__name__, instance, ex, tb))
                            continue
                        final_instances.append(instance)
                    self._cache[cur_plugin_type][cur_class] = final_instances
                    log("I found %s instances for %s(v%s): %s" % (len(final_instances), cur_class.__name__, cur_class.version, self._cache[cur_plugin_type][cur_class]))
            #log("Final plugin cache %s" % self._cache)

    def updatePlugins(self):
        with self._caching:
            done_types = []
            upgrade_done = False
            for plugin in self.getAll(True):
                if plugin.__class__ in done_types or not hasattr(plugin, 'update_url'):
                    continue
                else:
                    done_types.append(plugin.__class__)
                log("Checking if %s needs an update. Please wait... (%s)" % (plugin.__class__.__name__, plugin.update_url))
                try:
                    r = requests.get(plugin.update_url, timeout=20)
                except (requests.ConnectionError, requests.Timeout):
                    log.error("Error while retrieving the update for %s" % plugin.__class__.__name__)
                    continue
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
                    pluginFile = open(src, 'a')
                    try:
                        pluginFile.write(r.text)
                    finally:
                        pluginFile.close()
                except IOError as exe:
                    print exe
                    log.error("Error during writing updated version")
                    shutil.move(dst, src)
                else:
                    upgrade_done = True
            if upgrade_done:
                ActionManager.executeAction('hardReboot', 'PluginManager')
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
                #log("Will create new instance (%s) from %s" % (cur_instance, cur_c.__name__))
                new = cur_c(cur_instance)
                if wanted_i:
                    if wanted_i == cur_instance:
                        return new
                if new.enabled or returnAll:
                    plugin_instances.append(new)
                else:
                    log("%s is disabled" % cur_c.__name__)
        #print cls, wanted_i, returnAll, plugin_instances, sorted(plugin_instances, key=lambda x: x.c.plugin_order, reverse=False)
        return sorted(plugin_instances, key=lambda x: x.c.plugin_order, reverse=False)

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
                log.error("Error while imorting %s" % modulename)
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
                            log("Reloading module %s" % module)
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


