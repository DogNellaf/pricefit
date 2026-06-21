from django.contrib import admin

from .models import Analysis, Request, TargetGroup


@admin.register(TargetGroup)
class TargetGroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'min_budget', 'max_budget')
    search_fields = ('title', 'description')


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'min_price', 'max_price', 'created_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username',)
    date_hierarchy = 'created_at'


@admin.register(Analysis)
class AnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'request', 'target_group', 'coefficient')
    list_filter = ('target_group',)
    ordering = ('-coefficient',)
