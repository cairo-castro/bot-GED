"""
Script principal para automação de upload de documentos médicos
Robô completo para upload paralelo de documentos em site Laravel
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Importa módulos do projeto
from controller import run_controller
from db import get_db_manager


def setup_logging(log_level: str = 'INFO', log_to_file: bool = True) -> None:
    """Configura sistema de logging"""

    # Cria diretório de logs se não existir
    os.makedirs('logs', exist_ok=True)

    # Define formato dos logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Lista de handlers
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_to_file:
        handlers.append(logging.FileHandler('logs/main.log', encoding='utf-8'))

    # Configura logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers,
        force=True
    )

    # Configura níveis específicos para bibliotecas externas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)


def validate_environment() -> Dict[str, Any]:
    """Valida configurações de ambiente"""
    errors = []
    warnings = []

    # Variáveis obrigatórias
    required_vars = [
        'DB_HOST',
        'DB_USER',
        'DB_PASS',
        'DB_NAME',
        'SITE_USER',
        'SITE_PASS'
    ]

    for var in required_vars:
        if not os.getenv(var):
            errors.append(f"Variável de ambiente obrigatória não encontrada: {var}")

    # Variáveis opcionais com valores padrão
    optional_vars = {
        'SITE_BASE_URL': 'https://example.com',
        'DOCUMENTS_BASE_PATH': './documentos',
        'MAX_WORKERS': '5'
    }

    for var, default in optional_vars.items():
        if not os.getenv(var):
            warnings.append(f"Variável '{var}' não definida, usando valor padrão: {default}")
            os.environ[var] = default

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def test_database_connection() -> bool:
    """Testa conexão com o banco de dados"""
    try:
        logging.info("Testando conexão com banco de dados...")

        db_manager = get_db_manager()
        if not db_manager.connect():
            logging.error("Falha ao conectar com banco de dados")
            return False

        # Testa criação de tabela
        if not db_manager.create_table():
            logging.error("Falha ao criar/verificar tabela")
            return False

        # Testa operação básica
        stats = db_manager.get_stats()
        logging.info(f"Conexão com banco OK - Estatísticas atuais: {stats}")

        db_manager.disconnect()
        return True

    except Exception as e:
        logging.error(f"Erro ao testar conexão com banco: {e}")
        return False


def check_documents_directory(documents_path: str) -> Dict[str, Any]:
    """Verifica diretório de documentos"""
    try:
        path = Path(documents_path)

        if not path.exists():
            return {
                'valid': False,
                'error': f"Diretório de documentos não encontrado: {documents_path}"
            }

        if not path.is_dir():
            return {
                'valid': False,
                'error': f"Caminho especificado não é um diretório: {documents_path}"
            }

        # Conta subdiretórios (tipos de documento)
        subdirs = [d for d in path.iterdir() if d.is_dir()]

        if not subdirs:
            return {
                'valid': False,
                'error': f"Nenhum subdiretório encontrado em: {documents_path}"
            }

        # Conta arquivos por tipo
        file_counts = {}
        valid_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.dcm'}

        for subdir in subdirs:
            files = [f for f in subdir.rglob('*') if f.is_file() and f.suffix.lower() in valid_extensions]
            file_counts[subdir.name] = len(files)

        return {
            'valid': True,
            'subdirectories': [d.name for d in subdirs],
            'file_counts': file_counts,
            'total_files': sum(file_counts.values())
        }

    except Exception as e:
        return {
            'valid': False,
            'error': f"Erro ao verificar diretório: {e}"
        }


def print_banner():
    """Exibe banner do aplicativo"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🏥 ROBÔ DE UPLOAD DE DOCUMENTOS                ║
