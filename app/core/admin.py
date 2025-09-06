"""
Admin configuration for core app.

This module provides admin forms and ModelAdmin classes to manage the
external tables mapped by the project's models:
- PersonModel  -> external PERSONA table (managed=False)
- UserModel    -> external UTENTE table (managed=False)
- StaffModel   -> external DIPENDENTE table (managed=False)

Notes:
- Passwords for UserModel are hashed here with Django's make_password before saving.
- Database operations that touch multiple tables use transaction.atomic to keep consistency.
- Because these models map external tables, migrations are not managed by Django.
"""

from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.db import transaction
from .models import PersonModel, UserModel, StaffModel


class StaffForm(forms.ModelForm):
    """
    Custom ModelForm for StaffModel.

    Purpose:
    - Make the termination date (data_licenziamento) optional in the admin form.
      This allows creating a staff record without specifying a termination date.
    """

    class Meta:
        model = StaffModel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "data_licenziamento" in self.fields:
            self.fields["data_licenziamento"].required = False


class UserForm(forms.ModelForm):
    """
    Admin form for UserModel (external UTENTE table).

    Behavior:
    - On creation (no instance.username) the password field is required.
    - On edit, password is optional; leaving it blank preserves the stored hash.
    - The password field uses PasswordInput so plain text is not shown in admin.
    Security:
    - Hash passwords with Django's configured password hasher via make_password.
    """

    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Enter a password. Leave empty when editing to keep the current password.",
    )

    class Meta:
        model = UserModel
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not getattr(self.instance, "username", None):
            self.fields["password"].required = True


@admin.register(PersonModel)
class PersonAdmin(admin.ModelAdmin):
    """
    Admin registration for PersonModel.

    Shows CF, first name and last name in the changelist and enables search by CF.
    """

    list_display = ("CF", "nome", "cognome")
    search_fields = ("CF",)


@admin.register(UserModel)
class UserAdmin(admin.ModelAdmin):
    """
    Admin registration for UserModel.

    Responsibilities:
    - Use UserForm to control password input.
    - Hash password before saving to the external UTENTE table.
    - Keep save operation atomic to avoid partial writes.
    """

    form = UserForm
    list_display = ("CF", "username", "email", "password")
    search_fields = ("username",)

    def save_model(self, request, obj, form, change):
        """
        Save UserModel to external table with password hashing.

        Parameters:
        - request: HttpRequest (unused here but required signature)
        - obj: UserModel instance (not yet saved)
        - form: bound form with cleaned_data
        - change: bool, True if editing an existing object

        Behavior:
        - If creating: password must be provided and will be hashed.
        - If editing: if password left blank the existing hashed password is kept;
          if a new password is provided it will be hashed before save.
        """
        pwd = form.cleaned_data.get("password")

        if change:
            if not pwd:
                try:
                    existing = UserModel.objects.get(username=obj.username)
                    obj.password = existing.password
                except UserModel.DoesNotExist:
                    raise ValueError("Existing user not found; password required.")
            else:
                obj.password = make_password(pwd)
        else:
            obj.password = make_password(pwd)

        with transaction.atomic():
            obj.save()


@admin.register(StaffModel)
class StaffAdmin(admin.ModelAdmin):
    """
    Admin registration for StaffModel.

    Features:
    - Uses StaffForm to make termination date optional.
    - Hides data_licenziamento on the Add form, shows it on the Change form.
    """

    form = StaffForm
    list_display = ("username", "data_assunzione", "data_licenziamento")
    search_fields = ("username",)

    def get_fields(self, request, obj=None):
        """
        Return the fields to display in the admin form.

        When adding a new staff (obj is None) do not show the termination date.
        When editing show the termination date so admin can set it.
        """
        base = ("username", "ruolo", "data_assunzione")
        if obj is None:
            return base
        return base + ("data_licenziamento",)
