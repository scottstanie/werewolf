function startTimer(duration, $display) {
    var timer = duration;
    var minutes, seconds;
    setInterval(function () {
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        $display.text(minutes + ":" + seconds);

        if (--timer < 0) {
            timer = duration;
        }
    // Tick every second
    }, 1000);
}

function displayTimer()
    var fiveMinutes = 60 * 5;
    var $display = $('#timer');
    startTimer(fiveMinutes, $display);
});
