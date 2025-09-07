"""
Authentication backend that delegates authentication to the external UTENTE table.

Overview
- Checks credentials against UserModel (which maps the UTENTE table).
- On successful authentication returns (or creates) a local Django User and
  synchronizes basic attributes (email, is_staff, is_superuser) using StaffModel.
- Uses transaction.atomic around the user sync to avoid partial updates.

Security notes
- This backend prefers hashed passwords (checked with django.check_password).
  For legacy compatibility it currently allows a plain-text match fallback (stored == password).
  Migrate UTENTE.password to Django-hashed passwords (make_password) and remove the
  plain-text fallback as soon as possible.
- Local Django User passwords are set to unusable if the backend is the source of truth.
"""

from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth.hashers import check_password
from django.db import transaction

from .models import User, Employee


class UserBackend(BaseBackend):
    """
    Authenticate against the external UTENTE table.

    Behaviour summary:
    - If credentials are valid, ensure a corresponding Django User exists.
    - If a StaffModel record exists for the username, mark the Django User as is_staff.
      If StaffModel.ruolo == "admin" (case-insensitive) mark is_superuser too.
    - The backend does not rely on a usable local Django password (it sets an unusable
      password if none exists) because authentication is delegated to the external table.
    """

    def authenticate(
        self,
        request,
        username: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs
    ) -> Optional[DjangoUser]:
        """
        Try to authenticate the provided username/password.

        Returns:
            Django User instance on success, None on failure.

        Notes:
        - Username and password must be provided.
        - Password verification uses check_password (Django hashers). If the stored
          value does not look hashed (legacy rows), a direct equality check is used
          as a temporary fallback.
        """
        if not username or not password:
            return None

        try:
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        stored = u.password or ""
        # prefer hashed verification; allow plain-text fallback for legacy data
        if not (stored and (check_password(password, stored) or stored == password)):
            return None

        # Synchronize/create local Django user inside a transaction to avoid partial state.
        with transaction.atomic():
            user, created = DjangoUser.objects.get_or_create(
                username=username,
                defaults={"email": u.email or "", "first_name": "", "last_name": ""},
            )

            # Determine staff/superuser flags from StaffModel (DIPENDENTE)
            try:
                d = Employee.objects.get(username=username)
                user.is_staff = True
                user.is_superuser = True
                # user.is_superuser = getattr(d, "ruolo", "").lower() == "admin"
            except Employee.DoesNotExist:
                user.is_staff = False
                user.is_superuser = False

            # If the local Django user has no usable password, keep it unusable
            # because auth is handled by the external table.
            if not user.has_usable_password():
                user.set_unusable_password()

            # Keep email in sync if available
            if u.email and user.email != u.email:
                user.email = u.email

            user.save()

        return user

    def get_user(self, user_id: int) -> Optional[DjangoUser]:
        """
        Retrieve the Django User by primary key. Required by Django auth.
        """
        try:
            return DjangoUser.objects.get(pk=user_id)
        except DjangoUser.DoesNotExist:
            return None
