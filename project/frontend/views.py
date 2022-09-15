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
from django.template import loader
from django.http import HttpResponse
from django.middleware.csrf import get_token
import datetime
import json
from .models import Event
from .forms import EventForm
from django.http import Http404
import time
from django.http import JsonResponse
from .models import input_Timerange
from .models import input_Event
import uuid
from re import A, T
from dataclasses import dataclass
from django.db import models
import copy

@dataclass
class sc_Event:
    event_Id: str #ID：int
    name: str #名前：string
    required_Time: datetime.timedelta #時間：datetime.timedelta
    priority: int #優先度：int
    timeRanges: list #調整可能時刻リスト：[[datetime.datetime, datetime.datetime]]

@dataclass
class confirmed_Event:
    event_Id: str 
    name: str 
    required_Time: datetime.timedelta 
    priority: int 
    timeRanges: list 
    confirmed_Time: list # 決定時刻[start, end]

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

def scheduling():
    
    #-test用データ作成
    # t1=datetime.datetime(2022,9,15,12,0,0,0)
    # t2=datetime.datetime(2022,9,15,13,0,0,0)
    # t3=datetime.datetime(2022,9,15,14,0,0,0)
    # t4=datetime.datetime(2022,9,15,15,0,0,0)
    # t5=datetime.datetime(2022,9,16,12,0,0,0)
    # t6=datetime.datetime(2022,9,16,13,0,0,0)
    # t7=datetime.datetime(2022,9,16,14,0,0,0)
    # t8=datetime.datetime(2022,9,16,15,0,0,0)

    # t9=datetime.timedelta(hours=1)
    # t10=datetime.timedelta(hours=2)
    # t11=datetime.timedelta(hours=3)

    # Event1=sc_Event(1,"テスト1",t9,5,[[t1,t2]])
    # Event2=sc_Event(2,"テスト2",t9,3,[[t3,t4],[t6,t8]])
    # Event3=sc_Event(3,"テスト3",t9,4,[[t2,t4]])
    # Event4=sc_Event(4,"テスト4",t9,2,[[t3,t4]])
    # Event5=sc_Event(5,"テスト5",t9,1,[[t3,t4]])
    # Event6=sc_Event(6,"テスト6",t9,1,[[t5,t7]])
    # Event7=sc_Event(7,"テスト7",t9,5,[[t7,t8]])
    # Event8=sc_Event(8,"テスト8",t9,2,[[t5,t7]])
    # Event9=sc_Event(9,"テスト9",t9,4,[[t5,t6]])

    #datas = json.loads(request.body)
    start_date = datetime.datetime.now()
    #formatted_start_date = time.strftime("%Y-%m-%d", time.localtime(start_date / 1000))

    input_timerange_datas = input_Timerange.objects.filter(start_Date__gte=start_date)
    #IDリストの作成
    input_timerange_id_list =[]
    for input_timerange_data in input_timerange_datas:
        if not input_timerange_data.event_id in input_timerange_id_list:
            #IDリストにIDを追加  ["1", "aa", "apple"]
            input_timerange_id_list.append(input_timerange_data.event_id)
        
    #保存したIDをもとに検索をかけてInput_Eventを作成    
    input_events = input_Event.objects.filter(event_id__in= input_timerange_id_list)    
    print(1,input_timerange_id_list)
    #返すリスト作成する
    new_event_list = []
    #IDで回す
    for ID in input_timerange_id_list:
        #あるIDにおける調整時間を複数まとめるリスト（リストA）
        timerange_based_IDs_list = []
        #あるIDにおいて検索かけて抽出したデータ
        input_timeranges_based_ID = input_Timerange.objects.filter(event_id = ID)
        print(input_timeranges_based_ID)
        for input_timerange_based_ID in input_timeranges_based_ID:
            timerange_based_ID_list = []
            #1つのIDにおける調整時間を追加
            timerange_based_ID_list.append(input_timerange_based_ID.start_Date)
            timerange_based_ID_list.append(input_timerange_based_ID.end_Date)
            #リストAにIDにおける調整時間を複数まとめたリストを追加する
            timerange_based_IDs_list.append(timerange_based_ID_list)
        print(2,ID)
        ID_input_event = input_Event.objects.get(event_id = ID)
        print(3,ID_input_event.event_id)
        new_event_list.append(
            {
                "event_Id": ID_input_event.event_id,
                "name":ID_input_event.name,
                "required_Time":ID_input_event.required_Time,
                "priority":ID_input_event.priority,
                "timeRanges":timerange_based_IDs_list,
            }
        )

    Conflicts=[] #[[A,B,C],[D,F]] AとBとCが時刻被り、DとFが時刻被り
    BeatEvents=[] #カレンダーに記載する予定(優先度で勝ったもの)
    BeatedEvents=[] #カレンダーに載らない予定(優先度で負けたもの)
    Events=[]
    for n in new_event_list:
        e=sc_Event(n["event_Id"],n["name"],n["required_Time"],n["priority"],n["timeRanges"])
        Events.append(e)
    # Events=[Event1,Event2,Event3,Event4,Event5,Event6,Event7,Event8,Event9]
   
    l=[[e] for e in Events]

    for i in range(len(Events)):
        for t in Events[i].timeRanges:
            for j in range(len(Events)):
                if Events[i]==Events[j]:
                    continue
                for u in Events[j].timeRanges:
                    if t[0] <= u[0] < t[1] or t[0] < u[1] <= t[1]:
                        if not Events[j] in l[i]:
                            l[i].append(Events[j])

    Kakutei=[]
    kakutei=[]
    Shototsu=[]

    for x in l:
        if len(x)==1:
            conf=confirmed_Event(x[0].event_Id,x[0].name,x[0].required_Time,x[0].priority,x[0].timeRanges,[x[0].timeRanges[0][0],x[0].timeRanges[0][0]+x[0].required_Time])
            Kakutei.append(conf)
            kakutei.append(x[0])
        else:
            trs=copy.deepcopy(x[0].timeRanges)
            for t in range(len(trs)):
                for i in x:
                    if i==x[0]:
                        continue
                    for u in i.timeRanges:
                        if trs[t][0] <= u[0] < trs[t][1] and trs[t][0] <= u[1] < trs[t][1]:
                            trs.append([u[1],trs[t][1]])
                            trs[t][1]=u[0]
                        elif u[0] <= trs[t][0] and trs[t][0] <= u[1]:
                            trs[t][1]=trs[t][0]
                        else:
                            if trs[t][0] <= u[0] < trs[t][1]:
                                trs[t][1]=u[0]
                            if trs[t][0] <= u[1] < trs[t][1]:
                                trs[t][0]=u[1]
            for t in trs:
                if t[0]+x[0].required_Time <= t[1]:
                    conf=confirmed_Event(x[0].event_Id,x[0].name,x[0].required_Time,x[0].priority,x[0].timeRanges,[t[0],t[0]+x[0].required_Time])
                    Kakutei.append(conf)
                    kakutei.append(x[0])
    Shototsu=l
    count=0
    while(count<len(Shototsu)):
        if Shototsu[count][0] in kakutei:
            del Shototsu[count]
        else:
            for k in range(len(kakutei)):
                if kakutei[k] in Shototsu[count]:
                    del Shototsu[count][Shototsu[count].index(kakutei[k])]
            count+=1
    alreadies=[]
    S=[]
    for s in range(len(Shototsu)):
        alr=[]
        for n in Shototsu[s]:
            alr.append(n.name)
        alr=sorted(alr)
        if not alr in alreadies:
            alreadies.append(alr)
            S.append(Shototsu[s])
    
    Shototsu=S
    
    Shototsu=sorted(Shototsu, key=len)
    for s in Shototsu:
        print()
        print(11111111,s)

    BeatedList=[]

    while(True):
        # print(Shototsu)
        # print()
        # print()
        if len(Shototsu)==0:
            break
        if len(Shototsu[0])==0:
            break
        X=Shototsu[0]
        max_priority_Event=X[0]
        for x in X:
            if max_priority_Event.priority < x.priority:
                max_priority_Event=x
        min_loss_list=X
        loss=0
        for x in X:
            if x!=max_priority_Event:
                loss+=x.priority

        for Y in Shototsu:
            if not max_priority_Event in Y:
                continue
            Y_loss=0
            for y in Y:
                if y==max_priority_Event:
                    continue
                Y_loss+=y.priority
            if loss >= Y_loss:
                min_loss_list=Y
                loss=Y_loss
        # for k in Kakutei:
        #     if k.confirmed_Time[0]<= st < k.confirmed_Time[1]:
        #         st=k.confirmed_Time[1]
        #     if st+max_priority_Event.required_Time >= max_priority_Event.timeRanges[i][1]:
        #         if len(max_priority_Event.timeRanges)>i+1:
        #             i+=1
        #             st=max_priority_Event.timeRanges[i][0]
        # if not st+max_priority_Event.required_Time >= max_priority_Event.timeRanges[i][1]:
        conf=confirmed_Event(max_priority_Event.event_Id,max_priority_Event.name,max_priority_Event.required_Time,max_priority_Event.priority,max_priority_Event.timeRanges,[max_priority_Event.timeRanges[0][0],max_priority_Event.timeRanges[0][0]+max_priority_Event.required_Time])
        Kakutei.append(conf)
        if max_priority_Event in BeatedList:
            del BeatedList[BeatedList.index(max_priority_Event)]

        #ここでtimerange処理する。
        news=[]
        for x in min_loss_list:
            temp_x=copy.deepcopy(x)
            temp_timeRanges=[]
            for t in x.timeRanges:
                if t[1]<= conf.confirmed_Time[0] or conf.confirmed_Time[1] <=t[0]:
                    temp_timeRanges.append(t)
                elif t[0]<= conf.confirmed_Time[0] <t[1]:
                    temp_timeRanges.append([t[0],conf.confirmed_Time[0]])
                elif t[0]<= conf.confirmed_Time[1] <t[1]:
                    temp_timeRanges.append([conf.confirmed_Time[1],t[1]])
                # else:
                #     temp_timeRanges.append([t[0],t[0]])
            # temp_x.timeRanges=temp_timeRanges
            tem=[]
            for c in temp_timeRanges:
                if c[0]<c[1]:
                    tem.append(c)
            temp_x.timeRanges=tem
            flag=0
            for t in temp_x.timeRanges:
                if t[0]+temp_x.required_Time <= t[1]:
                    flag=1
                    break
            if flag==1:
                news.append(temp_x)
            else:
                BeatedList.append(x)
        del Shototsu[Shototsu.index(min_loss_list)]
        if len(news)!=0:
            Shototsu.append(news)

        for Y in Shototsu:
            if max_priority_Event in Y:
                del Y[Y.index(max_priority_Event)]
        # else:
        #     BeatedList.append(max_priority_Event)
        #     del X[X.index(max_priority_Event)]

        if len(Shototsu)==0:
            break

    print(len(Kakutei))
    print(len(BeatedList))
    k=[]
    b=[]
    for K in Kakutei:
        k.append(
            {
                "title": K.name,
                "start": K.confirmed_Time[0],
                "end": K.confirmed_Time[1],
            }
        )

    for B in BeatedList:
        b.append(
            {
                "title": B.name,
                "start": B.timeRanges[0][0],
                "end": B.timeRanges[0][1],
            }
        )

    return k, b

