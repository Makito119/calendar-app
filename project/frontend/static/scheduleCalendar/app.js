axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

document.addEventListener("DOMContentLoaded", function () {
  // CSRF対策

  var calendarEl = document.getElementById("calendar");
  
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",

    // 日付をクリック、または範囲を選択したイベント
    selectable: true,
    select: function (info) {
      //alert("selected " + info.startStr + " to " + info.endStr);
      const eventName = prompt("イベントを入力してください");

      if (eventName) {
        // イベントの追加
        // 登録処理の呼び出し
        axios
          .post("add/", {
            start_date: info.start.valueOf(),
            end_date: info.end.valueOf(),
            event_name: eventName,
          })
          .then(() => {
            // イベントの追加
            calendar.addEvent({
              title: eventName,
              start: info.start,
              end: info.end,
              allDay: true,
            });
          })
          .catch(() => {
            // バリデーションエラーなど
            alert("登録に失敗しました");
          });
      }
    },

    events: function (info, successCallback, failureCallback) {
      axios
        .post("list/", {
          start_date: info.start.valueOf(),
          end_date: info.end.valueOf(),
        })
        .then((response) => {
          calendar.removeAllEvents();
          successCallback(response.data);
        })
        .catch(() => {
          // バリデーションエラーなど
          alert("登録に失敗しました");
        });
    },
  });

  calendar.render();
});


