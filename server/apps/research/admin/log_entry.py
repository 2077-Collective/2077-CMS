from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.translation import gettext_lazy as _

class LogEntryAdmin(admin.ModelAdmin):
    list_display = ('action_time', 'user', 'content_type', 'object_id', 'action_flag', 'change_message')
    list_filter = ('action_flag', 'user', 'content_type')
    search_fields = ('object_id', 'change_message')

admin.site.register(LogEntry, LogEntryAdmin)