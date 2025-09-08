"""
Core views for the application.

This module exposes simple views used by the app:
- homepage: renders the site landing page.
- register_view: handles user registration (creates PersonModel and UserModel).
- login_view: displays & processes the authentication form.
- profile_view: shows data for the currently logged-in user.
- logout_view: logs out the current user.

Notes:
- Templates used by these views are under core/auth/ and user/.
- register_view relies on RegisterForm from .forms which encapsulates
  validation and persistence of PersonModel and UserModel.
- profile_view expects UserModel to relate to PersonModel via the CF FK.
"""

from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import DatabaseError
from datetime import datetime, timedelta
from django.db.models import Q, Prefetch
from .models import *

from .forms import RegisterForm
# from django.contrib.auth.decorators import login_required

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.core.exceptions import PermissionDenied

# View per prenotazione servizio


# Gestione doppia firma per compatibilità con entrambe le url
from django.http import Http404


# Backend booking logic for services from services.html
from django.views.decorators.http import require_POST

def homepage(request: HttpRequest) -> HttpResponse:
    """
    Render the site homepage.

    URL: /
    Methods: GET

    Template: index.html
    Context: none

    Returns a simple HttpResponse rendering the homepage template.
    """
    tipi_servizi = Service.objects.values_list("type", flat=True).distinct()
    servizi = Service.objects.filter(type__in=tipi_servizi, status="DISPONIBILE")
    tipi_unici = []
    visti = set()
    for s in servizi:
        if s.type not in visti:
            tipi_unici.append(s)
            visti.add(s.type)

    return render(request, "index.html", {"servizi_disponibili": tipi_unici})


def services(request):
    from collections import defaultdict

    service_types = Service.objects.filter(status="DISPONIBILE").values_list("type", flat=True).distinct()
    grouped_services = {}
    for s_type in service_types:
        # Get all services of this type
        services_of_type = Service.objects.filter(type=s_type, status="DISPONIBILE")
        # Get related instances
        if s_type == "CAMERA":
            instances = Room.objects.filter(id__in=services_of_type)
        elif s_type == "PISCINA":
            instances = Pool.objects.filter(id__in=services_of_type)
        elif s_type == "ATTIVITA_CON_ANIMALI":
            instances = AnimalActivity.objects.filter(id__in=services_of_type)
        elif s_type == "CAMPO_DA_GIOCO":
            instances = Playground.objects.filter(id__in=services_of_type)
        elif s_type == "RISTORANTE":
            instances = Restaurant.objects.filter(id__in=services_of_type)
        else:
            instances = []
        grouped_services[s_type] = instances

    hours = ["08", "10", "12", "14", "16", "18", "20"]
    return render(request, "services.html", {"grouped_services": grouped_services, "hours": hours})