def form2(request):
  if request.method =="GET":

    context = {
            'message': " GOT now! from View!!",
      }
    return render(request, 'scheduleCalendar/form2.html', context)
  elif request.method=="POST":
    context = {
            'message': "POST OK!!",
            'required_time':request.POST['required_time'],
            'event_name':request.POST['event_name'],
            'daterange_start':request.POST['daterange_start'],
            'daterange_end':request.POST['daterange_end'],
            'timerange_start':request.POST['timerange_start'],
            'timerange_end':request.POST['timerange_end'],
            'priority':int(request.POST['priority']),
            'frequency':int(request.POST['frequency']),
            
      }
      # リクエストの取得・成形
    event_name = context["event_name"]

    time = context["required_time"].split(":")
    required_Time = datetime.time(int(time[0]),int(time[1]))

    dateStart = context["daterange_start"]
    year = int(dateStart.split("-")[0])
    month = int(dateStart.split("-")[1])
    day = int(dateStart.split("-")[2])
    date_start = datetime.datetime(year,month,day)

    dateEnd = context["daterange_end"]
    year = int(dateEnd.split("-")[0])
    month = int(dateEnd.split("-")[1])
    day = int(dateEnd.split("-")[2])
    date_end = datetime.datetime(year,month,day)

    timeStart = context["timerange_start"].split(":")
    time_start = datetime.time(int(timeStart[0]),int(timeStart[1]))

    timeEnd = context["timerange_end"].split(":")
    time_end = datetime.time(int(timeEnd[0]),int(timeEnd[1]))

    priority = int(context["priority"])

    freq = int(context["frequency"])

    #調整可能時刻テーブルへの登録
    for ii in range(freq):
        id = uuid.uuid1() #現在時刻からユニークIDを生成
        for jj in range((date_end-date_start).days+1):
            timerange = input_Timerange(
                event_id = str(id),
                start_Date = date_start + datetime.timedelta(days = jj,hours=time_start.hour,minutes=time_start.minute), #フロントエンド側のデータ型によって処理変わる
                end_Date = date_start + datetime.timedelta(days = jj,hours=time_end.hour,minutes=time_end.minute),
            )
            timerange.save()
        # 登録処理
        event = input_Event(
            event_id = str(id),
            name = event_name,
            required_Time = datetime.timedelta(hours=required_Time.hour,minutes=required_Time.minute),
            priority = priority,
        )
        event.save()
    print(1)
    confirm_event,unconfirm_event = scheduling()

    for num in range(len(confirm_event)):
      event = Event(
      start_date = confirm_event[num]['start'],
      end_date = confirm_event[num]['end'],
      event_name = confirm_event[num]['title']
      )
      event.save()
    
    # [{'title': 'office', 'start': datetime.datetime(2022, 9, 15, 14, 0, tzinfo=datetime.timezone.utc), 'end': datetime.datetime(2022, 9, 15, 15, 0, tzinfo=datetime.timezone.utc)}]


    return render(request, 'scheduleCalendar/form2.html', context)
  else:
    raise Http404()


