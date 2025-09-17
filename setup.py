"""
Script de setup para configuração inicial do projeto
"""

import os
import sys
import subprocess
from pathlib import Path


def create_directories():
    """Cria diretórios necessários"""
    directories = [
        'logs',
        'screenshots',
        'documentos',
        'documentos/atestados',
        'documentos/prontuarios',
        'documentos/exames'
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Diretório criado: {directory}")


def install_requirements():
    """Instala dependências do requirements.txt"""
    try:
        print("📦 Instalando dependências Python...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependências Python instaladas")

        print("🎭 Instalando browsers do Playwright...")
        subprocess.check_call([sys.executable, '-m', 'playwright', 'install', 'chromium'])
        print("✅ Browser Chromium instalado")

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro na instalação: {e}")
        return False

    return True


def create_env_file():
    """Cria arquivo .env se não existir"""
    if not os.path.exists('.env'):
        print("📝 Criando arquivo .env...")

        # Copia do exemplo
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as source:
                with open('.env', 'w') as dest:
                    dest.write(source.read())
            print("✅ Arquivo .env criado a partir do exemplo")
            print("⚠️  IMPORTANTE: Configure suas credenciais no arquivo .env antes de executar!")
        else:
            print("❌ Arquivo .env.example não encontrado")
    else:
        print("ℹ️  Arquivo .env já existe")


def setup_database_schema():
    """Exibe instruções para setup do banco"""
    print("\n🗄️  CONFIGURAÇÃO DO BANCO DE DADOS:")
    print("Execute os seguintes comandos no MariaDB/MySQL:")
    print("""
CREATE DATABASE uploads_db;
CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'sua_senha_aqui';
GRANT ALL PRIVILEGES ON uploads_db.* TO 'bot_user'@'localhost';
FLUSH PRIVILEGES;
    """)


def test_setup():
    """Testa se o setup está correto"""
    print("\n🧪 Testando configuração...")

    # Verifica se requirements foram instalados
    try:
        import playwright
        import mysql.connector
        import pandas
        from dotenv import load_dotenv
        print("✅ Módulos Python OK")
    except ImportError as e:
        print(f"❌ Módulo não encontrado: {e}")
        return False

    # Verifica arquivos essenciais
    essential_files = [
        'main.py',
        'controller.py',
        'worker.py',
        'db.py',
        'flows/__init__.py',
        '.env'
    ]

    for file in essential_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} não encontrado")
            return False

    return True


def main():
    """Setup principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🛠️  SETUP DO ROBÔ DE UPLOAD                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        # 1. Criar diretórios
        print("1. Criando estrutura de diretórios...")
        create_directories()

        # 2. Instalar dependências
        print("\n2. Instalando dependências...")
        if not install_requirements():
            print("❌ Falha na instalação de dependências")
            return 1

        # 3. Criar arquivo .env
        print("\n3. Configurando arquivo .env...")
        create_env_file()

        # 4. Instruções do banco
        setup_database_schema()

        # 5. Teste final
        if test_setup():
            print("\n🎉 SETUP CONCLUÍDO COM SUCESSO!")
            print("\n📋 PRÓXIMOS PASSOS:")
            print("1. Configure suas credenciais no arquivo .env")
            print("2. Execute os comandos SQL para criar o banco de dados")
            print("3. Organize seus documentos na pasta 'documentos/'")
            print("4. Teste com: python main.py --test-only")
            print("5. Execute com: python main.py")
            return 0
        else:
            print("\n❌ Setup incompleto, verifique os erros acima")
            return 1

    except Exception as e:
        print(f"\n❌ Erro durante setup: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())