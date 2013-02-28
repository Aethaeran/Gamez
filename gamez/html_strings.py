import os
import gamez
import ConfigParser
from gamez import common
from gamez.classes import Platform

top = """
        <!DOCTYPE html>
        <html>
          <head>
            <title>Gamez</title>
            <link rel="stylesheet" type="text/css" href="css/navigation.css" />
            <link rel="stylesheet" type="text/css" href="css/smoothness/jquery-ui-1.10.1.custom.min.css" />
            <link rel="stylesheet" type="text/css" href="css/datatables.css" />
            <link rel="shortcut icon" href="images/favicon.ico">
            <script type="text/javascript" src="js/jquery.min.js"></script>
            <script type="text/javascript" src="js/jquery-ui-1.10.1.custom.min.js"></script>
            <script type="text/javascript" src="js/stupidtable.min.js"></script>
            </head><body id="dt_example">"""

bottom_js = """
            <script>
                $(document).ready(function() {
                    $("table.display").stupidtable();
                    $.widget( "custom.catcomplete", $.ui.autocomplete, {
                        _renderMenu: function( ul, items ) {
                          var that = this,
                            currentCategory = "";
                          $.each( items, function( index, item ) {
                            if ( item.system != currentCategory ) {
                              ul.append( "<li class='ui-autocomplete-category'>" + item.system + "</li>" );
                              currentCategory = item.system;
                            }
                            that._renderItemData( ul, item );
                          });
                        }
                      });

                    $("#search").catcomplete({
                        source:"/get_game_list/",
                        minChars: 2,
                        max:25,
                        dataType:'json',
                        select: function( event, ui ) {
                            $('#systemDropDown').val(ui.item.system);
                            $('#searchButton').click();
                        },
                        focus: function( event, ui ) {
                            $('#systemDropDown').val(ui.item.system);
                        }
                    });
                    $("button").button().click(function(){
                        var searchText = $("#search").val();
                        var system = $("#systemDropDown").val();
                        if(system == "---"){
                            system = "";
                        }
                        document.location.href = "search?term=" + searchText + "&system=" + system;
                    });
                });
            </script>
            """

bottom = """</div></body></html>"""


def menu():
    #config = ConfigParser.RawConfigParser()
    #configfile = os.path.abspath(gamez.CONFIG_PATH)
    #config.read(configfile)
    #defaultSearch = config.get('SystemGenerated', 'default_search').replace('"', '')

    options = ['<option>---</option>']
    for p in Platform.select():
        options.append('<option value="' + str(p.id) + '">' + p.name + '</option>')

    defaultSearch = "\n".join(options)

    return """
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
                <div style="text-align:right;margin-right:20px;position: absolute;right: 0;">
                    <div class=ui-widget>
                        <INPUT id=search />
                        &nbsp;
                        <select id="systemDropDown">""" + defaultSearch + """</select>
                        &nbsp;
                        <button style="margin-top:8px" id="searchButton" class="ui-widget" style="font-size:15px" name="searchButton" type="submit">Search</button>
                    </div>
                </div>
            </div>
            <div style="visibility:hidden"><a href="http://apycom.com/">jQuery Menu by Apycom</a></div>
            <div id="container">"""


