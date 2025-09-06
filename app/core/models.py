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
    data_assunzione = models.DateField()
    data_licenziamento = models.DateField(null=True)

    class Meta:
        db_table = "DIPENDENTE"
        managed = False
        verbose_name = verbose_name_plural = "Staff"

class EventModel(models.Model):
    """
    Represents the EVENTO table.

    Fields:
    - ID_evento: primary key (assumed INT AUTO_INCREMENT in DB).
    - posti: number of available seats for the event.
    - titolo: title of the event.
    - descrizione: description of the event.
    - data_evento: date of the event.
    - username: foreign key to UTENTE.username (the organizer).
    """

    ID_evento = models.AutoField(primary_key=True)
    posti = models.IntegerField()
    titolo = models.CharField(max_length=200)
    descrizione = models.TextField()
    data_evento = models.DateField()
    username = models.ForeignKey(
        UserModel,
        db_column="username",
        to_field="username",
        on_delete=models.CASCADE,
    )

    class Meta:
        db_table = "EVENTO"
        managed = False
        verbose_name = "Event"
        verbose_name_plural = "Events"


class EnrollModel(models.Model):
    """
    Represents the ISCRIVE table (associative entity between UTENTE and EVENTO).

    Fields:
    - ID_evento: foreign key to EVENTO.ID_evento.
    - username: foreign key to UTENTE.username.
    - partecipanti: number of participants that the user registers.
    Notes:
    - This table likely has a composite primary key (ID_evento + username).
      In Django, define one as PK and set `unique_together` in Meta to enforce both.
    """

    ID_evento = models.ForeignKey(
        EventModel,
        db_column="ID_evento",
        to_field="ID_evento",
        on_delete=models.CASCADE,
    )
    username = models.ForeignKey(
        UserModel,
        db_column="username",
        to_field="username",
        on_delete=models.CASCADE,
    )
    partecipanti = models.IntegerField()

    class Meta:
        db_table = "ISCRIVE"
        managed = False
        unique_together = (("ID_evento", "username"),)
        verbose_name = "Subscription"
        verbose_name_plural = "Subscriptions"
