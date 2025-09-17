"""
Controller para coordenação de processos paralelos
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
from multiprocessing import Pool, Manager, Process, Queue
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
import pandas as pd
from datetime import datetime

from db import DatabaseManager
from worker import worker_main

logger = logging.getLogger(__name__)


class UploadController:
    """Controller principal para coordenar uploads paralelos"""

    def __init__(self, max_workers: int = 5):
        self.max_workers = max_workers
        self.db_manager = DatabaseManager()
        self.documents_base_path = os.getenv('DOCUMENTS_BASE_PATH', './documentos')

    def setup(self) -> bool:
        """Inicializa o controller"""
        try:
            logger.info("Controller: Iniciando setup")

            # Conecta ao banco
            if not self.db_manager.connect():
                logger.error("Controller: Falha ao conectar com banco")
                return False

            # Cria tabela se não existir
            if not self.db_manager.create_table():
                logger.error("Controller: Falha ao criar/verificar tabela")
                return False

            # Cria diretórios necessários
            os.makedirs('logs', exist_ok=True)
            os.makedirs('screenshots', exist_ok=True)

            logger.info("Controller: Setup concluído")
            return True

        except Exception as e:
            logger.error(f"Controller: Erro no setup: {e}")
            return False

    def scan_documents(self, force_rescan: bool = False) -> int:
        """Escaneia diretórios de documentos e registra no banco"""
        try:
            logger.info("Controller: Iniciando scan de documentos")

            if force_rescan:
                # Limpa registros pendentes
                self.db_manager.clear_pending_files()
                logger.info("Controller: Registros pendentes limpos")

            # Extensões de arquivo aceitas
            valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'}

            total_files = 0
            base_path = Path(self.documents_base_path)

            if not base_path.exists():
                logger.warning(f"Controller: Diretório base não encontrado: {self.documents_base_path}")
                return 0

            # Escaneia cada subdiretório (cada um representa um tipo de documento)
            for tipo_dir in base_path.iterdir():
                if not tipo_dir.is_dir():
                    continue

                tipo_arquivo = tipo_dir.name.lower()
                logger.info(f"Controller: Escaneando tipo '{tipo_arquivo}'")

                files_in_type = 0

                # Escaneia todos os arquivos no diretório do tipo
                for file_path in tipo_dir.rglob('*'):
                    if not file_path.is_file():
                        continue

                    # Verifica extensão
                    if file_path.suffix.lower() not in valid_extensions:
                        logger.debug(f"Controller: Arquivo ignorado (extensão inválida): {file_path}")
                        continue

                    # Registra no banco
                    file_id = self.db_manager.insert_file_record(
                        str(file_path.absolute()),
                        tipo_arquivo
                    )

                    if file_id:
                        files_in_type += 1
                        total_files += 1
                        logger.debug(f"Controller: Arquivo registrado: {file_path}")
                    else:
                        logger.warning(f"Controller: Falha ao registrar: {file_path}")

                logger.info(f"Controller: Tipo '{tipo_arquivo}' - {files_in_type} arquivos encontrados")

            logger.info(f"Controller: Scan concluído - {total_files} arquivos registrados")
            return total_files

        except Exception as e:
            logger.error(f"Controller: Erro no scan de documentos: {e}")
            return 0

    def get_processing_stats(self) -> Dict[str, int]:
        """Obtém estatísticas de processamento"""
        try:
            return self.db_manager.get_stats()
        except Exception as e:
            logger.error(f"Controller: Erro ao obter estatísticas: {e}")
            return {'pendente': 0, 'enviado': 0, 'erro': 0}

    def start_parallel_processing(self) -> Dict[str, Any]:
        """Inicia processamento paralelo com múltiplos workers"""
        try:
            logger.info(f"Controller: Iniciando processamento paralelo com {self.max_workers} workers")

            # Verifica se há arquivos para processar
            stats = self.get_processing_stats()
            if stats['pendente'] == 0:
                logger.info("Controller: Nenhum arquivo pendente para processar")
                return {
                    'success': True,
                    'message': 'Nenhum arquivo pendente',
                    'stats': stats
                }

            start_time = time.time()

            # Usa ProcessPoolExecutor para melhor controle
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                # Submete jobs para os workers
                futures = []
                for worker_id in range(self.max_workers):
                    future = executor.submit(worker_main, worker_id)
                    futures.append(future)

                # Monitora progresso
                completed_workers = 0
                worker_results = []

                for future in as_completed(futures):
                    try:
                        result = future.result()
                        worker_results.append(result)
                        completed_workers += 1

                        logger.info(f"Controller: Worker {result['worker_id']} finalizado "
                                  f"({completed_workers}/{self.max_workers}) - "
                                  f"Processados: {result['processed']}, "
                                  f"Sucessos: {result['success']}, "
                                  f"Erros: {result['errors']}")

                    except Exception as e:
                        logger.error(f"Controller: Erro em worker: {e}")

            # Calcula estatísticas finais
            total_processed = sum(r['processed'] for r in worker_results)
            total_success = sum(r['success'] for r in worker_results)
            total_errors = sum(r['errors'] for r in worker_results)

            end_time = time.time()
            processing_time = end_time - start_time

            final_stats = self.get_processing_stats()

            result = {
                'success': True,
                'total_processed': total_processed,
                'total_success': total_success,
                'total_errors': total_errors,
                'processing_time_seconds': round(processing_time, 2),
                'workers_used': self.max_workers,
                'final_stats': final_stats,
                'worker_results': worker_results
            }

            logger.info(f"Controller: Processamento paralelo concluído - "
                       f"Processados: {total_processed}, "
                       f"Sucessos: {total_success}, "
                       f"Erros: {total_errors}, "
                       f"Tempo: {processing_time:.2f}s")

            return result

        except Exception as e:
            logger.error(f"Controller: Erro no processamento paralelo: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.get_processing_stats()
            }

    def generate_report(self, output_file: str = None) -> str:
        """Gera relatório CSV/Excel dos uploads"""
        try:
            if not output_file:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"relatorio_uploads_{timestamp}.csv"

            logger.info(f"Controller: Gerando relatório: {output_file}")

            # Busca todos os registros
            records = self.db_manager.get_all_records()

            if not records:
                logger.warning("Controller: Nenhum registro encontrado para relatório")
                return None

            # Converte para DataFrame
            df = pd.DataFrame(records)

            # Adiciona colunas calculadas
            df['nome_arquivo'] = df['caminho_arquivo'].apply(lambda x: os.path.basename(x) if x else '')
            df['data_envio_formatada'] = df['data_envio'].apply(
                lambda x: x.strftime('%Y-%m-%d %H:%M:%S') if x else ''
            )

            # Reordena colunas
            column_order = [
                'nome_arquivo',
                'caminho_arquivo',
                'tipo_arquivo',
                'status',
                'data_envio_formatada',
                'mensagem_erro'
            ]

            df_report = df[column_order].copy()
            df_report.columns = [
                'Nome do Arquivo',
                'Caminho Completo',
                'Tipo de Documento',
                'Status',
                'Data/Hora Envio',
                'Mensagem de Erro'
            ]

            # Salva relatório
            if output_file.endswith('.xlsx'):
                df_report.to_excel(output_file, index=False, engine='openpyxl')
            else:
                df_report.to_csv(output_file, index=False, encoding='utf-8-sig')

            # Adiciona estatísticas no final (apenas para CSV)
            if output_file.endswith('.csv'):
                stats = self.get_processing_stats()
                with open(output_file, 'a', encoding='utf-8-sig') as f:
                    f.write('\n\n# ESTATÍSTICAS\n')
                    f.write(f'Total de Arquivos,{sum(stats.values())}\n')
                    f.write(f'Enviados com Sucesso,{stats.get("enviado", 0)}\n')
                    f.write(f'Arquivos com Erro,{stats.get("erro", 0)}\n')
                    f.write(f'Pendentes,{stats.get("pendente", 0)}\n')
                    f.write(f'Relatório Gerado em,{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')

            logger.info(f"Controller: Relatório gerado com sucesso: {output_file}")
            logger.info(f"Controller: Total de registros: {len(records)}")

            return output_file

        except Exception as e:
            logger.error(f"Controller: Erro ao gerar relatório: {e}")
            return None

    def monitor_progress(self, update_interval: int = 30):
        """Monitora progresso em tempo real"""
        try:
            logger.info("Controller: Iniciando monitoramento de progresso")

            while True:
                stats = self.get_processing_stats()
                total = sum(stats.values())

                if total == 0:
                    logger.info("Controller: Nenhum arquivo para monitorar")
                    break

                pending = stats.get('pendente', 0)
                success = stats.get('enviado', 0)
                errors = stats.get('erro', 0)

                progress_pct = ((success + errors) / total * 100) if total > 0 else 0

                logger.info(f"Controller: Progresso - {progress_pct:.1f}% "
                           f"({success + errors}/{total}) - "
                           f"Sucessos: {success}, Erros: {errors}, Pendentes: {pending}")

                if pending == 0:
                    logger.info("Controller: Todos os arquivos foram processados")
                    break

                time.sleep(update_interval)

        except KeyboardInterrupt:
            logger.info("Controller: Monitoramento interrompido pelo usuário")
        except Exception as e:
            logger.error(f"Controller: Erro no monitoramento: {e}")

    def cleanup(self):
        """Limpa recursos do controller"""
        try:
            if self.db_manager:
                self.db_manager.disconnect()
            logger.info("Controller: Cleanup concluído")
        except Exception as e:
            logger.warning(f"Controller: Erro no cleanup: {e}")


def run_controller(max_workers: int = 5, documents_path: str = None, force_rescan: bool = False) -> Dict[str, Any]:
    """Função principal para executar o controller"""
    # Define o caminho dos documentos se fornecido
    if documents_path:
        os.environ['DOCUMENTS_BASE_PATH'] = documents_path

    controller = UploadController(max_workers=max_workers)

    try:
        # Setup inicial
        if not controller.setup():
            return {'success': False, 'error': 'Falha no setup do controller'}

        # Escaneia documentos
        files_found = controller.scan_documents(force_rescan=force_rescan)
        if files_found == 0:
            return {
                'success': True,
                'message': 'Nenhum documento encontrado para processar',
                'files_found': 0
            }

        # Inicia processamento paralelo
        result = controller.start_parallel_processing()

        # Gera relatório
        report_file = controller.generate_report()
        if report_file:
            result['report_file'] = report_file

        return result

    except Exception as e:
        logger.error(f"Erro na execução do controller: {e}")
        return {'success': False, 'error': str(e)}
    finally:
        controller.cleanup()