def form1(request):
  if request.method =="GET":
    context = {
            'message': " GOT now! from View!!",
        }
    return render(request, 'scheduleCalendar/form1.html', context)
  elif request.method=="POST":
    context = {
            'message': "POST OK!!",
            'event_name':request.POST['schedule'],        
            'required_time':datetime.time(int(request.POST['time'].split(":")[0]),int(request.POST['time'].split(":")[1])),
            'timerange_begin':request.POST.getlist('timerange_begin'),
            'timerange_end':request.POST.getlist('timerange_end'),
            'priority':int(request.POST['priority']),
        }
    time_range=[]
    for i in range(len(context['timerange_begin'])):
      time_range.append([context['timerange_begin'][i],context['timerange_end'][i]])
    context['time_range']=time_range
    del context['timerange_begin']
    del context['timerange_end']
    print(context)
    event_name = context["event_name"]

    time = context["required_time"]
    required_Time = datetime.timedelta(hours=int(time.hour),minutes=int(time.minute))

    ranges = context["time_range"]
    timeranges = []
    for ii in ranges:
        timerange = []
        year = int(ii[0].split("T")[0].split("-")[0])
        month = int(ii[0].split("T")[0].split("-")[1])
        day = int(ii[0].split("T")[0].split("-")[2])
        hour = int(ii[0].split("T")[1].split(":")[0])
        sec = int(ii[0].split("T")[1].split(":")[1])
        timerange.append(datetime.datetime(year,month,day,hour,sec))

        year = int(ii[1].split("T")[0].split("-")[0])
        month = int(ii[1].split("T")[0].split("-")[1])
        day = int(ii[1].split("T")[0].split("-")[2])
        hour = int(ii[1].split("T")[1].split(":")[0])
        sec = int(ii[1].split("T")[1].split(":")[1])
        timerange.append(datetime.datetime(year,month,day,hour,sec))

        timeranges.append(timerange)

    priority = int(context["priority"])

    #現在時刻からユニークIDを生成
    id = uuid.uuid1()

    #調整可能時刻テーブルへの登録
    for ii in range(len(timeranges)):
      timerange = input_Timerange(
            event_id = str(id),
            start_Date = timeranges[ii][0],
            end_Date = timeranges[ii][1]
        )
      timerange.save()

    # 登録処理
    event = input_Event(
        event_id = str(id),
        name = str(event_name),
        required_Time = required_Time,
        priority = int(priority)
    )
    event.save()
  

    return render(request, 'scheduleCalendar/form1.html', context)

  else:
    raise Http404()





