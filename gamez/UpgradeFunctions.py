
from Logger import LogEvent
import gamez
from classes import *
from classes import __all__ as allClasses
from gamez import common, classes
from gamez.Logger import DebugLogEvent

"""
def CheckForNewVersion(app_path):
    LogEvent("Checking to see if a new version is available")
    newVersionAvailable = False
    currentVersion = VersionNumber()
    mostRecentVersion = GetLatestVersion()
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    isToDeferUpgrade = config.get('SystemGenerated','is_to_ignore_update').replace('"','')
    ignoredVersion = config.get('SystemGenerated','ignored_version').replace('"','')
    if(LooseVersion(mostRecentVersion) > LooseVersion(currentVersion)):
        if(isToDeferUpgrade == '0'):
            newVersionAvailable = True
    if(isToDeferUpgrade == '1'):
        if(LooseVersion(mostRecentVersion) > LooseVersion(ignoredVersion)):
            newVersionAvailable = True
    return newVersionAvailable

def GetLatestVersion():
    LogEvent("Retrieving the latest version")
    mostRecentVersion = '0.0.0.0'
    url = 'https://api.github.com/repos/avjui/Gamez/tags'
    opener = urllib.FancyURLopener({})
    responseObject = opener.open(url)
    response = responseObject.read()
    responseObject.close()
    jsonObject = json.loads(response)
    for val in jsonObject:
        name = val['name']
        tagVersion = name.replace("v","").replace("'","")
        tagVersion = str(tagVersion)
        try:
            if(LooseVersion(tagVersion) > LooseVersion(mostRecentVersion)):
                mostRecentVersion = tagVersion
        except:
            continue
    return mostRecentVersion

def IgnoreVersion(app_path):
    LogEvent("Ignoring Version")
    versionToIgnore = GetLatestVersion()
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    if(config.has_section('SystemGenerated') == False):
        config.add_section('SystemGenerated')
    config.set('SystemGenerated','is_to_ignore_update','1')
    config.set('SystemGenerated','ignored_version','"' + versionToIgnore + '"')
    with open(configfile,'wb') as configFile:
        config.write(configFile)

def UpdateToLatestVersion(app_path):
    LogEvent("Updating to latest version")
    filesToIgnore = ["Gamez.ini","Gamez.db"]
    filesToIgnoreSet     = set(filesToIgnore)
    updatePath = os.path.join(app_path,"update")
    if not os.path.exists(updatePath):     
        os.makedirs(updatePath)
    latestVersion = GetLatestVersion()
    tagUrl = "https://github.com/avjui/Gamez/tarball/TheGamedb/v" + latestVersion
    LogEvent("Downloading from GitHub")
    data = urllib2.urlopen(tagUrl)
    downloadPath = os.path.join(app_path,data.geturl().split('/')[-1])
    downloadedFile = open(downloadPath,'wb')
    downloadedFile.write(data.read())
    downloadedFile.close()
    LogEvent("Extracting files")
    tarredFile = tarfile.open(downloadPath)
    tarredFile.extractall(updatePath)
    tarredFile.close()
    os.remove(downloadPath)
    LogEvent("Upgrading files")
    contentsDir = [x for x in os.listdir(updatePath) if os.path.isdir(os.path.join(updatePath, x))]
    updatedFilesPath = os.path.join(updatePath,contentsDir[0])
    for dirname, dirnames, filenames in os.walk(updatedFilesPath):
        dirname = dirname[len(updatedFilesPath)+1:]
        for file in filenames:
            src = os.path.join(updatedFilesPath,dirname,file)
            dest = os.path.join(app_path,dirname,file)
            if((file in filesToIgnoreSet) == True):
                continue
            if(os.path.isfile(dest)):
                os.remove(dest)
            os.renames(src,dest)
    shutil.rmtree(updatePath) 
    config = ConfigParser.RawConfigParser()
    configfile = os.path.abspath(gamez.CONFIG_PATH)
    config.read(configfile)
    if(config.has_section('SystemGenerated') == False):
        config.add_section('SystemGenerated')
    config.set('SystemGenerated','is_to_ignore_update','0')
    config.set('SystemGenerated','ignored_version','"versionToIgnore"')
    with open(configfile,'wb') as configFile:
        config.write(configFile)
    LogEvent("Upgrading complete")
    return "Successfully Upgraded to Version " + latestVersion
"""


def initDB():
    gamez.DATABASE.init(gamez.DATABASE_PATH)

    #classes = (Game, Platform, Status, Config, Download)
    classes = []
    for cur_c_name in allClasses:
        cur_c = globals()[cur_c_name]
        DebugLogEvent("Checking %s table" % cur_c.__name__)
        cur_c.create_table(True)
        classes.append(cur_c)

    migration_was_done = False
    for cur_c in classes:
        if cur_c.updateTable():
            migration_was_done = True
        DebugLogEvent("Selecting all of %s" % cur_c.__name__)
        try:
            cur_c.select().execute()
        except: # the database structure does not match the classstructure
            LogEvent("\n\nFATAL ERROR:\nThe database structure does not match the class structure.\nCheck log.\nOr assume no migration was implemented and you will have to delete your GameZZ.db database file :(")
            exit(1)

    checkDefaults(migration_was_done)
    if not common.WII:
        raise Exception('init went wrong the commons where not set to instances of the db obj')


def checkDefaults(resave=False):

    default_platforms = [{'setter': 'WII',        'alias': 'Nintendo Wii',        'name': 'Wii',      'tgdb_id': 9},
                         {'setter': 'XBOX360',    'alias': 'Microsoft Xbox 360',  'name': 'Xbox 360', 'tgdb_id': 15},
                         {'setter': 'PC',         'alias': 'PC',                  'name': 'PC',       'tgdb_id': 1},
                         {'setter': 'PS3',        'alias': 'Sony Playstation 3',  'name': 'PS3',      'tgdb_id': 12},
                        ]

    default_statuss = [ {'setter': 'WANTED',      'name': 'Wanted',               'hidden': False},
                        {'setter': 'SNATCHED',    'name': 'Snatched',             'hidden': False},
                        {'setter': 'DOWNLOADED',  'name': 'Downloaded',           'hidden': False},
                        {'setter': 'COMPLETED',   'name': 'Completed',            'hidden': True},
                        {'setter': 'FAILED',      'name': 'Failed',               'hidden': True},
                        {'setter': 'PP_FAIL',     'name': 'Post Processing Fail', 'hidden': True},
                        {'setter': 'UNKNOWN',     'name': 'Unknown',              'hidden': True},
                        {'setter': 'DELETED',     'name': 'Deleted',              'hidden': True}
                      ]

    #create default Platforms
    #http://wiki.thegamesdb.net/index.php?title=GetPlatformsList
    #move this to common.py
    for cur_p in default_platforms:
        try:
            p = Platform.get(Platform.name == cur_p['name'])
            setattr(common, cur_p['setter'], p)
            if not resave:
                continue
        except Platform.DoesNotExist:
            p = Platform()
        p.name = cur_p['name']
        p.alias = cur_p['alias']
        p.tgdb_id = cur_p['tgdb_id']
        p.save()
        setattr(common, cur_p['setter'], p)

    #create default Status
    for cur_s in default_statuss:
        try:
            s = Status.get(Status.name == cur_s['name'])
            setattr(common, cur_s['setter'], s)
            if not resave:
                continue
        except Status.DoesNotExist:
            s = Status()

        s.name = cur_s['name']
        s.hidden = cur_s['hidden']
        s.save(True) # the save function is overwritten to do nothing but when we create it we send a overwrite
        setattr(common, cur_s['setter'], s)
