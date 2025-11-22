-- ============================================================
--   SAE 3.02 - Base sae302
--   Tables : routeurs + routes
-- ============================================================

-- 1. Création de la base
CREATE DATABASE IF NOT EXISTS sae302
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE sae302;

-- ============================================================
-- 2. Table : routeurs
--    Stocke l'adresse + clé publique RSA (n, e)
-- ============================================================
DROP TABLE IF EXISTS routeurs;

CREATE TABLE routeurs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_port VARCHAR(100) NOT NULL UNIQUE,  -- ex : "192.168.1.10:5001"
    n TEXT NOT NULL,                       -- clé publique RSA (modulus)
    e TEXT NOT NULL,                       -- clé publique RSA (exponent)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index utile
CREATE INDEX idx_routeurs_ip_port ON routeurs(ip_port);


-- ============================================================
-- 3. Table : routes
--    Correspond à la table de routage gérée par le master
-- ============================================================
DROP TABLE IF EXISTS routes;

CREATE TABLE routes (
    id INT AUTO_INCREMENT PRIMARY KEY,

    -- Routeur auquel appartient la règle
    routeur_id INT NOT NULL,

    -- Destination finale (nom, ip ou client-id)
    destination VARCHAR(100) NOT NULL,

    -- Prochain saut (router suivant, ou client final)
    next_hop VARCHAR(100) NOT NULL,

    -- Optionnel : interface logique
    interface VARCHAR(20) DEFAULT NULL,

    -- Contrainte FK
    CONSTRAINT fk_routes_routeur
        FOREIGN KEY (routeur_id)
        REFERENCES routeurs(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

-- Index pour optimiser les recherches
CREATE INDEX idx_routes_routeur_id ON routes(routeur_id);
CREATE INDEX idx_routes_destination ON routes(destination);