def register_view(request: HttpRequest) -> HttpResponse:
    """
    Registration view (create PersonModel if missing and a linked UserModel).

    URL: /register/ (example)
    Methods: GET, POST

    GET:
      - Instantiate an empty RegisterForm and render the registration template.

    POST:
      - Bind RegisterForm(request.POST). If valid, call form.save() which:
         * creates PersonModel if missing (does NOT update an existing person),
         * creates UserModel with hashed password.
      - On success redirect to the login page (name="login").
      - On validation error re-render the form with errors.

    Template: core/auth/register.html
    Context:
      - form: RegisterForm instance

    Important:
      - RegisterForm.save() must only be called when form.is_valid() is True.
      - This view does not log the user in after registration; it redirects to login.
    """
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = RegisterForm()

    return render(request, "core/auth/register.html", {"form": form})


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Display and process the login form.

    Uses Django's AuthenticationForm to validate credentials.

    GET:
      - Renders core/auth/login.html with an empty AuthenticationForm.

    POST:
      - Binds AuthenticationForm(request, data=request.POST).
      - If valid logs the user in and redirects to:
          request.GET.get('next') if present, otherwise '/'.
      - If invalid re-renders the form with errors.

    Template: core/auth/login.html
    Context:
      - form: AuthenticationForm instance
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next") or "/")
    else:
        form = AuthenticationForm(request)
    return render(request, "core/auth/login.html", {"form": form})


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    """
    Show profile information for the logged-in user, including event enrollments
    and service bookings.
    """
    try:
        ut = User.objects.select_related("cf").get(username=request.user.username)
    except User.DoesNotExist:
        return render(request, "user/profile.html", {"person": None})

    person = getattr(ut, "cf", None)

    try:
        subscriptions = (
            Enrolls.objects.filter(
                Q(username__username=request.user.username)
                | Q(username=request.user.username)
            )
            .select_related("event")
            .order_by("-event__date")
        )
    except Exception:
        subscriptions = None

    try:
        bookings = (
            Booking.objects.filter(username__username=request.user.username)
            .select_related("username")
            .prefetch_related(
                Prefetch(
                    "details",
                    queryset=BookingDetail.objects.select_related("service"),
                )
            )
            .order_by("-booking_date") 
        )
    except Exception:
        bookings = Booking.objects.none()

    try:
        reviews = (
            Review.objects.filter(username__username=request.user.username)
            .select_related("id_booking")
            .order_by("-review_date")
        )
    except Exception:
        reviews = Review.objects.none()

    return render(
        request,
        "user/profile.html",
        {
            "person": person,
            "subscriptions": subscriptions,
            "bookings": bookings,
            "reviews": reviews,
        },
    )


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """
    Log out the current user and redirect to the homepage ('/').

    URL: /logout/ (example)
    Methods: GET or POST depending on how you wire it (POST recommended for safety).

    Behavior:
      - Calls django.contrib.auth.logout(request).
      - Redirects to '/'.

    Note:
      - Prefer POST-based logout to protect against CSRF; ensure templates use a form with {% csrf_token %}.
    """
    logout(request)
    return redirect("/")


def list_event(request):
    """
    Shows all future events (data_evento >= today).
    If the user is authenticated, allows subscription.
    """
    eventi = Event.objects.filter(date__gte=timezone.now().date()).order_by("date")
    return render(request, "core/events/event-list.html", {"eventi": eventi})


@login_required
def event_subscription(request, event_id):
    """
    Handles event enrollment for the authenticated user.

    - Retrieves the event by ID.
    - On POST: gets the number of participants (default 1), finds the user in the DB.
    - If an enrollment already exists, increments participants and decreases event seats accordingly.
    - Shows a success message on success, error message on DB error (e.g., event full).
    - Always redirects to the event list.
    """
    event = get_object_or_404(Event, pk=event_id)

    if request.method == "POST":
        participants = int(request.POST.get("partecipanti", 1))
        user_db = get_object_or_404(User, username=request.user.username)

        enrollment = Enrolls.objects.filter(event=event, username=user_db).first()

        try:
            if enrollment:
                if event.seats >= participants:
                    enrollment.participants += participants
                    enrollment.save()
                    event.seats -= participants
                    event.save()
                    messages.success(request, "Enrollment updated successfully!")
                else:
                    messages.error(request, "Not enough seats available.")
            else:
                if event.seats >= participants:
                    Enrolls.objects.create(
                        event=event,
                        username=user_db,
                        participants=participants,
                    )
                    event.seats -= participants
                    event.save()
                    messages.success(request, "Enrollment successful!")
                else:
                    messages.error(request, "Not enough seats available.")
        except DatabaseError:
            messages.error(
                request, "Invalid enrollment: no seats available or limit exceeded."
            )

    return redirect("list-event")


@login_required
def cancel_enrollment(request, event_id):
    """
    Cancels the logged-in user's enrollment for an event.
    The DB trigger handles seat increment.
    """
    if request.method == "POST":
        user_db = get_object_or_404(User, username=request.user.username)

        enrollment = Enrolls.objects.filter(event_id=event_id, username=user_db).first()

        if enrollment:
            enrollment.delete()

    return redirect("profile")


def choose_service(request, tipo):
    istanze = Service.objects.filter(type=tipo, status="DISPONIBILE")
    return render(
        request, "core/choose_service.html", {"istanze": istanze, "tipo": tipo}
    )


