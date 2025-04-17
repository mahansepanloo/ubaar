from django.contrib import admin
from .models import  FailedLoginAttempt


class FailedLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'ip_address', 'attempt_type', 'created_at')
    search_fields = ('phone_number', 'ip_address')
    list_filter = ('attempt_type', 'created_at')

admin.site.register(FailedLoginAttempt, FailedLoginAttemptAdmin)
