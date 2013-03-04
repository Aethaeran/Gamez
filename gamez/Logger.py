import os
import ConfigParser
import gamez
import time


def LogEvent(message):
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)

    if(config.get('global', 'logfile_enabled').replace('"', '') == "1"):
        LogToFile(message)
    if(config.get('global', 'log_to_screen').replace('"', '') == "1"):
        LogToScreen(message)

    return


def DebugLogEvent(message):
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    message = "DEBUG : " + message

    if(config.get('global', 'debug_enabled').replace('"', '') == "1"):
        if(config.get('global', 'logfile_enabled').replace('"', '') == "1"):
            LogToFile(message)
        if(config.get('global', 'log_to_screen').replace('"', '') == "1"):
            LogToScreen(message)
    return


def LogToScreen(message):
    createdDate = time.strftime("%a %d %b %Y / %X", time.localtime()) + ": "
    print createdDate + message


def LogToFile(message):
    createdDate = time.strftime("%a %d %b %Y / %X", time.localtime()) + ": "
    try:
        # This tries to open an existing file but creates a new file if necessary.
        logfile = open("gamez_log.log", "a")
        try:
            logfile.write(createdDate + message + "\n")
        finally:
            logfile.close()
    except IOError:
            pass


__all__ = ['LogEvent', 'DebugLogEvent']
