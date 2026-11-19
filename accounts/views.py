from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def signup(request):
    if request.user.is_authenticated:
        return redirect("production-list")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.save())
        return redirect("production-list")
    return render(request, "registration/signup.html", {"form": form})
