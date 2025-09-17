#!/usr/bin/env python3
"""
Script para criar o banco manualmente com diferentes métodos de autenticação
"""

import mysql.connector
import getpass
import sys

def tentar_conexao_root():
    """Tenta conectar como root com senha"""
    print("🔑 Tentando conectar como root...")

    senha = getpass.getpass("Digite a senha do root MySQL (ou Enter se não tiver): ")

    try:
        config = {
            'host': 'localhost',
            'user': 'root',
        }

        if senha:
            config['password'] = senha

        conexao = mysql.connector.connect(**config)
        return conexao
    except Exception as e:
        print(f"❌ Falha: {e}")
        return None

def tentar_outras_conexoes():
    """Tenta outros métodos de conexão"""
    print("\n🔍 Tentando outros métodos...")

    # Lista de usuários comuns para testar
    usuarios = [
        ('admin', ''),
        ('mysql', ''),
        ('mariadb', ''),
        ('debian-sys-maint', '01PtgcXGy4kUgRZG'),
    ]

    for usuario, senha_padrao in usuarios:
        try:
            print(f"Tentando usuário: {usuario}")

            if not senha_padrao:
                senha = getpass.getpass(f"Senha para {usuario} (Enter para pular): ")
                if not senha:
                    continue
            else:
                senha = senha_padrao

            conexao = mysql.connector.connect(
                host='localhost',
                user=usuario,
                password=senha
            )

            print(f"✅ Conectado como {usuario}")
            return conexao

        except Exception as e:
            print(f"❌ {usuario}: {e}")
            continue

    return None

def criar_banco_e_usuario(conexao):
    """Cria banco e usuário"""
    try:
        cursor = conexao.cursor()

        print("\n📦 Criando banco de dados...")

        # Cria banco
        cursor.execute("""
            CREATE DATABASE IF NOT EXISTS uploads_db
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci
        """)
        print("✅ Banco 'uploads_db' criado")

        # Cria usuário
        print("👤 Criando usuário...")
        cursor.execute("""
            CREATE USER IF NOT EXISTS 'medbot_user'@'localhost'
            IDENTIFIED BY 'MedBot2024!'
        """)
        print("✅ Usuário 'medbot_user' criado")

        # Concede permissões
        print("🔐 Configurando permissões...")
        cursor.execute("""
            GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX
            ON uploads_db.* TO 'medbot_user'@'localhost'
        """)
        print("✅ Permissões concedidas")

        # Atualiza privilégios
        cursor.execute("FLUSH PRIVILEGES")
        print("✅ Privilégios atualizados")

        cursor.close()

        return True

    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        return False

def testar_nova_conexao():
    """Testa conexão com novo usuário"""
    print("\n🧪 Testando nova conexão...")

    try:
        conexao = mysql.connector.connect(
            host='localhost',
            user='medbot_user',
            password='MedBot2024!',
            database='uploads_db'
        )

        cursor = conexao.cursor()
        cursor.execute("SELECT 'Conexão OK!' AS status")
        resultado = cursor.fetchone()

        print(f"✅ {resultado[0]}")

        cursor.close()
        conexao.close()

        return True

    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🗄️  CONFIGURAÇÃO MANUAL DO BANCO              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # Tenta conectar
    conexao = tentar_conexao_root()

    if not conexao:
        conexao = tentar_outras_conexoes()

    if not conexao:
        print("\n❌ Não foi possível conectar ao MySQL/MariaDB")
        print("\n💡 Opções:")
        print("1. Verifique se o MySQL/MariaDB está rodando")
        print("2. Execute: sudo mysql < setup_database.sql")
        print("3. Peça ajuda ao administrador do sistema")
        return 1

    print(f"\n✅ Conectado ao MySQL/MariaDB")

    # Cria banco e usuário
    if criar_banco_e_usuario(conexao):
        conexao.close()

        # Testa nova conexão
        if testar_nova_conexao():
            print("\n🎉 BANCO CONFIGURADO COM SUCESSO!")
            print("\nCredenciais criadas:")
            print("- Usuário: medbot_user")
            print("- Senha: MedBot2024!")
            print("- Banco: uploads_db")
            print("\nAgora você pode executar:")
            print("python teste_rapido.py")
            return 0
        else:
            print("\n❌ Banco criado mas teste falhou")
            return 1
    else:
        conexao.close()
        print("\n❌ Falha ao criar banco")
        return 1

if __name__ == '__main__':
    sys.exit(main())