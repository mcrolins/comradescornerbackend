from django.shortcuts import render
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job
from .serializers import JobSerializer
# Create your views here.
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
