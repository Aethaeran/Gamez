import cherrypy
import json
import os
from DBFunctions import GetGamesFromTerm, GetGameDataFromTerm, AddGameToDb, GetRequestedGames, RemoveGameFromDb, UpdateStatus, GetLog, ClearDBLog,AddWiiGamesIfMissing,AddXbox360GamesIfMissing,ApiGetGamesFromTerm,AddComingSoonGames,GetUpcomingGames,AddGameUpcomingToDb,ApiGetRequestedGames
from UpgradeFunctions import CheckForNewVersion,IgnoreVersion,UpdateToLatestVersion
from FolderFunctions import ApiUpdateRequestedStatus
import ConfigParser
from time import sleep
import urllib
from xml.dom import minidom
import base64
import hashlib
import random
from FolderFunctions import *
from Constants import *
from GameTasks import *
from TheGamesDBSearcher import GetGameDataFromTheGamesDB, AddGameToDbFromTheGamesDb
import gamez

class WebRoot:
    appPath = ''

    def __init__(self,app_path):
        WebRoot.appPath = app_path

    @cherrypy.expose
    def index(self,status_message='',version='',filter=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        defaultSearch = config.get('SystemGenerated','default_search').replace('"','')
        if(defaultSearch == "Wii"):
            defaultSearch = "<option>---</option><option selected>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "Xbox360"):
            defaultSearch = "<option>---</option><option>Wii</option><option selected>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "PS3"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option selected>PS3</option><option>PC</option>"
        elif(defaultSearch == "PC"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option selected>PC</option>"
        else:
            defaultSearch = "<option selected>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"        
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <title>Gamez :: Home</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>"""
        if(status_message <> ''):
            html = html + """<meta http-equiv="refresh" content="7, URL=/">"""
        html = html + """
          </head>
          <body id="dt_example">"""
        if(status_message <> ''):
            html = html + """
                            <div id='_statusbar' class='statusbar statusbarhighlight'>""" + status_message + """</div>"""
        #isNewVersionAvailable = CheckForNewVersion(WebRoot.appPath)
        isNewVersionAvailable = False
        if(isNewVersionAvailable):
            html = html + """
                            <div id='_statusbar' class='statusbar statusbarhighlight'>New Version Available :: <a href="/upgradetolatestversion?verification=SYSTEM_DIRECTED">Upgrade Now</a> | <a href="/ignorecurrentversion?verification=SYSTEM_DIRECTED">Ignore Until Next Version</a></div>
                          """
        html = html + """
            <div id="menu">
                <ul class="menu">
                    <a href="/"><img src="images/gamezlogo.png" height="41" alt="Gamez" border="0"></a>
                     <li class="parent">
                        <a href="/">
                            Home
                        </a>
                        <ul><li><a href="/?filter=Wanted">Wanted Games</a></li><li><a href="/?filter=Snatched">Snatched Games</a></li><li><a href="/?filter=Downloaded">Downloaded Games</a></li></ul>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/updategamelist">
                            Update Game List
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/comingsoon">
                            Upcoming Releases
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/shutdown"><img src="/css/datatables_images/shutdown.png" alt="OFF" border="0">
                        </a>
                        <ul><li><a href="/shutdown">Shutdown</a></li><li><a href="/reboot">Reboot</a></li></ul>
                    </li>
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json',
                                    select: function( event, ui ) {
                                            $('#searchButton').click();
                                    }
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                var system = document.getElementById("systemDropDown").options[document.getElementById("systemDropDown").selectedIndex].value;
                                if(system == "---")
                                {
                                    system = "";	
                                }
                                document.location.href = "search?term=" + searchText + "&system=" + system;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetRequestedGames(filter)
        if(db_result == ''):
            html  = html + """No games to show. Try searching for some."""
        else:
            html = html + """
                <script>function UpdateGameStatus(status,db_id){var redirectUrl = '/updatestatus?game_id=' + db_id + '&status=' + status;location.href=redirectUrl;}</script>
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                  <tr>
                    <th>Actions</th>
		            <th>Cover</th>
                    <th>Game Name</th>
                    <th>Game Type</th>
                    <th>System</th>
                    <th>Status</th>
                    <th>Update Status</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":true,"bLengthChange":false});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def search(self,term='',system=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        defaultSearch = config.get('SystemGenerated','default_search').replace('"','')
        if(defaultSearch == "Wii"):
            defaultSearch = "<option>---</option><option selected>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "Xbox360"):
            defaultSearch = "<option>---</option><option>Wii</option><option selected>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "PS3"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option selected>PS3</option><option>PC</option>"
        elif(defaultSearch == "PC"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option selected>PC</option>"
        else:
            defaultSearch = "<option selected>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"                     
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <title>Gamez :: Search</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">
            <div id="menu">
                <ul class="menu">
                    <a href="/"><img src="images/gamezlogo.png" height="41" alt="Gamez" border="0"></a>
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/updategamelist">
                            Update Game List
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/comingsoon">
                            Upcoming Releases
                        </a>
                    </li>                    
                </ul>
               <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json',
                                    select: function( event, ui ) {
                                            $('#searchButton').click();
                                    }
                                }
                            );
                            $("button").button().click(function(){
                                var searchText = document.getElementById("search").value;
                                var system = document.getElementById("systemDropDown").options[document.getElementById("systemDropDown").selectedIndex].value;
				if(system == "---")
				{
				    system = "";	
				}
                                document.location.href = "search?term=" + searchText + "&system=" + system;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetGameDataFromTheGamesDB(term,system)
        if(db_result == ''):
           db_result = GetGameDataFromTerm(term,system)
        if(db_result == ''):   
            html  = html + """No Results Found. Try Searching Again"""
        else:
            html = html + """
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                  <tr>
                    <th>Download</th>
                    <th>Cover</th>
                    <th>Game Name</th>
                    <th>Game Type</th>
                    <th>System</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":true,"bLengthChange":false});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def settings(self):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)        
        debugChecked = config.get('global','debug_enabled').replace('"','')
        sabChecked = config.get('SystemGenerated','sabnzbd_enabled').replace('"','')
        nzbmatrixChecked = config.get('SystemGenerated','nzbmatrix_enabled').replace('"','')
        newznabChecked = config.get('SystemGenerated','newznab_enabled').replace('"','')
        nzbsuChecked = config.get('SystemGenerated','nzbsu_enabled').replace('"','')
        growlChecked = config.get('SystemGenerated','growl_enabled').replace('"','')
        prowlChecked = config.get('SystemGenerated','prowl_enabled').replace('"','')
        notifoChecked = config.get('SystemGenerated','notifo_enabled').replace('"','')
        notifymyandroidChecked = config.get('SystemGenerated','notifymyandroid_enabled').replace('"','')
        xbmcChecked = config.get('SystemGenerated','xbmc_enabled').replace('"','')
        nzbBlackholeChecked = config.get('SystemGenerated','blackhole_nzb_enabled').replace('"','')
        torrentBlackholeChecked = config.get('SystemGenerated','blackhole_torrent_enabled').replace('"','')
        katChecked = config.get('SystemGenerated','torrent_kat_enabled').replace('"','')
        
        sabDownloadProcessChecked = config.get('SystemGenerated','process_sabnzbd_download_folder_enabled').replace('"','')
        nzbDownloadProcessChecked = config.get('SystemGenerated','process_nzb_download_folder_enabled').replace('"','')
        torrentDownloadProcessChecked = config.get('SystemGenerated','process_torrent_download_folder_enabled').replace('"','')
        downloadProcessWiiChecked = config.get('SystemGenerated','process_download_folder_wii_enabled').replace('"','')
        downloadProcessXbox360Checked = config.get('SystemGenerated','process_download_folder_xbox360_enabled').replace('"','')
        downloadProcessPS3Checked = config.get('SystemGenerated','process_download_folder_ps3_enabled').replace('"','')
        downloadProcessPCChecked = config.get('SystemGenerated','process_download_folder_pc_enabled').replace('"','')

        defaultSearch = config.get('SystemGenerated','default_search').replace('"','')
        ps3_tb_Checked = config.get('SystemGenerated','ps3_tb_enable').replace('"','')
        ps3_jb_Checked = config.get('SystemGenerated','ps3_jb_enable').replace('"','')       
        blacklist_words_xbox360 = config.get('SystemGenerated','blacklist_words_xbox360').replace('"','')
        blacklist_words_wii = config.get('SystemGenerated','blacklist_words_wii').replace('"','')
        clearlog_at_startup = config.get('SystemGenerated','clearlog_at_startup').replace('"','')
        https_support_enabled = config.get('SystemGenerated','https_support_enabled').replace('"','')
        retention = config.get('SystemGenerated','retention').replace('"','')

        if(debugChecked == "1"):
           debugChecked = "CHECKED"
        else:
            debugChecked = ""
        if(sabChecked == "1"):
            sabChecked = "CHECKED"
        else:
            sabChecked = ""
        if(nzbmatrixChecked == "1"):
            nzbmatrixChecked = "CHECKED"
        else:
            nzbmatrixChecked = ""
        if(newznabChecked == "1"):
            newznabChecked = "CHECKED"
        else:
            newznabChecked = ""       
        if(nzbsuChecked == "1"):
            nzbsuChecked = "CHECKED"
        else:
            nzbsuChecked = ""
        if(growlChecked == "1"):
            growlChecked = "CHECKED"
        else:
            growlChecked = ""       
        if(prowlChecked == "1"):
            prowlChecked = "CHECKED"
        else:
            prowlChecked = ""       
        if(notifoChecked == "1"):
            notifoChecked = "CHECKED"
        else:
            notifoChecked = ""    
        if(notifymyandroidChecked == "1"):
            notifymyandroidChecked = "CHECKED"
        else:
            notifymyandroidChecked = ""
        if(xbmcChecked == "1"):
            xbmcChecked = "CHECKED"
        else:
            xbmcChecked = ""  
        if(nzbBlackholeChecked == "1"):
            nzbBlackholeChecked = "CHECKED"
        else:
            nzbBlackholeChecked = ""             
        if(torrentBlackholeChecked == "1"):
            torrentBlackholeChecked = "CHECKED"
        else:
            torrentBlackholeChecked = ""             
        if(katChecked == "1"):
            katChecked = "CHECKED"
        else:
            katChecked = ""          

        if(sabDownloadProcessChecked == "1"):
            sabDownloadProcessChecked = "CHECKED"
        else:
            sabDownloadProcessChecked = ""  
        if(nzbDownloadProcessChecked == "1"):
            nzbDownloadProcessChecked = "CHECKED"
        else:
            nzbDownloadProcessChecked = ""  
        if(torrentDownloadProcessChecked == "1"):
            torrentDownloadProcessChecked = "CHECKED"
        else:
            torrentDownloadProcessChecked = ""  
        if(downloadProcessWiiChecked == "1"):
            downloadProcessWiiChecked = "CHECKED"
        else:
            downloadProcessWiiChecked = ""  
        if(downloadProcessXbox360Checked == "1"):
            downloadProcessXbox360Checked = "CHECKED"
        else:
            downloadProcessXbox360Checked = ""              
        if(downloadProcessPS3Checked == "1"):
            downloadProcessPS3Checked = "CHECKED"
        else:
            downloadProcessPS3Checked = ""
        if(downloadProcessPCChecked == "1"):
            downloadProcessPCChecked = "CHECKED"
        else:
            downloadProcessPCChecked = ""
        if(ps3_tb_Checked == "1"):
            ps3_tb_Checked = "CHECKED"
        else:
            ps3_tb_Checked = ""
        if(ps3_jb_Checked == "1"):
            ps3_jb_Checked = "CHECKED"
        else:
            ps3_jb_Checked = ""
        if(clearlog_at_startup == "1"):
            clearlog_at_startup = "CHECKED"
        else:
            clearlog_at_startup =""
        if(https_support_enabled == "1"):
            https_support_enabled = "CHECKED"
        else:
            https_support_enabled =""


        if(defaultSearch == "Wii"):
            defaultSearch = "<option>---</option><option selected>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "Xbox360"):
            defaultSearch = "<option>---</option><option>Wii</option><option selected>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "PS3"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option selected>PS3</option><option>PC</option>"
        elif(defaultSearch == "PC"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option selected>PC</option>"
        else:
            defaultSearch = "<option selected>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        
        webinterfacetheme = config.get('SystemGenerated','webinterface').replace('"','')
        if (webinterfacetheme == "grey"):
            defaultWebinterface = "<option>default</option><option selected>grey</option>"
            DebugLogEvent("It is the [" + webinterfacetheme + "] Theme for Webinterface selectet")
        else:
            defaultWebinterface = "<option selected>default</option><option>grey</option>"
            DebugLogEvent("It is the [" + webinterfacetheme + "] Theme for Webinterface selectet")
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <title>Gamez :: Settings</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="stylesheet" type="text/css" href="css/settings.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">
            <div id="menu">
                <ul class="menu">
                    <a href="/"><img src="images/gamezlogo.png" height="41" alt="Gamez" border="0"></a>
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/updategamelist">
                            Update Game List
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/comingsoon">
                            Upcoming Releases
                        </a>
                    </li>                    
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json',
                                    select: function( event, ui ) {
                                            $('#searchButton').click();
                                    }
                                }
                            );
                            $("#searchButton").button().click(function(){
                            	var searchText = document.getElementById("search").value;
                                var system = document.getElementById("systemDropDown").options[document.getElementById("systemDropDown").selectedIndex].value;
				if(system == "---")
				{
				    system = "";	
				}
                                document.location.href = "search?term=" + searchText + "&system=" + system;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="tabs">
		<ul>
			<li><a href="#gamez-tab">Gamez</a></li>
			<li><a href="#downloaders-tab">Downloaders</a></li>
			<li><a href="#searchproviders-tab">Search Providers</a></li>
			<li><a href="#notifications-tab">Notifications</a></li>
			<li><a href="#folders-tab">Folders</a></li>
		</ul>
		<form id="form" name="form" method="get" action="/savesettings">
		<div id="gamez-tab">
			<p>
				<table cellpadding="5">
					<tr>
						<td>
							<label><b>Gamez Host</b></label>
							<br />
							<input style="width:250px" type="text" name="cherrypyHost" id="cherrypyHost" value='""" + config.get('global','server.socket_host').replace('"','') +  """' />

						</td>
						
						<td>
							<label><b>Gamez Port</b></label>
							<br />
                					<input style="width:250px" type="text" name="cherrypyPort" id="cherrypyPort" value='""" + config.get('global','gamez_port').replace('"','') +  """' />
						</td>
						<td>
							<label><b>Gamez Username</b></label>
							<br />
							<input style="width:250px" type="text" name="gamezUsername" id="gamezUsername" value='""" + config.get('global','user_name').replace('"','') +  """' />
						</td>

						<td>
							<label><b>Gamez Password</b></label>
							<br />
							<input style="width:250px" type="text" name="gamezPassword" id="gamezPassword" value='""" + config.get('global','password').replace('"','') +  """' />
						</td>
					</tr>
					<tr><td colspan="4"></td></tr>
					<tr>
						<td>
							<label><b>Download Interval</b></label>
							<br />
							<label><b>(In Minutes)</b></label>
							<br />
                					<input style="width:250px" type="text" name="downloadInterval" id="downloadInterval" value='""" + config.get('Scheduler','download_interval').replace('"','') +  """' />
						</td>
						<td>
							<label><b>Game List Update Interval</b></label>
							<br />
							<label><b>(In Minutes)</b></label>
							<br />
							<input style="width:250px" type="text" name="gameListUpdateInterval" id="gameListUpdateInterval" value='""" + config.get('Scheduler','game_list_update_interval').replace('"','') +  """' />
						</td>
						<td colspan="2">
							<br />
							<label><b>Gamez API Key</b></label>
							<br />
							<input style="width:520px" type="text" name="gamezApiKey" id="gamezApiKey" value='""" + config.get('SystemGenerated','api_key').replace('"','') +  """' />

						</td>
					</tr>
					<tr><td colspan="4"></td></tr>
					<tr>
						<td>
							<label><b>Default System for Search</b></label>
							<br />
							<select name="defaultSearch" id="defaultSearch" style="width:200px">""" + defaultSearch + """</select>
						</td>
						<td>
							<label><b>Webinterface Theme</b></label>
							<br />
							<select name="webinterface" id="webinterface" style="width:200px">""" + defaultWebinterface + """</select>
						</td>
					<tr><td colspan="4"></td></tr>
						<td>
							<div style="float:middle">
							<input type="checkbox" name="https_support" id="https_support" value="https_support" """ + https_support_enabled + """ />&nbsp;<b>Enabled HTTPS Support</b>
							</div>
						</td>
					<tr><td colspan="4"></td></tr>
						<td>
							<div style="float:middle">
							<input type="checkbox" name="debugEnabled" id="debugEnabled" value="debugEnabled" """ + debugChecked + """ />&nbsp;<b>Enabled Debug</b>
							</div>
						</td>
					<tr><td colspan="4"></td></tr>
						<td>
							<div style="float:middle">
							<input type="checkbox" name="clearlog" id="clearlog" value="clearlog" """ + clearlog_at_startup + """ />&nbsp;<b>Enabled ClearLog a startup</b>
							</div>
						</td>
					   <br />
					</tr>
				</table>
			</p>
			
		</div>
		<div id="downloaders-tab">
			<p>
				<table cellpadding="5" width="100%">
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Sabnzbd+</u></b></label>
							<div style="float:right">
							<input type="checkbox" name="sabnzbdEnabled" id="sabnzbdEnabled" value="sabnzbdEnabled" """ + sabChecked + """ />Enabled
							</div>
							<br />
							<table>
								<tr>
									<td>
										<label><b>SABnzbd+ Host</b></label>
										<br />
										<input style="width:200px" type="text" name="sabHost" id="sabHost" value='""" + config.get('Sabnzbd','host').replace('"','') +  """' />
									</td>
									<td>
										<label><b>SABnzbd+ Port</b></label>
										<br />
										<input style="width:200px" type="text" name="sabPort" id="sabPort" value='""" + config.get('Sabnzbd','port').replace('"','') +  """' />
									</td>
									<td>
										<label><b>SABnzbd+ Download Category</b></label>
										<br />
										<input style="width:225px" type="text" name="sabCategory" id="sabCategory" value='""" + config.get('Sabnzbd','category').replace('"','') +  """' />
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>
								<tr>
									<td colspan="3">
										<label><b>SABnzbd+ API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="sabApi" id="sabApi" value='""" + config.get('Sabnzbd','api_key').replace('"','') +  """' />
									</td>
								</tr>
							</table>
						</td>
						<td width="10px">&nbsp;</td>
						<td style="border:solid 1px" valign="top">
							<legend><b><u>Blackhole</u></b></legend>
							<br />
							<label style="float:left"><b><u>NZB's</u></b></label>
							<div style="float:right">
								<input type="checkbox" name="nzbBlackholeEnabled" id="nzbBlackholeEnabled" value="nzbBlackholeEnabled" """ + nzbBlackholeChecked + """ />Enabled
							</div>
							<br />
							<table>
								<tr>
									<td>
										<label><b>NZB Blackhole Path</b></label>
										<br />
										<input style="width:400px" type="text" name="nzbBlackholePath" id="nzbBlackholePath" value='""" + config.get('Blackhole','nzb_blackhole_path').replace('"','') +  """' />
									</td>
								</tr>							
							</table>	
							<br />
							<label style="float:left"><b><u>BitTorrent</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="torrentBlackholeEnabled" id="torrentBlackholeEnabled" value="torrentBlackholeEnabled" """ + torrentBlackholeChecked + """ />Enabled
								</div>
								<br />
								<table>
									<tr>
										<td>
											<label><b>BitTorrent Blackhole Path</b></label>
											<br />
											<input style="width:400px" type="text" name="torrentBlackholePath" id="torrentBlackholePath" value='""" + config.get('Blackhole','torrent_blackhole_path').replace('"','') +  """' />
										</td>
									</tr>							
							</table>	
						</td>						
					</tr>
				</table>
			</p>
		</div>
		<div id="searchproviders-tab">
			<p>
				<table cellpadding="5" width="60%">
					<tr width="60%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>NZB Matrix</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="nzbmatrixEnabled" id="nzbmatrixEnabled" value="nzbmatrixEnabled" """ + nzbmatrixChecked + """ />Enabled
								</div>
							<br />
							<div id=nzbmatrixoptions>
							<table>
								<tr>
									<td>
										<label><b>NZB Matrix API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="nzbMatrixApi" id="nzbMatrixApi" value='""" + config.get('NZBMatrix','api_key').replace('"','') +  """' />
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>
								<tr>
									<td>
										<label><b>NZB Matrix Username</b></label>
										<br />
										<input style="width:225px" type="text" name="nzbMatrixUsername" id="nzbMatrixUsername" value='""" + config.get('NZBMatrix','username').replace('"','') +  """' />
									</td>
								</tr>
							</table>
							</div>
						</td>
						<tr><td>&nbsp;</td></tr>
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Newznab</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="newznabEnabled" id="newznabEnabled" value="newznabEnabled" """ + newznabChecked + """ />Enabled
								</div>
							<br />
					<div id=newznaboptions>
							<table>
								<tr>
									<td>
										<label><b>Newznab Host</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabHost" id="newznabHost" value='""" + config.get('Newznab','host').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Newznab Port</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabPort" id="newznabPort" value='""" + config.get('Newznab','port').replace('"','') +  """' />
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>
								<tr>
									<td>
										<label><b>Newznab Wii Category ID</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabWiiCat" id="newznabWiiCat" value='""" + config.get('Newznab','wii_category_id').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Newznab Xbox 360 Category ID</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabXbox360Cat" id="newznabXbox360Cat" value='""" + config.get('Newznab','xbox360_category_id').replace('"','') +  """' />
									</td>
								 </tr> 
                                                         <tr><td>&nbsp;</td></tr>
                                                               <td>
										<label><b>Newznab PS3 Category ID</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabPS3Cat" id="newznabPS3Cat" value='""" + config.get('Newznab','ps3_category_id').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Newznab PC Category ID</b></label>
										<br />
										<input style="width:225px" type="text" name="newznabPCCat" id="newznabPCCat" value='""" + config.get('Newznab','pc_category_id').replace('"','') +  """' />
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>
								<tr>
									<td colspan="2">
										<label><b>Newznab API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="newznabApi" id="newznabApi" value='""" + config.get('Newznab','api_key').replace('"','') +  """' />
									</td>
								</tr>
															
							</table>	
						</td>						
					</tr>
					<tr><td>&nbsp;</td></tr>
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>NZB.su</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="nzbsuEnabled" id="nzbsuEnabled" value="nzbsuEnabled" """ + nzbsuChecked + """ />Enabled
								</div>
							<br />
							<div id=nzbsuoptions>
							<table>
								<tr>
									<td>
										<label><b>NZB.su API</b></label>
										<br />
										<input style="width:400px" type="text" name="nzbsuapi" id="nzbsuapi" value='""" + config.get('NZBSU','api_key').replace('"','') +  """' />
									</td>
								</tr>
							</table>
							</div>
						</td>
					<tr><td>&nbsp;</td></tr>
					<tr>
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>BitTorrent</u></b></label>
							<br />
							<br />
							<input type="checkbox" name="katEnabled" id="katEnabled" value="katEnabled" """ + katChecked + """ />&nbsp;<b>KickAss Torrents</b>
						</td>
					</tr>
					<tr><td>&nbsp;</td></tr>
						<td  style="border:solid 1px" width="50%" valign="top">
							<br />
							<label style="float:left"><b><u>Advance Search Options</u></b></label>
							<br />
							<br />
							<table>
								<tr>
									<td>
										<label><b>Retention</b></label>
										<br />
										<input style="width:120px" type="text" name="retention" id="retention" value='""" + config.get('SystemGenerated','retention').replace('"','') +  """' />
										<br />
									</td>
							 	</tr>
								<tr><td>&nbsp;</td></tr>
    								<tr>
									<td>
										<label><b>Blacklisted Words for XBOX360</b></label>
										<br />
										<input style="width:400px" type="text" name="blacklist_words_xbox360" id="blacklist_words_xbox360" value='""" + config.get('SystemGenerated','blacklist_words_xbox360').replace('"','') +  """' />
									       <br />Note: This option can be use for Regions example (JPN;USA)
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>
								<tr>
									<td>
										<label><b>Blacklisted Word for Wii</b></label>
										<br />
										<input style="width:400px" type="text" name="blacklist_words_wii" id="blacklist_words_wii" value='""" + config.get('SystemGenerated','blacklist_words_wii').replace('"','') +  """' />
									       <br />Note: This option can be use for Regions example (JPN;USA;)
									</td>
								</tr>
								<tr><td>&nbsp;</td></tr>	
							<td>
								<label style="float:left"><b><u>Advance search for PS3 Games</u></b></label>
								<br />
								<br />
								<input type="checkbox" name="ps3_tb_enable" id="ps3_tb_enable" value="ps3_tb_enable" """ + ps3_tb_Checked + """ />&nbsp;<b>Disable search for Games with True Blue support</b>
								<input  align="right" type="checkbox" name="ps3_jb_enable" id="ps3_jb_enable" value="ps3_jb_enable" """ + ps3_jb_Checked + """ />&nbsp;<b>Disable search for Games with Jail Break support</b>
							</td>
						</tr>
					</table>
						</td>
				</table>
			</p>
		</div>
		<div id="notifications-tab">
			<p>
				<table cellpadding="5" width="100%">
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Growl</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="growlEnabled" id="growlEnabled" value="growlEnabled" """ + growlChecked + """ />Enabled
								</div>
							<br />	
							<div id=growloptions>
							<table>
								<tr>
									<td>
										<label><b>Growl Host</b></label>
										<br />
										<input type="text" name="growlHost" id="growlHost" value='""" + config.get('Notifications','growl_host').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Growl Port</b></label>
										<br />
										<input type="text" name="growlPort" id="growlPort" value='""" + config.get('Notifications','growl_port').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Growl Password</b></label>
										<br />
										<input type="text" name="growlPassword" id="growlPassword" value='""" + config.get('Notifications','growl_password').replace('"','') +  """' />
									</td>
								</tr>
							</table>
							</div>
						</td>
					<tr><td>&nbsp;</td></tr>
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Prowl</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="prowlEnabled" id="prowlEnabled" value="prowlEnabled" """ + prowlChecked + """ />Enabled
								</div>
							<br />
							<div id=prowloptions>
							<table>
								<tr>
									<td>
										<label><b>Prowl API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="prowlApi" id="prowlApi" value='""" + config.get('Notifications','prowl_api').replace('"','') +  """' />
									</td>
								</tr>							
							</table>
							</div>	
						</td>						
					</tr>
					<tr><td>&nbsp;</td></tr>
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Notifo</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="notifoEnabled" id="notifoEnabled" value="notifoEnabled" """ + notifoChecked + """ />Enabled
								</div>
							<br />	
							<div id=notifooptions>
							<table>
								<tr>
									<td>
										<label><b>Notifo Username</b></label>
										<br />
										<input type="text" name="notifoUsername" id="notifoUsername" value='""" + config.get('Notifications','notifo_username').replace('"','') +  """' />
									</td>
									<td>
										<label><b>Notifo API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="notifoApi" id="notifoApi" value='""" + config.get('Notifications','notifo_apikey').replace('"','') +  """' />
									</td>
								</tr>
							</table>
							</div>
						</td>
						<td width="10px">&nbsp;</td>						
					</tr>
					<tr><td>&nbsp;</td></tr>
					<tr width="100%"> 
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>Notify My Android</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="notifymyandroidEnabled" id="notifymyandroidEnabled" value="notifymyandroidEnabled" """ + notifymyandroidChecked + """ />Enabled
								</div>
							<br />	
							<div id=notifymyandroidoptions>
							<table>
								<tr>
									<td>
										<label><b>NMA API Key</b></label>
										<br />
										<input style="width:400px" type="text" name="notifymyandroidApi" id="notifymyandroidApi" value='""" + config.get('Notifications','notifymyandroid_apikey').replace('"','') +  """' />
									</td>
								</tr>
							</table>
							</div>
						</td>
						<td width="10px">&nbsp;</td>						
					</tr>
					<tr><td>&nbsp;</td></tr>
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<label style="float:left"><b><u>XBMC</u></b></label>
								<div style="float:right">
									<input type="checkbox" name="xbmcEnabled" id="xbmcEnabled" value="xbmcEnabled" """ + xbmcChecked + """ />Enabled
								</div>
							<br />	
							<div id=xbmcoptions>
							<table>
								<tr>
									<td>
										<label><b>XBMC Username</b></label>
										<br />
										<input style="width:300px" type="text" name="xbmcUsername" id="xbmcUsername" value='""" + config.get('Notifications','xbmc_username').replace('"','') +  """' />
									</td>
									<tr><td>&nbsp;</td></tr>
									<td>
										<label><b>XBMC Password</b></label>
										<br />
										<input style="width:300px" type="text" name="xbmcPassword" id="xbmcPassword" value='""" + config.get('Notifications','xbmc_password').replace('"','') +  """' />
									</td>
									<tr><td>&nbsp;</td></tr>
									<td>
										<label><b>XBMC Host(s)</b></label>
										<br />
										<input style="width:600px" type="text" name="xbmcHosts" id="xbmcHosts" value='""" + config.get('Notifications','xbmc_hosts').replace('"','') +  """' />
									       <br />Please sepearate the Hosts with a ';'  e.g. 192.168.0.100:8080
									</td>
								</tr>
							</table>
							</div>
						</td>
						<td width="10px">&nbsp;</td>						
					</tr>
				</table>
			</p>
		</div>	
		<div id="folders-tab">
			<p>
				<table cellpadding="5" width="100%">
					<tr width="100%">
						<td  style="border:solid 1px" width="45%" valign="top">
							<br />
							<input type="checkbox" name="processSabDirectoryEnabled" id="processSabDirectoryEnabled" value="processSabDirectoryEnabled" """ + sabDownloadProcessChecked + """ />
							<b>Post Process Sabnzbd Download Directory</b>
							<br /><br />
							<input type="checkbox" name="processTorrentsDirectoryEnabled" id="processTorrentsDirectoryEnabled" value="processTorrentsDirectoryEnabled" """ + torrentDownloadProcessChecked + """ />
							<b>Post Process Blackhole Torrents Directory</b>
							<br /><br />
							<input type="checkbox" name="processNzbsDirectoryEnabled" id="processNzbsDirectoryEnabled" value="processNzbsDirectoryEnabled" """ + nzbDownloadProcessChecked + """ />
							<b>Post Process Blackhole NZB's Directory</b>
							<br /><br />
							<input type="checkbox" name="processWiiEnabled" id="processWiiEnabled" value="processWiiEnabled" """ + downloadProcessWiiChecked + """ />
							<b>Post Process Wii Games</b>
							<br /><br />
							<input type="checkbox" name="processXbox360Enabled" id="processXbox360Enabled" value="processXbox360Enabled" """ + downloadProcessXbox360Checked + """ />
							<b>Post Process XBOX 360 Games</b>
			                <br /><br />
							<input type="checkbox" name="processPS3Enabled" id="processPS3Enabled" value="processPS3Enabled" """ + downloadProcessPS3Checked + """ />
							<b>Post Process PS 3 Games</b>
							<br /><br />
							<input type="checkbox" name="processPCEnabled" id="processPCEnabled" value="processPCEnabled" """ + downloadProcessPCChecked + """ />
							<b>Post Process PC Games</b>				
			            </td>
						<td width="10px">&nbsp;</td>
						<td style="border:solid 1px" valign="top">
							<legend><b><u>Folders</u></b></legend>
							<br />
							<table>
								<tr>
									<td>
										<label><b>Blackhole Torrent Download Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="torrentBlackholeDownloadDirectory" id="torrentBlackholeDownloadDirectory" value='""" + config.get('Folders','torrent_completed').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>	
								<tr>
									<td>
										<label><b>Blackhole NZB's Download Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="nzbBlackholeDownloadDirectory" id="nzbBlackholeDownloadDirectory" value='""" + config.get('Folders','nzb_completed').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>
								<tr>
									<td>
										<label><b>Sabnzbd Download Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="sabDownloadDirectory" id="sabDownloadDirectory" value='""" + config.get('Folders','sabnzbd_completed').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>
								<tr>
									<td>
										<label><b>Wii Destination Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="wiiDestination" id="wiiDestination" value='""" + config.get('Folders','wii_destination').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>	
								<tr>
									<td>
										<label><b>XBOX 360 Destination Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="xbox360Destination" id="xbox360Destination" value='""" + config.get('Folders','xbox360_destination').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>								
							    <tr>
									<td>
										<label><b>PS3 Destination Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="PS3Destination" id="PS3Destination" value='""" + config.get('Folders','ps3_destination').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>
                                <tr>
									<td>
										<label><b>PC Destination Directory</b></label>
										<br />
										<input style="width:400px" type="text" name="PCDestination" id="pcDestination" value='""" + config.get('Folders','pc_destination').replace('"','').replace("\\\\","\\") +  """' />
									</td>
								</tr>									
                            </table>	
						</td>						
					</tr>
				</table>
			</p>
		</div>
		</div>
		<script>
			$(function(){$("#tabs").tabs();});
			$(document).ready(function()
			{
				if ($("#nzbmatrixEnabled").is(":checked"))
				{
					$("#nzbmatrixoptions").show();
				}
				else
				{
					$("#nzbmatrixoptions").hide();
				}
				$("#nzbmatrixEnabled").click(function(){
				if ($("#nzbmatrixEnabled").is(":checked"))
				{
					$("#nzbmatrixoptions").show("fast");
				}
				else
				{
					$("#nzbmatrixoptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#newznabEnabled").is(":checked"))
				{
					$("#newznaboptions").show();
				}
				else
				{
					$("#newznaboptions").hide();
				}
				$("#newznabEnabled").click(function(){
				if ($("#newznabEnabled").is(":checked"))
				{
					$("#newznaboptions").show("fast");
				}
				else
				{
					$("#newznaboptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#nzbsuEnabled").is(":checked"))
				{
					$("#nzbsuoptions").show();
				}
				else
				{
					$("#nzbsuoptions").hide();
				}
				$("#nzbsuEnabled").click(function(){
				if ($("#nzbsuEnabled").is(":checked"))
				{
					$("#nzbsuoptions").show("fast");
				}
				else
				{
					$("#nzbsuoptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#growlEnabled").is(":checked"))
				{
					$("#growloptions").show();
				}
				else
				{
					$("#growloptions").hide();
				}
				$("#growlEnabled").click(function(){
				if ($("#growlEnabled").is(":checked"))
				{
					$("#growloptions").show("fast");
				}
				else
				{
					$("#growloptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#prowlEnabled").is(":checked"))
				{
					$("#prowloptions").show();
				}
				else
				{
					$("#prowloptions").hide();
				}
				$("#prowlEnabled").click(function(){
				if ($("#prowlEnabled").is(":checked"))
				{
					$("#prowloptions").show("fast");
				}
				else
				{
					$("#prowloptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#notifoEnabled").is(":checked"))
				{
					$("#notifooptions").show();
				}
				else
				{
					$("#notifooptions").hide();
				}
				$("#notifoEnabled").click(function(){
				if ($("#notifoEnabled").is(":checked"))
				{
					$("#notifooptions").show("fast");
				}
				else
				{
					$("#notifooptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#notifymyandroidEnabled").is(":checked"))
				{
					$("#notifymyandroidoptions").show();
				}
				else
				{
					$("#notifymyandroidoptions").hide();
				}
				$("#notifymyandroidEnabled").click(function(){
				if ($("#notifymyandroidEnabled").is(":checked"))
				{
					$("#notifymyandroidoptions").show("fast");
				}
				else
				{
					$("#notifymyandroidoptions").hide("fast");
				}
				});
			});
			$(document).ready(function()
			{
				if ($("#xbmcEnabled").is(":checked"))
				{
					$("#xbmcoptions").show();
				}
				else
				{
					$("#xbmcoptions").hide();
				}
				$("#xbmcEnabled").click(function(){
				if ($("#xbmcEnabled").is(":checked"))
				{
					$("#xbmcoptions").show("fast");
				}
				else
				{
					$("#xbmcoptions").hide("fast");
				}
				});
			});

		</script>
                
		<br /><br />
        <div style="margin-left:5px">Gamez Version: """ + VersionNumber() + """</div>
		<div align="right" style="margin-right:20px">
			<button style="border:0; margin:0; padding:0;clear:both;margin-left:250px;width:125px;height:31px;background:#666666 url(img/button.png) no-repeat;text-align:center;line-height:31px;color:#FFFFFF;font-size:11px;font-weight:bold;" type="submit">Save Settings</button>
		</div>	
		</form>
                
                




          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def log(self,status_message='',version=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)       
        defaultSearch = config.get('SystemGenerated','default_search').replace('"','')
        if(defaultSearch == "Wii"):
            defaultSearch = "<option>---</option><option selected>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "Xbox360"):
            defaultSearch = "<option>---</option><option>Wii</option><option selected>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "PS3"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option selected>PS3</option><option>PC</option>"
        elif(defaultSearch == "PC"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option selected>PC</option>"
        else:
            defaultSearch = "<option selected>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"        
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <title>Gamez :: Log</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">"""
        html = html + """
            <div id="menu">
                <ul class="menu">
                    <a href="/"><img src="images/gamezlogo.png" height="41" alt="Gamez" ></a>
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/updategamelist">
                            Update Game List
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/comingsoon">
                            Upcoming Releases
                        </a>
                    </li>                    
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json',
                                    select: function( event, ui ) {
                                            $('#searchButton').click();
                                    }
                                }
                            );
                            $("button").button().click(function(){
                            	var searchText = document.getElementById("search").value;
                                var system = document.getElementById("systemDropDown").options[document.getElementById("systemDropDown").selectedIndex].value;
				if(system == "---")
				{
				    system = "";	
				}
                                document.location.href = "search?term=" + searchText + "&system=" + system;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetLog()
        if(db_result == ''):
            html  = html + """No log entries."""
        else:
            html = html + """
                <script>function UpdateGameStatus(status,db_id){var redirectUrl = '/updatestatus?game_id=' + db_id + '&status=' + status;location.href=redirectUrl;}</script>
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                    <th>Message</th>
                    <th>Date / Time</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <div style="float:right;"><button name="clearLogBtn" id="clearLogBtn" class="clear-log-button" onclick="location.href='/clearlog'">Clear Log</button></div>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":false,"bLengthChange":false,"iDisplayLength":25});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def comingsoon(self):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)        
        defaultSearch = config.get('SystemGenerated','default_search').replace('"','')
        if(defaultSearch == "Wii"):
            defaultSearch = "<option>---</option><option selected>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "Xbox360"):
            defaultSearch = "<option>---</option><option>Wii</option><option selected>Xbox360</option><option>PS3</option><option>PC</option>"
        elif(defaultSearch == "PS3"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option selected>PS3</option><option>PC</option>"
        elif(defaultSearch == "PC"):
            defaultSearch = "<option>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option selected>PC</option>"
        else:
            defaultSearch = "<option selected>---</option><option>Wii</option><option>Xbox360</option><option>PS3</option><option>PC</option>"        
        html = """

        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
        <html>
          <head>
            <title>Gamez :: Upcoming Releases</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/redmond/jquery-ui-1.8.16.custom.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="stylesheet" type="text/css" href="css/jquery.ui.override.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery-1.6.2.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.8.16.custom.min.js"></script>
            <script type="text/javascript" src="js/menu.js"></script>
            <script type="text/javascript" language="javascript" src="/js/jquery.dataTables.min.js"></script>
          </head>
          <body id="dt_example">"""
        html = html + """
            <div id="menu">
                <ul class="menu">
                    <a href="/"><img src="images/gamezlogo.png" height="41" alt="Gamez" border="0"></a>
                    <li class="parent">
                        <a href="/">
                            Home
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/settings">
                            Settings
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/log">
                            Log
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/updategamelist">
                            Update Game List
                        </a>
                    </li>
                    <li class="parent">
                        <a href="/comingsoon">
                            Upcoming Releases
                        </a>
                    </li>                    
                </ul>
                <div style="text-align:right;margin-right:20px">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button> 
                        <script>
                            $("#search").autocomplete(
                                {
                                    source:"/get_game_list/",
                                    minChars: 1,
                                    max:25,
                                    dataType:'json',
                                    select: function( event, ui ) {
                                            $('#searchButton').click();
                                    }
                                }
                            );
                            $("button").button().click(function(){
                            	var searchText = document.getElementById("search").value;
                                var system = document.getElementById("systemDropDown").options[document.getElementById("systemDropDown").selectedIndex].value;
				if(system == "---")
				{
				    system = "";	
				}
                                document.location.href = "search?term=" + searchText + "&system=" + system;
                            });
                        </script>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""
        db_result = GetUpcomingGames()
        if(db_result == ''):
            html  = html + """No Upcoming Games."""
        else:
            html = html + """
              <table cellpadding="0" cellspacing="0" border="0" class="display" id="searchresults">
                <thead>
                    <th>Download</th>
                    <th>Game Name</th>
                    <th>Release Date</th>
                    <th>System</th>
                  </tr>
                </thead>
                <tbody>"""
            html = html + db_result
            html = html + """
                </tbody>
              </table>
              <script>$(document).ready(function() {
	            oTable = $('#searchresults').dataTable({"bJQueryUI": true,"bSort":true,"bLengthChange":false,"iDisplayLength":25});});
              </script>
             """
        html = html + """
            </div>
          </body>
        </html>
        

               """
        return html;

    @cherrypy.expose
    def updatestatus(self,game_id='',status='',filePath=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        if(status <> ''):
            UpdateStatus(game_id,status)
        if(status == 'Downloaded'):
            ProcessDownloaded(game_id,status,filePath)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def get_game_list(self,term=''):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        return GetGamesFromTerm(term)

    @cherrypy.expose
    def addgame(self,dbid): 
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        request_dbid = AddGameToDb(dbid,'Wanted')
        DebugLogEvent("Requested ID for forceSearch [" + request_dbid + "]")
        GameTasks().ForceSearch(request_dbid)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def addgambythegamesdb(self,thegamesdbid):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        request_dbid = AddGameToDbFromTheGamesDb(thegamesdbid,'Wanted')
        DebugLogEvent("Requested ID for forceSearch [" + request_dbid + "]")
        GameTasks().ForceSearch(request_dbid)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def addgameupcoming(self,dbid): 
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        request_dbid = AddGameUpcomingToDb(dbid,'Wanted')
        DebugLogEvent("Requested ID for forceSearch [" + request_dbid + "]")
        GameTasks().ForceSearch(request_dbid)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def removegame(self,dbid):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        RemoveGameFromDb(dbid)
        raise cherrypy.InternalRedirect('/')

    @cherrypy.expose
    def ignorecurrentversion(self,verification):
        if(verification == "SYSTEM_DIRECTED"):
            IgnoreVersion(WebRoot.appPath)
        raise cherrypy.InternalRedirect('/') 

    @cherrypy.expose
    def upgradetolatestversion(self,verification):
        if(verification == "SYSTEM_DIRECTED"):
            status = UpdateToLatestVersion(WebRoot.appPath)
            raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def savesettings(self,cherrypyHost='', nzbMatrixUsername='', downloadInterval=3600, sabPort='', nzbMatrixApi='', nzbsu='', sabApi='', cherrypyPort='', sabHost='',gamezApiKey='',newznabHost='',newznabPort='',newznabApi='',newznabWiiCat='',newznabXbox360Cat='',newznabPS3Cat='',newznabPCCat='',prowlApi='',debugEnabled='',gamezUsername='',gamezPassword='',gameListUpdateInterval='',sabCategory='',growlHost='',growlPort='',growlPassword='',sabnzbdEnabled='',nzbmatrixEnabled='',nzbsuEnable='',newznabEnabled='',growlEnabled='',prowlEnabled='',notifoEnabled='',notifoUsername='',notifoApi='',notifymyandroidEnabled='',notifymyandroidApi='',xbmcEnabled='',xbmcUsername='',xbmcPassword='',xbmcHosts='',nzbBlackholeEnabled='',nzbBlackholePath='',torrentBlackholeEnabled='',torrentBlackholePath='',katEnabled='',defaultSearch='',wiiDestination='', xbox360Destination='', PS3Destination='', PCDestination='', nzbBlackholeDownloadDirectory='', torrentBlackholeDownloadDirectory='', processTorrentsDirectoryEnabled='', sabDownloadDirectory='', processXbox360Enabled='', processWiiEnabled='', processPS3Enabled='', processPCEnabled='', processNzbsDirectoryEnabled='', processSabDirectoryEnabled='',webinterface='',ps3_jb_enable='',ps3_tb_enable='',blacklist_words_xbox360='',blacklist_words_wii='',nzbsuEnabled='',nzbsuapi='',https_support='',clearlog='',retention=''):
        cherrypyHost = '"' + cherrypyHost + '"'
        nzbMatrixUsername = '"' + nzbMatrixUsername + '"'
        nzbMatrixApi = '"' + nzbMatrixApi + '"'
        nzbsuapi = '"' + nzbsuapi + '"'
        sabApi = '"' + sabApi + '"'
        sabHost = '"' + sabHost + '"'
        sabCategory = '"' + sabCategory + '"'
        gamezApiKey = '"' + gamezApiKey + '"'
        newznabHost = '"' + newznabHost + '"'
        newznabApi = '"' + newznabApi + '"'
        newznabWiiCat = '"' + newznabWiiCat + '"'
        newznabXbox360Cat = '"' + newznabXbox360Cat + '"'
        newznabPS3Cat = '"' + newznabPS3Cat + '"'
        newznabPCCat = '"' + newznabPCCat + '"'
        prowlApi = '"' + prowlApi + '"'
        gamezUsername = '"' + gamezUsername + '"'
        gamezPassword = '"' + gamezPassword + '"'
        growlHost = '"' + growlHost + '"'
        growlPassword = '"' + growlPassword + '"'
        notifoUsername = '"' + notifoUsername + '"'
        notifoApi = '"' + notifoApi + '"'
        notifymyandroidApi = '"' + notifymyandroidApi + '"'
        xbmcUsername = '"' + xbmcUsername + '"'
        xbmcPassword = '"' + xbmcPassword + '"'
        xbmcHosts = '"' + xbmcHosts + '"'
        nzbBlackholePath = '"' + nzbBlackholePath + '"'
        torrentBlackholePath = '"' + torrentBlackholePath + '"'
        wiiDestination = '"' + wiiDestination.replace("\\","\\\\") + '"'
        xbox360Destination = '"' + xbox360Destination.replace("\\","\\\\") + '"'
        PS3Destination = '"' + PS3Destination.replace("\\","\\\\") + '"'
        PCDestination = '"' + PCDestination.replace("\\","\\\\") + '"'
        nzbBlackholeDownloadDirectory = '"' + nzbBlackholeDownloadDirectory.replace("\\","\\\\") + '"'
        torrentBlackholeDownloadDirectory = '"' + torrentBlackholeDownloadDirectory.replace("\\","\\\\") + '"'
        sabDownloadDirectory = '"' + sabDownloadDirectory.replace("\\","\\\\") + '"'
        defaultSearch = '"' + defaultSearch + '"'
        webinterface = '"' + webinterface + '"'
        blacklist_words_wii = '"' + blacklist_words_wii + '"'
        blacklist_words_xbox360 = '"' + blacklist_words_xbox360 + '"'
        retention = '"' + retention +'"'

        if(debugEnabled == 'debugEnabled'):
            debugEnabled = "1"
        else:
            debugEnabled = "0"
        if(sabnzbdEnabled == 'sabnzbdEnabled'):
            sabnzbdEnabled = "1"
        else:
            sabnzbdEnabled = "0"
        if(nzbmatrixEnabled == 'nzbmatrixEnabled'):
            nzbmatrixEnabled = "1"
        else:
            nzbmatrixEnabled = "0"
        if(nzbsuEnabled == 'nzbsuEnabled'):
            nzbsuEnabled = "1"
        else:
            nzbsuEnabled = "0"
        if(newznabEnabled == 'newznabEnabled'):
            newznabEnabled = "1"
        else:
            newznabEnabled = "0"        
        if(growlEnabled == 'growlEnabled'):
            growlEnabled = "1"
        else:
            growlEnabled = "0" 
        if(prowlEnabled == 'prowlEnabled'):
            prowlEnabled = "1"
        else:
            prowlEnabled = "0"       
        if(notifoEnabled == 'notifoEnabled'):
            notifoEnabled = "1"
        else:
            notifoEnabled = "0"     
        if(notifymyandroidEnabled == 'notifymyandroidEnabled'):
            notifymyandroidEnabled = "1"
        else:
            notifymyandroidEnabled = "0"
        if(xbmcEnabled == 'xbmcEnabled'):
            xbmcEnabled = "1"
        else:
            xbmcEnabled = "0"     
        if(nzbBlackholeEnabled == 'nzbBlackholeEnabled'):
            nzbBlackholeEnabled = "1"
        else:
            nzbBlackholeEnabled = "0"    
        if(torrentBlackholeEnabled == 'torrentBlackholeEnabled'):
            torrentBlackholeEnabled = "1"
        else:
            torrentBlackholeEnabled = "0"  
        if(katEnabled == 'katEnabled'):
            katEnabled = "1"
        else:
            katEnabled = "0"  
        if(processTorrentsDirectoryEnabled == 'processTorrentsDirectoryEnabled'):
            processTorrentsDirectoryEnabled = "1"
        else:
            processTorrentsDirectoryEnabled = "0"   
        if(processNzbsDirectoryEnabled == 'processNzbsDirectoryEnabled'):
            processNzbsDirectoryEnabled = "1"
        else:
            processNzbsDirectoryEnabled = "0"   
        if(processSabDirectoryEnabled == 'processSabDirectoryEnabled'):
            processSabDirectoryEnabled = "1"
        else:
            processSabDirectoryEnabled = "0"   
        if(processXbox360Enabled == 'processXbox360Enabled'):
            processXbox360Enabled = "1"
        else:
            processXbox360Enabled = "0"               
        if(processWiiEnabled == 'processWiiEnabled'):
            processWiiEnabled = "1"
        else:
            processWiiEnabled = "0"               
        if(processPS3Enabled == 'processPS3Enabled'):
            processPS3Enabled = "1"
        else:
            processPS3Enabled = "0"
        if(processPCEnabled == 'processPCEnabled'):
            processPCEnabled = "1"
        else:
            processPCEnabled = "0"
        if(ps3_tb_enable == 'ps3_tb_enable'):
            ps3_tb_enable = "1"
        else:
            ps3_tb_enable = "0"
        if(clearlog == 'clearlog'):
            clearlog = "1"
        else:
            clearlog = "0"
        if(ps3_jb_enable == 'ps3_jb_enable'):
            ps3_jb_enable = "1"
        else:
            ps3_jb_enable = "0"
        if(https_support == 'https_support'):
            https_support = "1"
        else:
            https_support = "0"


        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        config.set('global','server.socket_host',cherrypyHost)
        config.set('global','gamez_port',cherrypyPort)
        config.set('global','user_name',gamezUsername)
        config.set('global','password',gamezPassword)
        config.set('global','debug_enabled',debugEnabled)
        config.set('NZBMatrix','username',nzbMatrixUsername)
        config.set('NZBMatrix','api_key',nzbMatrixApi)
        config.set('NZBSU','api_key',nzbsuapi)
        config.set('Sabnzbd','host',sabHost)
        config.set('Sabnzbd','port',sabPort)
        config.set('Sabnzbd','api_key',sabApi)
        config.set('Sabnzbd','category',sabCategory)
        config.set('Scheduler','download_interval',downloadInterval)
        config.set('Scheduler','game_list_update_interval',gameListUpdateInterval)
        config.set('SystemGenerated','api_key',gamezApiKey)
        config.set('SystemGenerated','sabnzbd_enabled',sabnzbdEnabled)
        config.set('SystemGenerated','nzbmatrix_enabled',nzbmatrixEnabled)
        config.set('SystemGenerated','nzbsu_enabled',nzbsuEnabled)
        config.set('SystemGenerated','newznab_enabled',newznabEnabled)  
        config.set('SystemGenerated','growl_enabled',growlEnabled)
        config.set('SystemGenerated','prowl_enabled',prowlEnabled)
        config.set('SystemGenerated','notifo_enabled',notifoEnabled)
        config.set('SystemGenerated','notifymyandroid_enabled',notifymyandroidEnabled)
        config.set('SystemGenerated','xbmc_enabled',xbmcEnabled)
        config.set('SystemGenerated','blackhole_nzb_enabled',nzbBlackholeEnabled)
        config.set('SystemGenerated','blackhole_torrent_enabled',torrentBlackholeEnabled)
        config.set('SystemGenerated','torrent_kat_enabled',katEnabled)
        config.set('SystemGenerated','default_search',defaultSearch)
        config.set('SystemGenerated','process_torrent_download_folder_enabled',processTorrentsDirectoryEnabled)
        config.set('SystemGenerated','nzb_completed',processNzbsDirectoryEnabled)
        config.set('SystemGenerated','process_sabnzbd_download_folder_enabled',processSabDirectoryEnabled)
        config.set('SystemGenerated','process_download_folder_xbox360_enabled',processXbox360Enabled)
        config.set('SystemGenerated','process_download_folder_wii_enabled',processWiiEnabled)
        config.set('SystemGenerated','process_download_folder_ps3_enabled',processPS3Enabled)
        config.set('SystemGenerated','process_download_folder_pc_enabled',processPCEnabled)
        config.set('SystemGenerated','webinterface',webinterface)
        config.set('SystemGenerated','ps3_tb_enable',ps3_tb_enable)
        config.set('SystemGenerated','ps3_jb_enable',ps3_jb_enable)      
        config.set('SystemGenerated','blacklist_words_xbox360',blacklist_words_xbox360)
        config.set('SystemGenerated','blacklist_words_wii',blacklist_words_wii)
        config.set('SystemGenerated','clearlog_at_startup',clearlog)
        config.set('SystemGenerated','https_support_enabled',https_support)
        config.set('SystemGenerated','retention',retention)
        config.set('Newznab','host',newznabHost)
        config.set('Newznab','port',newznabPort)
        config.set('Newznab','wii_category_id',newznabWiiCat)
        config.set('Newznab','xbox360_category_id',newznabXbox360Cat)
        config.set('Newznab','ps3_category_id',newznabPS3Cat)
        config.set('Newznab','pc_category_id',newznabPCCat)
        config.set('Newznab','api_key',newznabApi)
        config.set('Notifications','prowl_api',prowlApi)
        config.set('Notifications','growl_host',growlHost)
        config.set('Notifications','growl_port',growlPort)
        config.set('Notifications','growl_password',growlPassword)
        config.set('Notifications','notifo_username',notifoUsername)
        config.set('Notifications','notifo_apikey',notifoApi)
        config.set('Notifications','notifymyandroid_apikey',notifymyandroidApi)
        config.set('Notifications','xbmc_username',xbmcUsername)
        config.set('Notifications','xbmc_password',xbmcPassword)
        config.set('Notifications','xbmc_hosts',xbmcHosts)
        config.set('Blackhole','nzb_blackhole_path',nzbBlackholePath)
        config.set('Blackhole','torrent_blackhole_path',torrentBlackholePath)	
        config.set('Folders','torrent_completed',torrentBlackholeDownloadDirectory)	
        config.set('Folders','nzb_completed',nzbBlackholeDownloadDirectory)
        config.set('Folders','sabnzbd_completed',sabDownloadDirectory)
        config.set('Folders','xbox360_destination',xbox360Destination)
        config.set('Folders','wii_destination',wiiDestination)
        config.set('Folders','ps3_destination',PS3Destination)
        config.set('Folders','pc_destination',PCDestination)
        with open(configfile,'wb') as configFile:
            config.write(configFile)
        status = "Application Settings Updated Successfully. Gamez is restarting. If after 5 seconds, Gamez isn't working, update the Gamez.ini file and re-launch Gamez"
        raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def clearlog(self):
        ClearDBLog()
        raise cherrypy.InternalRedirect('/') 

    @cherrypy.expose
    def api(self,api_key='',mode='',term='',system='',status='',db_id='',data=''):
        config = ConfigParser.RawConfigParser()
        configfile = os.path.abspath(gamez.CONFIG_PATH)
        config.read(configfile)
        systemApiKey = config.get('SystemGenerated','api_key').replace('"','')
        if(api_key == ''):
            return json.dumps({"Error" : "API Key Required"})
        elif(api_key <> systemApiKey):
            return json.dumps({"Error" : "Invalid API Key"})
        else:
            if(mode == 'SEARCH'):
                return ApiGetGamesFromTerm(term,system)
            elif(mode == 'UPDATEGAMELIST'):
            	try:
            	    AddWiiGamesIfMissing()
                    AddXbox360GamesIfMissing()
                    AddComingSoonGames()
                    return json.dumps({"Response":"Game list has been updated successfully"})
            	except:
            	    return json.dumps({"Error" : "Error Updating Game List"})
            elif(mode == 'GETREQUESTED'):
            	return ApiGetRequestedGames()
            elif(mode == 'ADDREQUESTED'):
            	response = {"Error" : mode + " Mode Not Implemented"}
            elif(mode == 'DELETEREQUESTED'):
            	response = {"Error" : mode + " Mode Not Implemented"}   
            elif(mode == 'UPDATEREQUESTEDSTATUS'):
                try:
                    return ApiUpdateRequestedStatus(db_id,status,data)
                except Exception, msg:
                    DebugLogEvent(str(msg))
                    response = {"Error" : " Status was not updatet"}
            elif(mode == 'UPDATEREQUESTEDSTATUSSAB'):
                try:
                    return ApiUpdateRequestedStatus(db_id, status, data, outLog=True)
                except Exception, msg:
                    DebugLogEvent(str(msg))
                    response = {"Error" : " Status was not updatet"}
            elif(mode == 'SEARCHUPCOMING'):
            	response = {"Error" : mode + " Mode Not Implemented"}     
            elif(mode == 'ADDUPCOMINGTOREQUESTED'):
            	response = {"Error" : mode + " Mode Not Implemented"}             	
            else:
                response = {"Error" : mode + " Mode Not Implemented"}
            return json.dumps(response)
        return json.dumps({"Error" : "Unkown Error"})     

    @cherrypy.expose
    def updategamelist(self):
        AddWiiGamesIfMissing()
        AddXbox360GamesIfMissing()
        AddComingSoonGames()
        status = "Game list has been updated successfully"
        raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        status = "Gamez will be shutting down!!! Bye"
        raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def reboot(self):
        cherrypy.engine.restart()
        status = "Gamez will be restart!!!"
        raise cherrypy.InternalRedirect("/?status_message=" + status)

    @cherrypy.expose
    def forcesearch(self,dbid):
        if(os.name <> 'nt'):
            os.chdir(WebRoot.appPath)
        GameTasks().ForceSearch(dbid)  
        raise cherrypy.InternalRedirect('/')
