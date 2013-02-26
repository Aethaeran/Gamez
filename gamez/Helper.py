import os
import re
import webbrowser

def replace_all(text):
    dic = {'...':'', ' & ':' ', ' = ': ' ', '?':'', '$':'s', ' + ':' ', '"':'', ',':'', '*':'', '.':'', ':':'', "'":''}	
    for i, j in dic.iteritems():
       text = text.replace(i, j)
    return text

# form couchpotato
def launchBrowser(host, port,https):


    if host == '0.0.0.0':
        host = 'localhost'

    if(https == '1'):
        url = 'https://%s:%d' % (host, int(port))
    else:
        url = 'http://%s:%d' % (host, int(port))
    try:
        webbrowser.open(url, 2, 1)
    except:
        try:
            webbrowser.open(url, 1, 1)
        except:
            LogEvent('Could not launch a browser.')

def FindAddition(title):
    additionlist = ['PAL', 'USA', 'NSTC', 'JAP', 'Region Free', 'RF', 'FRENCH', 'ITALIAN', 'GERMAN', 'SPANISH', 'ASIA', 'JTAG', 'XGD3', 'WiiWare', 'WiiVC', 'Mixed']
    regionword = ""
    for word in additionlist:
          if word.upper() in title:
             regionword = regionword + " (" + word + ")" 
          if word.lower() in title:
             regionword = regionword + " (" + word + ")" 
    return regionword

# looks if adress contain https

def ControlHost(host):
    
    if 'https' in host:
        checkedhost = host
    elif 'http' in host:
        checkedhost = host
    else:
        checkedhost = "http://" + host
    
    return checkedhost

def findGamezID(s):
    m = re.search("\((G.(?P<id>\d+))\)", s)
    if m and m.group('id'):
        return int(m.group('id'))
    return 0


# Code from Sickbeard
def create_https_certificates(ssl_cert, ssl_key):
    """
    Create self-signed HTTPS certificares and store in paths 'ssl_cert' and 'ssl_key'
    """
    try:
        from OpenSSL import crypto
        from lib.certgen import createKeyPair, createCertRequest, createCertificate, TYPE_RSA, serial
    except ImportError:
        LogEvent("pyopenssl module missing, please install for https access")
        return False

    # Create the CA Certificate
    cakey = createKeyPair(TYPE_RSA, 1024)
    careq = createCertRequest(cakey, CN='Certificate Authority')
    cacert = createCertificate(careq, (careq, cakey), serial, (0, 60*60*24*365*10)) # ten years

    cname = 'Gamez'
    pkey = createKeyPair(TYPE_RSA, 1024)
    req = createCertRequest(pkey, CN=cname)
    cert = createCertificate(req, (cacert, cakey), serial, (0, 60*60*24*365*10)) # ten years

    # Save the key and certificate to disk
    try:
        open(ssl_key, 'w').write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        open(ssl_cert, 'w').write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    except:
        DebugLogEvent("Error creating SSL key and certificate")
        return False

    return True
