from django.urls import path

from . import views

urlpatterns = [
    path("productions/", views.production_list, name="production-list"),
    path("productions/new/", views.production_create, name="production-create"),
    path("productions/<int:pk>/", views.production_detail, name="production-detail"),
    path("productions/<int:pk>/script/", views.script_upload, name="script-upload"),
    path("productions/<int:pk>/breakdown/", views.breakdown, name="breakdown"),
]
