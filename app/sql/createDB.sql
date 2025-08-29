-- -----------------------------------------------------
-- Schema farmhouse
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS farmhouse;
CREATE SCHEMA farmhouse;
USE farmhouse;

-- -----------------------------------------------------
-- Persona
-- -----------------------------------------------------
CREATE TABLE persona (
  CF CHAR(16) NOT NULL,
  nome VARCHAR(50) NOT NULL,
  cognome VARCHAR(50) NOT NULL,
  PRIMARY KEY (CF)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Utente
-- -----------------------------------------------------
CREATE TABLE utente (
  username VARCHAR(32) PRIMARY KEY,
  CF CHAR(16) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  FOREIGN KEY (CF) REFERENCES persona(CF)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Dipendente
-- -----------------------------------------------------
CREATE TABLE dipendente (
  username VARCHAR(32) PRIMARY KEY,
  data_assunzione DATE NOT NULL,
  FOREIGN KEY (username) REFERENCES utente(username)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Ruolo
-- -----------------------------------------------------
CREATE TABLE ruolo (
  ID_ruolo INT AUTO_INCREMENT PRIMARY KEY,
  tipo_ruolo VARCHAR(50) NOT NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Assegna Ruolo
-- -----------------------------------------------------
CREATE TABLE assegna_ruolo (
  username VARCHAR(32) NOT NULL,
  ID_ruolo INT NOT NULL,
  data_inizio DATE NOT NULL,
  data_fine DATE,
  PRIMARY KEY (username, ID_ruolo, data_inizio),
  FOREIGN KEY (username) REFERENCES dipendente(username),
  FOREIGN KEY (ID_ruolo) REFERENCES ruolo(ID_ruolo)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Pacchetto
-- -----------------------------------------------------
CREATE TABLE pacchetto (
  ID_pacchetto INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  descrizione TEXT
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Servizio
-- -----------------------------------------------------
CREATE TABLE servizio (
  ID_servizio INT AUTO_INCREMENT PRIMARY KEY,
  status ENUM('disponibile','indisponibile','fuori_servizio') NOT NULL,
  tipo_servizio ENUM('camera','tavolo','campo_da_calcio','lettino','attività_con_animali') NOT NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Specializzazioni Servizi
-- -----------------------------------------------------
CREATE TABLE camera (
  ID_servizio INT PRIMARY KEY,
  cod_camera VARCHAR(10) NOT NULL,
  max_capienza INT NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

CREATE TABLE tavolo (
  ID_servizio INT PRIMARY KEY,
  cod_tavolo VARCHAR(10) NOT NULL,
  max_capienza INT NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

CREATE TABLE campo_da_gioco (
  ID_servizio INT PRIMARY KEY,
  cod_campo VARCHAR(10) NOT NULL,
  max_capienza INT NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

CREATE TABLE lettino (
  ID_servizio INT PRIMARY KEY,
  cod_lettino VARCHAR(10) NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

CREATE TABLE attivita_con_animali (
  ID_servizio INT PRIMARY KEY,
  cod_attivita VARCHAR(10) NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Relazione Pacchetto - Servizio
-- -----------------------------------------------------
CREATE TABLE composto_da (
  ID_pacchetto INT NOT NULL,
  ID_servizio INT NOT NULL,
  quantita INT DEFAULT 1,
  PRIMARY KEY (ID_pacchetto, ID_servizio),
  FOREIGN KEY (ID_pacchetto) REFERENCES pacchetto(ID_pacchetto),
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Acquista Pacchetto
-- -----------------------------------------------------
CREATE TABLE acquista (
  ID_pacchetto INT NOT NULL,
  username VARCHAR(32) NOT NULL,
  PRIMARY KEY (ID_pacchetto, username),
  FOREIGN KEY (ID_pacchetto) REFERENCES pacchetto(ID_pacchetto),
  FOREIGN KEY (username) REFERENCES utente(username)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Prenotazione
-- -----------------------------------------------------
CREATE TABLE prenotazione (
  ID_prenotazione INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) NOT NULL,
  data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  stato ENUM('attiva','completata','cancellata') DEFAULT 'attiva',
  FOREIGN KEY (username) REFERENCES utente(username)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Dettagli Prenotazione
-- -----------------------------------------------------
CREATE TABLE dettagli_prenotazione (
  ID_prenotazione INT NOT NULL,
  ID_servizio INT NOT NULL,
  data_inizio DATE NOT NULL,
  data_fine DATE NOT NULL,
  PRIMARY KEY (ID_prenotazione, ID_servizio, data_inizio),
  FOREIGN KEY (ID_prenotazione) REFERENCES prenotazione(ID_prenotazione),
  FOREIGN KEY (ID_servizio) REFERENCES servizio(ID_servizio)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Recensione
-- -----------------------------------------------------
CREATE TABLE recensione (
  ID_recensione INT AUTO_INCREMENT PRIMARY KEY,
  ID_prenotazione INT NOT NULL,
  username VARCHAR(32) NOT NULL,
  voto TINYINT CHECK (voto BETWEEN 1 AND 5),
  descrizione VARCHAR(500),
  data_recensione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (ID_prenotazione) REFERENCES prenotazione(ID_prenotazione),
  FOREIGN KEY (username) REFERENCES utente(username),
  UNIQUE (ID_prenotazione, username) -- una recensione per utente per prenotazione
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Ordine
-- -----------------------------------------------------
CREATE TABLE ordine (
  ID_ordine INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(32) NOT NULL,
  data_creazione TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  stato ENUM('in_attesa','confermato','spedito') DEFAULT 'in_attesa',
  FOREIGN KEY (username) REFERENCES utente(username)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Prodotto
-- -----------------------------------------------------
CREATE TABLE prodotto (
  ID_prodotto INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  prezzo DECIMAL(10,2) NOT NULL
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Dettagli Ordine
-- -----------------------------------------------------
CREATE TABLE dettagli_ordine (
  ID_ordine INT NOT NULL,
  ID_prodotto INT NOT NULL,
  quantita INT NOT NULL,
  PRIMARY KEY (ID_ordine, ID_prodotto),
  FOREIGN KEY (ID_ordine) REFERENCES ordine(ID_ordine),
  FOREIGN KEY (ID_prodotto) REFERENCES prodotto(ID_prodotto)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Evento
-- -----------------------------------------------------
CREATE TABLE evento (
  ID_evento INT AUTO_INCREMENT PRIMARY KEY,
  descrizione VARCHAR(255) NOT NULL,
  max_partecipanti INT NOT NULL,
  data_evento DATE NOT NULL,
  username VARCHAR(32) NOT NULL,
  FOREIGN KEY (username) REFERENCES dipendente(username)
) ENGINE=InnoDB;

-- -----------------------------------------------------
-- Iscrizione Evento
-- -----------------------------------------------------
CREATE TABLE iscrive (
  ID_evento INT NOT NULL,
  username VARCHAR(32) NOT NULL,
  PRIMARY KEY (ID_evento, username),
  FOREIGN KEY (ID_evento) REFERENCES evento(ID_evento),
  FOREIGN KEY (username) REFERENCES utente(username)
) ENGINE=InnoDB;