@login_required(login_url="login")
def book_service(request, type=None, service_id=None, service_type=None):
    """
    Handles booking for various service types.

    Supports both 'type' and 'service_id' parameters for backward compatibility.

    - If 'type' or 'service_type' is provided, displays available instances for that type.
    - For non-room services, validates booking duration (must be 2 hours) on POST.
    - If 'service_id' is provided, renders the booking page for the specific service.
    - Raises 404 if parameters are invalid.
    """
    # Allow both 'type' and 'service_type' for compatibility
    if service_type:
        type = service_type

    if type:
        # Dynamically select instances based on service type
        if type == "ROOM":
            instances = Room.objects.select_related("id").all()
        elif type == "POOL":
            instances = Pool.objects.select_related("id").all()
        elif type == "ANIMAL_ACTIVITY":
            instances = AnimalActivity.objects.select_related("id").all()
        elif type == "PLAYGROUND":
            instances = Playground.objects.select_related("id").all()
        elif type == "RESTAURANT":
            instances = Restaurant.objects.select_related("id").all()
        else:
            instances = []

        context = {
            "instances": instances,
            "type": type,
        }
        errors = []
        # For non-room services, validate booking duration on POST
        if type != "ROOM" and request.method == "POST":
            date_str = request.POST.get("start_date")
            start_time_str = request.POST.get("start_time")
            end_time_str = request.POST.get("end_time")
            if date_str and start_time_str and end_time_str:
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                    start_time = datetime.strptime(start_time_str, "%H:%M").time()
                    end_time = datetime.strptime(end_time_str, "%H:%M").time()
                    dt_start = datetime.combine(date_obj, start_time)
                    dt_end = datetime.combine(date_obj, end_time)
                    if (dt_end - dt_start) > timedelta(hours=2):
                        errors.append("Booking duration must be exactly two hours.")
                except ValueError:
                    errors.append("Invalid date or time format.")
            if errors:
                context["errors"] = errors
        return render(request, "book_service.html", context)
    elif service_id:
        # Legacy logic: show details for a specific service by ID
        return render(request, "book_service.html", {"service_id": service_id})
    else:
        raise Http404("Invalid parameter for service booking.")


@login_required(login_url="login")
@require_POST
def book_service_from_services(request):
    """
    Handles booking submission from the services page.
    - Rooms (CAMERA): requires start_date and end_date.
    - Other services: requires start_date, start_time, end_time (max 2 consecutive hours).
    - Creates Booking and BookingDetail records for the user.
    """
    user_db = get_object_or_404(User, username=request.user.username)

    service_type = request.POST.get("service_type")
    instance_id = request.POST.get("instance")
    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")
    start_time = request.POST.get("start_time")
    end_time = request.POST.get("end_time")

    # Find the Service instance
    try:
        service = Service.objects.get(id=instance_id)
    except Service.DoesNotExist:
        messages.error(request, "Selected service does not exist.")
        return redirect("services")

    # Validate dates/times
    if service_type.upper() == "CAMERA":
        # Room booking → needs both start and end dates
        if not (start_date and end_date):
            messages.error(request, "Please provide start and end dates.")
            return redirect("services")
    else:
        # Other services → need date and both times
        if not (start_date and start_time and end_time):
            messages.error(request, "Please provide date and time.")
            return redirect("services")
        try:
            dt_start = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
            dt_end = datetime.strptime(f"{start_date} {end_time}", "%Y-%m-%d %H:%M")

            duration = dt_end - dt_start

            # End time must be after start time
            if duration <= timedelta(0):
                messages.error(request, "End time must be later than start time.")
                return redirect("services")

            # Max duration = 2 hours
            if duration > timedelta(hours=2):
                messages.error(request, "Maximum booking duration is 2 hours.")
                return redirect("services")

        except Exception:
            messages.error(request, "Invalid date or time format.")
            return redirect("services")

    # Create Booking and BookingDetail
    try:
        booking = Booking.objects.create(
            username=user_db,
            booking_date=timezone.now(),
        )

        if service_type.upper() == "CAMERA":
            # Room booking detail
            BookingDetail.objects.create(
                booking=booking,
                service=service,
                start_date=start_date,
                end_date=end_date,
            )
        else:
            # Other services → same-day booking with max 2 hours
            BookingDetail.objects.create(
                booking=booking,
                service=service,
                start_date=start_date,
                end_date=start_date,
            )

        messages.success(request, "Booking successful!")
    except Exception as e:
        messages.error(request, f"Booking failed: {str(e)}")

    return redirect("services")