def form3(request):
  if request.method =="GET":

    context = {
            'message': " GOT now! from View!!",
        }
    return render(request, 'scheduleCalendar/form3.html', context)
  elif request.method=="POST":
    context = {
            'message': "POST OK!!",
            'event_name':request.POST['schedule'],        
            'required_time':datetime.time(int(request.POST['time'].split(":")[0]),int(request.POST['time'].split(":")[1])),
            'timespan':request.POST['timespan'],
            'frequency':request.POST['frequency'],
            'last_date':request.POST['last_date'],
            'daterange_start':request.POST['timerange_start'],
            'daterange_end':request.POST['timerange_end'],
            'priority':int(request.POST['priority']),
        }
    print(context)
    # リクエストの取得・成形
    event_name = context["event_name"]

    time = context["required_time"]
    required_Time = datetime.timedelta(hours=int(time.hour),minutes=int(time.minute))

    timespan = context["timespan"]

    freq = int(context["frequency"])

    last_date = context["last_date"]
    year = int(last_date.split("-")[0])
    month = int(last_date.split("-")[1])
    day = int(last_date.split("-")[2])
    last_date = datetime.datetime(year,month,day)

    timeStart = context["daterange_start"].split(":")
    time_start = datetime.time(int(timeStart[0]),int(timeStart[1]))

    timeEnd = context["daterange_end"].split(":")
    time_end = datetime.time(int(timeEnd[0]),int(timeEnd[1]))

    priority = int(context["priority"])
    id = uuid.uuid1() #現在時刻からユニークIDを生成
    tommorow_date = datetime.datetime.now()+datetime.timedelta(days=1)

    #週の場合
    if timespan == "週":
      #終了日まで何週間あるか
        print('week go')
        freq_in_range = (last_date - tommorow_date).days//7
        #調整可能時刻テーブルへの登録
        for jj in range(freq_in_range):
            for ii in range(freq):
                id = uuid.uuid1() #現在時刻からユニークIDを生成
                # 登録処理
                event = input_Event(
                    event_id = str(id),
                    name = str(event_name),
                    required_Time = required_Time,
                    priority = int(priority),
                )
                event.save()
                for kk in range(7):
                    timerange = input_Timerange(
                        event_id = str(id),
                        start_Date = tommorow_date + jj*datetime.timedelta(days=7) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_start.hour, minutes = time_start.minute), #フロントエンド側のデータ型によって処理変わる
                        end_Date = tommorow_date+ jj*datetime.timedelta(days=7) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_end.hour, minutes = time_end.minute), #フロントエンド側のデータ型によって処理変わる
                    )
                    timerange.save()

    #月の場合
    elif timespan == "月":
        #終了日まで何週間あるか
        freq_in_range = (last_date - tommorow_date).days//30
        #調整可能時刻テーブルへの登録
        for jj in range(freq_in_range):
            for ii in range(freq):
                id = uuid.uuid1() #現在時刻からユニークIDを生成
                # 登録処理
                event = input_Event(
                    event_id = str(id),
                    name = str(event_name),
                    required_Time = datetime.timedelta(days=required_Time),
                    priority = int(priority),
                )
                event.save()
                for kk in range(30):
                    timerange = input_Timerange(
                        event_id = str(id),
                        start_Date = tommorow_date + jj*datetime.timedelta(days=30) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_start.hour, minutes = time_start.minute), #フロントエンド側のデータ型によって処理変わる
                        end_Date = tommorow_date+ jj*datetime.timedelta(days=30) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_end.hour, minutes = time_end.minute), #フロントエンド側のデータ型によって処理変わる
                    )
                    timerange.save()
    print("process2")
    confirm_event,unconfirm_event = scheduling()

    for num in range(len(confirm_event)):
      event = Event(
      start_date = confirm_event[num]['start'],
      end_date = confirm_event[num]['end'],
      event_name = confirm_event[num]['title']
      )
      event.save()

    return render(request, 'scheduleCalendar/form3.html', context)

  else:
    raise Http404()

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
    print(list)
    return JsonResponse(list, safe=False)





