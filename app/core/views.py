"""Core views for the application.

Provides simple homepage, login and logout views. The login view uses Django's
AuthenticationForm to validate credentials and redirects to the 'next' GET
parameter (if present) or to the site root ('/') on success.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from .models import PersonModel, UserModel


def homepage(request: HttpRequest) -> HttpResponse:
    """Render the site homepage.

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponse rendering 'index.html'.
    """
    return render(request, "index.html")


def register_view(request: HttpRequest) -> HttpResponse:
    """Render the site register.

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponse rendering 'register.html'.
    """
    return render(request, "user/register.html")


def login_view(request: HttpRequest) -> HttpResponse:
    """Display and process the login form.

    Uses Django's AuthenticationForm to authenticate users. On POST, if the
    form is valid, logs the user in and redirects to the 'next' GET parameter
    or to the root path ('/'). On GET, renders the login form.

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponse rendering 'login.html' with the form, or a redirect after
        successful login.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next") or "/")
    else:
        form = AuthenticationForm(request)
    return render(request, "user/login.html", {"form": form})


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Get logged user's related PersonModel via the FK on UserModel.
    Uses select_related for one query and passes 'person' to the template.
    Also passes a small debug dict so you can inspect values in the template.
    """
    person = None
    debug = {"request_user": request.user.username}

    try:
        ut = UserModel.objects.select_related("CF").get(username=request.user.username)
        person = getattr(ut, "CF", None)
        debug["user_CF_obj"] = (
            None
            if person is None
            else {"CF": person.CF, "nome": person.nome, "cognome": person.cognome}
        )
    except UserModel.DoesNotExist:
        debug["error"] = "UserModel.DoesNotExist"

    return render(request, "profile.html", {"person": person, "debug": debug})


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """Log out the current user and redirect to the homepage ('/').

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponseRedirect to '/'.
    """
    logout(request)
    return redirect("/")
