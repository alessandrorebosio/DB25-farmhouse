-- Demo insert e query per FARMHOUSE (dati falsi)
USE farmhouse;

-- 1) PERSONA -> UTENTE
INSERT INTO PERSONA (CF, nome, cognome, telefono, citta) VALUES
('RSSMRA80A01H501U','Mario','Rossi','3331112222','Torino'),
('BNCLRD85B02F205X','Luca','Bianchi','3332223333','Milano'),
('VRDLNZ90C03G345Y','Anna','Verdi','3333334444','Genova'),
('NTRSFR92D04H678Z','Sara','Neri','3334445555','Firenze'),
('TPLROR75E05I901W','Marco','Tapi','3335556666','Bologna'),
('MSTLNZ99F06J234V','Paolo','Mast','3336667777','Roma');

INSERT INTO UTENTE (username, CF, password, email) VALUES
('mrossi','RSSMRA80A01H501U','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','mario@example.com'),
('lbianchi','BNCLRD85B02F205X','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','luca@example.com'),
('averdi','VRDLNZ90C03G345Y','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','anna@example.com'),
('sneri','NTRSFR92D04H678Z','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','sara@example.com'),
('mtapi','TPLROR75E05I901W','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','marco@example.com'),
('pmast','MSTLNZ99F06J234V','pbkdf2_sha256$1000000$YBihCaRMRFKsgmUJPnaR70$+ZQ29axYaZe0aJ7usxHfqltidP79FMcIH0+T2NiOmYQ=','paolo@example.com');

-- 2) DIPENDENTE e ruoli storici
INSERT INTO DIPENDENTE (username, data_assunzione, data_licenziamento) VALUES
('pmast','2020-05-01', NULL),
('mtapi','2022-06-15', NULL);

INSERT INTO DIPENDENTE_RUOLO_STORICO (username, ruolo, data_inizio, data_fine) VALUES
('pmast','Staff','2020-05-01','2023-12-31'),
('pmast','Staff','2024-01-01',NULL),
('mtapi','Admin','2022-06-15',NULL);

-- 3) TURNO e svolge
INSERT INTO TURNO (giorno, ora_inizio, ora_fine, descrizione) VALUES
('LUN','08:00:00','14:00:00','Mattina'),
('VEN','16:00:00','22:00:00','Sera');

SET @t1 = LAST_INSERT_ID(); -- id ultimo inserito (qui t2), but we'll query explicit:
-- Recupero ids per semplicità
SELECT ID_turno INTO @turno1 FROM TURNO WHERE giorno='LUN' LIMIT 1;
SELECT ID_turno INTO @turno2 FROM TURNO WHERE giorno='VEN' LIMIT 1;

INSERT INTO SVOLGE (username, ID_turno, data_inizio) VALUES
('pmast', @turno1, NOW()),
('mtapi', @turno2, NOW());

-- 4) SERVIZI e sottotabelle
INSERT INTO SERVIZIO (prezzo, tipo_servizio) VALUES
(80.00,'CAMERA'),    -- Camera base 2 persone: €80
(120.00,'CAMERA'),   -- Camera suite 2 persone: €120  
(100.00,'CAMERA'),   -- Camera 4 persone: €100
(15.00,'PISCINA'),
(5.00,'ATTIVITA_CON_ANIMALI'),
(0.00,'CAMPO_DA_GIOCO'),
(0.00,'RISTORANTE');

SET @s1 = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='CAMERA' AND prezzo=80.00 LIMIT 1);
SET @s1_suite = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='CAMERA' AND prezzo=120.00 LIMIT 1);
SET @s1_family = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='CAMERA' AND prezzo=100.00 LIMIT 1);
SET @s2 = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='PISCINA' LIMIT 1);
SET @s3 = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='ATTIVITA_CON_ANIMALI' LIMIT 1);
SET @s4 = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='CAMPO_DA_GIOCO' LIMIT 1);
SET @s5 = (SELECT ID_servizio FROM SERVIZIO WHERE tipo_servizio='RISTORANTE' LIMIT 1);

INSERT INTO CAMERA (ID_servizio, cod_camera, max_capienza) VALUES
(@s1,'C01',2),        -- Camera base €80 per 2 persone
(@s1_suite,'C02',2),  -- Camera suite €120 per 2 persone  
(@s1_family,'C03',4); -- Camera famiglia €100 per 4 persone

INSERT INTO PISCINA (ID_servizio, cod_lettino) VALUES
(@s2,'L1');

INSERT INTO ATTIVITA_CON_ANIMALI (ID_servizio, cod_attivita, descrizione) VALUES
(@s3,'A01','Passeggiata con asinelli');

INSERT INTO CAMPO_DA_GIOCO (ID_servizio, cod_campo, max_capienza) VALUES
(@s4,'F1',22);

INSERT INTO RISTORANTE (ID_servizio, cod_tavolo, max_capienza) VALUES
(@s5,'T1',6);

-- 5) PACCHETTO, composto, acquista
INSERT INTO PACCHETTO (nome, descrizione) VALUES
('Weekend Famiglia','2 notti + piscina + attività animali'),
('Cena Romantica','Tavolo + menù degustazione');

SET @p1 = LAST_INSERT_ID(); -- last pacchetto (Cena Romantica)
-- better get both:
SELECT ID_pacchetto INTO @pac1 FROM PACCHETTO WHERE nome='Weekend Famiglia' LIMIT 1;
SELECT ID_pacchetto INTO @pac2 FROM PACCHETTO WHERE nome='Cena Romantica' LIMIT 1;

INSERT INTO COMPOSTO (ID_pacchetto, ID_servizio) VALUES
(@pac1, @s1),
(@pac1, @s2),
(@pac1, @s3),
(@pac2, @s5);

