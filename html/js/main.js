

var playPath = 'M11.166,23.963L22.359,17.5c1.43-0.824,1.43-2.175,0-3L11.166,8.037c-1.429-0.826-2.598-0.15-2.598,1.5v12.926C8.568,24.113,9.737,24.789,11.166,23.963z';
var playPathS = 'M84.23,73H17.968C8.91,73,1.54,65.63,1.54,56.571V20.429C1.54,11.37,8.91,4,17.968,4H84.23   c9.059,0,16.428,7.37,16.428,16.429v36.143C100.658,65.63,93.289,73,84.23,73z M17.968,13.857c-3.624,0-6.571,2.948-6.571,6.571   v36.143c0,3.624,2.948,6.571,6.571,6.571H84.23c3.623,0,6.571-2.947,6.571-6.571V20.429c0-3.624-2.948-6.571-6.571-6.571H17.968z'
var playPathS2 = 'M42.611,23.34c0-1.344,0.898-1.809,1.995-1.029l20.802,14.774c1.096,0.779,1.096,2.053,0,2.832L44.605,54.69  c-1.097,0.778-1.995,0.315-1.995-1.031V23.34z'
    
$(document).ready(function() {
    $(".youtube").youtube();
    $(".youtube").fancybox({
        openEffect  : 'none',
        closeEffect : 'none',
        nextEffect  : 'none',
        prevEffect  : 'none',
        padding     : 0,
        margin      : [20, 60, 20, 60] // Increase left/right margin
    });
    
    $('td.cover a').each(function(){
        var playPaper = new Raphael(this, 100, 77);
        var playIcon1 = playPaper.path(playPathS).attr({fill: "#e6311b", stroke: "none"});
        var playIcon2 = playPaper.path(playPathS2).attr({fill: "#e6311b", stroke: "none"});
        //playIcon.transform('s1.5')
    });

});
