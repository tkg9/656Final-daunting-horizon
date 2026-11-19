from django.conf import settings
from django.db import models


class Production(models.Model):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="+")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Membership(models.Model):
    ROLES = [
        ("director", "Director"),
        ("stage_manager", "Stage manager"),
        ("actor", "Actor"),
        ("crew", "Crew"),
    ]

    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=20, choices=ROLES)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["production", "user"], name="one_role_per_member")]


class Scene(models.Model):
    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name="scenes")
    number = models.PositiveIntegerField()
    heading = models.CharField(max_length=200)
    text = models.TextField()

    class Meta:
        ordering = ["number"]
        constraints = [models.UniqueConstraint(fields=["production", "number"], name="unique_scene_number")]
