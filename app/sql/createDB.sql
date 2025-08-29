-- *********************************************
-- * Standard SQL generation                   
-- *--------------------------------------------
-- * DB-MAIN version: 11.0.2              
-- * Generator date: Sep 14 2021              
-- * Generation date: Tue Aug 19 16:44:54 2025 
-- * LUN file: C:\Users\filip\Desktop\UNI\DataBase\project\Versione 4\Farmhouse_scheletro.lun 
-- * Schema: SCHEMA/SQL 
-- ********************************************* 


-- Database Section
-- ________________ 

drop database farmhouse;
create database farmhouse;
use farmhouse;

-- DBSpace Section
-- _______________


-- Tables Section
-- _____________ 

create table acquista (
     ID_pacchetto varchar(3) not null,
     CF varchar(32) not null,
     constraint ID_acquista_ID primary key (ID_pacchetto, CF));

create table ASSEGNA_RUOLO (
     CF varchar(32) not null,
     ID_ruolo char(1) not null,
     data_fine date not null,
     data_inizio date not null,
     constraint ID_ASSEGNA_RUOLO_ID primary key (CF, ID_ruolo, data_inizio));

create table ATTIVITA_CON_ANIMALI (
     ID_servizio varchar(32) not null,
     cod_attivita varchar(3) not null,
     constraint ID_ATTIV_SERVI_ID primary key (ID_servizio));

create table CAMERA (
     ID_servizio varchar(32) not null,
     cod_camera varchar(3) not null,
     max_capienza numeric(1) not null,
     constraint ID_CAMER_SERVI_ID primary key (ID_servizio));

create table CAMPO_DA_GIOCO (
     ID_servizio varchar(32) not null,
     cod_campo varchar(3) not null,
     max_capienza numeric(1) not null,
     constraint ID_CAMPO_SERVI_ID primary key (ID_servizio));

create table composto_da (
     ID_pacchetto varchar(3) not null,
     ID_servizio varchar(32) not null,
     constraint ID_composto_da_ID primary key (ID_servizio, ID_pacchetto));

create table DETTAGLI_ORDINE (
     ID_ordine varchar(32) not null,
     ID_prodotto char(1) not null,
     quantita numeric(2) not null,
     constraint ID_DETTAGLI_ORDINE_ID primary key (ID_prodotto, ID_ordine));

create table DETTAGLI_PRENOTAZIONE (
     ID_prenotazione varchar(32) not null,
     ID_servizio varchar(32) not null,
     data_inizio date not null,
     data_fine date not null,
     constraint ID_DETTAGLI_PRENOTAZIONE_ID primary key (ID_prenotazione, ID_servizio, data_inizio));

create table DIPENDENTE (
     CF varchar(32) not null,
     data_assunzione date not null,
     constraint ID_DIPEN_UTENT_ID primary key (CF));

create table EVENTO (
     ID_evento varchar(32) not null,
     max_partecipanti numeric(2) not null,
     descrizione varchar(32) not null,
     CF varchar(32) not null,
     constraint ID_EVENTO_ID primary key (ID_evento));

create table iscrive (
     ID_evento varchar(32) not null,
     CF varchar(32) not null,
     constraint ID_iscrive_ID primary key (ID_evento, CF));

create table LETTINO (
     ID_servizio varchar(32) not null,
     cod_lettino varchar(3) not null,
     constraint ID_LETTI_SERVI_ID primary key (ID_servizio));

create table ORDINE (
     ID_ordine varchar(32) not null,
     CF varchar(32) not null,
     constraint ID_ORDINE_ID primary key (ID_ordine));

create table PACCHETTO (
     ID_pacchetto varchar(3) not null,
     constraint ID_PACCHETTO_ID primary key (ID_pacchetto));

create table PERSONA (
     CF varchar(32) not null,
     nome varchar(32) not null,
     cognome varchar(32) not null,
     constraint ID_PERSONA_ID primary key (CF));

create table PRENOTAZIONE (
     ID_prenotazione varchar(32) not null,
     CF varchar(32) not null,
     constraint ID_PRENOTAZIONE_ID primary key (ID_prenotazione));

create table PRODOTTO (
     ID_prodotto char(1) not null,
     nome char(1) not null,
     prezzo numeric(2) not null,
     constraint ID_PRODOTTO_ID primary key (ID_prodotto));

create table RECENSIONE (
     ID_recensione varchar(32) not null,
     tipo_servizio varchar(32) not null,
     voto numeric(1) not null,
     descrizione varchar(500) not null,
     ID_prenotazione varchar(32) not null,
     CF varchar(32) not null,
     constraint ID_RECENSIONE_ID primary key (ID_recensione));

create table RUOLO (
     ID_ruolo char(1) not null,
     constraint ID_RUOLO_ID primary key (ID_ruolo));

create table SERVIZIO (
     status char not null,
     ID_servizio varchar(32) not null,
     prezzo numeric(3) not null,
     tipo_servizio varchar(32) not null,
     constraint ID_SERVIZIO_ID primary key (ID_servizio));

create table TAVOLO (
     ID_servizio varchar(32) not null,
     cod_tavolo varchar(3) not null,
     max_capienza numeric(1) not null,
     constraint ID_TAVOL_SERVI_ID primary key (ID_servizio));

create table UTENTE (
     CF varchar(32) not null,
     username varchar(32) not null,
     password varchar(32) not null,
     email varchar(32) not null,
     constraint SID_UTENTE_ID unique (username),
     constraint ID_UTENT_PERSO_ID primary key (CF));


-- Constraints Section
-- ___________________ 

alter table acquista add constraint REF_acqui_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table acquista add constraint REF_acqui_PACCH
     foreign key (ID_pacchetto)
     references PACCHETTO;