INSERT INTO ACQUISTA (ID_pacchetto, username) VALUES
(@pac1,'mrossi'),
(@pac2,'lbianchi');

-- 6) PRENOTAZIONI + DETTAGLIO_PRENOTAZIONE
INSERT INTO PRENOTAZIONE (username) VALUES ('mrossi'), ('averdi'), ('sneri');
SELECT ID_prenotazione INTO @pr1 FROM PRENOTAZIONE WHERE username='mrossi' ORDER BY ID_prenotazione DESC LIMIT 1;
SELECT ID_prenotazione INTO @pr2 FROM PRENOTAZIONE WHERE username='averdi' ORDER BY ID_prenotazione DESC LIMIT 1;
SELECT ID_prenotazione INTO @pr3 FROM PRENOTAZIONE WHERE username='sneri' ORDER BY ID_prenotazione DESC LIMIT 1;

-- pr1: passato (per recensione), pr2: attivo, pr3: futuro
INSERT INTO DETTAGLIO_PRENOTAZIONE (ID_prenotazione, ID_servizio, data_inizio, data_fine) VALUES
(@pr1, @s1, DATE_SUB(CURDATE(), INTERVAL 10 DAY), DATE_SUB(CURDATE(), INTERVAL 8 DAY)),
(@pr2, @s2, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 DAY)),
(@pr3, @s5, DATE_ADD(CURDATE(), INTERVAL 7 DAY), DATE_ADD(CURDATE(), INTERVAL 7 DAY));

-- 7) PRODOTTI, ORDINI, DETTAGLIO_ORDINE
INSERT INTO PRODOTTO (nome, prezzo) VALUES
('Marmellata Artigianale',6.50),
('Olio 500ml',12.00),
('Pane Casereccio',3.00);

INSERT INTO ORDINE (username) VALUES ('lbianchi'), ('mrossi');
SELECT ID_ordine INTO @o1 FROM ORDINE WHERE username='lbianchi' ORDER BY ID_ordine DESC LIMIT 1;
SELECT ID_ordine INTO @o2 FROM ORDINE WHERE username='mrossi' ORDER BY ID_ordine DESC LIMIT 1;
SELECT ID_prodotto INTO @prod1 FROM PRODOTTO WHERE nome='Marmellata Artigianale' LIMIT 1;
SELECT ID_prodotto INTO @prod2 FROM PRODOTTO WHERE nome='Olio 500ml' LIMIT 1;

INSERT INTO DETTAGLIO_ORDINE (ID_prodotto, ID_ordine, quantita, prezzo_unitario) VALUES
(@prod1, @o1, 2, 6.50),
(@prod2, @o1, 1, 12.00),
(@prod1, @o2, 1, 6.50);

-- 8) EVENTO e iscrive
INSERT INTO EVENTO (posti, titolo, descrizione, data_evento, username) VALUES
(20,'Torneo Calcetto','Torneo amatoriale', DATE_ADD(CURDATE(), INTERVAL 14 DAY),'pmast'),
(10,'Laboratorio Asini','Laboratorio per bambini', DATE_ADD(CURDATE(), INTERVAL 3 DAY),'mtapi');

SELECT ID_evento INTO @ev1 FROM EVENTO WHERE titolo='Torneo Calcetto' LIMIT 1;
SELECT ID_evento INTO @ev2 FROM EVENTO WHERE titolo='Laboratorio Asini' LIMIT 1;

INSERT INTO ISCRIVE (ID_evento, username, partecipanti) VALUES
(@ev1, 'mrossi', 4),
(@ev2, 'averdi', 2);

-- 9) ospita (collega PERSONA <-> UTENTE per ospitalità)
INSERT INTO OSPITA (CF, username, data_ospitazione) VALUES
('RSSMRA80A01H501U','mrossi', CURDATE()),
('VRDLNZ90C03G345Y','averdi', DATE_SUB(CURDATE(), INTERVAL 30 DAY));

-- 10) RECENSIONE (solo per prenotazione passata @pr1)
INSERT INTO RECENSIONE (tipo_servizio, voto, descrizione, username, ID_prenotazione) VALUES
('CAMERA',5,'Ottimo soggiorno, pulito e staff gentile.','mrossi', @pr1);

-- Esempi di query di demo
-- A) Elenco prenotazioni attive (oggi)
SELECT P.ID_prenotazione, P.username, DP.ID_servizio, DP.data_inizio, DP.data_fine
FROM PRENOTAZIONE P
JOIN DETTAGLIO_PRENOTAZIONE DP ON DP.ID_prenotazione = P.ID_prenotazione
WHERE DP.data_inizio <= CURDATE() AND DP.data_fine >= CURDATE();

-- B) Trova servizi occupati ora (utilizza evento schedulato logic)
SELECT * FROM SERVIZIO WHERE status = 'OCCUPATO';

-- C) Fatturato totale per prodotto (aggregato)
SELECT PR.nome, SUM(DO.quantita * DO.prezzo_unitario) AS totale_venduto
FROM DETTAGLIO_ORDINE DO
JOIN PRODOTTO PR ON PR.ID_prodotto = DO.ID_prodotto
GROUP BY PR.ID_prodotto;

-- D) Partecipanti residui per evento
SELECT E.ID_evento, E.titolo, E.posti FROM EVENTO E;

-- E) Pacchetti acquistati da utente
SELECT U.username, P.nome
FROM acquista A
JOIN UTENTE U ON U.username = A.username
JOIN PACCHETTO P ON P.ID_pacchetto = A.ID_pacchetto;

-- F) Recensioni recenti
SELECT * FROM RECENSIONE ORDER BY data_recensione DESC LIMIT 5;
