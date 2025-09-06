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


# Service Models
class ServizioModel(models.Model):
    """
    Represents the SERVIZIO table.
    
    Fields:
    - ID_servizio: service ID, primary key (auto-increment)
    - prezzo: service price (decimal with 2 decimal places)
    - tipo_servizio: service type (CAMERA, PISCINA, etc.)
    - status: service availability status (DISPONIBILE, OCCUPATO, MANUTENZIONE)
    """
    
    TIPO_CHOICES = [
        ('CAMERA', 'Camera'),
        ('PISCINA', 'Piscina'),
        ('RISTORANTE', 'Ristorante'),
        ('CAMPO_DA_GIOCO', 'Campo da Gioco'),
        ('ATTIVITA_CON_ANIMALI', 'Attività con Animali'),
    ]
    
    STATUS_CHOICES = [
        ('DISPONIBILE', 'Disponibile'),
        ('OCCUPATO', 'Occupato'),
        ('MANUTENZIONE', 'Manutenzione'),
    ]
    
    ID_servizio = models.AutoField(primary_key=True)
    prezzo = models.DecimalField(max_digits=10, decimal_places=2)
    tipo_servizio = models.CharField(max_length=50, choices=TIPO_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIBILE')
    
    class Meta:
        db_table = 'SERVIZIO'
        managed = False
        
    def get_tipo_servizio_display(self):
        """Returns human-readable service type"""
        return dict(self.TIPO_CHOICES).get(self.tipo_servizio, self.tipo_servizio)


class CameraModel(models.Model):
    """
    Represents the CAMERA table.
    
    Fields:
    - ID_servizio: foreign key to SERVIZIO table, primary key
    - cod_camera: room code (e.g., 'C01', 'C02')
    - max_capienza: maximum room capacity (number of guests)
    """
    ID_servizio = models.OneToOneField(
        ServizioModel, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='ID_servizio'
    )
    cod_camera = models.CharField(max_length=10)
    max_capienza = models.IntegerField()
    
    class Meta:
        db_table = 'CAMERA'
        managed = False


class RistoranteModel(models.Model):
    """
    Represents the RISTORANTE table.
    
    Fields:
    - ID_servizio: foreign key to SERVIZIO table, primary key
    - cod_tavolo: table code (e.g., 'T1', 'T2')
    - max_capienza: maximum table capacity (number of seats)
    """
    ID_servizio = models.OneToOneField(
        ServizioModel, 
        on_delete=models.CASCADE, 
        primary_key=True,
        db_column='ID_servizio'
    )
    cod_tavolo = models.CharField(max_length=10)
    max_capienza = models.IntegerField()
    
    class Meta:
        db_table = 'RISTORANTE'
        managed = False
        managed = False


class PiscinaModel(models.Model):
    """
    Represents the PISCINA table.
    
    Fields:
    - ID_servizio: foreign key to SERVIZIO table, primary key
    - cod_lettino: pool chair code (e.g., 'L1', 'L2')
    """
    ID_servizio = models.OneToOneField(ServizioModel, on_delete=models.CASCADE, primary_key=True)
    cod_lettino = models.CharField(max_length=10)
    
    class Meta:
        db_table = 'PISCINA'
        managed = False


class CampoDaGiocoModel(models.Model):
    """
    Represents the CAMPO_DA_GIOCO table.
    
    Fields:
    - ID_servizio: foreign key to SERVIZIO table, primary key
    - cod_campo: field code (e.g., 'F1', 'F2')
    - max_capienza: maximum field capacity (number of players)
    """
    ID_servizio = models.OneToOneField(ServizioModel, on_delete=models.CASCADE, primary_key=True)
    cod_campo = models.CharField(max_length=10)
    max_capienza = models.IntegerField()
    
    class Meta:
        db_table = 'CAMPO_DA_GIOCO'
        managed = False


class AttivitaConAnimaliModel(models.Model):
    """
    Represents the ATTIVITA_CON_ANIMALI table.
    
    Fields:
    - ID_servizio: foreign key to SERVIZIO table, primary key
    - cod_attivita: activity code (e.g., 'A01', 'A02')
    - descrizione: activity description
    """
    ID_servizio = models.OneToOneField(ServizioModel, on_delete=models.CASCADE, primary_key=True)
    cod_attivita = models.CharField(max_length=10)
    descrizione = models.TextField()
    
    class Meta:
        db_table = 'ATTIVITA_CON_ANIMALI'
        managed = False
