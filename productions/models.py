from django.conf import settings
from django.db import models
from django.urls import reverse


class Production(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="productions")
    title = models.CharField(max_length=200)
    script = models.TextField(blank=True, help_text="Paste the script as plain text.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("production-detail", args=[self.pk])


class Breakdown(models.Model):
    """A script breakdown drafted by the LLM, kept for the director to review."""

    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name="breakdowns")
    model = models.CharField(max_length=100, help_text="The LLM that drafted it.")
    data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Breakdown of {self.production} ({self.created_at:%Y-%m-%d %H:%M})"
