from django.urls import path
from . import views

app_name = "cal"
urlpatterns = [
   path('', views.index),
   path('cal',views.index1),
   path("cal/add/", views.add_event, name="add_event"),
   path("cal/list/", views.get_events, name="get_events"),
   path('form1',views.form1),
]