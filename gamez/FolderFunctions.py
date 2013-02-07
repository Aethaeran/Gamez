from Logger import *
import os
from DBFunctions import GetRequestedGameName, GetRequestedGameSystem, UpdateStatus
import shutil
import ConfigParser
import gamez
import re
import fnmatch

def ApiUpdateRequestedStatus(db_id, status, path, outLog=False):
    DebugLogEvent("DB ID [ " + db_id + " ] and Status [ " + status + " ]")
    out = ProcessDownloaded(db_id, status, path)
    UpdateStatus(db_id,status)
    if not outLog:
        out = '["RequestedStatus":{"' + status + '"}]'
    return out


def ProcessDownloaded(game_id,status,filePath):
    if not game_id:
        return
    game_name = GetRequestedGameName(game_id)
    system = GetRequestedGameSystem(game_id)
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    destPath = ""
    if(system == "Wii"):
        if(config.get('SystemGenerated','process_download_folder_wii_enabled').replace('"','') == "0"):
            LogEvent("Skipping Post Processing because settings is to not post process Wii downloads")
            return
        destPath = config.get('Folders','wii_destination').replace('"','')
    elif(system == "Xbox360"):
        if(config.get('SystemGenerated','process_download_folder_xbox360_enabled').replace('"','') == "0"):
            LogEvent("Skipping Post Processing because settings is to not post process Xbox360 downloads")
            return
        destPath = config.get('Folders','xbox360_destination').replace('"','')
    
    elif(system == "PS3"):
        if(config.get('SystemGenerated','process_download_folder_ps3_enabled').replace('"','') == "0"):
            LogEvent("Skipping Post Processing because settings is to not post process ps3 downloads")
            return
        destPath = config.get('Folders','ps3_destination').replace('"','')

    elif(system == "PC"):
        if(config.get('SystemGenerated','process_download_folder_pc_enabled').replace('"','') == "0"):
            LogEvent("Skipping Post Processing because settings is to not post process pc downloads")
            return
        destPath = config.get('Folders','pc_destination').replace('"','')

    if not destPath:
        LogEvent("Destination Folder Not Set")
        return False

    replaceSpace = " "
    if(config.get('SystemGenerated','process_filename_replace_space').replace('"','')):
        replaceSpace = config.get('SystemGenerated','process_filename_replace_space').replace('"','')
    DebugLogEvent("replaceSpace with: '" + replaceSpace + "'")

    if(destPath.endswith(os.sep) == False):
            destPath = destPath + os.sep
    if not os.path.isdir(destPath):
        LogEvent("Destination Folder Not Created. and i am not doing it :P")
        return False

    # log of the whole process routine from here on except debug
    # this looks hacky: http://stackoverflow.com/questions/7935966/python-overwriting-variables-in-nested-functions
    processLog = [""]

    def processLogger(message):
        LogEvent(message)
        createdDate = time.strftime("%a %d %b %Y / %X", time.localtime()) + ": "
        processLog[0] = processLog[0] + createdDate + message + "\n"

    def fixName(name, replaceSpace):
        return re.sub(r'[\\/:"*?<>|]+', "", name.replace(" ", replaceSpace))

    if(filePath.endswith(os.sep) == False):
        filePath = filePath + os.sep

    # gather all images -> .iso and .img
    allImageLocations = []
    for root, dirnames, filenames in os.walk(filePath):
        for filename in fnmatch.filter(filenames, '*.iso') + fnmatch.filter(filenames, '*.img'):
            curImage = os.path.join(root, filename)
            allImageLocations.append(curImage)
            processLogger("Found image: " + curImage)

    processLogger("Renaming and Moving Game")
    success = True
    allImageLocations.sort()
    for index, curFile in enumerate(allImageLocations):
        processLogger("Processing image: " + curFile)
        try:
            extension = os.path.splitext(curFile)[1]
            if len(allImageLocations) > 1:
                newFileName = game_name + " CD" + str(index + 1) + extension
            else:
                newFileName = game_name + extension
            newFileName = fixName(newFileName, replaceSpace)
            processLogger("New Filename shall be: " + newFileName)
            dest = destPath + newFileName
            processLogger("Moving File from: " + curFile + " to: " + dest)
            shutil.move(curFile, dest)
        except Exception, msg:
            processLogger("Unable to rename and move game: " + curFile + ". Please process manually")
            processLogger("given ERROR: " + msg)
            success = False

    processLogger("File processing done")
    # write process log
    logFileName = fixName(game_name + ".log", replaceSpace)
    logFilePath = destPath + logFileName
    try:
        # This tries to open an existing file but creates a new file if necessary.
        logfile = open(logFilePath, "a")
        try:
            logfile.write(processLog[0])
        finally:
            logfile.close()
    except IOError:
            pass

    if success:
        return processLog[0]
    else:
        return ""

