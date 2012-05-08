import os
import re
import webbrowser

def replace_all(text):
    dic = {'...':'', ' & ':' ', ' = ': ' ', '?':'', '$':'s', ' + ':' ', '"':'', ',':'', '*':'', '.':'', ':':'', "'":''}	
    for i, j in dic.iteritems():
       text = text.replace(i, j)
    return text

# form couchpotato
def launchBrowser(host, port):

    if host == '0.0.0.0':
        host = 'localhost'

    url = 'http://%s:%d' % (host, int(port))
    try:
        webbrowser.open(url, 2, 1)
    except:
        try:
            webbrowser.open(url, 1, 1)
        except:
            log.error('Could not launch a browser.')

def FindAddition(title):
    dic = {'PAL', 'USA', 'NSTC', 'JAP', 'Region Free', 'RF', 'FRENCH', 'ITALIAN', 'GERMAN', 'SPANISH', 'ASIA', 'JTAG', 'XGD3', 'WiiWare', 'WiiVC', 'Mixed'}
    regionword = ""
    for word in dic:
          if word.upper() in title:
             regionword = regionword + " (" + word + ")" 
          if word.lower() in title:
             regionword = regionword + " (" + word + ")" 
    return regionword
