import os
import gamez
import time


def LogEvent(message):
    LogToFile(message)
    LogToScreen(message)
    return


def DebugLogEvent(message):

    message = "DEBUG : " + message
    LogToFile(message)
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
