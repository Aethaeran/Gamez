#!/usr/bin/env python

import sys
import os

import cherrypy
import threading
import cherrypy.process.plugins
from cherrypy.process.plugins import PIDFile
from cherrypy import server
from gamez.WebRoot import WebRoot
from gamez.Helper import launchBrowser, create_https_certificates
import cherrypy.lib.auth_basic
import gamez
import logging
from gamez.UpgradeFunctions import initDB
from gamez.PluginManager import PluginManager

from gamez import common, Logger
from gamez.Logger import *

from optparse import OptionParser

from gamez import GameTasks

# Fix for correct path
if hasattr(sys, 'frozen'):
    app_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

os.chdir(app_path)

gamez.PROGDIR = app_path
gamez.CACHEPATH = os.path.join(app_path, gamez.CACHEDIR)
if not os.path.exists(gamez.CACHEDIR):
    os.mkdir(gamez.CACHEDIR)


class RunApp():

    def RunWebServer(self):
        log.info("Generating CherryPy configuration")
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
                    log("Create a new HTTPS Certification") 
                else:
                    log("HTTPS Certification exist")

                conf_https= {
                           'engine.autoreload.on':    False,
                           'server.ssl_certificate':  https_crt,
                           'server.ssl_private_key':  https_key
                            }
                cherrypy.config.update(conf_https)
             except:
                    log.warning("!!!!!!!! Unable to activate HTTPS support !!!!!!!!!! Perhaps you have forgotten to install openssl?")
                    SYSTEM.c.https = False
        """
        # Workoround for OSX. It seems have problem wit the autoreload engine
        if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
            cherrypy.config.update({'engine.autoreload.on': False})

        log.info("Setting up download scheduler")
        gameTasksScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runSearcher, common.SYSTEM.c.interval_search * 60, 'Game Searcher')
        gameTasksScheduler.subscribe()
        log.info("Setting up game list update scheduler")
        gameListUpdaterScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runUpdater, common.SYSTEM.c.interval_update * 60, 'Game Updater')
        gameListUpdaterScheduler.subscribe()
        log.info("Setting up folder processing scheduler")
        folderProcessingScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine, runChecker, common.SYSTEM.c.interval_check * 60, 'Check Downloads')
        folderProcessingScheduler.subscribe()
        log.info("Starting the Gamez web server")
        cherrypy.tree.mount(WebRoot(app_path), config=conf)
        cherrypy.server.socket_host = common.SYSTEM.c.socket_host
        try:
            cherrypy.log.screen = False
            cherrypy.engine.start()
            log.info("Gamez web server running")
            cherrypy.engine.block()
        except KeyboardInterrupt:
            log.info("Shutting down Gamez")
            sys.exit()


def runUpdater():
    GameTasks.updateGames()


def runSearcher():
    GameTasks.runSearcher()


def runChecker():
    GameTasks.runChecker()


# taken from Sick-Beard
# https://github.com/midgetspy/Sick-Beard/
# i dont know how this works but is does wokr pretty well !
def daemonize():
    """
    Fork off as a daemon
    """

    # pylint: disable=E1101
    # Make a non-session-leader child process
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("1st fork failed: %s [%d]" % (e.strerror, e.errno))

    os.setsid()  # @UndefinedVariable - only available in UNIX

    # Make sure I can read my own files and shut out others
    prev = os.umask(0)
    os.umask(prev and int('077', 8))

    # Make the child a session-leader by detaching from the terminal
    try:
        pid = os.fork()  # @UndefinedVariable - only available in UNIX
        if pid != 0:
            sys.exit(0)
    except OSError, e:
        raise RuntimeError("2nd fork failed: %s [%d]" % (e.strerror, e.errno))

    dev_null = file('/dev/null', 'r')
    os.dup2(dev_null.fileno(), sys.stdin.fileno())


def cmd():
    usage = "usage: %prog [-options] [arg]"
    p = OptionParser(usage=usage)
    p.add_option('-d', '--daemonize', action = "store_true",
                 dest = 'daemonize', help = "Run the server as a daemon")
    p.add_option('-D', '--debug', action = "store_true",
                 dest = 'debug', help = "Debug Log to screen")
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

    # Daemonize
    if options.daemonize:
        if sys.platform == 'win32':
            print "Daemonize not supported under Windows, starting normally"
        else:
            print "------------------- Preparing to run in daemon mode (screen logging is now OFF) -------------------"
            log.info("Preparing to run in daemon mode")
            Logger.cLogger.setLevel(logging.CRITICAL)
            daemonize()

    # Debug
    if options.debug:
        print "------------------- Gamez Debug Messages ON -------------------"
        Logger.cLogger.setLevel(logging.DEBUG)
        log.info('Gamez Debug mode ON')

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
        log("Plugin %s loaded successfully" % plugin.name)

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
