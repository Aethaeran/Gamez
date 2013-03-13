from gamez.Logger import DebugLogEvent, LogEvent
from gamez import common
from gamez.classes import Game, Download
from plugins import Indexer


def runSearcher():
    DebugLogEvent("running searcher")
    for game in Game.select():
        if game.status == common.FAILED and common.SYSTEM.c.again_on_fail:
            game.status = common.WANTED
        elif game.status != common.WANTED:
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
        downloads = indexer.searchForGame(game) #intensiv
        downloads = _filterBadDownloads(blacklist, downloads)
        return _snatchOne(game, downloads)
    return game.satus


# in a way we dont need game here since each download holds a ref to each game ... but it is easier to read
def _snatchOne(game, downloads):
    for downloader in common.PM.getDownloaders(types=Indexer.types):
        for download in downloads:
            if downloader.addDownload(game, download):
                game.status = common.SNATCHED # games save status automatically
                download.status = common.SNATCHED # downloads don't
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
            old_download = None
            try:
                old_download = Download.get(Download.url == download.url)
            except Download.DoesNotExist:
                #no download with that url found
                pass

            if not old_download:
                DebugLogEvent("Saving the new download we found %s" % download)
                download.status = common.UNKNOWN
                download.save()
            else:
                if old_download.status in (common.FAILED, common.DOWNLOADED):
                    LogEvent("Found a Download(%s) with the same url and it failed or we downloaded it already. Skipping..." % download)
                    continue
                if old_download.status == common.SNATCHED:
                    LogEvent("Found a Download(%s) with the same url and we snatched it already. I'l get it again..." % download)
                    #continue
                download = old_download
            if not min_size or min_size < download.size:
                clean.append(download)
    return clean


def runChecker():
    games = Game.select()
    for checker in common.PM.D:
        for game in games:
            if not game.status == common.SNATCHED:
                continue
            DebugLogEvent("Checking game status for %s" % game)
            status, download, path = checker.getGameStaus(game)
            DebugLogEvent("%s gave back status %s for game %s on download %s" % (checker, status, game, download))
            if status == common.DOWNLOADED:
                game.status = common.DOWNLOADED
                download.status = common.DOWNLOADED
                download.save()
                ppGame(game, download, path)
                notify(game)
            elif status == common.SNATCHED:
                game.status = common.SNATCHED #status setting on Game saves automatically
                download.status = common.SNATCHED
                download.save()
            elif status == common.FAILED:
                download.status = common.FAILED
                download.save()
                if common.SYSTEM.c.again_on_fail:
                    game.status = common.WANTED
                    searchGame(game)
                else:
                    game.status = common.FAILED


def ppGame(game, download, path):
    pp_try = False
    for pp in common.PM.PP:
        if pp.ppPath(game, path):
            game.status = common.COMPLETED # downloaded and pp success
            download.status = common.COMPLETED
            download.save()
            return True
        pp_try = True
    if pp_try:
        game.status = common.PP_FAIL # tried to pp but fail
        download.status = common.PP_FAIL
        download.save()
    return False
