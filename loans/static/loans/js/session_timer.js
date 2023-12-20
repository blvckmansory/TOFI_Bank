document.addEventListener('DOMContentLoaded', function () {
  var timerElement = document.getElementById('timer');

  function formatTime(hours, minutes, seconds) {
      return (hours < 10 ? '0' : '') + hours + ':' +
             (minutes < 10 ? '0' : '') + minutes + ':' +
             (seconds < 10 ? '0' : '') + seconds;
  }

  function updateTimer() {
      var currentTimer = timerElement.innerText.split(':');
      var hours = parseInt(currentTimer[0], 10);
      var minutes = parseInt(currentTimer[1], 10);
      var seconds = parseInt(currentTimer[2], 10);

      // Уменьшаем время на одну секунду
      if (seconds > 0) {
          seconds--;
      } else if (minutes > 0) {
          minutes--;
          seconds = 59;
      } else if (hours > 0) {
          hours--;
          minutes = 59;
          seconds = 59;
      }

      // Обновляем отображение времени
      timerElement.innerText = formatTime(hours, minutes, seconds);

      // Проверяем, достигли ли нуля
      if (hours === 0 && minutes === 0 && seconds === 0) {
          // Если достигли нуля, перезагружаем страницу
          location.reload();
      }
  }

  // Вызываем функцию обновления каждую секунду
  setInterval(updateTimer, 1000);
});
