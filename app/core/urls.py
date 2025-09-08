from django.urls import path
from . import views

urlpatterns = [
    path("", views.homepage, name="homepage"),
    path("servizio/<int:id_servizio>/prenota/", views.book_service, name="book_service"),
    path("services/", views.services, name="services"),
    path("services/book/", views.book_service_from_services, name="book_service_from_services"),
    # Registration endpoint:
    path("register/", views.register_view, name="register"),
    # Login endpoint:
    path("login/", views.login_view, name="login"),
    # Profile endpoint
    path("profile/", views.profile_view, name="profile"),
    # Logout endpoint
    path("logout/", views.logout_view, name="logout"),
    path("event/", views.list_event, name="list-event"),
    path("event/<int:event_id>/subscribe/", views.event_subscription, name="event_subscription"),
    path("event/<int:event_id>/cancel/", views.cancel_enrollment, name="cancel_enrollment"),
    path("services/<str:type>/", views.choose_service, name="choose_service"),
    path("booking/<str:type>/", views.book_service, name="book_service"),
]
