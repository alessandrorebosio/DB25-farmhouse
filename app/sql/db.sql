
DROP DATABASE DB;
CREATE DATABASE DB;
USE DB;

CREATE TABLE PERSONA (
    CF CHAR(16) PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    cognome VARCHAR(50) NOT NULL
);

CREATE TABLE UTENTE (
    username VARCHAR(30) PRIMARY KEY,
    CF CHAR(16) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL,
    FOREIGN KEY (CF) REFERENCES PERSONA(CF)
);

CREATE TABLE DIPENDENTE (
    username VARCHAR(30) PRIMARY KEY,
    ruolo VARCHAR(50) NOT NULL,
    data_assunzione DATE NOT NULL,
    data_licenziamento DATE,
    FOREIGN KEY (username) REFERENCES UTENTE(username)
);

CREATE TABLE DIPENDENTE_RUOLO_STORICO (
    username VARCHAR(30) NOT NULL,
    ruolo VARCHAR(50) NOT NULL,
    data_inizio DATE NOT NULL,
    data_fine DATE,
    PRIMARY KEY (username, data_inizio, ruolo),
    FOREIGN KEY (username) REFERENCES DIPENDENTE(username)
);

DELIMITER $$
CREATE TRIGGER trg_dipendente_after_insert
AFTER INSERT ON DIPENDENTE
FOR EACH ROW
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM DIPENDENTE_RUOLO_STORICO
        WHERE username = NEW.username AND data_inizio = NEW.data_assunzione
    ) THEN
        INSERT INTO DIPENDENTE_RUOLO_STORICO (username, ruolo, data_inizio)
        VALUES (NEW.username, NEW.ruolo, NEW.data_assunzione);
    END IF;
END$$

CREATE TRIGGER trg_dipendente_after_update
AFTER UPDATE ON DIPENDENTE
FOR EACH ROW
BEGIN
    -- solo se il ruolo è cambiato
    IF NEW.ruolo <> OLD.ruolo THEN
        -- chiudo la precedente voce di storico (se aperta)
        UPDATE DIPENDENTE_RUOLO_STORICO
        SET data_fine = DATE_SUB(CURDATE(), INTERVAL 0 DAY)
        WHERE username = NEW.username AND data_fine IS NULL;

        -- aggiungo nuova voce con data_inizio = oggi
        INSERT INTO DIPENDENTE_RUOLO_STORICO (username, ruolo, data_inizio)
        VALUES (NEW.username, NEW.ruolo, CURDATE());
    END IF;
END$$
DELIMITER ;

START TRANSACTION;

INSERT INTO PERSONA (CF, nome, cognome)
VALUES ('RSSMRA85M01H501U', 'Mario', 'Rossi');

INSERT INTO PERSONA (CF, nome, cognome)
VALUES ('0123456789ABCDEF', 'Luigi', 'Bianchi');

INSERT INTO UTENTE (username, CF, password, email)
VALUES ('mrossi', 'RSSMRA85M01H501U', 'admin', 'mario.rossi@example.com');

INSERT INTO UTENTE (username, CF, password, email)
VALUES ('lbianchi', '0123456789ABCDEF', 'user', 'luigi.bianchi@example.com');

INSERT INTO DIPENDENTE (username, ruolo, data_assunzione)
VALUES ('mrossi', 'Staff', '2025-09-03');

COMMIT;

SELECT * FROM PERSONA p JOIN UTENTE u ON p.CF = u.CF JOIN DIPENDENTE d ON u.username = d.username;
SELECT * FROM PERSONA p JOIN UTENTE u ON p.CF = u.CF;
UPDATE DIPENDENTE SET ruolo = 'Admin' WHERE username = 'mrossi';
SELECT * FROM DIPENDENTE_RUOLO_STORICO JOIN DIPENDENTE;
