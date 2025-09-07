from django.db import models
from django.core.validators import MinValueValidator
from cpkmodel import CPkModel


class Person(models.Model):
    cf = models.CharField(max_length=16, primary_key=True, db_column="CF")
    name = models.CharField(max_length=50, db_column="nome", null=True)
    surname = models.CharField(max_length=50, db_column="cognome", null=True)
    phone = models.CharField(max_length=20, db_column="telefono", null=True)
    city = models.CharField(max_length=50, db_column="citta", null=True)

    class Meta:
        db_table = "PERSONA"
        managed = False
        verbose_name = "Persona"
        verbose_name_plural = "Persone"


class User(models.Model):
    username = models.CharField(max_length=32, primary_key=True, db_column="username")
    cf = models.ForeignKey(
        Person,
        models.CASCADE,
        db_column="CF",
        to_field="cf",
        null=True,
    )
    password = models.CharField(max_length=255, db_column="password", null=True)
    email = models.CharField(max_length=255, db_column="email", null=True)

    class Meta:
        db_table = "UTENTE"
        managed = False
        verbose_name = "Utente"
        verbose_name_plural = "Utenti"


class Hosts(models.Model):
    cf = models.ForeignKey(Person, models.CASCADE, db_column="CF", to_field="cf")
    username = models.ForeignKey(
        User, models.CASCADE, db_column="username", to_field="username"
    )
    hosting_date = models.DateField(db_column="data_ospitazione", primary_key=True)

    class Meta:
        db_table = "OSPITA"
        managed = False
        verbose_name = "Ospitazione"
        verbose_name_plural = "Ospitazioni"
        unique_together = (("cf", "username", "hosting_date"),)


class Service(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_servizio")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        db_column="prezzo",
    )
    type = models.CharField(max_length=32, db_column="tipo_servizio")
    status = models.CharField(max_length=15, db_column="status", default="DISPONIBILE")

    class Meta:
        db_table = "SERVIZIO"
        managed = False
        verbose_name = "Servizio"
        verbose_name_plural = "Servizi"


class Package(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_pacchetto")
    name = models.CharField(max_length=32, db_column="nome")
    description = models.TextField(db_column="descrizione")

    class Meta:
        db_table = "PACCHETTO"
        managed = False
        verbose_name = "Pacchetto"
        verbose_name_plural = "Pacchetti"


class Compound(CPkModel):
    package = models.OneToOneField(
        Package,
        models.CASCADE,
        db_column="ID_pacchetto",
        to_field="id",
        primary_key=True,
    )
    service = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )

    class Meta:
        db_table = "COMPOSTO"
        managed = False
        verbose_name = "Composizione pacchetto"
        verbose_name_plural = "Composizioni pacchetto"
        unique_together = (("service", "package"),)


class Purchase(CPkModel):
    package = models.OneToOneField(
        Package,
        models.CASCADE,
        db_column="ID_pacchetto",
        to_field="id",
        primary_key=True,
    )
    username = models.OneToOneField(
        User,
        models.CASCADE,
        db_column="username",
        to_field="username",
        primary_key=True,
    )
    purchase_date = models.DateTimeField(db_column="data_acquisto", null=True)

    class Meta:
        db_table = "ACQUISTA"
        managed = False
        verbose_name = "Acquisto"
        verbose_name_plural = "Acquisti"
        unique_together = (("package", "username"),)


class Restaurant(models.Model):
    id = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )
    table_code = models.CharField(
        max_length=3,
        db_column="cod_tavolo",
        unique=True,
    )
    max_capacity = models.PositiveIntegerField(
        db_column="max_capienza",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        db_table = "RISTORANTE"
        managed = False
        verbose_name = "Ristorante"
        verbose_name_plural = "Ristoranti"


class Pool(models.Model):
    id = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )
    sunbed_code = models.CharField(max_length=3, db_column="cod_lettino", unique=True)

    class Meta:
        db_table = "PISCINA"
        managed = False
        verbose_name = "Piscina"
        verbose_name_plural = "Piscine"


