from django.db import models

class Event(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    event_name = models.CharField(max_length=200)
# Create your models here.
# class Todo(models.Model):
#     title = models.CharField(max_length=120)
#     description = models.TextField()
#     completed = models.BooleanField(default=False)
#      def _str_(self):
#         return self.title