alter table ASSEGNA_RUOLO add constraint REF_ASSEG_RUOLO_FK
     foreign key (ID_ruolo)
     references RUOLO;

alter table ASSEGNA_RUOLO add constraint REF_ASSEG_DIPEN
     foreign key (CF)
     references DIPENDENTE;

alter table ATTIVITA_CON_ANIMALI add constraint ID_ATTIV_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table CAMERA add constraint ID_CAMER_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table CAMPO_DA_GIOCO add constraint ID_CAMPO_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table composto_da add constraint REF_compo_SERVI
     foreign key (ID_servizio)
     references SERVIZIO;

alter table composto_da add constraint EQU_compo_PACCH_FK
     foreign key (ID_pacchetto)
     references PACCHETTO;

alter table DETTAGLI_ORDINE add constraint REF_DETTA_PRODO
     foreign key (ID_prodotto)
     references PRODOTTO;

alter table DETTAGLI_ORDINE add constraint REF_DETTA_ORDIN_FK
     foreign key (ID_ordine)
     references ORDINE;

alter table DETTAGLI_PRENOTAZIONE add constraint REF_DETTA_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table DETTAGLI_PRENOTAZIONE add constraint REF_DETTA_PRENO
     foreign key (ID_prenotazione)
     references PRENOTAZIONE;

alter table DIPENDENTE add constraint ID_DIPEN_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table EVENTO add constraint REF_EVENT_DIPEN_FK
     foreign key (CF)
     references DIPENDENTE;

alter table iscrive add constraint REF_iscri_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table iscrive add constraint REF_iscri_EVENT
     foreign key (ID_evento)
     references EVENTO;

alter table LETTINO add constraint ID_LETTI_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table ORDINE add constraint REF_ORDIN_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table PACCHETTO add constraint ID_PACCHETTO_CHK
     check(exists(select * from composto_da
                  where composto_da.ID_pacchetto = ID_pacchetto)); 

alter table PRENOTAZIONE add constraint REF_PRENO_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table RECENSIONE add constraint REF_RECEN_PRENO_FK
     foreign key (ID_prenotazione)
     references PRENOTAZIONE;

alter table RECENSIONE add constraint REF_RECEN_UTENT_FK
     foreign key (CF)
     references UTENTE;

alter table TAVOLO add constraint ID_TAVOL_SERVI_FK
     foreign key (ID_servizio)
     references SERVIZIO;

alter table UTENTE add constraint ID_UTENT_PERSO_FK
     foreign key (CF)
     references PERSONA;


-- Index Section
-- _____________ 

create unique index ID_acquista_IND
     on acquista (ID_pacchetto, CF);

create index REF_acqui_UTENT_IND
     on acquista (CF);

create unique index ID_ASSEGNA_RUOLO_IND
     on ASSEGNA_RUOLO (CF, ID_ruolo, data_inizio);

create index REF_ASSEG_RUOLO_IND
     on ASSEGNA_RUOLO (ID_ruolo);

create unique index ID_ATTIV_SERVI_IND
     on ATTIVITA_CON_ANIMALI (ID_servizio);

create unique index ID_CAMER_SERVI_IND
     on CAMERA (ID_servizio);

create unique index ID_CAMPO_SERVI_IND
     on CAMPO_DA_GIOCO (ID_servizio);

create unique index ID_composto_da_IND
     on composto_da (ID_servizio, ID_pacchetto);

create index EQU_compo_PACCH_IND
     on composto_da (ID_pacchetto);

create unique index ID_DETTAGLI_ORDINE_IND
     on DETTAGLI_ORDINE (ID_prodotto, ID_ordine);

create index REF_DETTA_ORDIN_IND
     on DETTAGLI_ORDINE (ID_ordine);

create unique index ID_DETTAGLI_PRENOTAZIONE_IND
     on DETTAGLI_PRENOTAZIONE (ID_prenotazione, ID_servizio, data_inizio);

create index REF_DETTA_SERVI_IND
     on DETTAGLI_PRENOTAZIONE (ID_servizio);

create unique index ID_DIPEN_UTENT_IND
     on DIPENDENTE (CF);

create unique index ID_EVENTO_IND
     on EVENTO (ID_evento);

create index REF_EVENT_DIPEN_IND
     on EVENTO (CF);

create unique index ID_iscrive_IND
     on iscrive (ID_evento, CF);

create index REF_iscri_UTENT_IND
     on iscrive (CF);

create unique index ID_LETTI_SERVI_IND
     on LETTINO (ID_servizio);

create unique index ID_ORDINE_IND
     on ORDINE (ID_ordine);

create index REF_ORDIN_UTENT_IND
     on ORDINE (CF);

create unique index ID_PACCHETTO_IND
     on PACCHETTO (ID_pacchetto);

create unique index ID_PERSONA_IND
     on PERSONA (CF);

create unique index ID_PRENOTAZIONE_IND
     on PRENOTAZIONE (ID_prenotazione);

create index REF_PRENO_UTENT_IND
     on PRENOTAZIONE (CF);

create unique index ID_PRODOTTO_IND
     on PRODOTTO (ID_prodotto);

create unique index ID_RECENSIONE_IND
     on RECENSIONE (ID_recensione);

create index REF_RECEN_PRENO_IND
     on RECENSIONE (ID_prenotazione);

create index REF_RECEN_UTENT_IND
     on RECENSIONE (CF);

create unique index ID_RUOLO_IND
     on RUOLO (ID_ruolo);

create unique index ID_SERVIZIO_IND
     on SERVIZIO (ID_servizio);

create unique index ID_TAVOL_SERVI_IND
     on TAVOLO (ID_servizio);

create unique index SID_UTENTE_IND
     on UTENTE (username);

create unique index ID_UTENT_PERSO_IND
     on UTENTE (CF);

