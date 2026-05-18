from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField, Q
from django.db.models.functions import TruncDate
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, SiteVisit
from .serializers import JobSerializer, AdminLoginSerializer, SiteVisitSerializer


# ── Public job endpoints ──────────────────────────────────────────────

class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]

    filterset_fields = [
        "level",
        "job_type",
        "is_remote",
        "category",
        "location"
    ]

    search_fields = [
        "title",
        "company",
        "description",
        "requirements"
    ]

    ordering_fields = ["created_at", "deadline"]


class JobDetailView(generics.RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count on every detail fetch
        Job.objects.filter(pk=instance.pk).update(view_count=F("view_count") + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# ── Visitor tracking ──────────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def track_visit(request):
    """Clock-in a visitor (or clock-out if session_key already exists)."""
    session_key = request.data.get("session_key", "")
    action = request.data.get("action", "clock_in")  # clock_in | clock_out

    if not session_key:
        return Response({"error": "session_key required"}, status=400)

    if action == "clock_in":
        visit = SiteVisit.objects.create(
            session_key=session_key,
            ip_address=_get_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response({"id": visit.id, "clock_in": visit.clock_in}, status=201)

    elif action == "clock_out":
        visit = (
            SiteVisit.objects.filter(session_key=session_key, clock_out__isnull=True)
            .order_by("-clock_in")
            .first()
        )
        if visit:
            visit.clock_out = timezone.now()
            visit.save(update_fields=["clock_out"])
            return Response({"id": visit.id, "clock_out": visit.clock_out})
        return Response({"detail": "No open session found."}, status=404)

    return Response({"error": "Invalid action"}, status=400)


def _get_client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ── Admin authentication ─────────────────────────────────────────────

@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login(request):
    """Validate admin credentials and return a session cookie."""
    from django.contrib.auth import login

    serializer = AdminLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    return Response({
        "username": user.username,
        "email": user.email,
        "is_staff": user.is_staff,
    })


@api_view(["POST"])
@permission_classes([AllowAny])
def admin_logout(request):
    from django.contrib.auth import logout
    logout(request)
    return Response({"detail": "Logged out."})


@api_view(["GET"])
@permission_classes([AllowAny])
def admin_check(request):
    """Check if the current session is an authenticated admin."""
    if request.user.is_authenticated and request.user.is_staff:
        return Response({
            "authenticated": True,
            "username": request.user.username,
            "email": request.user.email,
        })
    return Response({"authenticated": False}, status=401)


# ── Admin CRUD for jobs ──────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_jobs_list(request):
    """List all jobs for admin management."""
    jobs = Job.objects.all().order_by("-created_at")
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAdminUser])
def admin_job_create(request):
    """Create a new job listing."""
    serializer = JobSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=201)


@api_view(["DELETE"])
@permission_classes([IsAdminUser])
def admin_job_delete(request, pk):
    """Delete a job listing."""
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)
    job.delete()
    return Response(status=204)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAdminUser])
def admin_job_update(request, pk):
    """Update a job listing."""
    try:
        job = Job.objects.get(pk=pk)
    except Job.DoesNotExist:
        return Response({"detail": "Not found."}, status=404)
    partial = request.method == "PATCH"
    serializer = JobSerializer(job, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


# ── Admin analytics ──────────────────────────────────────────────────

@api_view(["GET"])
@permission_classes([IsAdminUser])
def admin_analytics(request):
    """Return dashboard analytics."""
    now = timezone.now()

    # Total counts
    total_jobs = Job.objects.count()
    total_visits = SiteVisit.objects.count()
    active_visitors = SiteVisit.objects.filter(clock_out__isnull=True).count()

    # Visits today
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    visits_today = SiteVisit.objects.filter(clock_in__gte=today_start).count()

    # Average session duration (completed visits only)
    completed = SiteVisit.objects.filter(clock_out__isnull=False)
    avg_duration = completed.annotate(
        dur=ExpressionWrapper(F("clock_out") - F("clock_in"), output_field=DurationField())
    ).aggregate(avg=Avg("dur"))
    avg_seconds = avg_duration["avg"].total_seconds() if avg_duration["avg"] else 0

    # Most demanding (most viewed) listings
    most_demanding = list(
        Job.objects.order_by("-view_count")[:5].values(
            "id", "title", "company", "view_count", "level", "category"
        )
    )

    # Least demanding (least viewed) listings
    least_demanding = list(
        Job.objects.order_by("view_count")[:5].values(
            "id", "title", "company", "view_count", "level", "category"
        )
    )

    # Jobs by level distribution
    level_dist = list(
        Job.objects.values("level").annotate(count=Count("id")).order_by("-count")
    )

    # Jobs by type distribution
    type_dist = list(
        Job.objects.values("job_type").annotate(count=Count("id")).order_by("-count")
    )

    # Recent visits (last 20)
    recent_visits = SiteVisitSerializer(
        SiteVisit.objects.all()[:20], many=True
    ).data

    # Daily visit trend (last 14 days)
    fourteen_days_ago = now - timezone.timedelta(days=14)
    daily_visits = list(
        SiteVisit.objects.filter(clock_in__gte=fourteen_days_ago)
        .annotate(day=TruncDate("clock_in"))
        .values("day")
        .annotate(count=Count("id"))
        .order_by("day")
    )
    # Convert date objects to strings
    for entry in daily_visits:
        entry["day"] = entry["day"].isoformat()

    return Response({
        "total_jobs": total_jobs,
        "total_visits": total_visits,
        "active_visitors": active_visitors,
        "visits_today": visits_today,
        "avg_session_seconds": round(avg_seconds, 1),
        "most_demanding": most_demanding,
        "least_demanding": least_demanding,
        "level_distribution": level_dist,
        "type_distribution": type_dist,
        "recent_visits": recent_visits,
        "daily_visits": daily_visits,
    })
