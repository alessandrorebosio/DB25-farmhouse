"""
Registration forms for creating a PersonModel and a corresponding UserModel.

This module provides RegisterForm, a simple form that collects:
- person data: tax_code (CF), name, surname
- account data: username, email, password1, password2

Behavior summary:
- Validates tax_code length (16 chars).
- Validates username uniqueness against UserModel.
- Validates passwords match.
- save(): must be called only after form.is_valid(); creates the PersonModel
  if missing (does NOT update existing person) and creates a UserModel linked
  to that PersonModel inside a transaction. Password is hashed via Django's
  make_password before storage.

Notes:
- UserModel and PersonModel are assumed to map your existing DB tables.
- Because models may be unmanaged, .create() / .get_or_create() still work.
- The form raises django.core.exceptions.ValidationError for misuse (e.g.
  calling save() when the form is not valid).
"""

from django import forms
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Person, User


class RegisterForm(forms.Form):
    """
    Form used to register a new user and (optionally) create the related PersonModel.

    Fields:
      - tax_code: str, 16 characters (CF)
      - name: str, first name
      - surname: str, last name
      - username: str, account username (must be unique)
      - email: str, account email
      - password1/password2: password and confirmation

    Validation:
      - clean_tax_code(): normalizes and validates tax_code length.
      - clean_username(): ensures username is not already present in UserModel.
      - clean(): ensures password1 and password2 match.

    Saving:
      - save(): must be called only when form.is_valid() is True.
        Creates PersonModel if missing (does NOT modify an existing PersonModel).
        Creates UserModel linked to the PersonModel (assigns the PersonModel instance
        to the UserModel FK). The password is hashed via make_password before saving.

    Returns:
      - the created UserModel instance.

    Raises:
      - ValidationError if save() is called when the form is invalid.
    """

    tax_code = forms.CharField(label="Tax Code", max_length=16, min_length=16)
    name = forms.CharField(label="Name", max_length=50)
    surname = forms.CharField(label="Surname", max_length=50)
    username = forms.CharField(label="Username", max_length=30)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    def clean_tax_code(self):
        """
        Normalize and validate the tax code (CF).

        Returns the uppercased CF on success or raises ValidationError.
        """
        cf = self.cleaned_data["tax_code"].strip().upper()
        if len(cf) != 16:
            raise ValidationError("Tax code must be 16 characters.")
        return cf

    def clean_username(self):
        """
        Ensure the chosen username is not already present in UserModel.
        """
        u = self.cleaned_data["username"]
        if User.objects.filter(username=u).exists():
            raise ValidationError("Username already in use.")
        return u

    def clean(self):
        """
        Cross-field validation: ensure password1 and password2 match.
        """
        cleaned = super().clean()
        if cleaned.get("password1") and cleaned.get("password2"):
            if cleaned["password1"] != cleaned["password2"]:
                raise ValidationError("Passwords do not match.")
        return cleaned

    def save(self):
        """
        Persist the PersonModel (if missing) and create the UserModel.

        Important behavior:
        - If a PersonModel with the given CF already exists, this method will NOT
          update the existing person's name or surname.
        - UserModel is created with the hashed password.
        - Operation runs inside transaction.atomic() to ensure consistency.

        Returns:
            UserModel: the newly created user instance.

        Raises:
            ValidationError: if the form is not valid when save() is called.
        """
        if not self.is_valid():
            raise ValidationError("Form must be valid before saving.")

        with transaction.atomic():
            # create person only if missing (do not update existing person)
            person, created = Person.objects.get_or_create(
                CF=self.cleaned_data["tax_code"],
                defaults={
                    "nome": self.cleaned_data["name"],
                    "cognome": self.cleaned_data["surname"],
                },
            )

            # create the user and link to the person instance (assign FK instance)
            user = User.objects.create(
                username=self.cleaned_data["username"],
                CF=person,  # if your FK field is named differently adapt accordingly
                password=make_password(self.cleaned_data["password1"]),
                email=self.cleaned_data["email"],
            )

        return user
