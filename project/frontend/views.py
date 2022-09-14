from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import json
from .models import Event
from .forms import EventForm
from django.http import Http404
import time
from django.middleware.csrf import get_token
from django.http import JsonResponse
from .forms import CalendarForm
from django.views import View
import datetime


def index(request, *args, **kwargs):
   return render(request, 'frontend/index.html')
# Create your views here.

def index1(request):
    """
    カレンダー画面
    """
    get_token(request)

    template = loader.get_template("scheduleCalendar/index.html")
    return HttpResponse(template.render())
# def form1(request):
#     """
#     カレンダー画面
#     """
    

#     template = loader.get_template("scheduleCalendar/form1.html")
#     return HttpResponse(template.render())

class HelloView(View):
    def get(self, request, *args, **kwargs):
     
        context = {
            'message': " GOT now! from View!!",
        }
        return render(request, 'scheduleCalendar/form1.html', context)

    def post(self, request, *args, **kwargs):
   
        context = {
            'message': "POST OK!!",
            'shcedule':request.POST['schedule'],
            'priority':int(request.POST['priority']),
            'time':datetime.time(int(request.POST['time'].split(":")[0]),int(request.POST['time'].split(":")[1])),
            'timerange_begin':request.POST['timerange_begin'],
            'timerange_end':request.POST['timerange_end'],
        }


        print(context)
        print(context['time'].hour,context['time'].minute)
        return render(request, 'scheduleCalendar/form1.html', context)

def form1(request):
  if request.method =="GET":

    context = {
            'message': " GOT now! from View!!",
        }
    return render(request, 'scheduleCalendar/form1.html', context)
  elif request.method=="POST":
    context = {
            'message': "POST OK!!",
            'shcedule':request.POST['schedule'],        
            'time':datetime.time(int(request.POST['time'].split(":")[0]),int(request.POST['time'].split(":")[1])),
            'timerange_begin':request.POST['timerange_begin'],
            'timerange_end':request.POST['timerange_end'],
            'priority':int(request.POST['priority']),
        }
    print(context)
    print(context['time'].hour,context['time'].minute)
    return render(request, 'scheduleCalendar/form1.html', context)

  else:
    raise Http404()

# form1 = HelloView.as_view()
form2 = HelloView.as_view()
# def result(request):
#   context = {
#             'input_text': request.POST['schedule'],

#         }
  
#   datas = json.loads(request.body)
#   print(datas)
#   return render(request,'result.html',context)

def add_event(request):
    """
    イベント登録
    """

    if request.method == "GET":
        # GETは対応しない
        raise Http404()

    # JSONの解析
    datas = json.loads(request.body)

    # バリデーション
    eventForm = EventForm(datas)
    if eventForm.is_valid() == False:
        # バリデーションエラー
        raise Http404()

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]
    event_name = datas["event_name"]

    # 日付に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_date = time.strftime(
        "%Y-%m-%d", time.localtime(start_date / 1000))
    formatted_end_date = time.strftime(
        "%Y-%m-%d", time.localtime(end_date / 1000))

    # 登録処理
    event = Event(
        event_name=str(event_name),
        start_date=formatted_start_date,
        end_date=formatted_end_date,
    )
    event.save()


    # 空を返却
    return HttpResponse("")

def get_events(request):
    """
    イベントの取得
    """

    if request.method == "GET":
        # GETは対応しない
        raise Http404()

    # JSONの解析
    datas = json.loads(request.body)

    # バリデーション
    calendarForm = CalendarForm(datas)
    if calendarForm.is_valid() == False:
        # バリデーションエラー
        raise Http404()

    # リクエストの取得
    start_date = datas["start_date"]
    end_date = datas["end_date"]

    # 日付に変換。JavaScriptのタイムスタンプはミリ秒なので秒に変換
    formatted_start_date = time.strftime(
        "%Y-%m-%d", time.localtime(start_date / 1000))
    formatted_end_date = time.strftime(
        "%Y-%m-%d", time.localtime(end_date / 1000))

    # FullCalendarの表示範囲のみ表示
    events = Event.objects.filter(
        start_date__lt=formatted_end_date, end_date__gt=formatted_start_date
    )

    # fullcalendarのため配列で返却
    list = []
    for event in events:
        list.append(
            {
                "title": event.event_name,
                "start": event.start_date,
                "end": event.end_date,
            }
        )

    return JsonResponse(list, safe=False)