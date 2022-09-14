from django.contrib import admin
from .models import Todo
from myapp1.models import Company
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'completed')

# Register your models here.

admin.site.register(Event, TodoAdmin)
#admin.site.register(Company)