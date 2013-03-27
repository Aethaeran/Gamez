<hr />

Gamez is currently in *Alpha* release. There may be bugs in the application.
This a pretty much a complete rewrite of Gamez it now has a ORM(Peewee), template engin(jinja2) and a pluginsystem(no name),
JSON based file logging and human version for the shell.

Gamez is an automated downloader for video games. The user adds the games they wish to download and Gamez will attempt to find the game and download it.

As of the current release, only Wii, Xbox360, PS3 and PC games are supported. 

Current Features:

    * Grep gamedata from TheGamesDB.net
    * Automatically sends NZB's to Sabnzbd
    * Torrents with "black hole" function
    * Plugin system for indexer and downloader and other things
    * Plugins can have multiple instances
    * Boxcar notifications
    * Generic newznab indexer
    * Generic blackwhole downloader

<hr />

***Dependencies***

Gamez requires Python and CherryPY. The CherryPy module is included with Gamez. Python 2.7 or higher must be installed on the system on which Gamez will be ran.

<hr />

***Options***

Gamez has some console options:
     
      *  -p PIDFILE, --pidfile=PIDFILE   Store the process id in the given file
      *  -P PORT,    --port=PORT         Force webinterface to listen on this port
      *  -n,         --nolaunch          Don't start browser
      *  -d,         --daemon            Run in daemon mode (also no log on screen)
      *  -D,         --debug             Debug Log to screen (overwrites the no screen looging by -d)

<hr />