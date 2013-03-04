from gamez.Logger import DebugLogEvent
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
    for indexer in common.PM.I:
        downloads = indexer.searchForGame(game)
        for downloader in common.PM.getDownloaders(types=indexer.types):
            for download in downloads:
                download.save()
                if downloader.addDownload(game, download):
                    game.status = common.SNATCHED
                    download.status = common.SNATCHED
                    download.save()
                    notify(game)
                    return game.status #exit on first success
    return game.status


def runChecker():
    games = Game.select()
    for checker in common.PM.D:
        for game in games:
            DebugLogEvent("Checking game status for %s" % game)
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