#パターン２の入力
def add_events_multi(request):
    if request.method == "GET":
        # GETは対応しない
        raise Http404()
    
    elif request.method=="POST":
        context = {
                'event_name':request.POST['event_name'],
                'required_time':request.POST('required_time'),
                'daterange_start':request.POST['daterange_start'],
                'daterange_end':request.POST['daterange_end'],
                'timerange_start':request.POST['timerange_start'],
                'timerange_end':request.POST['timerange_end'],
                'priority':request.POST['priority'],
                'frequency':request.POST['frequency'],
            }
    
    # サンプルデータ
    # context = {'event_name':'test','required_time': '01:00', 'daterange_start': '2022-09-17', 'daterange_end': '2022-09-28', 'timerange_start': '22:53', 'timerange_end': '23:53', 'priority': 2, 'frequency': 1}

    # リクエストの取得・成形
    event_name = context["event_name"]

    time = context["required_time"].split(":")
    required_Time = datetime.time(int(time[0]),int(time[1]))

    dateStart = context["daterange_start"]
    year = int(dateStart.split("-")[0])
    month = int(dateStart.split("-")[1])
    day = int(dateStart.split("-")[2])
    date_start = datetime.datetime(year,month,day)

    dateEnd = context["daterange_end"]
    year = int(dateEnd.split("-")[0])
    month = int(dateEnd.split("-")[1])
    day = int(dateEnd.split("-")[2])
    date_end = datetime.datetime(year,month,day)

    timeStart = context["timerange_start"].split(":")
    time_start = datetime.time(int(timeStart[0]),int(timeStart[1]))

    timeEnd = context["timerange_end"].split(":")
    time_end = datetime.time(int(timeEnd[0]),int(timeEnd[1]))

    priority = int(context["priority"])

    freq = int(context["frequency"])

    #調整可能時刻テーブルへの登録
    for ii in range(freq):
        id = uuid.uuid1() #現在時刻からユニークIDを生成
        for jj in range((date_end-date_start).days+1):
            timerange = input_Timerange(
                event_Id = str(id),
                start_Date = date_start + datetime.timedelta(days = jj,hours=time_start.hour,minutes=time_start.minute), #フロントエンド側のデータ型によって処理変わる
                end_Date = date_start + datetime.timedelta(days = jj,hours=time_end.hour,minutes=time_end.minute),
            )
            timerange.save()
        # 登録処理
        event = input_Event(
            event_Id = str(id),
            event_name = event_name,
            required_Time = datetime.timedelta(hours=required_Time.hour,minute=required_Time.minute),
            priority = priority,
        )
        event.save()

    # 空を返却
    return HttpResponse("")

