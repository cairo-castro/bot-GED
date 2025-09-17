#!/usr/bin/env python3
"""
Teste visual melhorado do fluxo GED - Versão com melhor gerenciamento de recursos
"""

import os
import time
import signal
import sys
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime

# Carrega configurações
load_dotenv()

class BrowserManager:
    """Gerenciador de browser com cleanup automático"""

    def __init__(self, headless=False, slow_mo=1000):
        self.headless = headless
        self.slow_mo = slow_mo
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

        # Configura handler para Ctrl+C
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handler para capturar Ctrl+C"""
        print("\n👋 Interrompido pelo usuário...")
        self.cleanup()
        sys.exit(0)

    def start(self):
        """Inicia o browser"""
        try:
            print("🚀 Iniciando Playwright...")
            self.playwright = sync_playwright().start()

            print("🌐 Abrindo browser...")
            browser_args = [
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled'
            ]

            if self.headless:
                browser_args.append('--no-sandbox')

            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo,
                args=browser_args
            )

            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            self.page = self.context.new_page()

            print("✅ Browser iniciado com sucesso!")
            return True

        except Exception as e:
            print(f"❌ Erro ao iniciar browser: {e}")
            self.cleanup()
            return False

    def cleanup(self):
        """Limpa recursos de forma segura"""
        try:
            if self.page:
                try:
                    self.page.close()
                except:
                    pass

            if self.context:
                try:
                    self.context.close()
                except:
                    pass

            if self.browser:
                try:
                    self.browser.close()
                except:
                    pass

            if self.playwright:
                try:
                    self.playwright.stop()
                except:
                    pass

        except Exception:
            pass

        print("🔒 Recursos limpos")

def executar_fluxo_visual(manager):
    """Executa o fluxo visual principal"""

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    page = manager.page

    try:
        # PASSO 1: Login
        print("\n🔐 PASSO 1: Realizando login...")

        print("   📍 Navegando para página de login...")
        page.goto(f"{site_url}/login", wait_until="networkidle", timeout=30000)

        print("   📝 Preenchendo usuário...")
        usuario_field = page.locator('#usuario')
        usuario_field.highlight()
        usuario_field.fill(usuario)

        print("   🔑 Preenchendo senha...")
        senha_field = page.locator('#password')
        senha_field.highlight()
        senha_field.fill(senha)

        print("   🖱️  Clicando em Entrar...")
        entrar_btn = page.locator('input[type="submit"][value="Entrar"]')
        entrar_btn.highlight()

        with page.expect_navigation(wait_until="networkidle", timeout=30000):
            entrar_btn.click()

        # Verifica login
        if '/login' in page.url:
            print("❌ Falha no login")
            return False

        print("✅ Login realizado com sucesso!")

        # PASSO 2: Navegar para GED
        print("\n📁 PASSO 2: Navegando para GED...")

        ged_url = f"{site_url}/ged"
        page.goto(ged_url, wait_until="networkidle", timeout=30000)

        print("✅ Página GED carregada!")

        # PASSO 3: Nova Solicitação
        print("\n➕ PASSO 3: Clicando em Nova Solicitação...")

        # Aguarda um pouco para garantir que a página carregou
        time.sleep(2)

        nova_solicitacao_btn = page.locator('#btnNovaSolicitacao')

        if nova_solicitacao_btn.count() == 0:
            print("❌ Botão Nova Solicitação não encontrado")
            return False

        print("✅ Botão encontrado!")
        nova_solicitacao_btn.highlight()
        nova_solicitacao_btn.click()

        # Aguarda modal abrir
        print("   ⏳ Aguardando modal abrir...")
        time.sleep(3)

        # PASSO 4: Verificar modal
        print("\n📋 PASSO 4: Verificando formulário...")

        # Procura por elementos do modal
        modal_elements = [
            ('input[placeholder*="título"], input[name*="titulo"]', 'Campo Título'),
            ('select, .dropdown-toggle', 'Dropdowns'),
            ('textarea', 'Campo Justificativa'),
            ('button:has-text("Salvar"), .btn-success', 'Botão Salvar')
        ]

        found_elements = 0
        for selector, nome in modal_elements:
            try:
                element = page.locator(selector).first
                if element.is_visible():
                    print(f"   ✅ {nome} encontrado")
                    element.highlight()
                    found_elements += 1
                    time.sleep(1)
                else:
                    print(f"   ⚠️  {nome} não visível")
            except:
                print(f"   ❌ {nome} não encontrado")

        print(f"\n📊 Formulário analisado: {found_elements} elementos encontrados")

        if found_elements > 0:
            print("✅ Modal de Nova Solicitação aberto com sucesso!")
            return True
        else:
            print("⚠️  Modal pode não ter aberto corretamente")
            return False

    except PlaywrightTimeoutError as e:
        print(f"⏰ Timeout durante execução: {e}")
        return False

    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        return False

def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Teste visual melhorado do bot GED')
    parser.add_argument('--headless', action='store_true', help='Executa em modo headless')
    parser.add_argument('--speed', type=int, default=1000, help='Velocidade em ms entre ações')
    parser.add_argument('--fast', action='store_true', help='Execução rápida (200ms)')
    parser.add_argument('--wait-time', type=int, default=60, help='Tempo para manter browser aberto (segundos)')

    args = parser.parse_args()

    if args.fast:
        args.speed = 200

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           👁️  TESTE VISUAL MELHORADO - GED EMSERH           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    print(f"🎛️  Configurações:")
    print(f"   • Modo: {'Headless' if args.headless else 'Visual'}")
    print(f"   • Velocidade: {args.speed}ms entre ações")
    print(f"   • Tempo de espera: {args.wait_time}s")

    if not args.headless:
        print(f"\n💡 Dicas:")
        print(f"   • Pressione Ctrl+C para fechar a qualquer momento")
        print(f"   • O browser permanecerá aberto por {args.wait_time}s após o teste")

    # Cria gerenciador de browser
    manager = BrowserManager(headless=args.headless, slow_mo=args.speed)

    try:
        # Inicia browser
        if not manager.start():
            return 1

        # Executa fluxo
        success = executar_fluxo_visual(manager)

        if success:
            print("\n🎉 TESTE VISUAL CONCLUÍDO COM SUCESSO!")

            if not args.headless:
                print(f"\n⏳ Mantendo browser aberto por {args.wait_time}s...")
                print("   (Pressione Ctrl+C para fechar antes)")

                try:
                    time.sleep(args.wait_time)
                except KeyboardInterrupt:
                    print("\n👋 Fechando por solicitação do usuário...")

            return 0
        else:
            print("\n❌ TESTE VISUAL FALHOU!")
            return 1

    except KeyboardInterrupt:
        print("\n👋 Teste interrompido pelo usuário")
        return 0

    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        return 1

    finally:
        manager.cleanup()

if __name__ == '__main__':
    sys.exit(main())