║                        MÉDICOS AUTOMÁTICO                    ║
║                                                              ║
║  • Processamento paralelo com múltiplos workers             ║
║  • Suporte a diferentes tipos de documentos                 ║
║  • Retry automático com backoff exponencial                 ║
║  • Relatórios detalhados em CSV/Excel                       ║
║  • Logging completo e screenshots de erro                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def main():
    """Função principal"""

    # Exibe banner
    print_banner()

    # Configura argumentos da linha de comando
    parser = argparse.ArgumentParser(
        description='Robô para upload automático de documentos médicos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py --documents ./meus_documentos --workers 3
  python main.py --test-only
  python main.py --force-rescan --workers 5 --log-level DEBUG
        """
    )

    parser.add_argument(
        '--documents', '-d',
        type=str,
        default=None,
        help='Caminho para diretório com documentos (padrão: ./documentos)'
    )

    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=5,
        help='Número de workers paralelos (padrão: 5)'
    )

    parser.add_argument(
        '--force-rescan',
        action='store_true',
        help='Força nova varredura de documentos (limpa registros pendentes)'
    )

    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Apenas testa configurações e conexões (não processa documentos)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Nível de logging (padrão: INFO)'
    )

    parser.add_argument(
        '--no-log-file',
        action='store_true',
        help='Não salva logs em arquivo'
    )

    args = parser.parse_args()

    # Configura logging
    setup_logging(args.log_level, not args.no_log_file)

    logger = logging.getLogger(__name__)
    logger.info("=== INICIANDO ROBÔ DE UPLOAD DE DOCUMENTOS ===")

    try:
        # 1. Validação do ambiente
        logger.info("1. Validando configurações de ambiente...")
        env_validation = validate_environment()

        if not env_validation['valid']:
            logger.error("❌ Erro nas configurações de ambiente:")
            for error in env_validation['errors']:
                logger.error(f"   • {error}")
            logger.info("\n💡 Verifique o arquivo .env com as configurações necessárias")
            return 1

        # Exibe warnings se houver
        for warning in env_validation['warnings']:
            logger.warning(f"⚠️  {warning}")

        logger.info("✅ Configurações de ambiente OK")

        # 2. Teste de conexão com banco
        logger.info("2. Testando conexão com banco de dados...")
        if not test_database_connection():
            logger.error("❌ Falha na conexão com banco de dados")
            return 1

        logger.info("✅ Conexão com banco de dados OK")

        # 3. Verificação do diretório de documentos
        documents_path = args.documents or os.getenv('DOCUMENTS_BASE_PATH', './documentos')
        logger.info(f"3. Verificando diretório de documentos: {documents_path}")

        docs_check = check_documents_directory(documents_path)

        if not docs_check['valid']:
            logger.error(f"❌ {docs_check['error']}")
            logger.info("\n💡 Organize seus documentos da seguinte forma:")
            logger.info("   documentos/")
            logger.info("   ├── atestados/")
            logger.info("   │   ├── documento1.pdf")
            logger.info("   │   └── documento2.jpg")
            logger.info("   ├── prontuarios/")
            logger.info("   │   └── prontuario1.pdf")
            logger.info("   └── exames/")
            logger.info("       └── exame1.pdf")
            return 1

        logger.info("✅ Diretório de documentos OK")
        logger.info(f"   • Tipos encontrados: {', '.join(docs_check['subdirectories'])}")
        logger.info(f"   • Total de arquivos: {docs_check['total_files']}")

        for tipo, count in docs_check['file_counts'].items():
            logger.info(f"     - {tipo}: {count} arquivos")

        # Se é apenas teste, para aqui
        if args.test_only:
            logger.info("🧪 Modo teste concluído - todas as verificações passaram!")
            logger.info("   Execute sem --test-only para iniciar o processamento")
            return 0

        # 4. Processamento principal
        logger.info(f"4. Iniciando processamento com {args.workers} workers...")

        result = run_controller(
            max_workers=args.workers,
            documents_path=documents_path,
            force_rescan=args.force_rescan
        )

        if not result['success']:
            logger.error(f"❌ Erro no processamento: {result.get('error', 'Erro desconhecido')}")
            return 1

        # 5. Exibir resultados
        logger.info("🎉 PROCESSAMENTO CONCLUÍDO!")

        if 'total_processed' in result:
            logger.info(f"   • Total processado: {result['total_processed']} arquivos")
            logger.info(f"   • Sucessos: {result['total_success']} ✅")
            logger.info(f"   • Erros: {result['total_errors']} ❌")
            logger.info(f"   • Tempo total: {result['processing_time_seconds']}s")

            if result.get('report_file'):
                logger.info(f"   • Relatório salvo: {result['report_file']} 📊")

        # Estatísticas finais
        if 'final_stats' in result:
            stats = result['final_stats']
            logger.info(f"   • Status final: {stats['enviado']} enviados, "
                       f"{stats['erro']} com erro, {stats['pendente']} pendentes")

        logger.info("=== ROBÔ FINALIZADO COM SUCESSO ===")
        return 0

    except KeyboardInterrupt:
        logger.info("⚠️  Processamento interrompido pelo usuário")
        return 1
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())