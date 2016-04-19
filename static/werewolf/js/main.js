
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
  var requestUser = $('#user-info').data('request-user');

	// When we're using HTTPS, use WSS too.
  var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
  var chatsock = new ReconnectingWebSocket(ws_scheme + '://' + window.location.host + "/chat" + window.location.pathname);

  chatsock.onmessage = function(message) {
      var data = JSON.parse(message.data);
      var chat = $("#chat")
      var ele = $('<tr></tr>')

      ele.append(
          $("<td></td>").text(data.timestamp)
      )
      ele.append(
          $("<td></td>").text(data.handle)
      )
      ele.append(
          $("<td></td>").text(data.message)
      )

      chat.append(ele)
  };

  $("#chatform").on("submit", function(event) {
      var message = {
          handle: $('#handle').val(),
          message: $('#message').val(),
      }
      chatsock.send(JSON.stringify(message));
      $("#message").val('').focus();
      return false;
  });
});

// Check if there are games waiting
function checkWaiting(requestUser) {
  $.ajax({
    type: 'GET',
    url: '/waiting/' + requestUser,
    success: function(result) {
      if(result['waitingOnYou']) {
        setWaiting();
      };
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
