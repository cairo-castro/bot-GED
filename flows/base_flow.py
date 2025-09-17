"""
Classe base para fluxos de upload de documentos
"""

import os
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from playwright.sync_api import Page, Browser, expect
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class BaseFlow(ABC):
    """Classe abstrata base para fluxos de upload"""

    def __init__(self, browser: Browser):
        self.browser = browser
        self.page: Optional[Page] = None
        self.site_user = os.getenv('SITE_USER')
        self.site_pass = os.getenv('SITE_PASS')
        self.base_url = os.getenv('SITE_BASE_URL', 'https://example.com')

    def create_page(self) -> Page:
        """Cria uma nova página no navegador"""
        self.page = self.browser.new_page()

        # Configurações da página
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        self.page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

        return self.page

    def login(self) -> bool:
        """Realiza login no site"""
        if not self.page:
            self.create_page()

        try:
            logger.info("Iniciando processo de login")

            # Navega para a página de login
            self.page.goto(f"{self.base_url}/login", wait_until="networkidle")

            # Aguarda elementos de login
            self.page.wait_for_selector('input[name="email"], input[name="username"], #email, #username', timeout=10000)

            # Preenche credenciais (adaptável a diferentes estruturas)
            email_selectors = [
                'input[name="email"]',
                'input[name="username"]',
                '#email',
                '#username',
                'input[type="email"]'
            ]

            password_selectors = [
                'input[name="password"]',
                '#password',
                'input[type="password"]'
            ]

            # Tenta encontrar e preencher campo de email/username
            email_filled = False
            for selector in email_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.fill(selector, self.site_user)
                        email_filled = True
                        break
                except:
                    continue

            if not email_filled:
                raise Exception("Campo de email/username não encontrado")

            # Tenta encontrar e preencher campo de senha
            password_filled = False
            for selector in password_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.fill(selector, self.site_pass)
                        password_filled = True
                        break
                except:
                    continue

            if not password_filled:
                raise Exception("Campo de senha não encontrado")

            # Clica no botão de login
            login_buttons = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Entrar")',
                '.btn-login',
                '#login-button'
            ]

            login_clicked = False
            for selector in login_buttons:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.click(selector)
                        login_clicked = True
                        break
                except:
                    continue

            if not login_clicked:
                raise Exception("Botão de login não encontrado")

            # Aguarda redirecionamento ou elemento que confirma login
            self.page.wait_for_load_state("networkidle")

            # Verifica se login foi bem-sucedido
            if self.page.url.endswith('/login') or 'error' in self.page.url.lower():
                # Captura screenshot em caso de erro
                self.take_screenshot("login_error")
                raise Exception("Falha no login - ainda na página de login")

            logger.info("Login realizado com sucesso")
            return True

        except Exception as e:
            logger.error(f"Erro durante login: {e}")
            self.take_screenshot("login_error")
            return False

    def take_screenshot(self, name: str):
        """Captura screenshot para debug"""
        if self.page:
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/{name}_{timestamp}.png"
                self.page.screenshot(path=screenshot_path, full_page=True)
                logger.debug(f"Screenshot salvo: {screenshot_path}")
            except Exception as e:
                logger.warning(f"Erro ao capturar screenshot: {e}")

    def wait_for_upload_completion(self, timeout: int = 30000) -> bool:
        """Aguarda confirmação de upload (implementação genérica)"""
        try:
            # Aguarda possíveis indicadores de sucesso
            success_indicators = [
                '.alert-success',
                '.success-message',
                '[class*="success"]',
                'text="Upload realizado com sucesso"',
                'text="Arquivo enviado"',
                'text="Documento salvo"'
            ]

            for indicator in success_indicators:
                try:
                    self.page.wait_for_selector(indicator, timeout=5000)
                    logger.info(f"Upload confirmado via: {indicator}")
                    return True
                except PlaywrightTimeoutError:
                    continue

            # Se não encontrou indicadores específicos, aguarda stabilização da página
            self.page.wait_for_load_state("networkidle", timeout=timeout)

            # Verifica se não há mensagens de erro
            error_indicators = [
                '.alert-danger',
                '.error-message',
                '[class*="error"]',
                'text="Erro"',
                'text="Falha"'
            ]

            for indicator in error_indicators:
                try:
                    if self.page.locator(indicator).is_visible():
                        error_text = self.page.locator(indicator).text_content()
                        raise Exception(f"Erro detectado: {error_text}")
                except PlaywrightTimeoutError:
                    continue

            logger.info("Upload aparentemente concluído")
            return True

        except Exception as e:
            logger.error(f"Erro ao aguardar confirmação de upload: {e}")
            self.take_screenshot("upload_error")
            return False

    def cleanup(self):
        """Limpa recursos da página"""
        if self.page:
            try:
                self.page.close()
            except:
                pass
            self.page = None

    @abstractmethod
    def navigate_to_upload_page(self) -> bool:
        """Navega para a página específica de upload (deve ser implementado por cada fluxo)"""
        pass

    @abstractmethod
    def upload_file(self, file_path: str) -> bool:
        """Realiza o upload do arquivo (deve ser implementado por cada fluxo)"""
        pass

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Processa um arquivo completo (login + navegação + upload)"""
        try:
            logger.info(f"Iniciando processamento do arquivo: {file_path}")

            # Cria página se necessário
            if not self.page:
                self.create_page()

            # Realiza login
            if not self.login():
                return {
                    'success': False,
                    'error': 'Falha no login'
                }

            # Navega para página de upload
            if not self.navigate_to_upload_page():
                return {
                    'success': False,
                    'error': 'Falha ao navegar para página de upload'
                }

            # Realiza upload
            if not self.upload_file(file_path):
                return {
                    'success': False,
                    'error': 'Falha no upload do arquivo'
                }

            logger.info(f"Arquivo processado com sucesso: {file_path}")
            return {
                'success': True,
                'error': None
            }

        except Exception as e:
            logger.error(f"Erro ao processar arquivo {file_path}: {e}")
            self.take_screenshot("process_error")
            return {
                'success': False,
                'error': str(e)
            }
        finally:
            self.cleanup()