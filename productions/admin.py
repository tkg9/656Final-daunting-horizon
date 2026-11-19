from django.contrib import admin

from .models import Breakdown, Production


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ["title", "owner", "created_at"]


@admin.register(Breakdown)
class BreakdownAdmin(admin.ModelAdmin):
    list_display = ["production", "model", "created_at"]
