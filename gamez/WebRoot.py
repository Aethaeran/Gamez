import cherrypy
import os
import ConfigParser
import threading
import gamez
from jinja2 import Environment, PackageLoader
from gamez import common, GameTasks
from classes import *
from gamez.Logger import LogEvent, DebugLogEvent

class WebRoot:
    appPath = ''

    def __init__(self,app_path):
        WebRoot.appPath = app_path
        self.env = Environment(loader=PackageLoader('html', 'templates'))

    def _globals(self):
        return {'p': Platform.select(), 's': Status.select()}

    @cherrypy.expose
    def index(self, status_message='', version=''):
        template = self.env.get_template('index.html')
        gs = Game.select()
        return template.render(games=gs, **self._globals())

    @cherrypy.expose
    def search(self, term='', platform=''):
        template = self.env.get_template('search.html')
        games = {}
        if term:
            for provider in common.PM.P:
                LogEvent("Searching on %s" % provider.name)
                games[provider.name] = provider.searchForGame(term, Platform.get(Platform.id == platform))

        return template.render(games=games, **self._globals())

    @cherrypy.expose
    def settings(self):
        template = self.env.get_template('settings.html')
        return template.render(plugins=common.PM.getAll(True), **self._globals())


    @cherrypy.expose
    def createInstance(self, plugin, instance):
        for cur_plugin in common.PM.getAll(True):
            if cur_plugin.type == plugin and not cur_plugin.single:
                c = cur_plugin.__class__
                c(instance=instance)
                break
        common.PM.cache()
        raise cherrypy.HTTPRedirect('/settings/')
    
    @cherrypy.expose
    def removeInstance(self, plugin, instance):
        for cur_plugin in common.PM.getAll(True):
            if cur_plugin.type == plugin and cur_plugin.instance == instance:
                c = cur_plugin.deleteInstance()
                break
        common.PM.cache()
        raise cherrypy.HTTPRedirect('/settings/')
    
    @cherrypy.expose
    def saveSettings(self, **kwargs):
        for k, v in kwargs.items():
            parts = k.split('-')
            try:
                cur_c = Config.get(Config.section == parts[0],
                                  Config.module == 'Plugin',
                                  Config.name == parts[2],
                                  Config.instance == parts[1])

                try:
                    cur_c.value = int(v)
                except ValueError:
                    if v == 'on':
                        v = True
                    if v == 'None':
                        v == False
                    cur_c.value = v
                cur_c.save()
            except Config.DoesNotExist:
                DebugLogEvent("Could not find config K:%s V:%s" % (k, v))

        raise cherrypy.HTTPRedirect('/settings/')

    @cherrypy.expose
    def log(self):
        template = self.env.get_template('index.html')
        gs = Game.select()
        return template.render(games=gs, **self._globals())

    @cherrypy.expose
    def comingsoon(self):
        template = self.env.get_template('index.html')
        gs = Game.select()
        return template.render(games=gs, **self._globals())

    @cherrypy.expose
    def addGame(self, gid, p='TheGameDB'):
        gid = int(gid)
        for provider in common.PM.P:
            if provider.type == p:
                game = provider.getGame(gid)
                if game:
                    game.save()
                    GameTasks.searchGame(game)

        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def removegame(self,gid):
        q = Game.delete().where(Game.id == gid)
        q.execute()
        raise cherrypy.HTTPRedirect()

    @cherrypy.expose
    def updateStatus(self, gid, s):
        g = Game.get(Game.id == gid)
        g.status = Status.get(Status.id == s)
        if g.status == common.WANTED:
            GameTasks.searchGame(g)
        raise cherrypy.HTTPRedirect()

    @cherrypy.expose
    def updategamelist(self):
        #addAllWii()
        #AddWiiGamesIfMissing()
        #AddXbox360GamesIfMissing()
        #AddComingSoonGames()
        status = "Game list has been updated successfully"
        raise cherrypy.HTTPRedirect("/?status_message=" + status)

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        status = "Gamez will be shutting down!!! Bye"
        raise cherrypy.HTTPRedirect("/?status_message=" + status)

    @cherrypy.expose
    def reboot(self):
        cherrypy.engine.restart()
        status = "Gamez will be restart!!!"
        raise cherrypy.HTTPRedirect("/?status_message=" + status)

    @cherrypy.expose
    def forcesearch(self, gid):
        GameTasks.searchGame(Game.get(Game.id == gid))
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def refreshinfo(self, gid, p='TheGameDB'):
        DebugLogEvent("init update")
        game = Game.get(Game.id == gid)
        for provider in common.PM.P:
            if provider.type == p:
                new = provider.getGame(game.tgdb_id)
                game.name = new.name
                game.boxart_url = new.boxart_url
                game.genre = new.genre
                game.save()
                game.cacheImg()

        raise cherrypy.HTTPRedirect('/')
