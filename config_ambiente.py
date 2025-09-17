#!/usr/bin/env python3
"""
Configurador de ambiente para o bot
Facilita setup em diferentes sistemas
"""

import os
import sys
import subprocess
from pathlib import Path

def detectar_sistema():
    """Detecta o sistema operacional"""
    if sys.platform.startswith('linux'):
        return 'linux'
    elif sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('darwin'):
        return 'macos'
    else:
        return 'unknown'

def verificar_dependencias():
    """Verifica se dependências estão instaladas"""
    dependencias = {
        'python': ['python3', '--version'],
        'pip': ['pip3', '--version'],
        'mysql': ['mysql', '--version'],
        'git': ['git', '--version']
    }

    resultados = {}

    for nome, comando in dependencias.items():
        try:
            resultado = subprocess.run(comando, capture_output=True, text=True, timeout=5)
            if resultado.returncode == 0:
                versao = resultado.stdout.strip().split('\n')[0]
                resultados[nome] = {'status': '✅', 'versao': versao}
            else:
                resultados[nome] = {'status': '❌', 'versao': 'Não encontrado'}
        except:
            resultados[nome] = {'status': '❌', 'versao': 'Erro ao verificar'}

    return resultados

def configurar_ambiente_virtual():
    """Configura ambiente virtual Python"""
    venv_path = Path('venv')

    if venv_path.exists():
        print("✅ Ambiente virtual já existe")
        return True

    try:
        print("📦 Criando ambiente virtual...")
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Ambiente virtual criado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao criar ambiente virtual: {e}")
        return False

def instalar_dependencias():
    """Instala dependências Python"""
    venv_python = './venv/bin/python' if os.name != 'nt' else './venv/Scripts/python.exe'
    venv_pip = './venv/bin/pip' if os.name != 'nt' else './venv/Scripts/pip.exe'

    try:
        print("📚 Instalando dependências Python...")
        subprocess.run([venv_pip, 'install', '-r', 'requirements.txt'], check=True)

        print("🎭 Instalando Playwright browsers...")
        subprocess.run([venv_python, '-m', 'playwright', 'install', 'chromium'], check=True)

        print("✅ Dependências instaladas")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def configurar_modo_visual():
    """Configura ambiente para modo visual"""
    sistema = detectar_sistema()

    if sistema == 'linux':
        # Verifica se está no WSL
        try:
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    print("🐧 WSL detectado - configurando X11...")
                    os.environ['DISPLAY'] = ':0'
                    print("   💡 Certifique-se de ter um X server rodando no Windows")
                    print("   💡 Recomendado: VcXsrv ou Xming")
        except:
            pass

        # Verifica dependências gráficas
        try:
            subprocess.run(['dpkg', '-l', 'xvfb'], capture_output=True, check=True)
            print("✅ Dependências gráficas OK")
        except:
            print("⚠️  Instale dependências gráficas: sudo apt install xvfb")

    elif sistema == 'windows':
        print("🪟 Windows detectado - modo visual deveria funcionar nativamente")

    return True

def criar_estrutura_diretorios():
    """Cria estrutura de diretórios necessária"""
    diretorios = [
        'documentos/atestados',
        'documentos/prontuarios',
        'documentos/exames',
        'logs',
        'screenshots'
    ]

    for diretorio in diretorios:
        Path(diretorio).mkdir(parents=True, exist_ok=True)

    print("✅ Estrutura de diretórios criada")

def verificar_configuracao():
    """Verifica se configuração está completa"""
    env_file = Path('.env')

    if not env_file.exists():
        print("⚠️  Arquivo .env não encontrado")
        print("   Copie .env.example para .env e configure suas credenciais")
        return False

    # Verifica variáveis essenciais
    from dotenv import load_dotenv
    load_dotenv()

    vars_essenciais = ['DB_USER', 'DB_PASS', 'SITE_USER', 'SITE_PASS']
    vars_faltando = []

    for var in vars_essenciais:
        if not os.getenv(var):
            vars_faltando.append(var)

    if vars_faltando:
        print(f"⚠️  Variáveis não configuradas: {', '.join(vars_faltando)}")
        return False

    print("✅ Configuração do .env OK")
    return True

def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🔧 CONFIGURADOR DE AMBIENTE                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    sistema = detectar_sistema()
    print(f"🖥️  Sistema: {sistema.title()}")

    # 1. Verificar dependências
    print("\n1️⃣ Verificando dependências do sistema...")
    deps = verificar_dependencias()
    for nome, info in deps.items():
        print(f"   {info['status']} {nome}: {info['versao']}")

    # 2. Configurar ambiente virtual
    print("\n2️⃣ Configurando ambiente virtual...")
    if not configurar_ambiente_virtual():
        return 1

    # 3. Instalar dependências
    print("\n3️⃣ Instalando dependências...")
    if not instalar_dependencias():
        return 1

    # 4. Criar estrutura
    print("\n4️⃣ Criando estrutura de diretórios...")
    criar_estrutura_diretorios()

    # 5. Configurar modo visual
    print("\n5️⃣ Configurando modo visual...")
    configurar_modo_visual()

    # 6. Verificar configuração
    print("\n6️⃣ Verificando configuração...")
    config_ok = verificar_configuracao()

    # Relatório final
    print(f"\n{'='*60}")
    print("📋 RELATÓRIO FINAL")
    print(f"{'='*60}")

    if all(info['status'] == '✅' for info in deps.values()) and config_ok:
        print("🎉 AMBIENTE CONFIGURADO COM SUCESSO!")
        print("\n📚 Próximos passos:")
        print("   1. Configure credenciais no arquivo .env")
        print("   2. Execute: python teste_rapido.py")
        print("   3. Teste visual: python teste_visual_ged.py")
        print("   4. Processamento: python main.py")
        return 0
    else:
        print("⚠️  CONFIGURAÇÃO INCOMPLETA")
        print("\n🔧 Problemas encontrados:")

        for nome, info in deps.items():
            if info['status'] == '❌':
                print(f"   - {nome}: {info['versao']}")

        if not config_ok:
            print("   - Configuração do .env incompleta")

        print("\n💡 Consulte o GUIA_COMPLETO.md para mais detalhes")
        return 1

if __name__ == '__main__':
    sys.exit(main())