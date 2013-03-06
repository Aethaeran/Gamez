#!/usr/bin/env python

import sys
import os

import traceback

import cherrypy
import threading
import cherrypy.process.plugins
from cherrypy.process.plugins import Daemonizer, PIDFile
from cherrypy import server
from gamez.WebRoot import WebRoot
from gamez.Logger import LogEvent
from gamez.Helper import launchBrowser, create_https_certificates
import cherrypy.lib.auth_basic
import gamez
from gamez.UpgradeFunctions import initDB
from gamez.PluginManager import PluginManager

from gamez import common
from gamez.Logger import DebugLogEvent

from gamez.classes import *
from gamez import GameTasks

# Fix for correct path
if hasattr(sys, 'frozen'):
    app_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

gamez.PROGDIR = app_path
gamez.CACHEPATH = os.path.join(app_path, gamez.CACHEDIR)
if not os.path.exists(gamez.CACHEDIR):
    os.mkdir(gamez.CACHEDIR)

class RunApp():

    def RunWebServer(self):
        LogEvent("Generating CherryPy configuration")
        #cherrypy.config.update(gamez.CONFIG_PATH)

        # Set Webinterface Path
        css_path = os.path.join(app_path, 'html', 'css')

        images_path = os.path.join(app_path, 'html', 'img')
        js_path = os.path.join(app_path, 'html', 'js')
        cover = gamez.CACHEPATH

        username = common.SYSTEM.c.login_user
        password = common.SYSTEM.c.login_password

        useAuth = False
        if username and password:
            useAuth = True
        userPassDict = {username: password}
        checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userPassDict)
        conf = {'/': {'tools.auth_basic.on': useAuth, 'tools.auth_basic.realm': 'Gamez', 'tools.auth_basic.checkpassword': checkpassword},
                '/api': {'tools.auth_basic.on': False},
                '/css': {'tools.staticdir.on': True, 'tools.staticdir.dir': css_path},
                '/js': {'tools.staticdir.on': True, 'tools.staticdir.dir': js_path},
                '/cover': {'tools.staticdir.on': True, 'tools.staticdir.dir': cover},
                '/img': {'tools.staticdir.on': True, 'tools.staticdir.dir': images_path},
                '/favicon.ico': {'tools.staticfile.on': True, 'tools.staticfile.filename': os.path.join(images_path, 'favicon.ico')},
               }

        # Https Support
        """
        if SYSTEM.c.https:

             # First set variable
             https_crt = app_path + "/gamez.crt"
             https_key = app_path + "/gamez.key"

             try:
                if not os.path.exists(https_crt) or not os.path.exists(https_key):
                    create_https_certificates(https_crt, https_key)
                    DebugLogEvent("Create a new HTTPS Certification") 
                else:
                    DebugLogEvent("HTTPS Certification exist")

                conf_https= {
                           'engine.autoreload.on':    False,
                           'server.ssl_certificate':  https_crt,
                           'server.ssl_private_key':  https_key
                            }
                cherrypy.config.update(conf_https)
             except:
                    LogEvent("!!!!!!!! Unable to activate HTTPS support !!!!!!!!!! Perhaps you have forgotten to install openssl?")
                    SYSTEM.c.https = False
        """
        # Workoround for OSX. It seems have problem wit the autoreload engine
        if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
            cherrypy.config.update({'engine.autoreload.on': False})
    
        LogEvent("Setting up download scheduler")
        gameTasksScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runSearcher, common.SYSTEM.c.interval_search * 60) #common.SYSTEM.c.search_interval * 60
        gameTasksScheduler.subscribe()
        LogEvent("Setting up game list update scheduler")
        gameListUpdaterScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runUpdater, common.SYSTEM.c.interval_update * 60)
        gameListUpdaterScheduler.subscribe()
        LogEvent("Setting up folder processing scheduler")
        folderProcessingScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runChecker, float(180))
        folderProcessingScheduler.subscribe()
        LogEvent("Starting the Gamez web server")
        cherrypy.tree.mount(WebRoot(app_path), config = conf)
        cherrypy.server.socket_host = common.SYSTEM.c.socket_host
        try:
            cherrypy.engine.start()
            cherrypy.log.screen = False
            cherrypy.engine.block()
        except KeyboardInterrupt:
            LogEvent("Shutting down Gamez")
            sys.exit()


