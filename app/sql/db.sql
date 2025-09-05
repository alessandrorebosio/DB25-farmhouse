
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

START TRANSACTION;

INSERT INTO PERSONA (CF, nome, cognome)
VALUES ('RSSMRA85M01H501U', 'Mario', 'Rossi');

INSERT INTO UTENTE (username, CF, password, email)
VALUES ('mrossi', 'RSSMRA85M01H501U', 'pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=', 'mario.rossi@example.com');

INSERT INTO DIPENDENTE (username, ruolo, data_assunzione)
VALUES ('mrossi', 'admin', '2025-09-03');

COMMIT;
