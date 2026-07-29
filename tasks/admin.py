from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'created_by', 'status', 'due_date')
    list_filter = ('status', 'due_date', 'assigned_to')
    search_fields = ('title', 'description')