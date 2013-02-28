import os
import sys
import shutil
import urllib
import urllib2
import ConfigParser

import gamez

from gamez.Logger import LogEvent, DebugLogEvent
import DBFunctions



#Postproccessing for Downloaded Games
#Fisrt we get Details from TheGamesdb.net
#
#               Notice! 
#  At the moment this only has a function
#  for Games how scraped from TheGamesdb.net 

def PostProcess(dbid, game_name):

    # First define some varaibles
    #term = ""
    tagnbr = int("0")
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    sabnzbd_complet = config.get('Sabnzbd', 'folder').replace('"', '')
    sabnzbd_folder = os.path.abspath(sabnzbd_complet)
    game_title = game_name

    system = DBFunctions.GetRequestedGameSystem(dbid)
    TheGamesDB_id = DBFunctions.GetRequestedTheGamesDBid(dbid)

    # Search for Gamefolder

    gamelist = os.listdir(sabnzbd_folder)
    return
   


# This writes a nfo file to the Downloaded folder
# Notice! At the moment only Sabnzbd is supportet

def WriteMeta(gamefoldername,game_title='',game_system='',game_description='',game_publisher='',game_developer='',game_genre='',game_release=''):

    try:
        filename = game_title.lower() + ".nfo"
        nfofile = os.path.join(os.path.abspath(gamefoldername),filename)
        file = open(nfofile,'w')
        file.write('<game>')
        file.write("\n")
        file.write('     <title>' + str(game_title) + '</title>')
        file.write("\n")
        file.write('     <platform>' + str(game_system) + '</platform>')
        file.write("\n")
        file.write('     <year>' + str(game_release) + '</year>')
        file.write("\n")
        file.write('     <plot>' + str(game_description) + '</plot>')
        file.write("\n")
        file.write('     <publisher>' + str(game_publisher) + '</publisher>')
        file.write("\n")
        file.write('     <developer>' + str(game_developer) + '<developer>')
        file.write("\n")
        file.write('     <genre>' + str(game_genre) + '</genre>')
        file.write("\n")
        file.write('</game>')
        file.close
        LogEvent("Writing of NFO file succses")
    except:
        LogEvent("ERROR: !!!!!!NFO File writing faild!!!!!!")

# This saves the Images to the Downloaded folder
# Notice! Not Implemet yet

def SaveArt(gamefoldername, TheGamesDB_id):
    
    boxartfile = os.path.join(os.path.abspath(gamefoldername),'folder.jpg')
    fanartfile = os.path.join(os.path.abspath(gamefoldername),'fanart.jpg')
    bannerfile = os.path.join(os.path.abspath(gamefoldername),'banner.jpg')
    logofile = os.path.join(os.path.abspath(gamefoldername),'logo.png')


# This will rename and remove the folder
# Notice! This is at the moment experimental

def RenameAndMoveFolder(srcFoldername, destFoldernam, game_system):
    
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    
    if(game_system == "PS3"):
        destfolder = config.get('Folders','ps3_destination').replace('"','')
        system = "ps3"
    if(game_system == "PC"):
        destfolder = config.get('Folders','pc_destination').replace('"','')
        system = "pc"
    if(game_system == "Wii"):
        destfolder = config.get('Folders','wii_destination').replace('"','')
        system = "wii"
    if(game_system == "Xbox360"):
        destfolder = config.get('Folders','xbox360_destination').replace('"','')
        system = "xbox360"
    
    systempostprocessenable = "process_download_folder_" + system + "_enable"
    if(systempostprocessenable):
        destpath = os.path.join(destfolder, destFoldernam)
        try:
            DebugLogEvent("Move from [" + str(srcFoldername) + "] to [" + str(destpath) + "]")
            os.renames(srcFoldername, destpath)
            LogEvent("Renaming and moving succses")
        except:
            LogEvent("ERROR: Directory [" + destpath + "]must be writeable!!!!!")


