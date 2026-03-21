
-- 1) Crear la base de datos
CREATE DATABASE IF NOT EXISTS `s2g_db`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
  
USE `s2g_db`;

-- 2) Crear la tabla de estaciones
CREATE TABLE IF NOT EXISTS `stations` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(255) NOT NULL,
  `location` VARCHAR(255) NOT NULL,
  `max_kw` FLOAT NOT NULL,
  `status` ENUM('activo','inactivo') NOT NULL DEFAULT 'inactivo',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3) Inserts de ejemplo
INSERT INTO `stations` (`name`, `location`, `max_kw`, `status`)
VALUES
  ('Estación Centro',    'Mérida, Yucatán',    50.0, 'activo'),
  ('Estación Norte',     'Tizimín, Yucatán',   22.5, 'inactivo'),
  ('Estación Sur',       'Valladolid, Yucatán',11.0, 'activo'),
  ('Estación Oriente',   'Tekax, Yucatán',     30.0, 'inactivo');