def runUpdater():
    pass


def runSearcher():
    GameTasks.runSearcher()


def runChecker():
    GameTasks.runChecker()


def cmd():
    from optparse import OptionParser

    usage = "usage: %prog [-options] [arg]"
    p = OptionParser(usage=usage)
    p.add_option('-d', '--daemonize', action = "store_true",
                 dest = 'daemonize', help = "Run the server as a daemon")
    p.add_option('-D', '--debug', action = "store_true",
                 dest = 'debug', help = "Enable Debug Log")
    p.add_option('-p', '--pidfile',
                 dest = 'pidfile', default = None,
                 help = "Store the process id in the given file")
    p.add_option('-P', '--port',
                 dest = 'port', default = None,
                 help = "Force webinterface to listen on this port")
    p.add_option('-n', '--nolaunch', action = "store_true",
                 dest = 'nolaunch', help="Don't start browser")
    p.add_option('-b', '--datadir', default = None,
                 dest = 'datadir', help="Set the directory for the database")
    p.add_option('-c', '--config', default = None,
                 dest = 'config', help="Path to configfile")

    options, args = p.parse_args()

    #Set the Paths
    if options.datadir:
        datadir = options.datadir
        if not os.path.isdir(datadir):
            os.makedirs(datadir)
    else:
        datadir = app_path
    datadir = os.path.abspath(datadir)

    if not os.access(datadir, os.W_OK):
        raise SystemExit("Data dir must be writeable '" + datadir + "'")

    if options.config:
        config_path = options.config
    else:
        config_path = os.path.join(datadir, 'Gamez.ini')

    #Set global variables
    gamez.CONFIG_PATH = config_path
    gamez.DATADIR = datadir
    gamez.DATABASE_PATH = os.path.join(gamez.DATADIR, gamez.DATABASE_NAME)
    gamez.CONFIG_DATABASE_PATH = os.path.join(gamez.DATADIR, gamez.CONFIG_DATABASE_NAME)

    gamez.DATABASE.init(gamez.DATABASE_PATH)
    gamez.CONFIG_DATABASE.init(gamez.CONFIG_DATABASE_PATH)

    initDB()
    common.PM = PluginManager()
    common.SYSTEM = common.PM.getSystems('Default') # yeah SYSTEM is a plugin
    # lets init all plugins once
    for plugin in common.PM.getAll():
        DebugLogEvent("Plugin %s loaded successfully" % plugin.name)

    # Let`s check some options
    # Daemonize
    if options.daemonize:
        print "------------------- Preparing to run in daemon mode -------------------"
        LogEvent("Preparing to run in daemon mode")  
        daemon = Daemonizer(cherrypy.engine)
        daemon.subscribe()

    # Debug
    if options.debug:
        print "------------------- Gamez run in Debug -------------------"
        LogEvent('Gamez run in Debug')

    # Set port
    if options.port:
        print "------------------- Port manual set to " + options.port + " -------------------"
        port = int(options.port)
        server.socket_port = port
    else:
        port = common.SYSTEM.c.port
        server.socket_port = port

    # PIDfile
    if options.pidfile:
        print "------------------- Set PIDfile to " + options.pidfile + " -------------------"
        PIDFile(cherrypy.engine, options.pidfile).subscribe()

    # from couchpotato
    host = common.SYSTEM.c.socket_host
    https = False
    try:
        if not options.nolaunch:
            print "------------------- launch Browser ( " + str(host) + ":" + str(port) + ") -------------------"
            timer = threading.Timer(5, launchBrowser, [host, port, https])
            timer.start()
        return
    except:
        pass

    # update config for cherrypy
    cherrypy.config.update({
                                'global': {
                                           'server.socket_port': port
                                          }
                            })


if __name__ == '__main__':
    cmd()
    RunApp().RunWebServer()