class Playground(models.Model):
    id = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )
    playground_code = models.CharField(max_length=3, db_column="cod_campo", unique=True)
    max_capacity = models.PositiveIntegerField(
        db_column="max_capienza", validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "CAMPO_DA_GIOCO"
        managed = False
        verbose_name = "Campo da gioco"
        verbose_name_plural = "Campi da gioco"


class Room(models.Model):
    id = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )
    room_code = models.CharField(max_length=3, db_column="cod_camera", unique=True)
    max_capacity = models.PositiveIntegerField(
        db_column="max_capienza", validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "CAMERA"
        managed = False
        verbose_name = "Camera"
        verbose_name_plural = "Camere"


class AnimalActivity(models.Model):
    id = models.OneToOneField(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        to_field="id",
        primary_key=True,
    )
    activity_code = models.CharField(
        unique=True, max_length=3, db_column="cod_attivita"
    )
    description = models.TextField(db_column="descrizione")

    class Meta:
        db_table = "ATTIVITA_CON_ANIMALI"
        managed = False
        verbose_name = "Attività con animali"
        verbose_name_plural = "Attività con animali"


class Booking(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_prenotazione")
    username = models.ForeignKey(
        User, models.CASCADE, db_column="username", to_field="username"
    )
    booking_date = models.DateTimeField(db_column="data_prenotazione", null=True)

    class Meta:
        db_table = "PRENOTAZIONE"
        managed = False
        verbose_name = "Prenotazione"
        verbose_name_plural = "Prenotazioni"


class BookingDetail(models.Model):
    booking = models.ForeignKey(
        Booking,
        models.CASCADE,
        db_column="ID_prenotazione",
        related_name="details",
    )
    service = models.ForeignKey(
        Service,
        models.CASCADE,
        db_column="ID_servizio",
        related_name="booking_details",
    )
    start_date = models.DateField(db_column="data_inizio")
    end_date = models.DateField(db_column="data_fine")

    class Meta:
        db_table = "DETTAGLIO_PRENOTAZIONE"
        managed = False
        verbose_name = "Dettaglio prenotazione"
        verbose_name_plural = "Dettagli prenotazione"
        unique_together = (("booking", "service"),)


class Review(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_recensione")
    service_type = models.CharField(max_length=32, db_column="tipo_servizio")
    vote = models.IntegerField(db_column="voto")
    description = models.TextField(db_column="descrizione")
    username = models.ForeignKey(
        User, models.CASCADE, db_column="username", to_field="username"
    )
    id_booking = models.ForeignKey(
        Booking,
        models.CASCADE,
        db_column="ID_prenotazione",
        to_field="id",
    )
    review_date = models.DateTimeField(db_column="data_recensione", null=True)

    class Meta:
        db_table = "RECENSIONE"
        managed = False
        verbose_name = "Recensione"
        verbose_name_plural = "Recensioni"
        unique_together = (("username", "id_booking"),)


class Employee(models.Model):
    username = models.OneToOneField(
        User,
        models.CASCADE,
        db_column="username",
        to_field="username",
        primary_key=True,
    )
    hire_date = models.DateField(db_column="data_assunzione", null=True)
    termination_date = models.DateField(db_column="data_licenziamento", null=True)

    class Meta:
        db_table = "DIPENDENTE"
        managed = False
        verbose_name = "Dipendente"
        verbose_name_plural = "Dipendenti"


class Event(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_evento")
    seats = models.IntegerField(db_column="posti")
    title = models.CharField(max_length=100, db_column="titolo")
    description = models.TextField(db_column="descrizione")
    date = models.DateField(db_column="data_evento")
    username = models.ForeignKey(
        Employee, models.CASCADE, db_column="username", to_field="username"
    )

    class Meta:
        db_table = "EVENTO"
        managed = False
        verbose_name = "Evento"
        verbose_name_plural = "Eventi"


class Enrolls(CPkModel):

    event = models.OneToOneField(
        Event, models.CASCADE, db_column="ID_evento", to_field="id", primary_key=True
    )
    username = models.OneToOneField(
        User,
        models.CASCADE,
        db_column="username",
        to_field="username",
        primary_key=True,
    )
    enroll_date = models.DateTimeField(db_column="data_iscrizione", null=True)
    participants = models.IntegerField(db_column="partecipanti", default=1)

    class Meta:
        db_table = "iscrive"
        managed = False
        verbose_name = "Iscrizione"
        verbose_name_plural = "Iscrizioni"
        unique_together = (("event", "username"),)


class Product(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_prodotto")
    name = models.CharField(max_length=100, db_column="nome")
    price = models.DecimalField(max_digits=8, decimal_places=2, db_column="prezzo")

    class Meta:
        db_table = "PRODOTTO"
        managed = False
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"


class Order(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_ordine")
    username = models.ForeignKey(
        User, models.CASCADE, db_column="username", to_field="username"
    )
    date = models.DateTimeField(db_column="data", null=True)

    class Meta:
        db_table = "ORDINE"
        managed = False
        verbose_name = "Ordine"
        verbose_name_plural = "Ordini"


class OrderDetail(CPkModel):
    order = models.OneToOneField(
        Order, models.CASCADE, db_column="ID_ordine", to_field="id", primary_key=True
    )
    product = models.OneToOneField(
        Product,
        models.CASCADE,
        db_column="ID_prodotto",
        to_field="id",
        primary_key=True,
    )
    quantity = models.IntegerField(db_column="quantita")
    unit_price = models.DecimalField(
        max_digits=8, decimal_places=2, db_column="prezzo_unitario"
    )

    class Meta:
        db_table = "DETTAGLIO_ORDINE"
        managed = False
        verbose_name = "Dettaglio ordine"
        verbose_name_plural = "Dettagli ordine"


class EmployeeRoleHistory(models.Model):
    username = models.OneToOneField(
        Employee, models.CASCADE, db_column="username", to_field="username"
    )
    role = models.CharField(max_length=32, db_column="ruolo")
    start_date = models.DateField(db_column="data_inizio", primary_key=True)
    end_date = models.DateField(db_column="data_fine", null=True)

    class Meta:
        db_table = "DIPENDENTE_RUOLO_STORICO"
        managed = False
        verbose_name = "Ruolo storico dipendente"
        verbose_name_plural = "Ruoli storici dipendenti"
        unique_together = (("username", "start_date"),)


class Shift(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID_turno")
    day = models.CharField(max_length=10, db_column="giorno", null=True)
    start_hour = models.TimeField(db_column="ora_inizio", null=True)
    end_hour = models.TimeField(db_column="ora_fine", null=True)
    description = models.CharField(max_length=100, db_column="descrizione", null=True)

    class Meta:
        db_table = "TURNO"
        managed = False
        verbose_name = "Turno"
        verbose_name_plural = "Turni"


class Performs(CPkModel):
    username = models.OneToOneField(
        Employee,
        models.CASCADE,
        db_column="username",
        to_field="username",
        primary_key=True,
    )
    shift = models.OneToOneField(
        Shift, models.CASCADE, db_column="ID_turno", to_field="id", primary_key=True
    )
    start_date = models.DateTimeField(db_column="data_inizio")

    class Meta:
        db_table = "SVOLGE"
        managed = False
        verbose_name = "Assegnazione turno"
        verbose_name_plural = "Assegnazioni turno"
        unique_together = (("username", "shift", "start_date"),)
