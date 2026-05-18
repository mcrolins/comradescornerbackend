from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import Job, SiteVisit


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = "__all__"


class AdminLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            username=data["username"],
            password=data["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_staff:
            raise serializers.ValidationError("Not an admin account.")
        data["user"] = user
        return data


class SiteVisitSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.FloatField(read_only=True)

    class Meta:
        model = SiteVisit
        fields = "__all__"
