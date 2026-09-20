from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required


def registro(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(request, "accounts/registro.html", {"form": form})


@login_required
def perfil(request):
    return render(request, "accounts/perfil.html", {"user": request.user})



from django.shortcuts import redirect


def panel(request):
    """Redirige al usuario según su rol."""
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.is_superuser:
        return redirect("/admin/")
    elif request.user.is_staff:
        return redirect("profesor:dashboard")
    else:
        return redirect("gamificacion:dashboard")
