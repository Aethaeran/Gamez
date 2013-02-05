import ConfigParser
import os
import lib.prowlpy
from Logger import LogEvent,DebugLogEvent
import lib.gntp
import lib.notifo as Notifo
import lib.pynma
from gamez.xbmc.Xbmc import * 
import gamez
import urllib2
import subprocess

def HandleNotifications(status,message,appPath):
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    prowlApi = config.get('Notifications','prowl_api').replace('"','')
    growlHost = config.get('Notifications','growl_host').replace('"','')
    growlPort = config.get('Notifications','growl_port').replace('"','')
    growlPassword = config.get('Notifications','growl_password').replace('"','')
    notifoUsername = config.get('Notifications','notifo_username').replace('"','')
    notifoApi = config.get('Notifications','notifo_apikey').replace('"','')
    nmaApi = config.get('Notifications', 'notifymyandroid_apikey').replace('"','')
    prowlEnabled = config.get('SystemGenerated','prowl_enabled').replace('"','')
    growlEnabled = config.get('SystemGenerated','growl_enabled').replace('"','')
    notifoEnabled = config.get('SystemGenerated','notifo_enabled').replace('"','')
    nmaEnabled = config.get('SystemGenerated', 'notifymyandroid_enabled').replace('"','')
    xbmcEnabled = config.get('SystemGenerated','xbmc_enabled').replace('"','')
    xbmcHosts = config.get('Notifications','xbmc_hosts').replace('"','')
    
    boxcarEnabled = config.get('SystemGenerated','boxcar_enabled').replace('"','')
    boxcarEmail = config.get('Notifications','boxcar_email').replace('"','')

    if(prowlEnabled == "1"):
        if(prowlApi <> ""):
            SendNotificationToProwl(status,message,prowlApi)  
        else:
            LogEvent("Missing Prowl API Key")
            
    if(growlEnabled == "1"):            
        if(growlHost <> ""):
            SendNotificationToGrowl(status,message,growlHost,growlPort,growlPassword)  
        else:
            LogEvent("Growl Settings Incomplete")
    
    if(notifoEnabled == "1"):
        if(notifoUsername <> "" and notifoApi <> ""):
            SendNotificationToNotifo(status,message,notifoUsername,notifoApi)
        else:
            LogEvent("Notifo Settings Incomplete")
    
    if(nmaEnabled == "1"):
        if(nmaApi <> ""):
            SendNotificationToNMA(status, message, nmaApi)
        else:
            LogEvent("NMA Settings Incomplete")
    
    if(xbmcEnabled == "1"):
        if(xbmcHosts <> ""):
            SendNotificationToXbmc(message,appPath,xbmcHosts)
        else:
            LogEvent("XBMC Settings Incomplete. Please add a Host")
             
    if(boxcarEnabled == "1"):
        if(boxcarEmail):
            SendNotificationToBoxcar(message, boxcarEmail)
        else:
            LogEvent("Boxcar Settings Incomplete. Please add an email")
    return
    
def SendNotificationToProwl(status,message,prowlApi):
    prowl = prowlpy.Prowl(prowlApi)
    try:
        prowl.add('Gamez',status,message,1,None,"http://www.prowlapp.com/")
        LogEvent("Prowl Notification Sent")
    except Exception,msg:
        LogEvent("Prowl Notification Error: " + msg)
    return
    
def SendNotificationToGrowl(status,message,growlHost,growlPort,growlPassword):
    if(growlPort == ""):
        growlPort = "23053"
    try:
        growl = lib.gntp.notifier.GrowlNotifier(applicationName = "Gamez",notifications = ["Gamez Download Alert"],defaultNotifications=["Gamez Download Alert"],hostname=growlHost,port=growlPort,password=growlPassword)
        growl.register()
        growl.notify(noteType="Gamez Download Alert",title=message,description=message,sticky=False,priority=1,)
        LogEvent("Growl Notification Sent")
    except Exception,msg:
        LogEvent("Growl Notification Error: " + msg)
    return   
    
def SendNotificationToNotifo(status,message,notifoUsername,notifoApiKey):
    notifoDict = {"to":notifoUsername,"msg":message,"label":"Gamez","title":"Gamez Download Alert"}
    try:
        notifo = Notifo(notifoUsername,notifoApiKey)
        LogEvent("Notifo Response: " + notifo.sendNotification(notifoDict))
    except Exception,msg:
        LogEvent("Growl Notification Error: " + msg)
    return
    
def SendNotificationToXbmc(message,appPath,xbmcHosts):
    try:
        message = str(message)
        xbmcnotify(message,appPath)
        DebugLogEvent("Sending Notification Message to " + xbmcHosts)
    except Exception,msg:
        LogEvent("XBMC Notification Error: " + str(msg))
        return

def SendNotificationToNMA(status, message, nmaApi):
    nma = lib.pynma.PyNMA(nmaApi)
    try:
        nma.push("Gamez", "Game " + status, message)
        LogEvent("NMA Notification Sent")
    except Exception,msg:
        LogEvent("NMA Notification Error: " + str(msg))
        return


def SendNotificationToBoxcar(message, boxcarEmail):
    message = message.replace(" ", "+")

    def curl(*args):
        curl_path = '/usr/bin/curl'
        curl_list = [curl_path]
        for arg in args:
            curl_list.append(arg)
        curl_result = subprocess.Popen(
                     curl_list,
                     stderr=subprocess.PIPE,
                     stdout=subprocess.PIPE).communicate()[0]
        return curl_result
    try:
        #url = 'http://boxcar.io/devices/providers/MH0S7xOFSwVLNvNhTpiC/notifications?notification[from_screen_name]=Gamez&email=%s&notification[message]=%s' % (boxcarEmail, message)
        curl("-d", "email=%s" %boxcarEmail, "-d", "&notification[from_screen_name]=Gamez", "-d", "&notification[message]=%s" %message, "http://boxcar.io/devices/providers/MH0S7xOFSwVLNvNhTpiC/notifications")

    except Exception,msg:
        LogEvent("boxcar Notification Error: " + str(msg))
        return
