from gamez.Logger import LogEvent
import cherrypy
import traceback


ACTIONS = ['reboot']


def executeAction(action, callers):
    print type(action).__name__ == 'function'
    if not action in ACTIONS and not type(action).__name__ == 'function':
        LogEvent("There is no action %s. Called from %s" % (action, callers))
        return False

    LogEvent("Executing actions '%s'. Called from %s" % (action, callers))
    if action == 'reboot':
        cherrypy.engine.restart()
    else:
        for caller in callers:
            _callMethod(caller, action)


def _callMethod(o, function):
    try:
        getattr(o, function.__name__)()
    except Exception as ex:
        tb = traceback.format_exc()
        LogEvent("Error during %s of %s \nError: %s\n\n%s" % (o.name, function.__name__, ex, tb))
