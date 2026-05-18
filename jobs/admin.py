from django.contrib import admin
from .models import Job, SiteVisit
# Register your models here.


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "level", "job_type", "is_remote", "view_count", "created_at")
    list_filter = ("level", "job_type", "is_remote", "category")
    search_fields = ("title", "company", "location", "category", "description")


@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ("session_key", "clock_in", "clock_out", "ip_address")
    list_filter = ("clock_in",)
    search_fields = ("session_key", "ip_address")
