-- Bâtiments
INSERT INTO BATIMENT (nom, localisation, type_batiment) VALUES
('Université Ankatso', 'Antananarivo', 'Université'),
('Hôpital Befelatanana', 'Antananarivo', 'Hôpital');

-- Sources d'énergie
INSERT INTO SOURCE_ENERGIE (nom_source, cout_kwh, description) VALUES
('JIRAMA', 0.20, 'Réseau électrique national'),
('Groupe électrogène', 0.45, 'Groupe diesel');

-- Types d'équipement
INSERT INTO TYPE_EQUIPEMENT (nom_type, consommation_theorique) VALUES
('Éclairage', 0.5),
('Climatisation', 3.0),
('Informatique', 1.2),
('Laboratoire', 2.5);

-- Équipements Université
INSERT INTO EQUIPEMENT (nom_equipement, puissance_watt, id_type, id_batiment) VALUES
('Salle Info 1', 500, 3, 1),
('Amphi A', 1200, 1, 1),
('Clim Centrale', 3500, 2, 1);

-- Équipements Hôpital
INSERT INTO EQUIPEMENT (nom_equipement, puissance_watt, id_type, id_batiment) VALUES
('Bloc opératoire', 2500, 4, 2),
('Salle Urgences', 1500, 1, 2);

-- Consommations
INSERT INTO CONSOMMATION (id_equipement, id_source, date_heure, duree_minutes, energie_kwh) VALUES
(1, 1, '2025-01-10 07:00:00', 60, 1.1),
(2, 1, '2025-01-10 07:00:00', 60, 0.6),
(3, 1, '2025-01-10 07:00:00', 60, 3.2),
(1, 2, '2025-01-10 09:00:00', 60, 1.4),
(2, 2, '2025-01-10 09:00:00', 60, 0.8),
(3, 2, '2025-01-10 09:00:00', 60, 3.9),
(3, 2, '2025-01-10 10:00:00', 60, 7.5),
(1, 1, '2025-01-11 08:00:00', 60, 1.0),
(2, 1, '2025-01-11 08:00:00', 60, 0.5),
(3, 1, '2025-01-11 08:00:00', 60, 3.1),
(1, 1, '2025-01-12 08:00:00', 60, 1.2),
(2, 1, '2025-01-12 08:00:00', 60, 0.6),
(3, 1, '2025-01-12 08:00:00', 60, 3.3);