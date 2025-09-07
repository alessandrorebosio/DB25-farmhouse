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

from .models import *
from .models import Person, User, Service, Room, Pool, AnimalActivity, Playground, Restaurant
from .forms import RegisterForm

from django.contrib.auth.decorators import login_required
# View per prenotazione servizio


# Gestione doppia firma per compatibilità con entrambe le url
from django.http import Http404


def homepage(request: HttpRequest) -> HttpResponse:
    """
    Render the site homepage.

    URL: /
    Methods: GET

    Template: index.html
    Context: none

    Returns a simple HttpResponse rendering the homepage template.
    """
    tipi_servizi = Service.objects.values_list('type', flat=True).distinct()
    servizi = Service.objects.filter(type__in=tipi_servizi, status='DISPONIBILE')
    tipi_unici = []
    visti = set()
    for s in servizi:
        if s.type not in visti:
            tipi_unici.append(s)
            visti.add(s.type)
    return render(request, "index.html", {"servizi_disponibili": tipi_unici})


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
    Show profile information for the logged-in user.

    URL: /profile/ (example)
    Methods: GET

    Behavior:
      - Uses request.user.username to locate the corresponding UserModel row.
      - Uses select_related on the FK to PersonModel to avoid extra queries when possible.
      - Passes `person` (PersonModel instance or None) to the template along with
        a small debug dict for development.

    Template: user/profile.html
    Context:
      - person: PersonModel instance (or None)
      - debug: dict with diagnostic values (can be removed in production)

    Security:
      - Protected with @login_required so only authenticated users can access it.
    """
    iscrizioni = []
    debug = {}

    try:
        ut = User.objects.select_related("cf").get(username=request.user.username)
        iscrizioni = (
            Enrolls.objects.filter(
                username=ut,
                event__date__gte=timezone.now().date(), 
            )
            .select_related("event")
            .order_by("event__date")
        )

        debug["iscrizioni_count"] = iscrizioni.count()
    except User.DoesNotExist:
        return render(request, "user/profile.html", {"person": None})

    person = getattr(ut, "cf", None)

    return render(
        request,
        "user/profile.html",
        {"person": person, "iscrizioni": iscrizioni, "debug": debug},
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
    istanze = Service.objects.filter(type=tipo, status='DISPONIBILE')
    return render(request, "core/choose_service.html", {"istanze": istanze, "tipo": tipo})




from datetime import datetime, timedelta

@login_required(login_url='login')
def book_service(request, tipo=None, id_servizio=None, tipo_servizio=None):
  # Supporta chiamate sia con tipo che con id_servizio (per retrocompatibilità url)
  if tipo_servizio:
    tipo = tipo_servizio
  if tipo:
    # Logica dinamica per istanze in base al tipo
    if tipo == 'CAMERA':
      istanze = Room.objects.select_related('id').all()
    elif tipo == 'PISCINA':
      istanze = Pool.objects.select_related('id').all()
    elif tipo == 'ATTIVITA_CON_ANIMALI':
      istanze = AnimalActivity.objects.select_related('id').all()
    elif tipo == 'CAMPO_DA_GIOCO':
      istanze = Playground.objects.select_related('id').all()
    elif tipo == 'RISTORANTE':
      istanze = Restaurant.objects.select_related('id').all()
    else:
      istanze = []
    context = {
      'istanze': istanze,
      'tipo': tipo,
    }
    errors = []
    if tipo != 'CAMERA' and request.method == "POST":
      data = request.POST.get('data_inizio')
      ora_inizio = request.POST.get('ora_inizio')
      ora_fine = request.POST.get('ora_fine')
      if data and ora_inizio and ora_fine:
        try:
          d = datetime.strptime(data, "%Y-%m-%d").date()
          t_inizio = datetime.strptime(ora_inizio, "%H:%M").time()
          t_fine = datetime.strptime(ora_fine, "%H:%M").time()
          dt_inizio = datetime.combine(d, t_inizio)
          dt_fine = datetime.combine(d, t_fine)
          if (dt_fine - dt_inizio) > timedelta(hours=2):
            errors.append("La prenotazione deve essere di fasce di due ore.")
        except ValueError:
          errors.append("Formato data o ora non valido.")
      if errors:
        context['errors'] = errors
    return render(request, 'book_service.html', context)
  elif id_servizio:
    # Logica legacy: mostra dettagli per id_servizio
    return render(request, "book_service.html", {"id_servizio": id_servizio})
  else:
    raise Http404("Parametro non valido per prenotazione servizio.")
