from django.contrib import admin
from .models import Job
# Register your models here.


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "level", "job_type", "is_remote", "created_at")
    list_filter = ("level", "job_type", "is_remote", "category")
    search_fields = ("title", "company", "location", "category", "description")
