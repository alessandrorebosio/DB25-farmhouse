"""
URL configuration for the core app.

This module exposes simple routes used by the site frontend:
- ""        -> homepage view (name="homepage")
- "login/"   -> login view, accepts normal and AJAX POSTs (name="login")
- "logout/"  -> logout view, expects POST (AJAX or normal) (name="logout")

Notes:
- Use the named routes in templates and JS (reverse / {% url %}) to keep links consistent.
- The login view returns JSON when called via X-Requested-With: XMLHttpRequest (used by the
  AJAX modal on the homepage). The logout view similarly supports AJAX POST.
"""

from django.urls import path
from . import views

urlpatterns = [
    # Main landing page
    path("", views.homepage, name="homepage"),
    # Login endpoint:
    # - GET: renders the login page (or is used by the AJAX modal)
    # - POST: processes credentials; returns JSON for AJAX, redirect for normal POST
    path("login/", views.login_view, name="login"),
    # Logout endpoint:
    # - should be called with POST (AJAX or normal). For AJAX returns JSON {success: True}
    path("logout/", views.logout_view, name="logout"),
]
