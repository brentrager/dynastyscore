function timeStamp()
{
    // Create a date object with the current time
    var now = new Date();
    // Create an array with the current month, day and time
    var date = [ now.getMonth() + 1, now.getDate(), now.getFullYear() ];
    // Create an array with the current hour, minute and second
    var time = [ now.getHours(), now.getMinutes(), now.getSeconds() ];
    // Determine AM or PM suffix based on the hour
    var suffix = ( time[0] < 12 ) ? "AM" : "PM";
    // Convert hour from military time
    time[0] = ( time[0] < 12 ) ? time[0] : time[0] - 12;
    // If hour is 0, set it to 12
    time[0] = time[0] || 12;
    // If seconds and minutes are less than 10, add a zero
    for ( var i = 1; i < 3; i++ )
    {
        if ( time[i] < 10 )
        {
            time[i] = "0" + time[i];
        }
    }
    // Return the formatted string
    return date.join(".") + "-" + time.join(":") + "-" + suffix;
}

function loadRankings(data)
{
    $.ajax({
        url: $("#generate-dynasty-score-uri").html(),
        data: data,
        type: "POST",
        success: function(response)
        {
            $("#rankingsContainer").html(response);

            if ($("#leagueName").html()) {
                var pathArray = window.location.pathname.split( '/' );
                var timeStamp = pathArray[3];
                document.title = $("#leagueName").html() + " - " + timeStamp + " - Rankings";
            }

            var rankingsContainer = $("#rankingsContainer");
            setTimeout(function() {
                html2canvas(rankingsContainer, {
                    width: 1200,
                    onrendered: function(canvas) {
                        postCanvasToURL("/image" + window.location.pathname, "file", "file.png", canvas, "image/png");
                    }
                });
            }, 500);
        },
        error: function(error)
        {
            $("#rankingsContainer").html(error);
        }
    });
}

function showFullRankings(element)
{
    var rankingTitle = element.find("thead").find("th").html();

    if (rankingTitle)
    {
        fullRankingId = "#ranking-roster-" + rankingTitle.replace(/ /g, "-");
        var fullRankings = $(fullRankingId);
        $.fancybox(fullRankings);
    }
}

if (!('sendAsBinary' in XMLHttpRequest.prototype)) {
  XMLHttpRequest.prototype.sendAsBinary = function(string) {
    var bytes = Array.prototype.map.call(string, function(c) {
      return c.charCodeAt(0) & 0xff;
    });
    this.send(new Uint8Array(bytes).buffer);
  };
}

/*
 * @description        Uploads a file via multipart/form-data, via a Canvas elt
 * @param url  String: Url to post the data
 * @param name String: name of form element
 * @param fn   String: Name of file
 * @param canvas HTMLCanvasElement: The canvas element.
 * @param type String: Content-Type, eg image/png
 ***/
function postCanvasToURL(url, name, fn, canvas, type) {
  var data = canvas.toDataURL(type);
  data = data.replace('data:' + type + ';base64,', '');

  var xhr = new XMLHttpRequest();
  xhr.open('POST', url, true);
  var boundary = 'ohaiimaboundary';
  xhr.setRequestHeader(
    'Content-Type', 'multipart/form-data; boundary=' + boundary);
  xhr.sendAsBinary([
    '--' + boundary,
    'Content-Disposition: form-data; name="' + name + '"; filename="' + fn + '"',
    'Content-Type: ' + type,
    '',
    atob(data),
    '--' + boundary + '--'
  ].join('\r\n'));
}

function initiateYahooOauth() {
    $("#formContainer").html('<img src="/static/img/loading.gif" alt="Loading..." class="img-responsive img-center"/>');
    key = uuid.v1();

    $.ajax({
        url: $("#yahoo-leagues-uri").html().replace('REPLACE_WITH_KEY', key),
        type: "GET",
        success: function(response)
        {
            if (response.authUri) {
                window.location.href = response.authUri;
            }
        },
        error: function(error)
        {
            console.error(error);
        }
    });
}

$( document ).ready(function() {
    $("body").on("click", "div.ranking", function()
    {
        console.log("Div");
        showFullRankings($(this));
    });

    $("body").on("click", "a.ranking-zoom", function(e)
    {
        e.preventDefault();
        showFullRankings($(this).parent("div.ranking"));
    });

    $("#dynastyScoreForm").submit(function(event)
    {
        var form = $("#dynastyScoreForm");
        if (!form.attr("action"))
        {
            event.preventDefault();
            var pathArray = window.location.pathname.split( '/' );
            if (pathArray.length > 1) pathArray.shift();

            var action = "/" + $("input:radio[name ='leagueHost']:checked").val() + "/" + $("input#leagueId").val() + "/" + timeStamp() + "/" + $("input:radio[name ='rankingsType']:checked").val() + "/";
            if (pathArray[0] === "yahoo") {
                var action = "/yahoo/" + $("input:radio[name ='leagueId']:checked").val() + "/" + timeStamp() + "/" + $("input:radio[name ='rankingsType']:checked").val() + "/";
            }
            form.attr("action", action).submit()
        }
    });

    $("input[name='leagueHost']").change(function(e)
    {
        if ($(this).val() == "yahoo")
        {
            $("div#leagueId").hide()
            initiateYahooOauth();
        }
        else
        {
            $("div#leagueId").show()
        }
    });
});
