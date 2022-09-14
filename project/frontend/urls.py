from django.urls import path
from . import views


urlpatterns = [
  
   path('',views.index1),
   path("add/", views.add_event, name="add_event"),
   path("list/", views.get_events, name="get_events"),
   path('form1',views.form1,name='form1'),
  #  path('form1/result',views.result,name='result'),
]