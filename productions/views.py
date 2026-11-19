from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .breakdown import draft_breakdown
from .forms import ProductionForm
from .llm import LLMError
from .models import Breakdown


def _own_production(request, pk):
    return get_object_or_404(request.user.productions, pk=pk)


@login_required
def production_list(request):
    return render(request, "productions/list.html", {"productions": request.user.productions.all()})


@login_required
def production_create(request):
    form = ProductionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        production = form.save(commit=False)
        production.owner = request.user
        production.save()
        messages.success(request, f"Created {production.title}.")
        return redirect(production)
    return render(request, "productions/form.html", {"form": form})


@login_required
def production_edit(request, pk):
    production = _own_production(request, pk)
    form = ProductionForm(request.POST or None, instance=production)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Saved.")
        return redirect(production)
    return render(request, "productions/form.html", {"form": form, "production": production})


@login_required
def production_detail(request, pk):
    production = _own_production(request, pk)
    return render(request, "productions/detail.html", {
        "production": production,
        "breakdown": production.breakdowns.first(),
        "ai_configured": bool(settings.OPENROUTER_API_KEY),
    })


@login_required
@require_POST
def production_breakdown(request, pk):
    production = _own_production(request, pk)
    try:
        data = draft_breakdown(production.script)
    except LLMError as e:
        messages.error(request, str(e))
    else:
        Breakdown.objects.create(production=production, model=settings.OPENROUTER_MODEL, data=data)
        messages.success(request, "Draft breakdown ready. Check it against the script before you rely on it.")
    return redirect(production)
