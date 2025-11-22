CREATE DATABASE IF NOT EXISTS onion_project
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE onion_project;

CREATE TABLE IF NOT EXISTS routers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(64) NOT NULL UNIQUE,
  ip VARCHAR(64) NOT NULL,
  port INT NOT NULL,
  n LONGTEXT NOT NULL,
  e BIGINT NOT NULL,
  enabled TINYINT(1) DEFAULT 1,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS routes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  router_id INT NOT NULL,
  destination VARCHAR(64) NOT NULL,
  next_hop VARCHAR(64) NOT NULL,
  interface VARCHAR(32) DEFAULT NULL,
  priority INT DEFAULT 0,
  FOREIGN KEY (router_id) REFERENCES routers(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX idx_routes_router_id ON routes(router_id);
CREATE INDEX idx_routes_destination ON routes(destination);

CREATE TABLE IF NOT EXISTS router_status (
  router_name VARCHAR(64) PRIMARY KEY,
  last_seen TIMESTAMP NOT NULL,
  router_load INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS logs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  router_name VARCHAR(64) NOT NULL,
  event TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS mutex (
  name VARCHAR(64) PRIMARY KEY,
  note VARCHAR(255)
);

INSERT IGNORE INTO mutex(name, note)
VALUES ('global_write', 'serialize critical updates');
