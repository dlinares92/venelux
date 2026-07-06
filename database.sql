-- Venelux Database Instantiation
CREATE DATABASE IF NOT EXISTS `venelux_db`;
USE `venelux_db`;

CREATE TABLE IF NOT EXISTS `form_contact` (
    `id` INT(11) AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(150) NOT NULL,
    `message` TEXT NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar un dato de prueba
INSERT INTO `form_contact` (`name`, `email`, `message`) VALUES 
('Usuario de Prueba', 'test@example.com', 'Hola, este es un mensaje de prueba para verificar el guardado.');
