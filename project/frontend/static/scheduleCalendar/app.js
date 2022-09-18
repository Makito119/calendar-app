axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

document.addEventListener("DOMContentLoaded", function () {
  // CSRF対策

  var calendarEl = document.getElementById("calendar");
  // let calendar = new FullCalendar.Calendar(calendarEl, {
  //   //plugins: [ dayGridPlugin, timeGridPlugin, listPlugin ],
  //   initialView: 'dayGridMonth',
  

  // });
  window.onload = function(){
 
    // テキストボックスのDOMを取得
    const username = document.getElementById("username");
    // 活性/非活性を切り替えるボタンのDOMを取得
    const button = document.getElementById("sendbutton");
    
    username.addEventListener('keyup', function() {
      // テキストボックスに入力された値を取得
      const text = username.value;
      console.log(text);
      
      if(text) {
        // 入力文字があれば、display:noneを指定したクラスを取り除く
        button.className = null;
      } else {
        // 入力文字がなければ、display: noneを指定したクラスを設定する
        button.className = "hidden";
      }
    })
  }
  var calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "timeGridWeek",
    fisrtDay:5,
    editable: true,
    // 日付をクリック、または範囲を選択したイベント
    selectable: true,
  
    headerToolbar: {
      left: "prev,next,today",
      center: "title",
      right: "timeGridWeek,dayGridMonth",
    },
    views:{
      timeGridWeek:{
        slotMinTime: '09:00:00',
        slotMaxTime: '24:00:00',
      }
    },
    timeZone: "Asia/Tokyo",
  
    eventColor: '#ff8c00',

    locale: "ja",
    navLinks: true,
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
