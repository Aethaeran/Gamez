from gamez.Logger import DebugLogEvent, LogEvent
from gamez import common
from gamez.classes import Game

def runSearcher():
    DebugLogEvent("running searcher")
    for game in Game.select():
        if game.status != common.WANTED: # for whatever reasons the selcet().where() thing does not work here
            continue
        DebugLogEvent("Looking for %s" % game)
        searchGame(game)


def notify(game):
    for notifier in common.PM.N:
        if notifier.c.on_snatch and game.status == common.SNATCHED:
            notifier.sendMessage("%s has been snatched" % game, game)
        if notifier.c.on_complete and game.status in (common.COMPLETED, common.DOWNLOADED, common.PP_FAIL):
            notifier.sendMessage("%s is now %s" % (game, game.status), game)


def searchGame(game):
    blacklist = common.SYSTEM.getBlacklistForPlatform(game.platform)
    for indexer in common.PM.I:
        downloads = indexer.searchForGame(game)
        downloads = _filterBadDownloads(blacklist, downloads)
        for downloader in common.PM.getDownloaders(types=indexer.types):
            for download in downloads:
                DebugLogEvent("Saving the download we found %s" % download)
                try:
                    download.save(force_insert=True)
                except:
                    # i just want to catch IntegrityError but thats a sqlite thing and i dont want to import that. this occures if we find the same nzb again
                    # i thing peewee should wrapp this and send a DoesExist error or something
                    pass # we could handle the previous downloaded stuff here first check for the status of the nzb with download.url
                if downloader.addDownload(game, download):
                    game.status = common.SNATCHED
                    download.status = common.SNATCHED
                    download.save()
                    notify(game)
                    return game.status #exit on first success
    return game.status


def _filterBadDownloads(blacklist, downloads, min_size=0):
    clean = []
    for download in downloads:
        for black_word in blacklist:
            DebugLogEvent("Checking Word: '%s' in '%s'" % (black_word, download.name))
            if black_word in download.name:
                LogEvent("Found '%s' in Title: '%s'. Skipping..." % (black_word, download.name))
                break
        else:
            if not min_size or min_size < download.size:
                clean.append(download)
    return clean


def runChecker():
    games = Game.select()
    for checker in common.PM.D:
        for game in games:
            #DebugLogEvent("Checking game status for %s" % game)
            status, path = checker.getGameStaus(game)
            if status == common.DOWNLOADED:
                game.status = common.DOWNLOADED
                DebugLogEvent("Game %s is now downloded" % game)
                ppGame(game, path)
            elif status == common.SNATCHED:
                game.status = common.SNATCHED #status setting on Game saves automatically
                DebugLogEvent("Game %s is now snatched" % game)


def ppGame(game, path):
    pp_try = False
    for pp in common.PM.P:
        if pp.ppPath(game, path):
            game.status = common.COMPLETED # downloaded and pp success
            return True
        pp_try = True
    if pp_try:
        game.status = common.PP_FAIL # tried to pp but fail
    return False
