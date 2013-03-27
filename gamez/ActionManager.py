import os
import sys
import cherrypy
import traceback
from gamez.Logger import *

ACTIONS = ['reboot', 'hardReboot']


def executeAction(action, callers):
    print type(action).__name__ == 'function'
    if not action in ACTIONS and not type(action).__name__ == 'function':
        log.warning("There is no action %s. Called from %s" % (action, callers))
        return False

    log.info("Executing actions '%s'. Called from %s" % (action, callers))
    if action == 'reboot':
        cherrypy.engine.restart()
    elif action == 'hardReboot':
        hardReboot()
    else:
        for caller in callers:
            _callMethod(caller, action)


def _callMethod(o, function):
    try:
        getattr(o, function.__name__)()
    except Exception as ex:
        tb = traceback.format_exc()
        log.error("Error during %s of %s \nError: %s\n\n%s" % (o.name, function.__name__, ex, tb))


def hardReboot():
    # this should not be here ... because its very strong and should not be in the plugin manager
    # how will it react to a .exe ?
    # how will it to an .app ?
    """Restarts the current program.
    Note: this function does not return. Any cleanup action (like
    saving data) must be done before calling this function."""
    log.info("Doing a hard REBOOT!!")
    python = sys.executable
    os.execl(python, python, * sys.argv)
