"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from django.views.decorators.csrf import csrf_exempt

from jobs.views import (
    JobDetailView,
    JobListCreateView,
    track_visit,
    admin_login,
    admin_logout,
    admin_check,
    admin_jobs_list,
    admin_job_create,
    admin_job_delete,
    admin_job_update,
    admin_analytics,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", RedirectView.as_view(url="jobs/", permanent=False), name="home"),
    path("jobs/", JobListCreateView.as_view(), name="job-list"), 
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),

    # Visitor tracking
    path("api/track-visit", csrf_exempt(track_visit), name="track-visit"),

    # Admin dashboard API
    path("api/admin/login", csrf_exempt(admin_login), name="admin-login"),
    path("api/admin/logout", csrf_exempt(admin_logout), name="admin-logout"),
    path("api/admin/check", csrf_exempt(admin_check), name="admin-check"),
    path("api/admin/jobs", csrf_exempt(admin_jobs_list), name="admin-jobs-list"),
    path("api/admin/jobs/create", csrf_exempt(admin_job_create), name="admin-job-create"),
    path("api/admin/jobs/<int:pk>/delete", csrf_exempt(admin_job_delete), name="admin-job-delete"),
    path("api/admin/jobs/<int:pk>/update", csrf_exempt(admin_job_update), name="admin-job-update"),
    path("api/admin/analytics", csrf_exempt(admin_analytics), name="admin-analytics"),
]

