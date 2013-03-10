// Avoid `console` errors in browsers that lack a console.
(function() {
    var method;
    var noop = function () {};
    var methods = [
        'assert', 'clear', 'count', 'debug', 'dir', 'dirxml', 'error',
        'exception', 'group', 'groupCollapsed', 'groupEnd', 'info', 'log',
        'markTimeline', 'profile', 'profileEnd', 'table', 'time', 'timeEnd',
        'timeStamp', 'trace', 'warn'
    ];
    var length = methods.length;
    var console = (window.console = window.console || {});

    while (length--) {
        method = methods[length];

        // Only stub undefined methods.
        if (!console[method]) {
            console[method] = noop;
        }
    }
}());

// Place any jQuery/helper plugins in here.
(function(){

    $.Browser = {
        defaults: {
            title:             'Choose Directory',
            url:               'http://localhost:8085/browser/',
            autocompleteURL:   'http://localhost:8085/browser/complete'
        }
    };

    var fileBrowserDialog  = null;
    var currentBrowserPath = null;
    var currentRequest     = null;

    function browse(path, endpoint) {

        if(currentBrowserPath == path)
            return;
        
        currentBrowserPath = path;
        
        if(currentRequest)
            currentRequest.abort();
            
        fileBrowserDialog.dialog('option', 'dialogClass', 'browserDialog busy');
        
        currentRequest = $.getJSON(endpoint, { path: path }, function(data){
            fileBrowserDialog.empty();
            var first_val = data[0];
            var i = 0;
            data = jQuery.grep(data, function(value) {
                return i++ != 0;
            });
            $('<h3>').text(first_val.current_path).appendTo(fileBrowserDialog);
            list = $('<ul>').appendTo(fileBrowserDialog);
            $.each(data, function(i, entry) {
                link = $("<a href='javascript:void(0)' />").click(function(){ browse(entry.path, endpoint); }).text(entry.name);
                $('<span class="ui-icon ui-icon-folder-collapsed"></span>').prependTo(link);
                link.hover(
                    function(){jQuery("span", this).addClass("ui-icon-folder-open");    },
                    function(){jQuery("span", this).removeClass("ui-icon-folder-open"); }
                );
                link.appendTo(list);
            });
            $("a", list).wrap('<li class="ui-state-default ui-corner-all">');
            fileBrowserDialog.dialog('option', 'dialogClass', 'browserDialog');
        });
    }

    $.fn.nFileBrowser = function(callback, options){
        
        options = $.extend({}, $.Browser.defaults, options);
        
        // make a fileBrowserDialog object if one doesn't exist already
        if(!fileBrowserDialog) {
        
            // set up the jquery dialog
            fileBrowserDialog = $('<div id="fileBrowserDialog" style="display:hidden"></div>').appendTo('body').dialog({
                dialogClass: 'browserDialog',
                title:       options.title,
                position:    ['center', 40],
                minWidth:    Math.min($(window).width()-80, 650),
                minHeight:   320,
                height:      $(window).height()-80,
                modal:       true,
                autoOpen:    false
            });
        }
        
        // add the OK/Close buttons to the dialog
        fileBrowserDialog.dialog('option', 'buttons',
        {
            "Ok": function(){
                callback(currentBrowserPath, options);
                fileBrowserDialog.dialog("close");
            },

            "Cancel": function(){
                fileBrowserDialog.dialog("close");
            }
            
        });
        
        // set up the browser and launch the dialog
        if (options.initialDir)
            initialDir = options.initialDir;
        else
            initialDir = '';
        browse(initialDir, options.url)
        fileBrowserDialog.dialog('open');

        return false;
    };

    $.fn.fileBrowser = function(options){
        options = $.extend({}, $.Browser.defaults, options);
        
        // text field used for the result
        options.field = $(this);
        
        if(options.field.autocomplete && options.autocompleteURL) {
            options.field.autocomplete({ 
                source: options.autocompleteURL,
                open: function(event, ui) { 
                    $(".ui-autocomplete li.ui-menu-item a").removeClass("ui-corner-all");
                    $(".ui-autocomplete li.ui-menu-item:odd a").addClass("ui-menu-item-alternate");
                }
            });
        }
        
        callback = function(path, options){
            // store the browsed path to the associated text field
            options.field.val(path);
        
        }

        initialDir = options.field.val() || '';
        
        options = $.extend(options, {initialDir: initialDir})
        
        // append the browse button and give it a click behavior
        return options.field.addClass('fileBrowserField').after($('<input type="button" value="Browse&hellip;" class="fileBrowser" />').click(function(){
            
            $(this).nFileBrowser(callback, options);
            
            return false;
        }));
    };
})();
