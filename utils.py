"""
Utilitários e funções auxiliares
"""

import os
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import csv


logger = logging.getLogger(__name__)


class RetryHandler:
    """Handler para retry com backoff exponencial"""

    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute_with_retry(self, func, *args, **kwargs):
        """Executa função com retry automático"""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                if attempt < self.max_retries - 1:  # Não é a última tentativa
                    delay = min(self.base_delay * (2 ** attempt), self.max_delay)
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Tentando novamente em {delay}s")
                    time.sleep(delay)
                else:
                    logger.error(f"Todas as {self.max_retries} tentativas falharam")

        raise last_exception


class FileUtils:
    """Utilitários para manipulação de arquivos"""

    @staticmethod
    def get_file_hash(file_path: str) -> Optional[str]:
        """Calcula hash MD5 de um arquivo"""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Erro ao calcular hash do arquivo {file_path}: {e}")
            return None

    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Retorna tamanho do arquivo em bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return 0

    @staticmethod
    def is_valid_document_file(file_path: str) -> bool:
        """Verifica se é um arquivo de documento válido"""
        valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'}
        file_extension = Path(file_path).suffix.lower()

        if file_extension not in valid_extensions:
            return False

        # Verifica se o arquivo existe e não está vazio
        try:
            return os.path.exists(file_path) and os.path.getsize(file_path) > 0
        except Exception:
            return False

    @staticmethod
    def clean_filename(filename: str) -> str:
        """Limpa nome de arquivo removendo caracteres inválidos"""
        invalid_chars = '<>:"/\\|?*'
        cleaned = filename

        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')

        return cleaned.strip()


class ProgressTracker:
    """Rastreador de progresso para operações longas"""

    def __init__(self, total: int, description: str = "Processando"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
        self.last_update = self.start_time

    def update(self, increment: int = 1):
        """Atualiza o progresso"""
        self.current = min(self.current + increment, self.total)
        now = datetime.now()

        # Atualiza log a cada 30 segundos ou quando completa
        if (now - self.last_update).seconds >= 30 or self.current == self.total:
            self.log_progress()
            self.last_update = now

    def log_progress(self):
        """Registra progresso atual no log"""
        if self.total == 0:
            return

        percentage = (self.current / self.total) * 100
        elapsed = datetime.now() - self.start_time

        if self.current > 0:
            avg_time_per_item = elapsed.total_seconds() / self.current
            remaining_items = self.total - self.current
            eta = timedelta(seconds=avg_time_per_item * remaining_items)

            logger.info(f"{self.description}: {self.current}/{self.total} "
                       f"({percentage:.1f}%) - ETA: {eta}")
        else:
            logger.info(f"{self.description}: {self.current}/{self.total} ({percentage:.1f}%)")


class ReportGenerator:
    """Gerador de relatórios customizados"""

    @staticmethod
    def generate_summary_report(data: List[Dict[str, Any]], output_file: str):
        """Gera relatório resumido"""
        try:
            # Agrupa dados por tipo e status
            summary = {}

            for record in data:
                tipo = record.get('tipo_arquivo', 'unknown')
                status = record.get('status', 'unknown')

                if tipo not in summary:
                    summary[tipo] = {'total': 0, 'enviado': 0, 'erro': 0, 'pendente': 0}

                summary[tipo]['total'] += 1
                summary[tipo][status] = summary[tipo].get(status, 0) + 1

            # Salva relatório resumido
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)

                # Cabeçalho
                writer.writerow([
                    'Tipo de Documento',
                    'Total de Arquivos',
                    'Enviados com Sucesso',
                    'Com Erro',
                    'Pendentes',
                    'Taxa de Sucesso (%)'
                ])

                # Dados
                for tipo, stats in summary.items():
                    success_rate = (stats['enviado'] / stats['total'] * 100) if stats['total'] > 0 else 0

                    writer.writerow([
                        tipo.title(),
                        stats['total'],
                        stats['enviado'],
                        stats['erro'],
                        stats['pendente'],
                        f"{success_rate:.1f}%"
                    ])

                # Totais
                total_files = sum(s['total'] for s in summary.values())
                total_success = sum(s['enviado'] for s in summary.values())
                total_errors = sum(s['erro'] for s in summary.values())
                total_pending = sum(s['pendente'] for s in summary.values())
                overall_success_rate = (total_success / total_files * 100) if total_files > 0 else 0

                writer.writerow([])  # Linha vazia
                writer.writerow([
                    'TOTAL GERAL',
                    total_files,
                    total_success,
                    total_errors,
                    total_pending,
                    f"{overall_success_rate:.1f}%"
                ])

            logger.info(f"Relatório resumido salvo: {output_file}")

        except Exception as e:
            logger.error(f"Erro ao gerar relatório resumido: {e}")


class PerformanceMonitor:
    """Monitor de performance do sistema"""

    def __init__(self):
        self.start_time = None
        self.checkpoints = {}

    def start(self):
        """Inicia monitoramento"""
        self.start_time = datetime.now()
        logger.info("Monitor de performance iniciado")

    def checkpoint(self, name: str):
        """Cria um checkpoint de performance"""
        if not self.start_time:
            self.start()

        self.checkpoints[name] = {
            'time': datetime.now(),
            'elapsed_from_start': datetime.now() - self.start_time
        }

        logger.debug(f"Checkpoint '{name}': {self.checkpoints[name]['elapsed_from_start']}")

    def get_summary(self) -> Dict[str, Any]:
        """Retorna resumo de performance"""
        if not self.start_time:
            return {}

        total_time = datetime.now() - self.start_time

        return {
            'total_execution_time': total_time,
            'checkpoints': self.checkpoints,
            'average_checkpoint_interval': total_time / len(self.checkpoints) if self.checkpoints else timedelta(0)
        }


class ConfigValidator:
    """Validador de configurações"""

    @staticmethod
    def validate_database_config() -> Dict[str, Any]:
        """Valida configurações do banco de dados"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASS', 'DB_NAME']
        missing_vars = []

        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        return {
            'valid': len(missing_vars) == 0,
            'missing_variables': missing_vars
        }

    @staticmethod
    def validate_site_config() -> Dict[str, Any]:
        """Valida configurações do site"""
        required_vars = ['SITE_USER', 'SITE_PASS']
        optional_vars = ['SITE_BASE_URL']

        missing_required = []
        missing_optional = []

        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)

        return {
            'valid': len(missing_required) == 0,
            'missing_required': missing_required,
            'missing_optional': missing_optional
        }

    @staticmethod
    def validate_paths() -> Dict[str, Any]:
        """Valida caminhos de diretórios"""
        documents_path = os.getenv('DOCUMENTS_BASE_PATH', './documentos')

        issues = []

        if not os.path.exists(documents_path):
            issues.append(f"Diretório de documentos não existe: {documents_path}")
        elif not os.path.isdir(documents_path):
            issues.append(f"Caminho não é um diretório: {documents_path}")
        else:
            # Verifica se há subdiretórios
            subdirs = [d for d in Path(documents_path).iterdir() if d.is_dir()]
            if not subdirs:
                issues.append(f"Nenhum subdiretório encontrado em: {documents_path}")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'documents_path': documents_path
        }