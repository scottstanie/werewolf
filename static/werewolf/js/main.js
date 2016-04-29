window.stageInfo = {};
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

  // Only set the stage info on the first round of moves
  var stageInfo, countdownTime, moveTime;
  chatsock.onmessage = function(message) {
      var data = JSON.parse(message.data);
      if (data.starting || data.advancing) {
          // Midgame message logic
          console.log(data);
          if (data.starting) {
            stageInfo = data.stage_info;
            countdownTime = data.countdown_time;
            // Define the movetime only for the game driver
            moveTime = 1000 * parseInt($('#move-time').val());
          };

          console.log('Stage Info:');
          console.log(stageInfo);

          $('body').empty();
          if (data.current_stage > 4) {
            $('body').append('<h2 id="timer"></h2>')
            startTimer(countdownTime, $('#timer'), gameName);
            return;

          } else if ((stageInfo[requestUser] === 0) ||
              (stageInfo[requestUser] === data.current_stage)) {
            $('body').append(data.characters[requestUser]);
          } else {
            $('body').append('<h2>Waiting...</h2>');
          };
          console.log('Wait Time');
          console.log(moveTime);
          if (!isNaN(moveTime)) {
            setTimeout(
                function() {
                  signalAdvance(gameName, requestUser);
                }, moveTime
            );
          }
      } else if (data.finished) {
        // End game logic
        var winners = data.winners;
        console.log(winners);
        var votes = data.votes;
        console.log(votes);
        $('body').empty();
        $('body').append(
            '<div id="finished"> ' +
            'Winning Teams:<ul id="winners"></ul>' +
            'Votes (excluding self-votes): <ul id="votes"></ul></div>');
        for (var i=0; i < winners.length; i++) {
          $('#winners').append('<li>' + winners[i] + '</li>')
        }
        for (user in votes) {
          $('#votes').append('<li>' + user + ': ' + votes[user] + '</li>')
        }
      } else {
        // Pregame ready signals
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
      type: 'POST',
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
    countdownTime =  parseInt($('#countdown-time').val());
    var startUrl = '/start/' + gameName;
    var chosenCharacters = getChosenCharacters();
    $.ajax({
      type: 'POST',
      url: startUrl,
      data: {
        chars: JSON.stringify(chosenCharacters),
        countdownTime: countdownTime,
      },
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

  // Drunk view logic
  $('body').on('click', '.drunk.pick-one', function() {
    $('.pick-one').removeClass('pick-one');
    var afterId = $(this).data('after-id');
    var beforeId = $(this).data('before-id');
    // Drunk initiates switch on himself
    var initiatorId = beforeId;
    var switchUrl = '/switch/' + initiatorId + '/' + beforeId + '/' + afterId;
    $.ajax({
      type: 'POST',
      url: switchUrl,
      success: function(result) {
        console.log(result);
      }
    });
  });

  // Robber view logic
  $('body').on('click', '.robber.pick-one', function() {
    var robbedVictimId = $(this).data('victim-id');
    var robberId = $(this).data('robber-id');
    var initiatorId = robberId;
    $(this).next().removeClass('disabled');
    $('.pick-one').removeClass('pick-one');

    // Record a switch for each players card, initiated by the robber
    var url = '/switch/' + initiatorId + '/' + robberId + '/' + robbedVictimId;
    $.ajax({
      type: 'POST',
      url: url,
      success: function(result) {
        console.log(result);
      }
    });
    var url = '/switch/' + initiatorId + '/' + robbedVictimId + '/' + robberId;
    $.ajax({
      type: 'POST',
      url: url,
      success: function(result) {
        console.log(result);
      }
    });
  });

  // Insomniac view logic
  $('body').on('click', '.insomniac.pick-one', function() {
    $(this).next().removeClass('disabled');
    $('.pick-one').removeClass('pick-one');
  });

  // Voting view logic
  $('body').on('click', '.vote.pick-one', function() {
    $('.pick-one').removeClass('pick-one');
    var playerId = $(this).data('player-id');
    var voteUrl = '/vote/' + gameName;
    $.ajax({
      type: 'POST',
      url: voteUrl,
      data: {
        playerId: playerId,
      }
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

function signalAdvance(gameName, userId) {
  var readyUrl = '/advance/' + gameName + '/' + userId;
  $.ajax({
    type: 'POST',
    url: readyUrl,
    success: function(result) {
      console.log(result);
    },
  });
}

function startTimer(duration, $display, gameName) {
    var timer = duration;
    var minutes, seconds;

    function checkFinished(gameName, intervalId) {
      // End condition
      if (timer === 0) {
          clearInterval(intervalId);
          triggerVoting(gameName);
          timer--;
          return true;
      } else {
        // otherwise, check in a second
        setTimeout(function() {
          checkFinished(gameName, intervalId);
        }, 1000)
      };
    }

    refreshIntervalId = setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        $display.text(minutes + ":" + seconds);

        timer--;

    // Tick every second
    }, 1000);

    checkFinished(gameName, refreshIntervalId);
}

function triggerVoting(gameName) {
  console.log('VOTE!');
  setTimeout(function() {
    $('#timer').text('Time is up!');
  }, 500);
  setTimeout(function() {
    $('#timer').text('3!');
  }, 2000);
  setTimeout(function() {
    $('#timer').text('2!');
  }, 3000);
  setTimeout(function() {
    $('#timer').text('1!');
  }, 4000);
  setTimeout(function() {
    $('#timer').text('Vote!');
  }, 5000);
  // Retrieve the voting view
  $.ajax({
    type: 'GET',
    url: '/vote/' + gameName,
    success: function(result) {
      console.log(result);
      setTimeout(function() {
        $('body').empty();
        $('body').append(result['template']);
      }, 5500);
    },
  });

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
