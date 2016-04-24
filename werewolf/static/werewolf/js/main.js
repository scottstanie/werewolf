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
      if (data.starting) {
        console.log(data);
        $('body').empty();
        $('body').append(data.characters[requestUser]);
      } else {
        console.log(readyUsers);
        if (! _.includes(readyUsers, data.user)) {
          $('#ready-user-list').append(
              '<li class="ready-user">' + data.user + '</li>'
          );
        };
        readyUsers = findReadyUsers();
        checkGameReady(readyUsers, gameSize);
      }
  };


  $("#ready").on("click", function() {
    var readyUrl = '/ready/' + gameName + '/' + requestUser;
    var allowed = false;
    $.ajax({
      type: 'GET',
      url: readyUrl,
      success: function(result) {
        allowed = result['allowed'];
        if (result['allowed']) {
          var message = {
              starting: false,
              user: username,
          }
          chatsock.send(JSON.stringify(message));
        }
      },
    });
  });

  $('body').on('click', '#start', function() {
    var startUrl = '/start/' + gameName;
    var chosenCharacters = getChosenCharacters();
    $.ajax({
      type: 'POST',
      url: startUrl,
      data: {chars: JSON.stringify(chosenCharacters)},
    });
  });


  $('.character').on('click', function() {
    $(this).toggleClass('chosen');
  });

  // Seer view logic
  $('body').on('click', '.seer.pick-one', function() {
    $(this).next().removeClass('disabled');
    $('.pick-one').removeClass('pick-one');
  });

  // Robber view logic
  $('body').on('click', '.robber.pick-one', function() {
    var robbedUser = $(this).data('robbed-id')
    $(this).next().removeClass('disabled');
    $('.pick-one').removeClass('pick-one');
    // TODO: record the robbing action
    // requestUser, robbedId
  });

});

function findReadyUsers() {
 return $('.ready-user').map(function() {
    return $(this).text();
  })
}


function checkGameReady(readyUsers, gameSize) {
  if (readyUsers.length >= gameSize) {
    if ($('#buttons').children().length == 1) {
      $('#buttons').append(
        '<button type="submit" id="start">Start!!</button>'
      );
      console.log('ready!!!');
    }
  }
}

function getChosenCharacters() {
  return $.map($('.character.chosen'), function(c) {
    return $(c).children('p').data('id');
  })
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
