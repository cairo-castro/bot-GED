-- Script para criar banco e usuário do sistema de upload
-- Execute como root no MySQL/MariaDB

-- Cria o banco de dados
CREATE DATABASE IF NOT EXISTS uploads_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Cria usuário específico para o bot
-- Senha: MedBot2024!
CREATE USER IF NOT EXISTS 'medbot_user'@'localhost' IDENTIFIED BY 'MedBot2024!';

-- Concede permissões específicas no banco uploads_db
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX ON uploads_db.* TO 'medbot_user'@'localhost';

-- Atualiza privilégios
FLUSH PRIVILEGES;

-- Mostra bancos criados
SHOW DATABASES;

-- Mostra usuários
SELECT User, Host FROM mysql.user WHERE User = 'medbot_user';

-- Testa conexão (opcional)
SELECT 'Banco de dados criado com sucesso!' AS status;