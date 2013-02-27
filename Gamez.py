#!/usr/bin/env python
import traceback

import cherrypy
import os
import sys
import socket
import sched
import time
import threading
import thread
import datetime
import gamez.GameTasks
import ConfigParser
import cherrypy.process.plugins
from cherrypy.process.plugins import Daemonizer,PIDFile
from cherrypy import server
from gamez.WebRoot import WebRoot
from gamez.ConfigFunctions import CheckConfigForAllKeys
from gamez.DBFunctions import ValidateDB,AddWiiGamesIfMissing,AddXbox360GamesIfMissing,AddComingSoonGames,ClearDBLog
from gamez.Logger import LogEvent
from gamez.Helper import launchBrowser,create_https_certificates
import cherrypy.lib.auth_basic
from gamez.FolderFunctions import *
import gamez

# Fix for correct path
if hasattr(sys, 'frozen'):
    app_path = os.path.dirname(os.path.abspath(sys.executable))
else:
    app_path = os.path.dirname(os.path.abspath(__file__))

gamez.PROGDIR = app_path

class RunApp():


    def RunWebServer(self):
        LogEvent("Generating CherryPy configuration")
        cherrypy.config.update(gamez.CONFIG_PATH)
        config = ConfigParser.RawConfigParser()
        config.read(gamez.CONFIG_PATH)
        # Set Webinterface Path
        css_webinterface = "css/" + config.get('SystemGenerated','webinterface').replace('"','')
        css_path = os.path.join(app_path,css_webinterface)
        
        images_path = os.path.join(app_path,'css/images')
        navigation_images_path = os.path.join(css_path,'navigation_images')
        datatables_images_path = os.path.join(css_path,'datatables_images')
        js_path = os.path.join(app_path,'css/js')
        theme_path = os.path.join(css_path,'redmond')
        theme_images_path = os.path.join(theme_path,'images')
        username = config.get('global','user_name').replace('"','')
        password = config.get('global','password').replace('"','')
        https_support_enabled = config.get('SystemGenerated','https_support_enabled').replace('"','')
        https_crt = app_path + "/gamez.crt"
        https_key = app_path + "/gamez.key"
       
        useAuth = False
        if(username <> "" or password <> ""):
            useAuth = True          	
        userPassDict = {username:password}  
        checkpassword = cherrypy.lib.auth_basic.checkpassword_dict(userPassDict)
        conf = {
        	  '/':{'tools.auth_basic.on':useAuth,'tools.auth_basic.realm':'Gamez','tools.auth_basic.checkpassword':checkpassword},
                '/api':{'tools.auth_basic.on':False},
                '/css': {'tools.staticdir.on':True,'tools.staticdir.dir':css_path},
                '/js':{'tools.staticdir.on':True,'tools.staticdir.dir':js_path},
                '/css/redmond':{'tools.staticdir.on':True,'tools.staticdir.dir':theme_path},
                '/css/redmond/images':{'tools.staticdir.on':True,'tools.staticdir.dir':theme_images_path},
                '/css/navigation_images':{'tools.staticdir.on':True,'tools.staticdir.dir':navigation_images_path},
                '/css/datatables_images':{'tools.staticdir.on':True,'tools.staticdir.dir':datatables_images_path},
                '/images':{'tools.staticdir.on':True,'tools.staticdir.dir':images_path},
                '/favicon.ico':{'tools.staticfile.on':True,'tools.staticfile.filename':"images/favicon.ico"},
               }
        
        # Https Support
        if(https_support_enabled == "1"):

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
                    config.set('SystemGenerated','https_support_enabled',"0")

        # Workoround for OSX. It seems have problem wit the autoreload engine
        if sys.platform.startswith('darwin') or sys.platform.startswith('win'):
             cherrypy.config.update({'engine.autoreload.on':    False,})
     
        RunGameTask()

        LogEvent("Getting download interval from config file and invoking scheduler")
        interval = config.get('Scheduler','download_interval').replace('"','')
        updateGameListInterval = config.get('Scheduler','game_list_update_interval').replace('"','')
        # Turn in Minutes
        fInterval = float(interval) * 60
        fUpdateGameListInterval = float(updateGameListInterval) * 60
        try:
            LogEvent("Setting up download scheduler")
            gameTasksScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,RunGameTask,fInterval)
            gameTasksScheduler.subscribe()
            LogEvent("Setting up game list update scheduler")
            gameListUpdaterScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,RunGameListUpdaterTask,fUpdateGameListInterval)
            gameListUpdaterScheduler.subscribe()
            LogEvent("Setting up folder processing scheduler")
            folderProcessingScheduler = cherrypy.process.plugins.Monitor(cherrypy.engine,CheckSab,float(180))
            folderProcessingScheduler.subscribe()
            LogEvent("Starting the Gamez web server")
            cherrypy.tree.mount(WebRoot(app_path), config = conf)
            
            cherrypy.engine.start()
            cherrypy.log.screen = False
            cherrypy.engine.block()

        except KeyboardInterrupt:
            LogEvent("Shutting down Gamez")
            if(isToDaemonize == 1):
                daemon.unsubscribe()
            sys.exit()

