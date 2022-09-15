from django.db import models

class Event(models.Model):
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event_name = models.CharField(max_length=200)

class input_Event(models.Model):
    event_id = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    required_Time=models.DurationField()
    priority=models.IntegerField()

class input_Timerange(models.Model):
    event_id = models.CharField(max_length=100)
    start_Date = models.DateTimeField()
    end_Date = models.DateTimeField()