#パターン３
def add_events_hubit(request):
    if request.method == "GET":
        # GETは対応しない
        raise Http404()
    
    elif request.method=="POST":
        context = {
                'event_name':request.POST['event_name'],
                'required_time':request.POST('required_time'),
                'timespan':request.POST('timespan'),
                'frequency':request.POST('frequency'),
                'last_date':request.POST('last_date'),
                'daterange_start':request.POST['daterange_start'],
                'daterange_end':request.POST['daterange_end'],
                'priority':request.POST['priority'],
            }
    
    # リクエストの取得・成形
    event_name = context["event_names"]

    time = context["required_time"].split(":")
    required_Time = datetime.time(int(time[0]),int(time[1]))

    timespan = context["timespan"]

    freq = int(context["frequency"])

    last_date = context["last_date"]
    year = int(last_date.split("-")[0])
    month = int(last_date.split("-")[1])
    day = int(last_date.split("-")[2])
    last_date = datetime.datetime(year,month,day)

    timeStart = context["timerange_start"].split(":")
    time_start = datetime.time(timeStart[0],timeStart[1])

    timeEnd = context["timerange_end"].split(":")
    time_end = datetime.time(timeEnd[0],timeEnd[1])

    priority = int(context["priority"])
    id = uuid.uuid1() #現在時刻からユニークIDを生成
    tommorow_date = datetime.datetime.now()+datetime.timedelta(days=1)

    #週の場合
    if timespan == "週":
        #終了日まで何週間あるか
        freq_in_range = (last_date - tommorow_date)//7
        #調整可能時刻テーブルへの登録
        for jj in range(freq_in_range):
            for ii in range(freq):
                id = uuid.uuid1() #現在時刻からユニークIDを生成
                # 登録処理
                event = input_Event(
                    event_Id = str(id),
                    event_name = str(event_name),
                    required_Time = datetime.timedelta(days=required_Time),
                    priority = int(priority),
                )
                event.save()
                for kk in range(7):
                    timerange = input_Timerange(
                        event_Id = str(id),
                        start_Date = tommorow_date + jj*datetime.timedelta(days=7) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_start.hour, minutes = time_start.minute), #フロントエンド側のデータ型によって処理変わる
                        end_Date = tommorow_date+ jj*datetime.timedelta(days=7) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_end.hour, minutes = time_end.minute), #フロントエンド側のデータ型によって処理変わる
                    )
                    timerange.save()

    #月の場合
    elif timespan == "月":
        #終了日まで何週間あるか
        freq_in_range = (last_date - tommorow_date)//30
        #調整可能時刻テーブルへの登録
        for jj in range(freq_in_range):
            for ii in range(freq):
                id = uuid.uuid1() #現在時刻からユニークIDを生成
                # 登録処理
                event = input_Event(
                    event_Id = str(id),
                    event_name = str(event_name),
                    required_Time = datetime.timedelta(days=required_Time),
                    priority = int(priority),
                )
                event.save()
                for kk in range(30):
                    timerange = input_Timerange(
                        event_Id = str(id),
                        start_Date = tommorow_date + jj*datetime.timedelta(days=30) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_start.hour, minutes = time_start.minute), #フロントエンド側のデータ型によって処理変わる
                        end_Date = tommorow_date+ jj*datetime.timedelta(days=30) + kk*datetime.timedelta(days=1) + datetime.timedelta(hours = time_end.hour, minutes = time_end.minute), #フロントエンド側のデータ型によって処理変わる
                    )
                    timerange.save()

    # 空を返却
    return HttpResponse("")



