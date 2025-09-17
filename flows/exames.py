"""
Fluxo específico para upload de exames médicos
"""

import logging
from typing import Dict, Any
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from .base_flow import BaseFlow

logger = logging.getLogger(__name__)


class ExamesFlow(BaseFlow):
    """Fluxo para upload de exames médicos"""

    def navigate_to_upload_page(self) -> bool:
        """Navega para a página de upload de exames"""
        try:
            logger.info("Navegando para página de upload de exames")

            # URLs possíveis para exames
            exames_urls = [
                f"{self.base_url}/exames/upload",
                f"{self.base_url}/documentos/exames",
                f"{self.base_url}/upload/exames",
                f"{self.base_url}/admin/exames/create",
                f"{self.base_url}/laboratorio/exames"
            ]

            # Tenta navegar para página de exames
            navigation_success = False
            for url in exames_urls:
                try:
                    self.page.goto(url, wait_until="networkidle", timeout=10000)

                    # Verifica se chegou na página correta
                    if any(text in self.page.content().lower() for text in ['exame', 'laboratorio', 'upload', 'documento']):
                        navigation_success = True
                        logger.info(f"Página de exames encontrada: {url}")
                        break
                except:
                    continue

            # Se não conseguiu pela URL direta, tenta navegar pelo menu
            if not navigation_success:
                logger.info("Tentando navegar via menu")

                # Selectors comuns para menus de exames
                menu_selectors = [
                    'a:has-text("Exames")',
                    'a:has-text("Laboratório")',
                    'a:has-text("Laboratorio")',
                    'a:has-text("Resultados")',
                    'a[href*="exame"]',
                    'a[href*="laboratorio"]',
                    '.menu-item:has-text("Exames")',
                    'nav a:has-text("Exames")'
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
                                'a:has-text("Novo Exame")',
                                'a:has-text("Cadastrar")',
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
                logger.info("Navegação para página de exames bem-sucedida")
                return True
            else:
                logger.error("Não foi possível navegar para página de exames")
                self.take_screenshot("navigation_error_exames")
                return False

        except Exception as e:
            logger.error(f"Erro ao navegar para página de exames: {e}")
            self.take_screenshot("navigation_error_exames")
            return False

    def upload_file(self, file_path: str) -> bool:
        """Realiza o upload do arquivo de exame"""
        try:
            logger.info(f"Iniciando upload do exame: {file_path}")

            # Aguarda página carregar completamente
            self.page.wait_for_load_state("networkidle")

            # Preenche campos obrigatórios antes do upload
            self.fill_required_fields()

            # Selectors comuns para input de arquivo
            file_input_selectors = [
                'input[type="file"]',
                'input[name="arquivo"]',
                'input[name="documento"]',
                'input[name="exame"]',
                'input[name="resultado"]',
                'input[name="laudo"]',
                'input[accept*="pdf"]',
                'input[accept*="image"]',
                '#file-upload',
                '#exame-upload',
                '#resultado-upload',
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
                    'button:has-text("Resultado")',
                    '.upload-button',
                    '.btn-upload',
                    '.btn-anexar',
                    '.btn-resultado'
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
            self.page.wait_for_timeout(2000)

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
                'button:has-text("Processar")',
                '.btn-submit',
                '.btn-save',
                '.btn-confirmar',
                '.btn-processar',
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
            if self.wait_for_upload_completion(timeout=30000):
                logger.info(f"Upload do exame concluído: {file_path}")
                return True
            else:
                logger.error(f"Falha na confirmação do upload: {file_path}")
                return False

        except Exception as e:
            logger.error(f"Erro durante upload do exame: {e}")
            self.take_screenshot("upload_error_exame")
            return False

    def fill_required_fields(self) -> bool:
        """Preenche campos obrigatórios antes do upload"""
        try:
            # Campos que podem ser obrigatórios para exames
            required_fields = {
                'input[name="paciente"]': 'Paciente Anônimo',
                'input[name="medico_solicitante"]': 'Dr. Sistema',
                'select[name="tipo_exame"]': 'laboratorio',
                'input[name="data_coleta"]': '2024-01-01',
                'input[name="codigo_exame"]': 'AUTO001'
            }

            for selector, value in required_fields.items():
                try:
                    if self.page.locator(selector).is_visible():
                        if selector.startswith('select'):
                            self.page.select_option(selector, value)
                        else:
                            self.page.fill(selector, value)
                        logger.debug(f"Campo obrigatório preenchido: {selector} = {value}")
                except:
                    continue

            return True

        except Exception as e:
            logger.warning(f"Erro ao preencher campos obrigatórios: {e}")
            return False

    def fill_additional_fields(self) -> bool:
        """Preenche campos adicionais específicos para exames"""
        try:
            # Campos específicos para exames
            fields = {
                'input[name="tipo_documento"]': 'Resultado de Exame',
                'select[name="categoria"]': 'exame',
                'select[name="status"]': 'finalizado',
                'input[name="descricao"]': 'Upload automático de resultado via bot',
                'textarea[name="observacoes"]': 'Resultado carregado automaticamente pelo sistema',
                'input[name="laboratorio"]': 'Laboratório Externo'
            }

            for selector, value in fields.items():
                try:
                    if self.page.locator(selector).is_visible():
                        if selector.startswith('select'):
                            # Tenta várias opções para selects
                            options_to_try = [value, value.lower(), value.upper()]
                            for option in options_to_try:
                                try:
                                    self.page.select_option(selector, option)
                                    break
                                except:
                                    continue
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

    def validate_file_type(self, file_path: str) -> bool:
        """Valida se o tipo de arquivo é aceito para exames"""
        import os

        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.dcm']
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension not in valid_extensions:
            logger.warning(f"Tipo de arquivo pode não ser aceito: {file_extension}")
            return False

        return True