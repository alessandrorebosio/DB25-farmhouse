"""Core views for the application.

Provides simple homepage, login and logout views. The login view uses Django's
AuthenticationForm to validate credentials and redirects to the 'next' GET
parameter (if present) or to the site root ('/') on success.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


def homepage(request: HttpRequest) -> HttpResponse:
    """Render the site homepage.

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponse rendering 'index.html'.
    """
    return render(request, "index.html")


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
    return render(request, "auth/login.html", {"form": form})


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """Log out the current user and redirect to the homepage ('/').

    Args:
        request: Django HttpRequest instance.

    Returns:
        HttpResponseRedirect to '/'.
    """
    logout(request)
    return redirect("/")
