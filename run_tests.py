"""
Script de testes para validar funcionamento do sistema
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Carrega ambiente
load_dotenv()

# Importa módulos do projeto
from db import get_db_manager
from utils import ConfigValidator, FileUtils, PerformanceMonitor
from flows.base_flow import BaseFlow


def setup_test_logging():
    """Configura logging para testes"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - TEST - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def test_database_connection():
    """Testa conexão e operações básicas do banco"""
    print("\n🗄️  Testando conexão com banco de dados...")

    try:
        db_manager = get_db_manager()

        # Testa conexão
        if not db_manager.connect():
            print("❌ Falha ao conectar com banco")
            return False

        print("✅ Conexão estabelecida")

        # Testa criação de tabela
        if not db_manager.create_table():
            print("❌ Falha ao criar tabela")
            return False

        print("✅ Tabela criada/verificada")

        # Testa operações básicas
        test_file_id = db_manager.insert_file_record('/test/file.pdf', 'test')
        if not test_file_id:
            print("❌ Falha ao inserir registro de teste")
            return False

        print("✅ Inserção de registro OK")

        # Testa busca
        pending = db_manager.get_pending_files(1)
        if not pending:
            print("❌ Falha ao buscar registros pendentes")
            return False

        print("✅ Busca de registros OK")

        # Testa atualização
        if not db_manager.update_file_status(test_file_id, 'enviado'):
            print("❌ Falha ao atualizar status")
            return False

        print("✅ Atualização de status OK")

        # Testa estatísticas
        stats = db_manager.get_stats()
        if not isinstance(stats, dict):
            print("❌ Falha ao obter estatísticas")
            return False

        print(f"✅ Estatísticas OK: {stats}")

        # Limpa teste
        db_manager.connection.cursor().execute("DELETE FROM uploads WHERE id = %s", (test_file_id,))
        print("✅ Registro de teste removido")

        db_manager.disconnect()
        print("✅ Teste de banco de dados passou")
        return True

    except Exception as e:
        print(f"❌ Erro no teste de banco: {e}")
        return False


def test_configuration_validation():
    """Testa validação de configurações"""
    print("\n⚙️  Testando validação de configurações...")

    try:
        # Testa validação do banco
        db_config = ConfigValidator.validate_database_config()
        if db_config['valid']:
            print("✅ Configuração do banco válida")
        else:
            print(f"⚠️  Configuração do banco incompleta: {db_config['missing_variables']}")

        # Testa validação do site
        site_config = ConfigValidator.validate_site_config()
        if site_config['valid']:
            print("✅ Configuração do site válida")
        else:
            print(f"⚠️  Configuração do site incompleta: {site_config['missing_required']}")

        # Testa validação de caminhos
        paths_config = ConfigValidator.validate_paths()
        if paths_config['valid']:
            print("✅ Configuração de caminhos válida")
        else:
            print(f"⚠️  Problemas nos caminhos: {paths_config['issues']}")

        print("✅ Teste de configuração passou")
        return True

    except Exception as e:
        print(f"❌ Erro no teste de configuração: {e}")
        return False


def test_file_utilities():
    """Testa utilitários de arquivo"""
    print("\n📁 Testando utilitários de arquivo...")

    try:
        # Cria arquivo temporário para teste
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b"PDF test content")
            temp_path = temp_file.name

        # Testa validação de arquivo
        if FileUtils.is_valid_document_file(temp_path):
            print("✅ Validação de arquivo OK")
        else:
            print("❌ Falha na validação de arquivo")
            return False

        # Testa tamanho do arquivo
        size = FileUtils.get_file_size(temp_path)
        if size > 0:
            print(f"✅ Tamanho do arquivo OK: {size} bytes")
        else:
            print("❌ Erro ao obter tamanho do arquivo")
            return False

        # Testa hash do arquivo
        file_hash = FileUtils.get_file_hash(temp_path)
        if file_hash:
            print(f"✅ Hash do arquivo OK: {file_hash[:8]}...")
        else:
            print("❌ Erro ao calcular hash do arquivo")
            return False

        # Testa limpeza de nome de arquivo
        dirty_name = "arquivo<>test?.pdf"
        clean_name = FileUtils.clean_filename(dirty_name)
        if clean_name == "arquivo__test_.pdf":
            print("✅ Limpeza de nome OK")
        else:
            print(f"❌ Limpeza de nome falhou: {clean_name}")
            return False

        # Remove arquivo temporário
        os.unlink(temp_path)

        print("✅ Teste de utilitários passou")
        return True

    except Exception as e:
        print(f"❌ Erro no teste de utilitários: {e}")
        return False


def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n📦 Testando imports de módulos...")

    modules_to_test = [
        ('playwright.sync_api', 'Playwright'),
        ('mysql.connector', 'MySQL Connector'),
        ('pandas', 'Pandas'),
        ('dotenv', 'Python Dotenv'),
    ]

    all_imports_ok = True

    for module_name, friendly_name in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ {friendly_name}")
        except ImportError as e:
            print(f"❌ {friendly_name}: {e}")
            all_imports_ok = False

    # Testa imports do projeto
    project_modules = [
        'db',
        'worker',
        'controller',
        'utils',
        'flows'
    ]

    for module_name in project_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name}")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
            all_imports_ok = False

    if all_imports_ok:
        print("✅ Todos os imports passaram")
        return True
    else:
        print("❌ Alguns imports falharam")
        return False


def test_performance_monitor():
    """Testa monitor de performance"""
    print("\n📊 Testando monitor de performance...")

    try:
        monitor = PerformanceMonitor()
        monitor.start()

        # Simula alguns checkpoints
        import time
        monitor.checkpoint("inicio")
        time.sleep(0.1)
        monitor.checkpoint("meio")
        time.sleep(0.1)
        monitor.checkpoint("fim")

        summary = monitor.get_summary()

        if summary and 'total_execution_time' in summary:
            print("✅ Monitor de performance OK")
            print(f"   Tempo total: {summary['total_execution_time']}")
            print(f"   Checkpoints: {len(summary['checkpoints'])}")
            return True
        else:
            print("❌ Erro no monitor de performance")
            return False

    except Exception as e:
        print(f"❌ Erro no teste de performance: {e}")
        return False


def run_all_tests():
    """Executa todos os testes"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🧪 TESTES DO SISTEMA DE UPLOAD                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    setup_test_logging()

    tests = [
        ("Imports de Módulos", test_imports),
        ("Configurações", test_configuration_validation),
        ("Utilitários de Arquivo", test_file_utilities),
        ("Monitor de Performance", test_performance_monitor),
        ("Banco de Dados", test_database_connection),  # Por último pois pode falhar se DB não configurado
    ]

    results = []
    passed = 0
    total = len(tests)

    for test_name, test_function in tests:
        print(f"\n{'='*60}")
        print(f"🔍 EXECUTANDO: {test_name}")
        print('='*60)

        try:
            result = test_function()
            results.append((test_name, result))
            if result:
                passed += 1
                print(f"✅ {test_name}: PASSOU")
            else:
                print(f"❌ {test_name}: FALHOU")
        except Exception as e:
            print(f"❌ {test_name}: ERRO - {e}")
            results.append((test_name, False))

    # Relatório final
    print(f"\n{'='*60}")
    print("📋 RELATÓRIO FINAL DOS TESTES")
    print('='*60)

    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status:<12} {test_name}")

    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")

    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
        return 0
    else:
        print("⚠️  ALGUNS TESTES FALHARAM. Verifique as configurações antes de usar o sistema.")
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())