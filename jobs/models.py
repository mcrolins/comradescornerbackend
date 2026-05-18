from django.db import models


# Create your models here.
class Job(models.Model):
    LEVEL_CHOICES = [
        ("attachment", "Attachment"),
        ("intern", "Internship"),
        ("entry", "Entry Level"),
        ("junior", "Junior"),
        ("grad", "Graduate Trainee"),
    ]

    TYPE_CHOICES = [
        ("full_time", "Full-time"),
        ("part_time", "Part-time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    is_remote = models.BooleanField(default=False)

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="entry")
    job_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="full_time")
    category = models.CharField(max_length=100, blank=True)

    description = models.TextField()
    requirements = models.TextField(blank=True)

    apply_url = models.URLField(blank=True)
    apply_email = models.EmailField(blank=True)

    deadline = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"


class SiteVisit(models.Model):
    """Tracks anonymous visitor sessions – clock-in / clock-out."""
    session_key = models.CharField(max_length=64)
    clock_in = models.DateTimeField(auto_now_add=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    @property
    def duration_seconds(self):
        if self.clock_out and self.clock_in:
            return (self.clock_out - self.clock_in).total_seconds()
        return None

    class Meta:
        ordering = ["-clock_in"]

    def __str__(self):
        return f"Visit {self.session_key[:8]}… @ {self.clock_in:%Y-%m-%d %H:%M}"