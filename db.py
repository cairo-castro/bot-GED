"""
Módulo para gerenciamento de conexão e operações com MariaDB
"""

import os
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASS')
        self.database = os.getenv('DB_NAME')

    def connect(self) -> bool:
        """Estabelece conexão com o banco de dados"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                autocommit=True
            )
            logger.info("Conexão com MariaDB estabelecida com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao conectar com MariaDB: {e}")
            return False

    def disconnect(self):
        """Fecha a conexão com o banco"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("Conexão com MariaDB fechada")

    def create_table(self) -> bool:
        """Cria a tabela uploads se não existir"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS uploads (
            id INT AUTO_INCREMENT PRIMARY KEY,
            caminho_arquivo TEXT NOT NULL,
            tipo_arquivo VARCHAR(100) NOT NULL,
            status ENUM('pendente','enviado','erro') DEFAULT 'pendente',
            data_envio DATETIME NULL,
            mensagem_erro TEXT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(create_table_query)
            cursor.close()
            logger.info("Tabela 'uploads' criada/verificada com sucesso")
            return True
        except Error as e:
            logger.error(f"Erro ao criar tabela: {e}")
            return False

    def insert_file_record(self, caminho_arquivo: str, tipo_arquivo: str) -> Optional[int]:
        """Insere um novo registro de arquivo no banco"""
        query = """
        INSERT INTO uploads (caminho_arquivo, tipo_arquivo, status)
        VALUES (%s, %s, 'pendente')
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (caminho_arquivo, tipo_arquivo))
            record_id = cursor.lastrowid
            cursor.close()
            logger.debug(f"Arquivo inserido no banco: {caminho_arquivo}")
            return record_id
        except Error as e:
            logger.error(f"Erro ao inserir arquivo no banco: {e}")
            return None

    def get_pending_files(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Busca arquivos com status pendente"""
        query = """
        SELECT id, caminho_arquivo, tipo_arquivo, status
        FROM uploads
        WHERE status = 'pendente'
        ORDER BY created_at ASC
        LIMIT %s
        """

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Erro ao buscar arquivos pendentes: {e}")
            return []

    def update_file_status(self, file_id: int, status: str, mensagem_erro: str = None) -> bool:
        """Atualiza o status de um arquivo"""
        query = """
        UPDATE uploads
        SET status = %s, data_envio = %s, mensagem_erro = %s
        WHERE id = %s
        """

        data_envio = datetime.now() if status in ['enviado', 'erro'] else None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (status, data_envio, mensagem_erro, file_id))
            cursor.close()
            logger.debug(f"Status do arquivo ID {file_id} atualizado para: {status}")
            return True
        except Error as e:
            logger.error(f"Erro ao atualizar status do arquivo: {e}")
            return False

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Busca todos os registros para relatório"""
        query = """
        SELECT caminho_arquivo, tipo_arquivo, status, data_envio, mensagem_erro
        FROM uploads
        ORDER BY created_at ASC
        """

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except Error as e:
            logger.error(f"Erro ao buscar registros: {e}")
            return []

    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas dos uploads"""
        query = """
        SELECT
            status,
            COUNT(*) as count
        FROM uploads
        GROUP BY status
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            stats = {'pendente': 0, 'enviado': 0, 'erro': 0}
            for status, count in results:
                stats[status] = count

            return stats
        except Error as e:
            logger.error(f"Erro ao buscar estatísticas: {e}")
            return {'pendente': 0, 'enviado': 0, 'erro': 0}

    def clear_pending_files(self) -> bool:
        """Remove todos os arquivos com status pendente (útil para restart)"""
        query = "DELETE FROM uploads WHERE status = 'pendente'"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            rows_affected = cursor.rowcount
            cursor.close()
            logger.info(f"Removidos {rows_affected} registros pendentes")
            return True
        except Error as e:
            logger.error(f"Erro ao limpar registros pendentes: {e}")
            return False


def get_db_manager() -> DatabaseManager:
    """Factory function para criar instância do DatabaseManager"""
    return DatabaseManager()