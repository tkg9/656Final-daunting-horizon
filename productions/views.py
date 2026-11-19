from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from . import script
from .breakdown import draft_breakdown
from .forms import ProductionForm, ScriptForm
from .models import Membership, Production, Scene

EDITORS = ("director", "stage_manager")


def _membership(request, pk):
    production = get_object_or_404(Production, pk=pk)
    membership = production.memberships.filter(user=request.user).first()
    if membership is None:
        raise Http404
    return production, membership


@login_required
def production_list(request):
    memberships = request.user.memberships.select_related("production").order_by("-production__created_at")
    return render(request, "productions/list.html", {"memberships": memberships})


@login_required
def production_create(request):
    form = ProductionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            production = form.save(commit=False)
            production.created_by = request.user
            production.save()
            Membership.objects.create(production=production, user=request.user, role="director")
        return redirect("production-detail", pk=production.pk)
    return render(request, "productions/create.html", {"form": form})


@login_required
def production_detail(request, pk):
    production, membership = _membership(request, pk)
    return render(request, "productions/detail.html", {
        "production": production,
        "membership": membership,
        "can_edit": membership.role in EDITORS,
        "members": production.memberships.select_related("user").order_by("role"),
        "scenes": production.scenes.all(),
    })


@login_required
def script_upload(request, pk):
    production, membership = _membership(request, pk)
    if membership.role not in EDITORS:
        raise Http404
    form = ScriptForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            production.scenes.all().delete()
            Scene.objects.bulk_create(
                Scene(production=production, **s) for s in script.split_scenes(form.cleaned_data["script"])
            )
        return redirect("production-detail", pk=production.pk)
    return render(request, "productions/script.html", {"production": production, "form": form})


@login_required
def breakdown(request, pk):
    production, _ = _membership(request, pk)
    return render(request, "productions/breakdown.html", {
        "production": production,
        "breakdown": draft_breakdown(production),
    })
