import os
import gamez
import time


def LogEvent(message):
    createdDate = time.strftime("[%d/%b/%Y:%X]", time.localtime())
    message = "%s %s" % (createdDate, message)
    LogToFile(message)
    LogToScreen(message)
    return


def DebugLogEvent(message):
    createdDate = time.strftime("[%d/%b/%Y:%X]", time.localtime())
    message = "%s DEBUG : %s" % (createdDate, message)
    LogToFile(message)
    LogToScreen(message)
    return


def LogToScreen(message):
    print message


def LogToFile(message):
    try:
        # This tries to open an existing file but creates a new file if necessary.
        logfile = open("gamez_log.log", "a")
        try:
            logfile.write(message + "\n")
        finally:
            logfile.close()
    except IOError:
            pass


__all__ = ['LogEvent', 'DebugLogEvent']
