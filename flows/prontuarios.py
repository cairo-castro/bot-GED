"""
Fluxo específico para upload de prontuários médicos
"""

import logging
from typing import Dict, Any
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .base_flow import BaseFlow

logger = logging.getLogger(__name__)


class ProntuariosFlow(BaseFlow):
    """Fluxo para upload de prontuários médicos"""

    def navigate_to_upload_page(self) -> bool:
        """Navega para a página de upload de prontuários"""
        try:
            logger.info("Navegando para página de upload de prontuários")

            # URLs possíveis para prontuários
            prontuarios_urls = [
                f"{self.base_url}/prontuarios/upload",
                f"{self.base_url}/documentos/prontuarios",
                f"{self.base_url}/upload/prontuarios",
                f"{self.base_url}/admin/prontuarios/create",
                f"{self.base_url}/pacientes/prontuarios"
            ]

            # Tenta navegar para página de prontuários
            navigation_success = False
            for url in prontuarios_urls:
                try:
                    self.page.goto(url, wait_until="networkidle", timeout=10000)

                    # Verifica se chegou na página correta
                    if any(text in self.page.content().lower() for text in ['prontuário', 'prontuario', 'upload', 'documento']):
                        navigation_success = True
                        logger.info(f"Página de prontuários encontrada: {url}")
                        break
                except:
                    continue

            # Se não conseguiu pela URL direta, tenta navegar pelo menu
            if not navigation_success:
                logger.info("Tentando navegar via menu")

                # Selectors comuns para menus de prontuários
                menu_selectors = [
                    'a:has-text("Prontuários")',
                    'a:has-text("Prontuarios")',
                    'a:has-text("Pacientes")',
                    'a[href*="prontuario"]',
                    'a[href*="paciente"]',
                    '.menu-item:has-text("Prontuários")',
                    'nav a:has-text("Prontuários")'
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
                                'a:has-text("Novo Prontuário")',
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
                logger.info("Navegação para página de prontuários bem-sucedida")
                return True
            else:
                logger.error("Não foi possível navegar para página de prontuários")
                self.take_screenshot("navigation_error_prontuarios")
                return False

        except Exception as e:
            logger.error(f"Erro ao navegar para página de prontuários: {e}")
            self.take_screenshot("navigation_error_prontuarios")
            return False

    def upload_file(self, file_path: str) -> bool:
        """Realiza o upload do arquivo de prontuário"""
        try:
            logger.info(f"Iniciando upload do prontuário: {file_path}")

            # Aguarda página carregar completamente
            self.page.wait_for_load_state("networkidle")

            # Preenche campos obrigatórios antes do upload (se existirem)
            self.fill_required_fields()

            # Selectors comuns para input de arquivo
            file_input_selectors = [
                'input[type="file"]',
                'input[name="arquivo"]',
                'input[name="documento"]',
                'input[name="prontuario"]',
                'input[name="anexo"]',
                'input[accept*="pdf"]',
                'input[accept*="image"]',
                '#file-upload',
                '#prontuario-upload',
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
                    'button:has-text("Anexar")',
                    '.upload-button',
                    '.btn-upload',
                    '.btn-anexar'
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

            # Aguarda processamento do arquivo
            self.page.wait_for_timeout(3000)

            # Preenche campos adicionais após upload
            self.fill_additional_fields()

            # Procura e clica no botão de enviar/salvar
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Enviar")',
                'button:has-text("Salvar")',
                'button:has-text("Gravar")',
                'button:has-text("Confirmar")',
                '.btn-submit',
                '.btn-save',
                '.btn-confirmar',
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
            if self.wait_for_upload_completion(timeout=45000):  # Timeout maior para prontuários
                logger.info(f"Upload do prontuário concluído: {file_path}")
                return True
            else:
                logger.error(f"Falha na confirmação do upload: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Erro durante upload do prontuário: {e}")
            self.take_screenshot("upload_error_prontuario")
            return False

    def fill_required_fields(self) -> bool:
        """Preenche campos obrigatórios antes do upload"""
        try:
            # Campos que podem ser obrigatórios para prontuários
            required_fields = {
                'input[name="paciente_nome"]': 'Paciente Anônimo',
                'input[name="numero_prontuario"]': '000000',
                'select[name="especialidade"]': 'geral',
                'input[name="data_consulta"]': '2024-01-01'
            }

            for selector, value in required_fields.items():
                try:
                    if self.page.locator(selector).is_visible():
                        if selector.startswith('select'):
                            self.page.select_option(selector, value)
                        else:
                            self.page.fill(selector, value)
                        logger.debug(f"Campo preenchido: {selector} = {value}")
                except:
                    continue

            return True

        except Exception as e:
            logger.warning(f"Erro ao preencher campos obrigatórios: {e}")
            return False

    def fill_additional_fields(self) -> bool:
        """Preenche campos adicionais específicos para prontuários"""
        try:
            # Campos específicos para prontuários
            fields = {
                'input[name="tipo_documento"]': 'Prontuário',
                'select[name="categoria"]': 'prontuario',
                'input[name="descricao"]': 'Upload automático de prontuário via bot',
                'textarea[name="observacoes"]': 'Documento carregado automaticamente'
            }

            for selector, value in fields.items():
                try:
                    if self.page.locator(selector).is_visible():
                        if selector.startswith('select'):
                            self.page.select_option(selector, value)
                        elif selector.startswith('textarea'):
                            self.page.fill(selector, value)
                        else:
                            self.page.fill(selector, value)
                        logger.debug(f"Campo adicional preenchido: {selector}")
                except:
                    continue

            return True

        except Exception as e:
            logger.warning(f"Erro ao preencher campos adicionais: {e}")
            return False