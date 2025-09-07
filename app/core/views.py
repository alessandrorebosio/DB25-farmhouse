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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import PersonModel, UserModel, EventModel, EnrollModel, ServizioModel
from .forms import RegisterForm


def homepage(request: HttpRequest) -> HttpResponse:
    """
    Render the site homepage.

    URL: /
    Methods: GET

    Template: index.html
    Context: 
    - servizi_disponibili: list of available services (one per type)

    Returns a simple HttpResponse rendering the homepage template.
    Shows only one representative service per type to avoid duplicates.
    """
    # Get one service per type to avoid showing duplicates
    # Use distinct() on tipo_servizio to get unique service types
    servizi_disponibili = []
    
    # Get all unique service types that are available
    tipi_servizi = ServizioModel.objects.filter(
        status='DISPONIBILE'
    ).values_list('tipo_servizio', flat=True).distinct()
    
    # For each service type, get the first available service as representative
    for tipo in tipi_servizi:
        servizio_rappresentativo = ServizioModel.objects.filter(
            status='DISPONIBILE',
            tipo_servizio=tipo
        ).first()
        if servizio_rappresentativo:
            servizi_disponibili.append(servizio_rappresentativo)
    
    context = {
        'servizi_disponibili': servizi_disponibili
    }
    
    return render(request, "index.html", context)


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
    person = None
    iscrizioni = []
    debug = {"request_user": request.user.username}

    try:
        ut = UserModel.objects.select_related("CF").get(username=request.user.username)
        person = getattr(ut, "CF", None)
        
        # recupero le iscrizioni solo ad eventi futuri
        iscrizioni = (
            EnrollModel.objects.filter(
                username=ut,
                ID_evento__data_evento__gte=timezone.now(),  # 👈 filtro eventi futuri
            )
            .select_related("ID_evento")
            .order_by("ID_evento__data_evento")
        )
        
        debug["iscrizioni_count"] = iscrizioni.count()
        
        debug["user_CF_obj"] = (
            None
            if person is None
            else {
                "CF": getattr(person, "CF", None),
                "nome": getattr(person, "nome", None),
                "cognome": getattr(person, "cognome", None),
            }
        )
    except UserModel.DoesNotExist:
        debug["error"] = "UserModel.DoesNotExist"

    return render(request, "user/profile.html", {"person": person,"iscrizioni":iscrizioni, "debug": debug})


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


def eventi_list(request):
    """
    Shows all future events (data_evento >= today).
    If the user is authenticated, allows subscription.
    """
    eventi = EventModel.objects.filter(data_evento__gte=timezone.now().date()).order_by("data_evento")
    return render(request, "core/events/eventi.html", {"eventi": eventi})

@login_required
def iscrizione_evento(request, evento_id):
    evento = get_object_or_404(EventModel, pk=evento_id)

    if request.method == "POST":
        partecipanti = int(request.POST.get("partecipanti", 1))

        utente_db = get_object_or_404(UserModel, username=request.user.username)

        iscrizione = EnrollModel.objects.filter(ID_evento=evento, username=utente_db).first()



        if iscrizione:
            iscrizione.partecipanti += partecipanti
            iscrizione.save()
        else:
            EnrollModel.objects.create(
                ID_evento=evento,
                username=utente_db,
                partecipanti=partecipanti,
            )

        return redirect("eventi-list")

    return redirect("eventi-list")
  
@login_required
def cancella_iscrizione(request, evento_id):
    """
    Cancella l'iscrizione dell'utente loggato a un evento.
    Il trigger nel DB gestisce l'incremento dei posti.
    """
    if request.method == "POST":
        utente_db = get_object_or_404(UserModel, username=request.user.username)

        iscrizione = EnrollModel.objects.filter(
            ID_evento_id=evento_id, username=utente_db
        ).first()

        if iscrizione:
            iscrizione.delete()  

    return redirect("profile")


