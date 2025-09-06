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

from .models import PersonModel, UserModel, ServizioModel
from .forms import RegisterForm


def homepage(request: HttpRequest) -> HttpResponse:
    """
    Render the site homepage.

    URL: /
    Methods: GET

    Template: index.html
    Context: 
    - servizi_disponibili: list of available services

    Returns a simple HttpResponse rendering the homepage template.
    """
    # Get all available services
    servizi_disponibili = ServizioModel.objects.filter(status='DISPONIBILE')
    
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
    debug = {"request_user": request.user.username}

    try:
        ut = UserModel.objects.select_related("CF").get(username=request.user.username)
        person = getattr(ut, "CF", None)
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

    return render(request, "user/profile.html", {"person": person, "debug": debug})


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
        # Get available camera instances
        from .models import CameraModel
        istanze_disponibili = CameraModel.objects.filter(
            ID_servizio=service,
        )
        ha_istanze = len(istanze_disponibili) > 0
    elif service.tipo_servizio == 'RISTORANTE':
        # Get available restaurant tables
        from .models import RistoranteModel
        istanze_disponibili = RistoranteModel.objects.filter(
            ID_servizio=service,
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
