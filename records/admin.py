from django.contrib import admin

from .models import EntryExitLog


class EntryExitLogAdmin(admin.ModelAdmin):
    fields = ("user", "action", "timestamp")


admin.site.register(EntryExitLog)
