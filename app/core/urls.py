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
  path("servizio/<int:id_servizio>/prenota/", views.book_service, name="book_service"),
    # Registration endpoint:
    # - GET: renders the registration page
    # - POST: processes registration form
    path("register/", views.register_view, name="register"),
    # Login endpoint:
    # - GET: renders the login page
    # - POST: processes credentials; returns JSON for AJAX, redirect for normal POST
    path("login/", views.login_view, name="login"),
    # Profile endpoint;
    path("profile/", views.profile_view, name="profile"),
    # Logout endpoint:
    # - should be called with POST (AJAX or normal). For AJAX returns JSON {success: True}
    path("logout/", views.logout_view, name="logout"),
    path('servizi/<str:tipo>/', views.scegli_servizio, name='scegli_servizio'),
    path("prenota/<str:tipo>/", views.book_service, name="book_service"),
]
