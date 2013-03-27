import datetime
import gamez


import json
import logging
import logging.handlers
import inspect
from jsonHelper import MyEncoder


lvlNames = {logging.ERROR:          {'c': '   ERROR', 'p': 'ERROR'},
                logging.WARNING:    {'c': ' WARNING', 'p': 'WARING'},
                logging.INFO:       {'c': '    INFO', 'p': 'INFO'},
                logging.DEBUG:      {'c': '   DEBUG', 'p': 'DEBUG'},
                logging.CRITICAL:   {'c': 'CRITICAL', 'p': 'CRITICAL'}
                }


cLogger = logging.getLogger('Gamez.Console')
fLogger = logging.getLogger('Gamez.File')
cLogger.setLevel(logging.INFO)
fLogger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.handlers.RotatingFileHandler('gamez.log', maxBytes=10 * 1024 * 1024, backupCount=5)
# create console handler with a higher log level
ch = logging.StreamHandler()

# add the handlers to logger
cLogger.addHandler(ch)
fLogger.addHandler(fh)
""" at some point i want the cherrypy stuff logged
cpLogger = logging.getLogger('cherrypy')
cph = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s| %(asctime)s: %(message)s ')
cph.setFormatter(formatter)
cpLogger.addHandler(cph)
"""


class StructuredMessage(object):
    def __init__(self, lvl, message, calframe, **kwargs):
        self.lvl = lvl
        self.message = message
        self.calframe = calframe
        self.kwargs = kwargs
        self.time = datetime.datetime.now()

    def console(self):
        return '%s| %s: %s' % (lvlNames[self.lvl]['c'], self.time, self.message)

    def __str__(self):
        return json.dumps({'time': self.time,
                           'lvl': lvlNames[self.lvl]['p'],
                            'msg': self.message,
                            'caller': {'file': self.calframe[2][1], 'line': self.calframe[2][2], 'fn': self.calframe[2][3]},
                            'data': self.kwargs}, cls=MyEncoder)


class LogWrapper():

    def _log(self, lvl, msg, **kwargs):
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        sm = StructuredMessage(lvl, msg, calframe, **kwargs)
        cLogger.log(lvl, sm.console())
        fLogger.log(lvl, sm)

    def error(self, msg, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def info(self, msg, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def debug(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def critical(self, msg, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)

    def __call__(self, msg, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

log = LogWrapper()


__all__ = ['log']
