#!/usr/bin/env python3
"""
Teste visual do fluxo GED - Bot em ação visível
Permite ver o navegador funcionando em tempo real
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime

# Carrega configurações
load_dotenv()

def teste_visual_ged(headless=False, slow_mo=1000):
    """
    Testa o fluxo completo de forma visual

    Args:
        headless (bool): False para mostrar navegador, True para headless
        slow_mo (int): Atraso em ms entre ações (para visualização)
    """

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    print(f"🌐 Site: {site_url}")
    print(f"👤 Usuário: {usuario}")
    print(f"👁️  Modo visual: {'SIM' if not headless else 'NÃO'}")
    print(f"⏱️  Velocidade: {slow_mo}ms entre ações")
    print()

    with sync_playwright() as p:
        try:
            # Configurações do browser
            print("🚀 Iniciando browser...")

            browser_args = [
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]

            # Remove --no-sandbox apenas se não for headless (para melhor compatibilidade visual)
            if headless:
                browser_args.append('--no-sandbox')

            browser = p.chromium.launch(
                headless=headless,
                slow_mo=slow_mo,  # Atraso entre ações para visualização
                args=browser_args
            )

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # PASSO 1: Login
            print("🔐 PASSO 1: Fazendo login...")
            page.goto(f"{site_url}/login", wait_until="networkidle", timeout=30000)

            print("   📝 Preenchendo usuário...")
            page.locator('#usuario').highlight()  # Destaca o elemento
            page.locator('#usuario').fill(usuario)

            print("   🔑 Preenchendo senha...")
            page.locator('#password').highlight()
            page.locator('#password').fill(senha)

            print("   🖱️  Clicando em Entrar...")
            with page.expect_navigation(wait_until="networkidle", timeout=30000):
                page.locator('input[type="submit"][value="Entrar"]').highlight()
                page.locator('input[type="submit"][value="Entrar"]').click()

            # Verifica se login foi bem-sucedido
            if '/login' in page.url:
                print("❌ Falha no login")
                return False

            print("✅ Login realizado com sucesso!")

            # PASSO 2: Navegar para GED
            print("\n📁 PASSO 2: Navegando para GED...")
            ged_url = f"{site_url}/ged"
            page.goto(ged_url, wait_until="networkidle", timeout=30000)
            print("✅ Página GED carregada!")

            # PASSO 3: Clicar em Nova Solicitação
            print("\n🔍 PASSO 3: Procurando botão Nova Solicitação...")
            botao_nova_solicitacao = page.locator('#btnNovaSolicitacao')

            if botao_nova_solicitacao.count() == 0:
                print("❌ Botão não encontrado")
                return False

            print("✅ Botão encontrado!")
            print("🖱️  Clicando no botão...")

            # Destaca e clica no botão
            botao_nova_solicitacao.highlight()
            botao_nova_solicitacao.click()

            # Aguarda modal abrir
            time.sleep(2)

            # Verifica se modal abriu
            modal = page.locator('.modal, [role="dialog"]').first
            if modal.is_visible():
                print("✅ Modal de Nova Solicitação aberto!")

                # Destaca elementos do formulário
                print("\n📋 PASSO 4: Destacando campos do formulário...")

                campos = [
                    ('input[name="titulo"], input:has-text("Digite o título")', 'Campo Título'),
                    ('select, .dropdown', 'Dropdowns'),
                    ('textarea', 'Campo Justificativa'),
                    ('button:has-text("Salvar"), .btn-success', 'Botão Salvar')
                ]

                for seletor, nome in campos:
                    try:
                        elemento = page.locator(seletor).first
                        if elemento.is_visible():
                            print(f"   ✅ {nome} encontrado")
                            elemento.highlight()
                            time.sleep(1)  # Pausa para visualização
                    except:
                        print(f"   ⚠️  {nome} não encontrado")

            print("\n🎉 Fluxo visual concluído!")
            print("   O modal está aberto e pronto para preenchimento")

            if not headless:
                print("\n⏳ Mantendo navegador aberto para visualização...")
                print("   Pressione Ctrl+C para fechar")
                try:
                    # Mantém o navegador aberto para visualização
                    time.sleep(60)  # 1 minuto
                except KeyboardInterrupt:
                    print("\n👋 Fechando navegador...")

            return True

        except KeyboardInterrupt:
            print("\n👋 Teste interrompido pelo usuário")
            return True

        except Exception as e:
            print(f"❌ Erro durante teste: {e}")
            return False

        finally:
            # Fecha browser de forma segura
            try:
                if not headless:
                    print("🔒 Fechando browser...")

                # Fecha contexto primeiro
                if 'context' in locals():
                    context.close()

                # Depois fecha browser
                if 'browser' in locals():
                    browser.close()

            except Exception as e:
                # Ignora erros de fechamento
                pass

def main():
    """Função principal com opções"""
    import argparse

    parser = argparse.ArgumentParser(description='Teste visual do bot GED')
    parser.add_argument('--headless', action='store_true', help='Executa em modo headless (sem interface)')
    parser.add_argument('--speed', type=int, default=1000, help='Velocidade em ms entre ações (padrão: 1000)')
    parser.add_argument('--fast', action='store_true', help='Execução rápida (equivale a --speed 200)')

    args = parser.parse_args()

    # Ajusta velocidade se --fast foi usado
    if args.fast:
        args.speed = 200

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               👁️  TESTE VISUAL GED EMSERH                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if args.headless:
        print("🤖 Modo: Headless (sem interface)")
    else:
        print("👁️  Modo: Visual (navegador visível)")
        print("💡 Dica: Use --headless para modo invisível")
        print("💡 Dica: Use --fast para execução mais rápida")
        print("💡 Dica: Use --speed 500 para personalizar velocidade")

    if teste_visual_ged(headless=args.headless, slow_mo=args.speed):
        print("\n🎉 TESTE VISUAL CONCLUÍDO COM SUCESSO!")
        return 0
    else:
        print("\n❌ TESTE VISUAL FALHOU!")
        return 1

if __name__ == '__main__':
    exit(main())