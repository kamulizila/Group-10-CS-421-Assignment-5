from django.contrib import admin
from .models import Target, Status, History, Alert, SSLCheck, DomainCheck

@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('url', 'description', 'created_at')
    search_fields = ('url', 'description')
    list_filter = ('created_at',)

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'status_code', 'latency_ms', 'checked_at')
    list_filter = ('status_code', 'checked_at')
    search_fields = ('target__url',)
    raw_id_fields = ('target_url',)

@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'status_code', 'latency_ms', 'checked_at')
    list_filter = ('status_code', 'checked_at')
    search_fields = ('target__url',)
    date_hierarchy = 'checked_at'
    raw_id_fields = ('target_url',)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'message', 'created_at', 'read')
    list_filter = ('read', 'created_at')
    search_fields = ('target__url', 'message')
    raw_id_fields = ('target_url',)
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Mark selected alerts as read"

@admin.register(SSLCheck)
class SSLCheckAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'expires_at', 'days_to_expiry', 'checked_at')
    search_fields = ('target__url',)
    list_filter = ('expires_at', 'checked_at')
    raw_id_fields = ('target_url',)

@admin.register(DomainCheck)
class DomainCheckAdmin(admin.ModelAdmin):
    list_display = ('target_url', 'expires_at', 'days_to_expiry', 'checked_at')
    search_fields = ('target__url',)
    list_filter = ('expires_at', 'checked_at')
    raw_id_fields = ('target_url',)