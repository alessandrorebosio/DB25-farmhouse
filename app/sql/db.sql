-- *********************************************
-- * Improved SQL schema for Farm Database (fixed)
-- * Eliminati i CHECK con subquery non supportati in MySQL
-- * Aggiunti TRIGGER per garantire integrità su DIPENDENTE e PACCHETTO
-- *********************************************

-- Database Section
-- ________________ 

DROP DATABASE IF EXISTS farmhouse;
CREATE DATABASE farmhouse;
USE farmhouse;

-- Tables Section
-- _____________ 

CREATE TABLE PERSONA (
    CF VARCHAR(16) NOT NULL,
    nome VARCHAR(32) NOT NULL,
    cognome VARCHAR(32) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    citta VARCHAR(50),
    CONSTRAINT ID_PERSONA_ID PRIMARY KEY (CF)
);

CREATE TABLE UTENTE (
    username VARCHAR(32) NOT NULL,
    CF VARCHAR(16) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    CONSTRAINT ID_UTENTE_ID PRIMARY KEY (username),
    CONSTRAINT FKPER_UTE_ID UNIQUE (CF),
    CONSTRAINT FKPER_UTE_FK FOREIGN KEY (CF) REFERENCES PERSONA(CF)
);

CREATE TABLE DIPENDENTE (
    username VARCHAR(32) NOT NULL,
    data_assunzione DATE NOT NULL,
    data_licenziamento DATE,
    CONSTRAINT FKUTE_DIP_ID PRIMARY KEY (username),
    CONSTRAINT FKUTE_DIP_FK FOREIGN KEY (username) REFERENCES UTENTE(username)
);

CREATE TABLE DIPENDENTE_RUOLO_STORICO (
    username VARCHAR(32) NOT NULL,
    ruolo VARCHAR(32) NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE ,
    CONSTRAINT ID_DIPENDENTE_RUOLO_STORICO_ID PRIMARY KEY (username, data_inizio),
    CONSTRAINT FKricopre FOREIGN KEY (username) REFERENCES DIPENDENTE(username),
    CONSTRAINT CHK_date CHECK (data_inizio <= data_fine)
);

CREATE TABLE TURNO (
    ID_turno INT AUTO_INCREMENT NOT NULL,
    giorno ENUM('LUN', 'MAR', 'MER', 'GIO', 'VEN', 'SAB', 'DOM') NOT NULL,
    ora_inizio TIME NOT NULL,
    ora_fine TIME NOT NULL,
    descrizione VARCHAR(45) NOT NULL,
    CONSTRAINT ID_TURNO_ID PRIMARY KEY (ID_turno),
    CONSTRAINT CHK_orario CHECK (ora_inizio < ora_fine)
);

CREATE TABLE SVOLGE (
    username VARCHAR(32) NOT NULL,
    ID_turno INT NOT NULL,
    data_inizio DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ID_svolge_ID PRIMARY KEY (username, ID_turno,data_inizio),
    CONSTRAINT FKsvo_DIP FOREIGN KEY (username) REFERENCES DIPENDENTE(username),
    CONSTRAINT FKsvo_TUR_FK FOREIGN KEY (ID_turno) REFERENCES TURNO(ID_turno)
);

CREATE TABLE SERVIZIO (
    ID_servizio INT AUTO_INCREMENT NOT NULL,
    prezzo DECIMAL(8,2) NOT NULL CHECK (prezzo >= 0),
    tipo_servizio ENUM('RISTORANTE', 'PISCINA', 'CAMPO_DA_GIOCO', 'CAMERA', 'ATTIVITA_CON_ANIMALI') NOT NULL,
    status ENUM('DISPONIBILE', 'OCCUPATO', 'MANUTENZIONE') NOT NULL DEFAULT 'DISPONIBILE',
    CONSTRAINT ID_SERVIZIO_ID PRIMARY KEY (ID_servizio)
);

