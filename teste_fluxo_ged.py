#!/usr/bin/env python3
"""
Teste do fluxo GED - Login + Acesso GED + Nova Solicitação
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime

# Carrega configurações
load_dotenv()

def teste_fluxo_ged():
    """Testa o fluxo completo até Nova Solicitação"""

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    print(f"🌐 Site: {site_url}")
    print(f"👤 Usuário: {usuario}")
    print()

    with sync_playwright() as p:
        try:
            # Inicia browser
            print("🚀 Iniciando browser...")
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # PASSO 1: Login
            print("🔐 PASSO 1: Realizando login...")
            page.goto(f"{site_url}/login", wait_until="networkidle", timeout=30000)

            # Preenche credenciais
            page.locator('#usuario').fill(usuario)
            page.locator('#password').fill(senha)

            # Faz login
            with page.expect_navigation(wait_until="networkidle", timeout=30000):
                page.locator('input[type="submit"][value="Entrar"]').click()

            # Verifica se login foi bem-sucedido
            if '/login' in page.url:
                print("❌ Falha no login")
                return False

            print("✅ Login realizado com sucesso!")
            print(f"   URL atual: {page.url}")

            # Screenshot após login
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            os.makedirs("screenshots", exist_ok=True)

            screenshot_login = f"screenshots/01_apos_login_{timestamp}.png"
            page.screenshot(path=screenshot_login, full_page=True)
            print(f"📸 Screenshot pós-login: {screenshot_login}")

            # PASSO 2: Navegar para GED
            print("\n📁 PASSO 2: Navegando para página GED...")

            ged_url = f"{site_url}/ged"
            response = page.goto(ged_url, wait_until="networkidle", timeout=30000)

            print(f"📄 URL GED: {page.url}")
            print(f"📊 Status: {response.status}")

            if response.status != 200:
                print(f"❌ Erro ao acessar GED: Status {response.status}")
                return False

            print("✅ Página GED carregada com sucesso!")

            # Aguarda um pouco para garantir que a página carregou completamente
            time.sleep(2)

            # Screenshot da página GED
            screenshot_ged = f"screenshots/02_pagina_ged_{timestamp}.png"
            page.screenshot(path=screenshot_ged, full_page=True)
            print(f"📸 Screenshot página GED: {screenshot_ged}")

            # PASSO 3: Procurar botão Nova Solicitação
            print("\n🔍 PASSO 3: Procurando botão Nova Solicitação...")

            # Procura pelo botão específico
            botao_nova_solicitacao = page.locator('#btnNovaSolicitacao')

            # Verifica se o botão existe
            if botao_nova_solicitacao.count() == 0:
                print("❌ Botão 'Nova Solicitação' não encontrado")

                # Tenta encontrar botões similares para debug
                print("\n🔍 Debug - Procurando botões similares...")

                # Procura por diferentes variações
                botoes_alternativos = [
                    'a[title*="solicitação"]',
                    'a[title*="Solicitação"]',
                    'button[title*="solicitação"]',
                    '.btn:has-text("Nova")',
                    '.btn:has-text("Adicionar")',
                    '.fa-plus-circle',
                    '[class*="btn"]:has(.fa-plus-circle)'
                ]

                for selector in botoes_alternativos:
                    try:
                        elementos = page.locator(selector)
                        count = elementos.count()
                        if count > 0:
                            print(f"   ✅ Encontrado(s) {count} elemento(s) com seletor: {selector}")
                            for i in range(min(count, 3)):  # Mostra até 3 elementos
                                try:
                                    elemento = elementos.nth(i)
                                    texto = elemento.text_content() or "Sem texto"
                                    title = elemento.get_attribute('title') or "Sem title"
                                    print(f"      - Elemento {i+1}: '{texto}' (title: '{title}')")
                                except:
                                    pass
                    except:
                        continue

                return False

            print("✅ Botão 'Nova Solicitação' encontrado!")

            # Verifica se o botão está visível
            if not botao_nova_solicitacao.is_visible():
                print("❌ Botão 'Nova Solicitação' não está visível")
                return False

            print("✅ Botão 'Nova Solicitação' está visível!")

            # PASSO 4: Clicar no botão
            print("\n🖱️  PASSO 4: Clicando no botão Nova Solicitação...")

            try:
                # Clica no botão e aguarda possível navegação ou modal
                botao_nova_solicitacao.click()

                # Aguarda um pouco para ver se algo acontece
                time.sleep(3)

                print("✅ Clique realizado com sucesso!")
                print(f"📄 URL após clique: {page.url}")

                # Screenshot final
                screenshot_final = f"screenshots/03_apos_clique_nova_solicitacao_{timestamp}.png"
                page.screenshot(path=screenshot_final, full_page=True)
                print(f"📸 Screenshot após clique: {screenshot_final}")

                return True

            except Exception as e:
                print(f"❌ Erro ao clicar no botão: {e}")
                return False

        except Exception as e:
            print(f"❌ Erro durante teste: {e}")

            # Screenshot de erro
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_erro = f"screenshots/erro_fluxo_ged_{timestamp}.png"
                page.screenshot(path=screenshot_erro, full_page=True)
                print(f"📸 Screenshot de erro: {screenshot_erro}")
            except:
                pass

            return False

        finally:
            # Fecha browser
            try:
                browser.close()
                print("🔒 Browser fechado")
            except:
                pass

def main():
    """Função principal"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║               🧪 TESTE FLUXO GED EMSERH                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if teste_fluxo_ged():
        print("\n🎉 TESTE DO FLUXO GED PASSOU!")
        print("   O bot conseguiu:")
        print("   ✅ Fazer login")
        print("   ✅ Acessar página GED")
        print("   ✅ Encontrar botão Nova Solicitação")
        print("   ✅ Clicar no botão")
        print("\n📸 Screenshots salvos na pasta 'screenshots/'")
        return 0
    else:
        print("\n❌ TESTE DO FLUXO GED FALHOU!")
        print("   Verifique os screenshots para debug")
        return 1

if __name__ == '__main__':
    exit(main())