def book_service(request, service_id):
    """
    Handle service booking for specific service ID.
    
    URL: /book/<int:service_id>/
    Methods: GET, POST
    
    GET:
      - Display booking form for the specified service
      - Show available instances if applicable (cameras, tables, etc.)
    
    POST:
      - Process booking form submission
      - Create booking record
      
    Behavior:
      - Redirects to login if user is not authenticated
      - Shows service details and booking form
    """
    # Check if user is authenticated
    if not request.user.is_authenticated:
        from django.urls import reverse
        login_url = reverse('login')
        book_url = reverse('book_service', args=[service_id])
        return redirect(f"{login_url}?next={book_url}")
    
    # Get the service or return 404
    from django.shortcuts import get_object_or_404
    from datetime import datetime
    
    service = get_object_or_404(ServizioModel, ID_servizio=service_id)
    
    # Determine if this service type has instances
    ha_istanze = False
    istanze_disponibili = []
    
    if service.tipo_servizio == 'CAMERA':
        # Get ALL available camera instances of this service type
        from .models import CameraModel
        # Find all services of type CAMERA that are available
        servizi_camera = ServizioModel.objects.filter(
            tipo_servizio='CAMERA',
            status='DISPONIBILE'
        )
        # Get camera instances for all these services
        istanze_disponibili = CameraModel.objects.filter(
            ID_servizio__in=servizi_camera
        )
        ha_istanze = len(istanze_disponibili) > 0
    elif service.tipo_servizio == 'RISTORANTE':
        # Get ALL available restaurant table instances of this service type
        from .models import RistoranteModel
        # Find all services of type RISTORANTE that are available
        servizi_ristorante = ServizioModel.objects.filter(
            tipo_servizio='RISTORANTE',
            status='DISPONIBILE'
        )
        # Get restaurant instances for all these services
        istanze_disponibili = RistoranteModel.objects.filter(
            ID_servizio__in=servizi_ristorante
        )
        ha_istanze = len(istanze_disponibili) > 0
    elif service.tipo_servizio == 'PISCINA':
        # Get ALL available pool chair instances of this service type
        from .models import PiscinaModel
        # Find all services of type PISCINA that are available
        servizi_piscina = ServizioModel.objects.filter(
            tipo_servizio='PISCINA',
            status='DISPONIBILE'
        )
        # Get pool instances for all these services
        istanze_disponibili = PiscinaModel.objects.filter(
            ID_servizio__in=servizi_piscina
        )
        ha_istanze = len(istanze_disponibili) > 0
    elif service.tipo_servizio == 'CAMPO_DA_GIOCO':
        # Get ALL available field instances of this service type
        from .models import CampoDaGiocoModel
        # Find all services of type CAMPO_DA_GIOCO that are available
        servizi_campo = ServizioModel.objects.filter(
            tipo_servizio='CAMPO_DA_GIOCO',
            status='DISPONIBILE'
        )
        # Get field instances for all these services
        istanze_disponibili = CampoDaGiocoModel.objects.filter(
            ID_servizio__in=servizi_campo
        )
        ha_istanze = len(istanze_disponibili) > 0
    elif service.tipo_servizio == 'ATTIVITA_CON_ANIMALI':
        # Get ALL available animal activity instances of this service type
        from .models import AttivitaConAnimaliModel
        # Find all services of type ATTIVITA_CON_ANIMALI that are available
        servizi_animali = ServizioModel.objects.filter(
            tipo_servizio='ATTIVITA_CON_ANIMALI',
            status='DISPONIBILE'
        )
        # Get animal activity instances for all these services
        istanze_disponibili = AttivitaConAnimaliModel.objects.filter(
            ID_servizio__in=servizi_animali
        )
        ha_istanze = len(istanze_disponibili) > 0
    
    if request.method == 'POST':
        # Process booking form
        data_inizio = request.POST.get('data_inizio')
        data_fine = request.POST.get('data_fine')
        istanza_selezionata = request.POST.get('istanza_selezionata')
        
        # TODO: Create booking record in database
        # For now, just show success message
        from django.contrib import messages
        messages.success(request, f'Prenotazione per {service.get_tipo_servizio_display()} confermata!')
        return redirect('homepage')
    
    context = {
        'service': service,
        'ha_istanze': ha_istanze,
        'istanze_disponibili': istanze_disponibili,
        'today': datetime.today(),
    }
    
    return render(request, 'book_service.html', context)
