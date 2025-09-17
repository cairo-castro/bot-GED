#!/usr/bin/env python3
"""
Teste rápido para verificar se o sistema está funcionando
"""

import os
import sys
from dotenv import load_dotenv

# Carrega configurações
load_dotenv()

def teste_imports():
    """Testa se todos os módulos estão disponíveis"""
    print("🔍 Testando imports...")

    try:
        import mysql.connector
        print("✅ MySQL Connector")
    except ImportError:
        print("❌ MySQL Connector não encontrado")
        return False

    try:
        import playwright
        print("✅ Playwright")
    except ImportError:
        print("❌ Playwright não encontrado")
        return False

    try:
        import pandas
        print("✅ Pandas")
    except ImportError:
        print("❌ Pandas não encontrado")
        return False

    print("✅ Todos os imports OK\n")
    return True

def teste_configuracao():
    """Testa se as configurações estão corretas"""
    print("⚙️  Testando configuração...")

    vars_obrigatorias = ['DB_HOST', 'DB_USER', 'DB_PASS', 'DB_NAME']
    vars_faltando = []

    for var in vars_obrigatorias:
        if not os.getenv(var):
            vars_faltando.append(var)

    if vars_faltando:
        print(f"❌ Variáveis faltando: {', '.join(vars_faltando)}")
        return False

    print("✅ Configuração OK\n")
    return True

def teste_banco():
    """Testa conexão com banco de dados"""
    print("🗄️  Testando banco de dados...")

    try:
        import mysql.connector

        config = {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASS'),
            'database': os.getenv('DB_NAME')
        }

        conexao = mysql.connector.connect(**config)
        cursor = conexao.cursor()
        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()

        if resultado[0] == 1:
            print("✅ Conexão com banco OK")

            # Testa se a tabela pode ser criada
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploads (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    caminho_arquivo TEXT NOT NULL,
                    tipo_arquivo VARCHAR(100) NOT NULL,
                    status ENUM('pendente','enviado','erro') DEFAULT 'pendente',
                    data_envio DATETIME NULL,
                    mensagem_erro TEXT NULL
                )
            """)
            print("✅ Tabela criada/verificada")

            cursor.close()
            conexao.close()
            print("✅ Teste de banco OK\n")
            return True

    except Exception as e:
        print(f"❌ Erro no banco: {e}")
        print("\n💡 Execute o setup do banco:")
        print("   Veja o arquivo CONFIGURAR_BANCO.md")
        return False

def teste_estrutura():
    """Testa estrutura de diretórios"""
    print("📁 Testando estrutura de diretórios...")

    docs_path = os.getenv('DOCUMENTS_BASE_PATH', './documentos')

    if not os.path.exists(docs_path):
        print(f"❌ Diretório de documentos não existe: {docs_path}")
        return False

    subdirs = ['atestados', 'prontuarios', 'exames']
    for subdir in subdirs:
        path = os.path.join(docs_path, subdir)
        if os.path.exists(path):
            print(f"✅ {subdir}/")
        else:
            print(f"⚠️  {subdir}/ não existe (será criado se necessário)")

    print("✅ Estrutura OK\n")
    return True

def main():
    """Executa todos os testes"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🧪 TESTE RÁPIDO DO SISTEMA                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    testes = [
        ("Imports", teste_imports),
        ("Configuração", teste_configuracao),
        ("Banco de Dados", teste_banco),
        ("Estrutura", teste_estrutura)
    ]

    sucessos = 0
    total = len(testes)

    for nome, teste in testes:
        print(f"🔍 {nome}...")
        if teste():
            sucessos += 1
        print("-" * 60)

    print(f"\n📊 RESULTADO: {sucessos}/{total} testes passaram")

    if sucessos == total:
        print("🎉 SISTEMA PRONTO! Você pode executar:")
        print("   python main.py --test-only")
        print("   python main.py")
        return 0
    else:
        print("⚠️  Configure os itens que falharam antes de usar o sistema")
        return 1

if __name__ == '__main__':
    sys.exit(main())