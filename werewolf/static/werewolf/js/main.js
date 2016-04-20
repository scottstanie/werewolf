$(document).ready(function(){
  // CSRF setup for ajax calls
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  var $gameInfo = $('#game-info');
  var requestUser = $gameInfo.data('request-user');
  var username = $gameInfo.data('username');
  var gameName = $gameInfo.data('game-name');
  var gameSize = parseInt($('#game-size').text());
  var readyUsers = findReadyUsers();
  checkGameReady(readyUsers, gameSize);

	// When we're using HTTPS, use WSS too.
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

  chatsock.onmessage = function(message) {
      var data = JSON.parse(message.data);
      if (!_.includes(readyUsers, data.user)) {
        $('#ready-user-list').append(
            '<li class="ready-user">' + data.user + '</li>'
        );
      };
      readyUsers = findReadyUsers();
      checkGameReady(readyUsers, gameSize);
  };


  $("#ready").on("click", function() {
    var url = '/ready/' + gameName + '/' + requestUser;
    var allowed = false;
    $.ajax({
      type: 'GET',
      url: url,
      success: function(result) {
        allowed = result['allowed'];
        console.log('Ajax return!');
        if (result['allowed']) {
          var message = {
              handle: $('#handle').val(),
              message: $('#message').val(),
              user: username,
          }
          chatsock.send(JSON.stringify(message));
        }
        $("#message").val('').focus();
      },
    });
  });
});

function findReadyUsers() {
 return $('.ready-user').map(function() {
    return $(this).text();
  })
}


function checkGameReady(readyUsers, gameSize) {
  if (readyUsers.length >= gameSize) {
    $('#buttons').append(
      '<button type="submit" id="start">Start!!</button>'
    );
    console.log('ready!!!');
  }
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
