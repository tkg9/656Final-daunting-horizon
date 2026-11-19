from django.urls import path

from . import views

urlpatterns = [
    path("productions/", views.production_list, name="production-list"),
    path("productions/new/", views.production_create, name="production-create"),
    path("productions/<int:pk>/", views.production_detail, name="production-detail"),
    path("productions/<int:pk>/edit/", views.production_edit, name="production-edit"),
    path("productions/<int:pk>/breakdown/", views.production_breakdown, name="production-breakdown"),
]
