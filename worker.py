"""
Worker para processamento individual de arquivos
"""

import os
import logging
import time
from typing import Dict, Any, Optional
from pathlib import Path
from playwright.sync_api import sync_playwright, Browser, BrowserContext
from db import DatabaseManager
from flows import AtestadosFlow, ProntuariosFlow, ExamesFlow

logger = logging.getLogger(__name__)


class DocumentWorker:
    """Worker responsável por processar arquivos individuais"""

    def __init__(self, worker_id: int):
        self.worker_id = worker_id
        self.db_manager = DatabaseManager()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.retry_count = 3
        self.retry_delay_base = 2  # segundos

    def setup(self) -> bool:
        """Inicializa o worker"""
        try:
            logger.info(f"Worker {self.worker_id}: Iniciando setup")

            # Conecta ao banco
            if not self.db_manager.connect():
                logger.error(f"Worker {self.worker_id}: Falha ao conectar com banco")
                return False

            logger.info(f"Worker {self.worker_id}: Setup concluído")
            return True

        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Erro no setup: {e}")
            return False

    def cleanup(self):
        """Limpa recursos do worker"""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.db_manager:
                self.db_manager.disconnect()

            logger.info(f"Worker {self.worker_id}: Cleanup concluído")

        except Exception as e:
            logger.warning(f"Worker {self.worker_id}: Erro no cleanup: {e}")

    def create_browser(self) -> bool:
        """Cria instância do navegador"""
        try:
            playwright = sync_playwright().start()

            self.browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=VizDisplayCompositor'
                ]
            )

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            return True

        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Erro ao criar browser: {e}")
            return False

    def get_flow_handler(self, tipo_arquivo: str):
        """Retorna o handler apropriado para o tipo de arquivo"""
        flow_map = {
            'atestados': AtestadosFlow,
            'prontuarios': ProntuariosFlow,
            'prontuário': ProntuariosFlow,
            'prontuario': ProntuariosFlow,
            'exames': ExamesFlow,
            'laudos': ExamesFlow,
            'resultados': ExamesFlow
        }

        flow_class = flow_map.get(tipo_arquivo.lower())
        if not flow_class:
            # Fallback: tenta determinar pelo nome
            if 'atestado' in tipo_arquivo.lower():
                flow_class = AtestadosFlow
            elif 'prontuario' in tipo_arquivo.lower() or 'prontuário' in tipo_arquivo.lower():
                flow_class = ProntuariosFlow
            elif any(word in tipo_arquivo.lower() for word in ['exame', 'laudo', 'resultado']):
                flow_class = ExamesFlow
            else:
                # Default para atestados se não conseguir determinar
                flow_class = AtestadosFlow

        return flow_class(self.browser)

    def process_file(self, file_record: Dict[str, Any]) -> Dict[str, Any]:
        """Processa um arquivo específico"""
        file_id = file_record['id']
        file_path = file_record['caminho_arquivo']
        tipo_arquivo = file_record['tipo_arquivo']

        logger.info(f"Worker {self.worker_id}: Processando arquivo {file_id} - {file_path}")

        try:
            # Verifica se o arquivo existe
            if not os.path.exists(file_path):
                error_msg = f"Arquivo não encontrado: {file_path}"
                logger.error(f"Worker {self.worker_id}: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'file_id': file_id
                }

            # Cria browser se necessário
            if not self.browser:
                if not self.create_browser():
                    return {
                        'success': False,
                        'error': 'Falha ao criar browser',
                        'file_id': file_id
                    }

            # Obtém o handler de fluxo apropriado
            flow_handler = self.get_flow_handler(tipo_arquivo)

            # Processa o arquivo
            result = flow_handler.process_file(file_path)
            result['file_id'] = file_id

            logger.info(f"Worker {self.worker_id}: Arquivo {file_id} processado - Sucesso: {result['success']}")
            return result

        except Exception as e:
            error_msg = f"Erro inesperado ao processar arquivo: {str(e)}"
            logger.error(f"Worker {self.worker_id}: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'file_id': file_id
            }

    def process_with_retry(self, file_record: Dict[str, Any]) -> Dict[str, Any]:
        """Processa arquivo com retry automático"""
        file_id = file_record['id']

        for attempt in range(self.retry_count):
            try:
                logger.info(f"Worker {self.worker_id}: Tentativa {attempt + 1}/{self.retry_count} para arquivo {file_id}")

                result = self.process_file(file_record)

                if result['success']:
                    # Sucesso - atualiza banco
                    self.db_manager.update_file_status(file_id, 'enviado')
                    return result
                else:
                    # Falha - se não é a última tentativa, tenta novamente
                    if attempt < self.retry_count - 1:
                        delay = self.retry_delay_base ** (attempt + 1)  # Backoff exponencial
                        logger.warning(f"Worker {self.worker_id}: Falha na tentativa {attempt + 1}, tentando novamente em {delay}s")
                        time.sleep(delay)

                        # Recria browser para próxima tentativa
                        try:
                            if self.context:
                                self.context.close()
                            if self.browser:
                                self.browser.close()
                        except:
                            pass
                        self.browser = None
                        self.context = None
                    else:
                        # Última tentativa falhada - atualiza banco com erro
                        self.db_manager.update_file_status(file_id, 'erro', result.get('error', 'Erro desconhecido'))
                        return result

            except Exception as e:
                error_msg = f"Erro crítico na tentativa {attempt + 1}: {str(e)}"
                logger.error(f"Worker {self.worker_id}: {error_msg}")

                if attempt == self.retry_count - 1:
                    # Última tentativa - salva erro no banco
                    self.db_manager.update_file_status(file_id, 'erro', error_msg)
                    return {
                        'success': False,
                        'error': error_msg,
                        'file_id': file_id
                    }

        return {
            'success': False,
            'error': 'Todas as tentativas falharam',
            'file_id': file_id
        }

    def run(self) -> Dict[str, Any]:
        """Loop principal do worker"""
        stats = {
            'processed': 0,
            'success': 0,
            'errors': 0,
            'worker_id': self.worker_id
        }

        try:
            if not self.setup():
                return stats

            logger.info(f"Worker {self.worker_id}: Iniciando processamento")

            while True:
                # Busca próximo arquivo pendente
                pending_files = self.db_manager.get_pending_files(limit=1)

                if not pending_files:
                    logger.info(f"Worker {self.worker_id}: Nenhum arquivo pendente, finalizando")
                    break

                file_record = pending_files[0]
                file_id = file_record['id']

                # Marca como em processamento (atualiza para prevenir outros workers)
                self.db_manager.update_file_status(file_id, 'processando')

                # Processa o arquivo
                result = self.process_with_retry(file_record)

                stats['processed'] += 1
                if result['success']:
                    stats['success'] += 1
                    logger.info(f"Worker {self.worker_id}: ✓ Arquivo {file_id} processado com sucesso")
                else:
                    stats['errors'] += 1
                    logger.error(f"Worker {self.worker_id}: ✗ Falha no arquivo {file_id}: {result.get('error', 'Erro desconhecido')}")

                # Pequena pausa entre arquivos
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info(f"Worker {self.worker_id}: Interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Worker {self.worker_id}: Erro crítico: {e}")
        finally:
            self.cleanup()

        logger.info(f"Worker {self.worker_id}: Finalizado - Processados: {stats['processed']}, Sucessos: {stats['success']}, Erros: {stats['errors']}")
        return stats


def worker_main(worker_id: int) -> Dict[str, Any]:
    """Função principal para ser chamada em processo separado"""
    # Configura logging para o processo worker
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(asctime)s - Worker-{worker_id} - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/worker_{worker_id}.log'),
            logging.StreamHandler()
        ]
    )

    worker = DocumentWorker(worker_id)
    return worker.run()