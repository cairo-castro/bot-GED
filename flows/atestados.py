"""
Fluxo específico para upload de atestados médicos
"""

import logging
from typing import Dict, Any
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .base_flow import BaseFlow

logger = logging.getLogger(__name__)


class AtestadosFlow(BaseFlow):
    """Fluxo para upload de atestados médicos"""

    def navigate_to_upload_page(self) -> bool:
        """Navega para a página de upload de atestados"""
        try:
            logger.info("Navegando para página de upload de atestados")

            # URLs possíveis para atestados (ajuste conforme seu sistema)
            atestados_urls = [
                f"{self.base_url}/atestados/upload",
                f"{self.base_url}/documentos/atestados",
                f"{self.base_url}/upload/atestados",
                f"{self.base_url}/admin/atestados/create"
            ]

            # Tenta navegar para página de atestados
            navigation_success = False
            for url in atestados_urls:
                try:
                    self.page.goto(url, wait_until="networkidle", timeout=10000)

                    # Verifica se chegou na página correta
                    if any(text in self.page.content().lower() for text in ['atestado', 'upload', 'documento']):
                        navigation_success = True
                        logger.info(f"Página de atestados encontrada: {url}")
                        break
                except:
                    continue

            # Se não conseguiu pela URL direta, tenta navegar pelo menu
            if not navigation_success:
                logger.info("Tentando navegar via menu")

                # Selectors comuns para menus de atestados
                menu_selectors = [
                    'a:has-text("Atestados")',
                    'a:has-text("Documentos")',
                    'a[href*="atestado"]',
                    'a[href*="documento"]',
                    '.menu-item:has-text("Atestados")',
                    'nav a:has-text("Atestados")'
                ]

                for selector in menu_selectors:
                    try:
                        if self.page.locator(selector).is_visible():
                            self.page.click(selector)
                            self.page.wait_for_load_state("networkidle")

                            # Procura por link de "Novo" ou "Upload"
                            upload_selectors = [
                                'a:has-text("Novo")',
                                'a:has-text("Upload")',
                                'a:has-text("Adicionar")',
                                'button:has-text("Novo")',
                                '.btn-new',
                                '.btn-upload'
                            ]

                            for upload_selector in upload_selectors:
                                try:
                                    if self.page.locator(upload_selector).is_visible():
                                        self.page.click(upload_selector)
                                        self.page.wait_for_load_state("networkidle")
                                        navigation_success = True
                                        break
                                except:
                                    continue

                            if navigation_success:
                                break
                    except:
                        continue

            if navigation_success:
                logger.info("Navegação para página de atestados bem-sucedida")
                return True
            else:
                logger.error("Não foi possível navegar para página de atestados")
                self.take_screenshot("navigation_error_atestados")
                return False

        except Exception as e:
            logger.error(f"Erro ao navegar para página de atestados: {e}")
            self.take_screenshot("navigation_error_atestados")
            return False

    def upload_file(self, file_path: str) -> bool:
        """Realiza o upload do arquivo de atestado"""
        try:
            logger.info(f"Iniciando upload do atestado: {file_path}")

            # Aguarda página carregar completamente
            self.page.wait_for_load_state("networkidle")

            # Selectors comuns para input de arquivo
            file_input_selectors = [
                'input[type="file"]',
                'input[name="arquivo"]',
                'input[name="documento"]',
                'input[name="atestado"]',
                'input[accept*="pdf"]',
                'input[accept*="image"]',
                '#file-upload',
                '.file-input'
            ]

            # Procura pelo campo de upload
            file_input = None
            for selector in file_input_selectors:
                try:
                    locator = self.page.locator(selector)
                    if locator.count() > 0:
                        file_input = locator.first
                        break
                except:
                    continue

            if not file_input:
                # Tenta encontrar botões de upload que abrem dialog
                upload_buttons = [
                    'button:has-text("Upload")',
                    'button:has-text("Escolher")',
                    'button:has-text("Selecionar")',
                    '.upload-button',
                    '.btn-upload'
                ]

                for button_selector in upload_buttons:
                    try:
                        if self.page.locator(button_selector).is_visible():
                            # Configura listener para file chooser
                            with self.page.expect_file_chooser() as fc_info:
                                self.page.click(button_selector)
                            file_chooser = fc_info.value
                            file_chooser.set_files(file_path)
                            break
                    except:
                        continue
            else:
                # Upload direto via input file
                file_input.set_input_files(file_path)

            # Aguarda um pouco para o arquivo ser processado
            self.page.wait_for_timeout(2000)

            # Procura e clica no botão de enviar/salvar
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Enviar")',
                'button:has-text("Salvar")',
                'button:has-text("Upload")',
                '.btn-submit',
                '.btn-save',
                '#submit-button'
            ]

            submit_clicked = False
            for selector in submit_selectors:
                try:
                    if self.page.locator(selector).is_visible():
                        self.page.click(selector)
                        submit_clicked = True
                        break
                except:
                    continue

            if not submit_clicked:
                logger.warning("Botão de envio não encontrado, assumindo upload automático")

            # Aguarda confirmação
            if self.wait_for_upload_completion():
                logger.info(f"Upload do atestado concluído: {file_path}")
                return True
            else:
                logger.error(f"Falha na confirmação do upload: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Erro durante upload do atestado: {e}")
            self.take_screenshot("upload_error_atestado")
            return False

    def fill_additional_fields(self) -> bool:
        """Preenche campos adicionais específicos para atestados (se necessário)"""
        try:
            # Campos específicos para atestados
            fields = {
                'input[name="tipo"]': 'Atestado Médico',
                'select[name="categoria"]': 'atestado',
                'input[name="descricao"]': 'Upload automático via bot'
            }

            for selector, value in fields.items():
                try:
                    if self.page.locator(selector).is_visible():
                        if selector.startswith('select'):
                            self.page.select_option(selector, value)
                        else:
                            self.page.fill(selector, value)
                except:
                    continue

            return True

        except Exception as e:
            logger.warning(f"Erro ao preencher campos adicionais: {e}")
            return False