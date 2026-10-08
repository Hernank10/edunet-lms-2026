from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

from .forms import CustomUserCreationForm


def registro(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:panel")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/registro.html", {"form": form})


@login_required
def perfil(request):
    return render(request, "accounts/perfil.html", {"user": request.user})


def panel(request):
    """Redirige al usuario segÃºn su rol."""
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_superuser:
        return redirect("/admin/")
    elif request.user.is_staff:
        return redirect("profesor:dashboard")
    else:
        return redirect("gamificacion:dashboard")