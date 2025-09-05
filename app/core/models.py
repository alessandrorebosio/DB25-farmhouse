"""
Django models mapping existing database tables.

These models use managed = False because the tables are created/managed
outside Django (no migrations will be created for them).

Mapped tables:
- PERSONA     -> Person
- UTENTE      -> User
- DIPENDENTE  -> Staff
"""

from django.db import models


class PersonModel(models.Model):
    """
    Represents the PERSONA table.

    Fields:
    - CF: fiscal code, primary key (CHAR(16) in DB)
    - nome: first name
    - cognome: last name
    """

    CF = models.CharField(primary_key=True, max_length=16)
    nome = models.CharField(max_length=50)
    cognome = models.CharField(max_length=50)

    class Meta:
        db_table = "PERSONA"
        managed = False
        verbose_name = "Person"
        verbose_name_plural = "People"


class UserModel(models.Model):
    """
    Represents the UTENTE table.

    Notes:
    - username is the PK.
    - CF links to Persona (kept as CharField to match existing schema).
    - password is stored in the DB; prefer hashed values (use Django hashers).
    - email kept as CharField to match existing table; consider EmailField
      if you plan to let Django validate/modify this field.
    """

    username = models.CharField(primary_key=True, max_length=30)
    CF = models.ForeignKey(
        PersonModel,
        db_column="CF",
        to_field="CF",
        on_delete=models.CASCADE,
    )
    password = models.CharField(max_length=255)
    email = models.CharField(max_length=255)

    class Meta:
        db_table = "UTENTE"
        managed = False
        verbose_name = "User"
        verbose_name_plural = "Users"


class StaffModel(models.Model):
    """
    Represents the DIPENDENTE table.

    Fields:
    - username: PK referencing Utente.username (kept as CharField to match DB)
    - ruolo: role name
    - data_assunzione: hire date
    - data_licenziamento: termination date (nullable)
    """

    username = models.OneToOneField(
        UserModel,
        db_column="username",
        to_field="username",
        on_delete=models.CASCADE,
        primary_key=True,
    )
    ruolo = models.CharField(max_length=50)
    data_assunzione = models.DateField()
    data_licenziamento = models.DateField(null=True)

    class Meta:
        db_table = "DIPENDENTE"
        managed = False
        verbose_name = verbose_name_plural = "Staff"
