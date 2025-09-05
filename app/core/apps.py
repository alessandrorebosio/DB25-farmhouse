"""
App configuration for the 'core' Django application.

This AppConfig subclass provides metadata used by Django at startup:

- `name` should match the Python package path for the app.
- `default_auto_field` controls the default type for automatically
  created primary keys (BigAutoField here).

Use the ready() hook to perform one-time initialization (for example,
importing and registering signal handlers). Keep side effects idempotent
to avoid issues during tests or migrations.
"""

from django.apps import AppConfig


class StaffConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        """
        Called when the app registry is fully populated.

        Typical use-cases:
        - import and register signal handlers: `from . import signals`
        - perform lightweight startup checks

        Avoid heavy work here (long-running tasks); keep it safe for tests.
        """
        pass