CREATE TABLE RISTORANTE (
    ID_servizio INT NOT NULL,
    cod_tavolo VARCHAR(3) NOT NULL,
    max_capienza INT NOT NULL CHECK (max_capienza >= 1),
    CONSTRAINT SID_TAVOLO_ID UNIQUE (cod_tavolo),
    CONSTRAINT FKSER_TAV_ID PRIMARY KEY (ID_servizio),
    CONSTRAINT FKSER_TAV_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE PISCINA (
    ID_servizio INT NOT NULL,
    cod_lettino VARCHAR(3) NOT NULL,
    CONSTRAINT SID_LETTINO_ID UNIQUE (cod_lettino),
    CONSTRAINT FKSER_LET_ID PRIMARY KEY (ID_servizio),
    CONSTRAINT FKSER_LET_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE CAMPO_DA_GIOCO (
    ID_servizio INT NOT NULL,
    cod_campo VARCHAR(3) NOT NULL,
    max_capienza INT NOT NULL CHECK (max_capienza >= 1),
    CONSTRAINT SID_CAMPO_DA_GIOCO_ID UNIQUE (cod_campo),
    CONSTRAINT FKSER_CAM_1_ID PRIMARY KEY (ID_servizio),
    CONSTRAINT FKSER_CAM_1_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE CAMERA (
    ID_servizio INT NOT NULL,
    cod_camera VARCHAR(3) NOT NULL,
    max_capienza INT NOT NULL CHECK (max_capienza >= 1),
    CONSTRAINT SID_CAMERA_ID UNIQUE (cod_camera),
    CONSTRAINT FKSER_CAM_ID PRIMARY KEY (ID_servizio),
    CONSTRAINT FKSER_CAM_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE ATTIVITA_CON_ANIMALI (
    ID_servizio INT NOT NULL,
    cod_attivita VARCHAR(3) NOT NULL,
    descrizione TEXT NOT NULL,
    CONSTRAINT SID_ATTIVITA_CON_ANIMALI_ID UNIQUE (cod_attivita),
    CONSTRAINT FKSER_ATT_ID PRIMARY KEY (ID_servizio),
    CONSTRAINT FKSER_ATT_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE PACCHETTO (
    ID_pacchetto INT AUTO_INCREMENT NOT NULL,
    nome VARCHAR(32) NOT NULL,
    descrizione TEXT NOT NULL,
    CONSTRAINT ID_PACCHETTO_ID PRIMARY KEY (ID_pacchetto)
);

CREATE TABLE COMPOSTO (
    ID_pacchetto INT NOT NULL,
    ID_servizio INT NOT NULL,
    CONSTRAINT ID_composto_ID PRIMARY KEY (ID_servizio, ID_pacchetto),
    CONSTRAINT FKcom_PAC_FK FOREIGN KEY (ID_pacchetto) REFERENCES PACCHETTO(ID_pacchetto),
    CONSTRAINT FKcom_SER FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio)
);

CREATE TABLE ACQUISTA (
    ID_pacchetto INT NOT NULL,
    username VARCHAR(32) NOT NULL,
    data_acquisto DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ID_acquista_ID PRIMARY KEY (username, ID_pacchetto),
    CONSTRAINT FKacq_UTE FOREIGN KEY (username) REFERENCES UTENTE(username),
    CONSTRAINT FKacq_PAC_FK FOREIGN KEY (ID_pacchetto) REFERENCES PACCHETTO(ID_pacchetto)
);

CREATE TABLE PRENOTAZIONE (
    ID_prenotazione INT AUTO_INCREMENT NOT NULL,
    username VARCHAR(32) NOT NULL,
    data_prenotazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ID_PRENOTAZIONE_ID PRIMARY KEY (ID_prenotazione),
    CONSTRAINT FKeffettua_FK FOREIGN KEY (username) REFERENCES UTENTE(username)
);

CREATE TABLE DETTAGLIO_PRENOTAZIONE (
    ID_prenotazione INT NOT NULL,
    ID_servizio INT NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE NOT NULL,
    CONSTRAINT ID_DETTAGLIO_PRENOTAZIONE_ID PRIMARY KEY (ID_prenotazione, ID_servizio),
    CONSTRAINT FKcompone FOREIGN KEY (ID_prenotazione) REFERENCES PRENOTAZIONE(ID_prenotazione),
    CONSTRAINT FKriguarda_FK FOREIGN KEY (ID_servizio) REFERENCES SERVIZIO(ID_servizio),
    CONSTRAINT CHK_date_prenotazione CHECK (data_inizio <= data_fine)
);

CREATE TABLE PRODOTTO (
    ID_prodotto INT AUTO_INCREMENT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    prezzo DECIMAL(8,2) NOT NULL CHECK (prezzo >= 0),
    CONSTRAINT ID_PRODOTTO_ID PRIMARY KEY (ID_prodotto)
);

CREATE TABLE ORDINE (
    ID_ordine INT AUTO_INCREMENT NOT NULL,
    data DATETIME DEFAULT CURRENT_TIMESTAMP,
    username VARCHAR(32) NOT NULL,
    CONSTRAINT ID_ORDINE_ID PRIMARY KEY (ID_ordine),
    CONSTRAINT FKesegue_FK FOREIGN KEY (username) REFERENCES UTENTE(username)
);

CREATE TABLE DETTAGLIO_ORDINE (
    ID_prodotto INT NOT NULL,
    ID_ordine INT NOT NULL,
    quantita INT NOT NULL CHECK (quantita > 0),
    prezzo_unitario DECIMAL(8,2) NOT NULL CHECK (prezzo_unitario >= 0),
    CONSTRAINT ID_DETTAGLIO_ORDINE_ID PRIMARY KEY (ID_prodotto, ID_ordine),
    CONSTRAINT FKcontiene FOREIGN KEY (ID_prodotto) REFERENCES PRODOTTO(ID_prodotto),
    CONSTRAINT FKriguardano_FK FOREIGN KEY (ID_ordine) REFERENCES ORDINE(ID_ordine)
);

CREATE TABLE EVENTO (
    ID_evento INT AUTO_INCREMENT NOT NULL,
    posti INT NOT NULL CHECK (posti >= 0),
    titolo VARCHAR(100) NOT NULL,
    descrizione TEXT NOT NULL,
    data_evento DATE NOT NULL,
    username VARCHAR(32) NOT NULL,
    CONSTRAINT ID_EVENTO_ID PRIMARY KEY (ID_evento),
    CONSTRAINT FKcrea_FK FOREIGN KEY (username) REFERENCES DIPENDENTE(username)
);

CREATE TABLE ISCRIVE (
    ID_evento INT NOT NULL,
    username VARCHAR(32) NOT NULL,
    data_iscrizione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    partecipanti INT NOT NULL CHECK (partecipanti > 0),
    CONSTRAINT ID_iscrive_ID PRIMARY KEY (ID_evento, username),
    CONSTRAINT FKisc_EVE FOREIGN KEY (ID_evento) REFERENCES EVENTO(ID_evento),
    CONSTRAINT FKisc_UTE_FK FOREIGN KEY (username) REFERENCES UTENTE(username)
);

CREATE TABLE OSPITA (
    CF VARCHAR(16) NOT NULL,
    username VARCHAR(32) NOT NULL,
    data_ospitazione DATE NOT NULL,
    CONSTRAINT ID_ospita_ID PRIMARY KEY (CF, username, data_ospitazione),
    CONSTRAINT FKosp_UTE_FK FOREIGN KEY (username) REFERENCES UTENTE(username),
    CONSTRAINT FKosp_PER FOREIGN KEY (CF) REFERENCES PERSONA(CF)
);

CREATE TABLE RECENSIONE (
    ID_recensione INT AUTO_INCREMENT NOT NULL,
    tipo_servizio ENUM('RISTORANTE', 'PISCINA', 'CAMPO_DA_GIOCO', 'CAMERA', 'ATTIVITA_CON_ANIMALI') NOT NULL,
    voto INT NOT NULL CHECK (voto BETWEEN 1 AND 5),
    descrizione TEXT NOT NULL,
    username VARCHAR(32) NOT NULL,
    ID_prenotazione INT NOT NULL,
    data_recensione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ID_RECENSIONE_ID PRIMARY KEY (ID_recensione),
    CONSTRAINT FKscrive_FK FOREIGN KEY (username) REFERENCES UTENTE(username),
    CONSTRAINT FKgiudica_FK FOREIGN KEY (ID_prenotazione) REFERENCES PRENOTAZIONE(ID_prenotazione)
);

-- Index Section
-- _____________ 

CREATE INDEX FKacq_PAC_IND ON acquista (ID_pacchetto);
CREATE INDEX FKcrea_IND ON EVENTO (username);
CREATE INDEX FKesegue_IND ON ORDINE (username);
CREATE INDEX FKeffettua_IND ON PRENOTAZIONE (username);
CREATE INDEX FKgiudica_IND ON RECENSIONE (ID_prenotazione);
CREATE INDEX FKisc_UTE_IND ON iscrive (username);
CREATE INDEX FKosp_UTE_IND ON ospita (username);
CREATE INDEX FKriguarda_IND ON DETTAGLIO_PRENOTAZIONE (ID_servizio);
CREATE INDEX FKriguardano_IND ON DETTAGLIO_ORDINE (ID_ordine);
CREATE INDEX FKscrive_IND ON RECENSIONE (username);
CREATE INDEX FKsvo_TUR_IND ON svolge (ID_turno);
CREATE INDEX FKcom_PAC_IND ON composto (ID_pacchetto);

-- Trigger Section
-- _______________

DELIMITER $$

-- Trigger: impedisce di eliminare l'ultimo turno di un dipendente
CREATE TRIGGER trg_check_dipendente_turni
BEFORE DELETE ON svolge
FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM svolge 
        WHERE username = OLD.username 
          AND ID_turno <> OLD.ID_turno
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un dipendente deve avere almeno un turno';
    END IF;
END$$

-- Trigger: impedisce di eliminare l’ultimo servizio da un pacchetto
CREATE TRIGGER trg_check_pacchetto_servizi
BEFORE DELETE ON composto
FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM composto
        WHERE ID_pacchetto = OLD.ID_pacchetto
          AND ID_servizio <> OLD.ID_servizio
    ) THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Un pacchetto deve avere almeno un servizio';
    END IF;
END$$

-- Trigger: che decrementa il numero di posti rimasti dell'evento in base al numero di partecipanti iscritti
CREATE TRIGGER trg_decrementa_posti_evento
BEFORE INSERT ON iscrive
FOR EACH ROW
BEGIN
    DECLARE posti_disponibili INT;

    -- Recupero i posti disponibili
    SELECT posti
    INTO posti_disponibili
    FROM EVENTO
    WHERE ID_evento = NEW.ID_evento;

    -- Se non ci sono abbastanza posti, blocco l'iscrizione
    IF posti_disponibili < NEW.partecipanti THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Posti insufficienti per questo evento';
    ELSE
        -- Decremento i posti disponibili
        UPDATE EVENTO
        SET posti = posti_disponibili - NEW.partecipanti
        WHERE ID_evento = NEW.ID_evento;
    END IF;
END$$

-- Trigger: che si assicura che un utente abbia usufruito del servizio che vuole recensire
CREATE TRIGGER trg_recensione_valida
BEFORE INSERT ON RECENSIONE
FOR EACH ROW
BEGIN
    DECLARE fine_servizio DATE;

    -- Recupero la data_fine dal dettaglio prenotazione corrispondente
    SELECT DP.data_fine
    INTO fine_servizio
    FROM DETTAGLIO_PRENOTAZIONE DP
    WHERE DP.ID_prenotazione = NEW.ID_prenotazione
      AND DP.ID_servizio = (
          SELECT S.ID_servizio
          FROM SERVIZIO S
          WHERE S.tipo_servizio = NEW.tipo_servizio
          LIMIT 1
      )
    LIMIT 1;

    -- Se non trovo alcun dettaglio collegato al servizio
    IF fine_servizio IS NULL THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Non esiste un dettaglio prenotazione valido per questa recensione.';
    END IF;

    -- Se il servizio non è ancora terminato, blocco la recensione
    IF fine_servizio >= CURDATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'La recensione può essere inserita solo dopo la fine del servizio prenotato.';
    END IF;
END$$

DELIMITER ;

-- Event Section
-- _______________
DELIMITER $$

CREATE EVENT IF NOT EXISTS evt_aggiorna_stato_servizi
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- 1. Servizi che devono essere OCCUPATI perché la prenotazione è attiva
    UPDATE SERVIZIO S
    SET S.status = 'OCCUPATO'
    WHERE EXISTS (
        SELECT 1
        FROM DETTAGLIO_PRENOTAZIONE DP
        WHERE DP.ID_servizio = S.ID_servizio
          AND DP.data_inizio <= NOW()
          AND DP.data_fine > NOW()
    );

    -- 2. Servizi che devono tornare DISPONIBILI perché la prenotazione è finita
    UPDATE SERVIZIO S
    SET S.status = 'DISPONIBILE'
    WHERE S.status = 'OCCUPATO'
      AND NOT EXISTS (
          SELECT 1
          FROM DETTAGLIO_PRENOTAZIONE DP
          WHERE DP.ID_servizio = S.ID_servizio
            AND DP.data_fine > NOW()
      );
END$$

DELIMITER $$


CREATE EVENT IF NOT EXISTS evt_aggiorna_stato_servizi
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- 1. Servizi che devono essere OCCUPATI perché la prenotazione è attiva
    UPDATE SERVIZIO S
    SET S.status = 'OCCUPATO'
    WHERE EXISTS (
        SELECT 1
        FROM DETTAGLIO_PRENOTAZIONE DP
        WHERE DP.ID_servizio = S.ID_servizio
          AND DP.data_inizio <= NOW()
          AND DP.data_fine > NOW()
    );

    -- 2. Servizi che devono tornare DISPONIBILI perché la prenotazione è finita
    UPDATE SERVIZIO S
    SET S.status = 'DISPONIBILE'
    WHERE S.status = 'OCCUPATO'
      AND NOT EXISTS (
          SELECT 1
          FROM DETTAGLIO_PRENOTAZIONE DP
          WHERE DP.ID_servizio = S.ID_servizio
            AND DP.data_fine > NOW()
      );
END$$

DELIMITER $$

CREATE EVENT IF NOT EXISTS evt_aggiorna_stato_servizi
ON SCHEDULE EVERY 1 HOUR
STARTS CURRENT_TIMESTAMP
DO
BEGIN
    -- 1. Servizi che devono essere OCCUPATI perché la prenotazione è attiva
    UPDATE SERVIZIO S
    SET S.status = 'OCCUPATO'
    WHERE EXISTS (
        SELECT 1
        FROM DETTAGLIO_PRENOTAZIONE DP
        WHERE DP.ID_servizio = S.ID_servizio
          AND DP.data_inizio <= NOW()
          AND DP.data_fine > NOW()
    );

    -- 2. Servizi che devono tornare DISPONIBILI perché la prenotazione è finita
    UPDATE SERVIZIO S
    SET S.status = 'DISPONIBILE'
    WHERE S.status = 'OCCUPATO'
      AND NOT EXISTS (
          SELECT 1
          FROM DETTAGLIO_PRENOTAZIONE DP
          WHERE DP.ID_servizio = S.ID_servizio
            AND DP.data_fine > NOW()
      );
END$$

DELIMITER ;
