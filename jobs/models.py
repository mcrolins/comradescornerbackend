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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} @ {self.company}"