def RunGameTask():
    try:
        isDebugEnabled = config.get('global','debug_enabled').replace('"','')
        nzbsrusUser = config.get('nzbsrus','username').replace('"','')
        nzbsrusApi = config.get('nzbsrus','api_key').replace('"','')
        nzbsuApi = config.get('NZBSU','api_key').replace('"','')
        sabnzbdHost = config.get('Sabnzbd','host').replace('"','')
        sabnzbdPort = config.get('Sabnzbd','port').replace('"','')
        sabnzbdApi = config.get('Sabnzbd','api_key').replace('"','')
        sabnzbdCategory = config.get('Sabnzbd','category').replace('"','')
        newznabWiiCat = config.get('Newznab','wii_category_id').replace('"','')
        newznabXbox360Cat = config.get('Newznab','xbox360_category_id').replace('"','')
        newznabPS3Cat = config.get('Newznab','ps3_category_id').replace('"','')
        newznabPCCat = config.get('Newznab','pc_category_id').replace('"','')
        newznabApi = config.get('Newznab','api_key').replace('"','')
        newznabHost = config.get('Newznab','host').replace('"','')
        newznabPort = config.get('Newznab','port').replace('"','')
        isSabEnabled = config.get('SystemGenerated','sabnzbd_enabled').replace('"','')
        isnzbsrusEnabled = config.get('SystemGenerated','nzbsrus_enabled').replace('"','')
        isnzbsuEnable = config.get('SystemGenerated','nzbsu_enabled').replace('"','')
        isNewznabEnabled = config.get('SystemGenerated','newznab_enabled').replace('"','')
        isNzbBlackholeEnabled = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        nzbBlackholePath = config.get('Blackhole','nzb_blackhole_path').replace('"','')
        isTorrentBlackholeEnabled = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        isTorrentKATEnabled = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        torrentBlackholePath  = config.get('Blackhole','torrent_blackhole_path').replace('"','')
        retention = config.get('SystemGenerated','retention').replace('"','')
        manualSearchGame = ''
        LogEvent("Searching for games")
        gamez.GameTasks.GameTasks().FindGames(manualSearchGame,nzbsrusUser,nzbsrusApi,sabnzbdApi,sabnzbdHost,sabnzbdPort,newznabWiiCat,newznabApi,newznabHost,newznabPort,newznabXbox360Cat,newznabPS3Cat,newznabPCCat,sabnzbdCategory,isSabEnabled,isnzbsrusEnabled,isNewznabEnabled,isNzbBlackholeEnabled,nzbBlackholePath,isTorrentBlackholeEnabled,isTorrentKATEnabled,torrentBlackholePath,isnzbsuEnable,nzbsuApi,retention)
    except:
        errorMessage = "Major error occured when running scheduled tasks"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)

def RunGameListUpdaterTask():
    try:
        LogEvent("Updating Game Lists")
        AddWiiGamesIfMissing()
        LogEvent("Wii Game List Updated")
        AddXbox360GamesIfMissing()
        LogEvent("XBOX 360 Game List Updated")
        AddComingSoonGames
        LogEvent("Coming Soon Game List Updated")
    except:
        errorMessage = "Major error occured when running Update Game List scheduled tasks"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)

def RunFolderProcessingTask():
    try:
        ProcessFolder()
    except:
        errorMessage = "Error occurred while processing folders"
        for message in sys.exc_info():
            errorMessage = errorMessage + " - " + str(message)
        LogEvent(errorMessage)


def CheckSab():
    try:
        gamez.GameTasks.GameTasks().CheckStatusInSabAndPP()
    except Exception, msg:
        LogEvent(traceback.format_exc())
        LogEvent("Error occurred while checking sab")


def ComandoLine():
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

    config_dir = os.path.abspath(config_path)

    if not os.access(os.path.dirname(config_dir), os.W_OK) and not os.access(config_dir, os.W_OK):
        if not os.path.exists(os.path.dirname(config_dir)):
            os.makedirs(os.path.dirname(config_dir))
        else:
            raise SystemExit("Directory for config file must be writeable")
    
    #Set global variables
    gamez.CONFIG_PATH = config_path
    gamez.DATADIR = datadir

    #Some cheks and Settings
    CheckConfigForAllKeys()
    ValidateDB()
    config = ConfigParser.RawConfigParser()
    config.read(gamez.CONFIG_PATH)

    # Let`s check some options
    # Daemonize
    if options.daemonize:
        print "------------------- Preparing to run in daemon mode -------------------"
        LogEvent("Preparing to run in daemon mode")  
        daemon = Daemonizer(cherrypy.engine)
        daemon.subscribe()
   
    # Debug
    if options.debug:
        config.set('global','debug_enabled','1')
        print "------------------- Gamez run in Debug -------------------"
        LogEvent('Gamez run in Debug')
    
    # Set port
    if options.port:
        print "------------------- Port manual set to " + options.port + " -------------------"
        port = int(options.port)
        server.socket_port = port
    else:
        port = int(config.get('global','gamez_port'))
        server.socket_port = port
	 
    # PIDfile
    if options.pidfile:
        print "------------------- Set PIDfile to " + options.pidfile + " -------------------"
        PIDFile(cherrypy.engine, options.pidfile).subscribe()

    # from couchpotato
    host = config.get('global', 'server.socket_host').replace('"','')
    https = config.get('SystemGenerated','https_support_enabled').replace('"','')
    try:
        if not options.nolaunch:
            print "------------------- launch Browser ( " + str(host) + ":" + str(port) + ") -------------------"
            timer = threading.Timer(5,launchBrowser,[host,port,https])
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
    ComandoLine()
    config = ConfigParser.RawConfigParser()
    configfile = gamez.CONFIG_PATH
    config.read(configfile)
    clearLog = config.get('SystemGenerated','clearlog_at_startup').replace('"','')
    if(clearLog == "1"):
       ClearDBLog()
       LogEvent("Log cleared")
  
    RunApp().RunWebServer()