#パターン１の入力
def add_events_one(request):
    if request.method == "GET":
        # GETは対応しない
        raise Http404()
    
    elif request.method=="POST":
        context = {
                'event_name':request.POST['event_name'],
                'required_time':request.POST('required_time'),
                'time_range':request.POST['time_range'],
                'priority':request.POST['priority'],
            }

    #サンプルデータ
    # context = {'event_name': 'jin', 'required_time': datetime.time(2, 0), 'priority': 4, 'time_range': [['2022-09-14T23:17', '2022-09-14T23:20'], ['2022-09-15T23:17', '2022-09-15T23:20']]}

    # リクエストの取得・成形
    event_name = context["event_name"]

    time = context["required_time"]
    required_Time = datetime.timedelta(hours=int(time.hour),minutes=int(time.minute))

    ranges = context["time_range"]
    timeranges = []
    for ii in ranges:
        timerange = []
        year = int(ii[0].split("T")[0].split("-")[0])
        month = int(ii[0].split("T")[0].split("-")[1])
        day = int(ii[0].split("T")[0].split("-")[2])
        hour = int(ii[0].split("T")[1].split(":")[0])
        sec = int(ii[0].split("T")[1].split(":")[1])
        timerange.append(datetime.datetime(year,month,day,hour,sec))

        year = int(ii[1].split("T")[0].split("-")[0])
        month = int(ii[1].split("T")[0].split("-")[1])
        day = int(ii[1].split("T")[0].split("-")[2])
        hour = int(ii[1].split("T")[1].split(":")[0])
        sec = int(ii[1].split("T")[1].split(":")[1])
        timerange.append(datetime.datetime(year,month,day,hour,sec))

        timeranges.append(timerange)

    priority = int(context["priority"])

    #現在時刻からユニークIDを生成
    id = uuid.uuid1()

    #調整可能時刻テーブルへの登録
    for ii in range(len(timeranges)):
        timerange = input_Timerange(
            event_Id = str(id),
            start_Date = timeranges[ii][0],
            end_Date = timeranges[ii][1]
        )
        timerange.save()

    # 登録処理
    event = input_Event(
        event_Id = str(id),
        event_name = str(event_name),
        required_Time = required_Time,
        priority = int(priority)
    )
    event.save()

    # 空を返却
    return HttpResponse("")