def ScanFoldersToProcess():
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    processSabFolder = config.get('SystemGenerated','process_sabnzbd_download_folder_enabled').replace('"','')
    processNzbFolder = config.get('SystemGenerated','process_nzb_download_folder_enabled').replace('"','')
    processTorrentFolder = config.get('SystemGenerated','process_torrent_download_folder_enabled').replace('"','')
    sabFolder = config.get('Folders','sabnzbd_completed').replace('"','').replace("\\\\","\\")
    nzbFolder = config.get('Folders','nzb_completed').replace('"','').replace("\\\\","\\")
    torrentFolder = config.get('Folders','torrent_completed').replace('"','').replace("\\\\","\\")
    if(processSabFolder == "1"):
        ProcessFolder(sabFolder)
    if(processNzbFolder == "1"):
        ProcessFolder(nzbFolder)
    if(processTorrentFolder == "1"):
        ProcessFolder(torrentFolder)
    return

def ProcessFolder(folderPath):
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    for subdir,dirs,files in os.walk(folderPath):
        for file in files:
            moveFile = False
            if ".iso" in file or ".img" in file:
                LogEvent("Image Found: " + file + ". Trying to match to a valid requested game")
                processFile = False
                game_name = ""
                system = ""
                for record in GetRequestedGamesForFolderProcessing():
                    game_name = record[0]
                    system = record[1]
                    LogEvent("Trying to match on Game Name: " + game_name)
                    allPartsMatched = True
                    for gameNamePart in game_name.split(" "):
                        if gameNamePart.upper() not in subdir.upper() and gameNamePart.upper() not in file.upper():
                            allPartsMatched = False
                    if(allPartsMatched):
                        processFile = True
                        break
                if(processFile):
                    if(CheckForSameGame(game_name)):
                        processForWii = False
                        processForXbox360 = False
                        processForPsThree = False
                        processForPC = False 			
                        if("WII" in subdir.upper() or "WII" in file.upper()):
                            processForWii = True
                        if("XBOX360" in subdir.upper() or "XBOX360" in file.upper() or "360" in subdir.upper() or "360" in file.upper()):
                            processForXbox360 = True
                        if("PS3" in subdir.upper() or "PS3" in file.upper()):
                            processForWii = True
                        if("PC" in subdir.upper() or "PC" in file.upper()):
                            processForWii = True							
                        if(processForWii):
                            system = "Wii"
                            moveFile = True
                        elif(processForXbox360):
                            system = "Xbox360"
                            moveFile = True
                        elif(processForPsThree):
                            system = "PS3"
                            moveFile = True
                        elif(processForPC):
                            system = "PC"
                            moveFile = True
                        else:
                            LogEvent("Same game name found for multiple systems and unable to parse system from file name. Skipping Image File")
                    else:
                        moveFile = True
                else:
                    LogEvent("No Match Found. Skipping Image File")
                if(moveFile):
                    LogEvent("Match Found. Renaming and Moving [" + system + "] Game")
                    destPath = ""
                    if(system == "Wii"):
                        if(config.get('SystemGenerated','process_download_folder_wii_enabled').replace('"','') == "0"):
                            LogEvent("Skipping Post Processing because settings is to not post process Wii downloads")
                            return
                        destPath = config.get('Folders','wii_destination').replace('"','').replace("\\\\","\\")
                    elif(system == "Xbox360"):
                        if(config.get('SystemGenerated','process_download_folder_xbox360_enabled').replace('"','') == "0"):
                            LogEvent("Skipping Post Processing because settings is to not post process Xbox360 downloads")
                            return
                        destPath = config.get('Folders','xbox360_destination').replace('"','').replace("\\\\","\\")
                    elif(system == "PS3"):
                        if(config.get('SystemGenerated','process_download_folder_ps3_enabled').replace('"','') == "0"):
                            LogEvent("Skipping Post Processing because settings is to not post process PS3 downloads")
                            return
                        destPath = config.get('Folders','ps3_destination').replace('"','').replace("\\\\","\\")
                    elif(system == "Xbox360"):
                        if(config.get('SystemGenerated','process_download_folder_pc_enabled').replace('"','') == "0"):
                            LogEvent("Skipping Post Processing because settings is to not post process PC downloads")
                            return
                        destPath = config.get('Folders','pc_destination').replace('"','').replace("\\\\","\\")
                    #Copy File
                    if(destPath <> ""):
                        if(destPath.endswith(os.sep) == False):
                            destPath = destPath + os.sep
                        extension = os.path.splitext(file)[1]
                        newFileName = game_name + extension
                        dest = destPath + os.sep + newFileName
                        src = subdir + os.sep + file
                        LogEvent("Moving File " + src + " to " + dest)
                        try:
                            shutil.move(src,dest)
                            #Update status to wanted
                            if(game_name <> "" and system <> ""):
                                UpdateStatusForFolderProcessing(game_name,system,'Downloaded')
                        except:
                            LogEvent("Error Moving File")
                        LogEvent(game_name + " Processed Successfully")
                    else:
                        LogEvent("Destination Folder Not Set")
    return