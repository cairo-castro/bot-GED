#!/usr/bin/env python3
"""
Teste específico para login no site GPC EMSERH
"""

import os
import asyncio
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

# Carrega configurações
load_dotenv()

def teste_login_emserh():
    """Testa login no site da EMSERH"""

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    print(f"🌐 Testando login em: {site_url}")
    print(f"👤 Usuário: {usuario}")
    print(f"🔑 Senha: {'*' * len(senha)}")
    print()

    with sync_playwright() as p:
        try:
            # Inicia browser em modo headless
            print("🚀 Iniciando browser...")
            browser = p.chromium.launch(
                headless=True,  # Modo headless
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )

            # Cria contexto com configurações
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )

            page = context.new_page()

            # Navega para a página de login
            print("📍 Navegando para página de login...")
            response = page.goto(f"{site_url}/login", wait_until="networkidle", timeout=30000)

            if response.status != 200:
                print(f"❌ Erro ao acessar página: Status {response.status}")
                return False

            print(f"✅ Página carregada com sucesso (Status: {response.status})")

            # Verifica se chegou na página correta
            current_url = page.url
            print(f"📄 URL atual: {current_url}")

            # Procura pelos elementos de login
            print("\n🔍 Procurando elementos de login...")

            # Campo usuário
            try:
                usuario_input = page.locator('#usuario')
                if usuario_input.is_visible():
                    print("✅ Campo usuário encontrado")
                else:
                    print("❌ Campo usuário não visível")
                    return False
            except Exception as e:
                print(f"❌ Campo usuário não encontrado: {e}")
                return False

            # Campo senha
            try:
                senha_input = page.locator('#password')
                if senha_input.is_visible():
                    print("✅ Campo senha encontrado")
                else:
                    print("❌ Campo senha não visível")
                    return False
            except Exception as e:
                print(f"❌ Campo senha não encontrado: {e}")
                return False

            # Botão entrar
            try:
                botao_entrar = page.locator('input[type="submit"][value="Entrar"]')
                if botao_entrar.is_visible():
                    print("✅ Botão entrar encontrado")
                else:
                    print("❌ Botão entrar não visível")
                    return False
            except Exception as e:
                print(f"❌ Botão entrar não encontrado: {e}")
                return False

            # Preenche os campos
            print("\n📝 Preenchendo credenciais...")

            # Preenche usuário
            usuario_input.clear()
            usuario_input.fill(usuario)
            print("✅ Usuário preenchido")

            # Preenche senha
            senha_input.clear()
            senha_input.fill(senha)
            print("✅ Senha preenchida")

            # Clica no botão entrar
            print("\n🔐 Realizando login...")

            # Aguarda resposta de navegação após click
            with page.expect_navigation(wait_until="networkidle", timeout=30000):
                botao_entrar.click()

            # Verifica se login foi bem-sucedido
            new_url = page.url
            print(f"📄 Nova URL: {new_url}")

            # Verifica indicadores de sucesso/falha
            if '/login' in new_url:
                # Ainda na página de login, verificar se há mensagem de erro
                try:
                    error_elements = page.locator('.alert-danger, .error, .invalid-feedback, [class*="error"]')
                    if error_elements.count() > 0:
                        error_text = error_elements.first.text_content()
                        print(f"❌ Erro de login detectado: {error_text}")
                        return False
                    else:
                        print("❌ Ainda na página de login (credenciais podem estar incorretas)")
                        return False
                except:
                    print("❌ Ainda na página de login")
                    return False
            else:
                print("✅ Login realizado com sucesso!")
                print(f"   Redirecionado para: {new_url}")

                # Tenta encontrar indicadores de usuário logado
                try:
                    # Procura por elementos que indicam usuário logado
                    user_indicators = [
                        '[class*="user"]',
                        '[class*="profile"]',
                        '[class*="logout"]',
                        'text="Sair"',
                        'text="Logout"',
                        '[class*="dashboard"]'
                    ]

                    for indicator in user_indicators:
                        if page.locator(indicator).count() > 0:
                            print(f"✅ Indicador de login encontrado: {indicator}")
                            break

                except Exception as e:
                    print(f"⚠️  Não foi possível verificar indicadores de login: {e}")

                return True

        except Exception as e:
            print(f"❌ Erro durante teste de login: {e}")

            # Captura screenshot para debug
            try:
                screenshot_path = "screenshots/login_error_debug.png"
                os.makedirs("screenshots", exist_ok=True)
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot salvo: {screenshot_path}")
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
║               🧪 TESTE DE LOGIN EMSERH                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if teste_login_emserh():
        print("\n🎉 TESTE DE LOGIN PASSOU!")
        print("   O bot consegue fazer login no site da EMSERH")
        return 0
    else:
        print("\n❌ TESTE DE LOGIN FALHOU!")
        print("   Verifique credenciais ou elementos da página")
        return 1

if __name__ == '__main__':
    exit(main())