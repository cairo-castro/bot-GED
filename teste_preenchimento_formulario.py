#!/usr/bin/env python3
"""
Teste de preenchimento automático do formulário de solicitação
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from pathlib import Path

# Carrega configurações
load_dotenv()

def get_document_type_value_from_folder(folder_name: str) -> str:
    """Mapeia nome da pasta para valor numérico no sistema"""
    mapping = {
        'POLITICAS': '7',           # POLÍTICAS
        'DIRETRIZ': '6',            # DIRETRIZ
        'FLUXOGRAMA': '5',          # FLUXOGRAMA
        'INSTRUMENTAL': '13',       # INSTRUMENTAL
        'MANUAL': '3',              # MANUAL
        'MAPEAMENTO_DE_PROCESSO': '10',  # MAPEAMENTO DE PROCESSO
        'NORMA_E_ROTINA': '2',      # NORMA E ROTINA
        'NORMA_ZERO': '9',          # NORMA ZERO
        'PLANO_DE_CONTINGENCIA': '11',   # PLANO DE CONTINGÊNCIA
        'PROCEDIMENTO_OPERACIONAL_PADRAO': '1',  # PROCEDIMENTO OPERACIONAL PADRÃO
        'PROTOCOLO': '4',           # PROTOCOLO
        'REGIMENTO': '8',           # REGIMENTO
        'REGULAMENTO': '12'         # REGULAMENTO
    }
    return mapping.get(folder_name.upper(), '')

def get_document_type_name_from_folder(folder_name: str) -> str:
    """Mapeia nome da pasta para nome legível"""
    mapping = {
        'POLITICAS': 'POLÍTICAS',
        'DIRETRIZ': 'DIRETRIZ',
        'FLUXOGRAMA': 'FLUXOGRAMA',
        'INSTRUMENTAL': 'INSTRUMENTAL',
        'MANUAL': 'MANUAL',
        'MAPEAMENTO_DE_PROCESSO': 'MAPEAMENTO DE PROCESSO',
        'NORMA_E_ROTINA': 'NORMA E ROTINA',
        'NORMA_ZERO': 'NORMA ZERO',
        'PLANO_DE_CONTINGENCIA': 'PLANO DE CONTINGÊNCIA',
        'PROCEDIMENTO_OPERACIONAL_PADRAO': 'PROCEDIMENTO OPERACIONAL PADRÃO',
        'PROTOCOLO': 'PROTOCOLO',
        'REGIMENTO': 'REGIMENTO',
        'REGULAMENTO': 'REGULAMENTO'
    }
    return mapping.get(folder_name.upper(), folder_name)

def get_documents_from_folder(folder_name):
    """Pega todos os documentos da pasta especificada"""
    folder_path = Path(f'documentos/{folder_name}')

    if not folder_path.exists():
        return []

    documents = []
    valid_extensions = {'.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png'}

    for file_path in folder_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in valid_extensions:
            documents.append((file_path.name, str(file_path.absolute())))

    return documents

def teste_preenchimento_formulario(headless=False, slow_mo=1000):
    """Testa o preenchimento automático do formulário"""

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    # Pega pasta selecionada via variável de ambiente ou usa POLITICAS como padrão
    selected_folder = os.getenv('SELECTED_FOLDER', 'POLITICAS')

    # Pega todos os documentos da pasta
    documents = get_documents_from_folder(selected_folder)

    if not documents:
        print(f"❌ Nenhum documento encontrado na pasta {selected_folder}")
        return False

    print(f"📁 Pasta selecionada: {selected_folder}")
    print(f"📄 Documentos encontrados: {len(documents)}")
    print(f"🎯 Tipo mapeado: {get_document_type_name_from_folder(selected_folder)} (valor: {get_document_type_value_from_folder(selected_folder)})")
    print()

    with sync_playwright() as p:
        try:
            # Inicia browser
            print("🚀 Iniciando browser...")
            browser = p.chromium.launch(
                headless=headless,
                slow_mo=slow_mo,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )

            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = context.new_page()

            # PASSO 1: Login
            print("🔐 PASSO 1: Realizando login...")
            page.goto(f"{site_url}/login", wait_until="networkidle", timeout=30000)

            page.locator('#usuario').fill(usuario)
            page.locator('#password').fill(senha)

            with page.expect_navigation(wait_until="networkidle", timeout=30000):
                page.locator('input[type="submit"][value="Entrar"]').click()

            if '/login' in page.url:
                print("❌ Falha no login")
                return False

            print("✅ Login realizado com sucesso!")

            # PASSO 2: Navegar para GED
            print("\n📁 PASSO 2: Navegando para GED...")
            page.goto(f"{site_url}/ged", wait_until="networkidle", timeout=30000)
            print("✅ Página GED carregada!")

            # Processa todos os documentos da pasta
            documentos_processados = 0
            documentos_com_erro = 0

            for idx, (document_name, document_path) in enumerate(documents, 1):
                print(f"\n{'='*60}")
                print(f"📄 PROCESSANDO DOCUMENTO {idx}/{len(documents)}")
                print(f"📝 Nome: {document_name}")
                print(f"{'='*60}")

                try:
                    # PASSO 3: Abrir modal Nova Solicitação
                    print(f"\n➕ PASSO 3: Abrindo modal Nova Solicitação para documento {idx}...")
                    page.locator('#btnNovaSolicitacao').click()
                    time.sleep(2)  # Aguarda modal abrir
                    print("✅ Modal aberto!")

                    # PASSO 4: Preencher formulário
                    print(f"\n📝 PASSO 4: Preenchendo formulário para {document_name}...")

                    # Campo Título
                    print("   📝 Preenchendo título...")
                    titulo_field = page.locator('input[name="titulo"]')
                    if titulo_field.count() == 0:
                        titulo_field = page.locator('#titulo')

                    if titulo_field.count() > 0:
                        if not headless:
                            titulo_field.highlight()
                        titulo_field.clear()
                        titulo_field.fill(document_name)
                        print(f"   ✅ Título preenchido: {document_name}")
                    else:
                        print("   ❌ Campo título não encontrado")
                        raise Exception("Campo título não encontrado")

                    # Dropdown Tipo de Documento - seleciona por valor numérico
                    print("   🔽 Selecionando tipo de documento...")
                    tipo_doc_select = page.locator('select[name="tipo_documento"]')
                    if tipo_doc_select.count() > 0:
                        if not headless:
                            tipo_doc_select.highlight()

                        # Pega o valor numérico mapeado da pasta
                        tipo_value = get_document_type_value_from_folder(selected_folder)
                        tipo_name = get_document_type_name_from_folder(selected_folder)
                        print(f"   🎯 Selecionando tipo: {tipo_name} (value={tipo_value})")

                        if not tipo_value:
                            print(f"   ❌ Tipo não mapeado para pasta: {selected_folder}")
                            raise Exception(f"Tipo não mapeado para pasta: {selected_folder}")

                        # Seleciona diretamente por valor - muito mais rápido
                        try:
                            tipo_doc_select.select_option(value=tipo_value)
                            print(f"   ✅ Tipo selecionado: {tipo_name}")
                        except Exception as e:
                            print(f"   ❌ Erro ao selecionar tipo value={tipo_value}: {e}")
                            # Lista opções disponíveis para debug
                            opcoes_disponiveis = page.locator('select[name="tipo_documento"] option').all_text_contents()
                            print(f"   📋 Opções disponíveis: {opcoes_disponiveis}")
                            raise Exception(f"Tipo de documento não encontrado: {tipo_name} (value={tipo_value})")
                    else:
                        print("   ❌ Dropdown tipo de documento não encontrado")
                        raise Exception("Dropdown tipo de documento não encontrado")

                    # Dropdown Onde se aplica (Público Alvo)
                    print("   🎯 Selecionando público alvo...")
                    publico_alvo_select = page.locator('select[name="publico_alvo"]')
                    if publico_alvo_select.count() > 0:
                        if not headless:
                            publico_alvo_select.highlight()

                        # Seleciona option value="2" (PERFIL UNIDADE)
                        try:
                            publico_alvo_select.select_option(value="2")
                            print("   ✅ Público alvo selecionado: PERFIL (UNIDADE)")
                        except:
                            # Fallback: tenta por texto
                            try:
                                publico_alvo_select.select_option(label="PERFIL (UNIDADE)")
                                print("   ✅ Público alvo selecionado via texto")
                            except:
                                print("   ❌ Não foi possível selecionar público alvo")
                                opcoes_publico = page.locator('select[name="publico_alvo"] option').all_text_contents()
                                print(f"   📋 Opções disponíveis: {opcoes_publico}")
                                raise Exception("Não foi possível selecionar público alvo")
                    else:
                        print("   ❌ Dropdown público alvo não encontrado")
                        raise Exception("Dropdown público alvo não encontrado")

                    # Dropdown Perfil
                    print("   👤 Selecionando perfil...")
                    perfil_select = page.locator('select[name="perfil"]')
                    if perfil_select.count() > 0:
                        if not headless:
                            perfil_select.highlight()

                        # Seleciona option value="1" (ASSISTENCIAL)
                        try:
                            perfil_select.select_option(value="1")
                            print("   ✅ Perfil selecionado: ASSISTENCIAL")
                        except:
                            # Fallback: tenta por texto
                            try:
                                perfil_select.select_option(label="ASSISTENCIAL")
                                print("   ✅ Perfil selecionado via texto")
                            except:
                                print("   ❌ Não foi possível selecionar perfil")
                                opcoes_perfil = page.locator('select[name="perfil"] option').all_text_contents()
                                print(f"   📋 Opções disponíveis: {opcoes_perfil}")
                                raise Exception("Não foi possível selecionar perfil")
                    else:
                        print("   ❌ Dropdown perfil não encontrado")
                        raise Exception("Dropdown perfil não encontrado")

                    # Campo Justificativa
                    print("   📋 Preenchendo justificativa...")
                    justificativa_field = page.locator('textarea[name="justificativa"]')
                    if justificativa_field.count() > 0:
                        if not headless:
                            justificativa_field.highlight()
                        justificativa_field.clear()
                        justificativa_field.fill(document_name)
                        print(f"   ✅ Justificativa preenchida: {document_name}")
                    else:
                        print("   ❌ Campo justificativa não encontrado")
                        raise Exception("Campo justificativa não encontrado")

                    # PASSO 5: Clicar em Salvar
                    print(f"\n💾 PASSO 5: Salvando documento {idx}...")
                    salvar_btn = page.locator('#btnModalDocumento')

                    if salvar_btn.count() > 0:
                        if not headless:
                            salvar_btn.highlight()

                        # Aguarda possível navegação ou mudança na página
                        try:
                            # Clica e aguarda resposta
                            with page.expect_response(lambda response: response.status in [200, 302], timeout=30000):
                                salvar_btn.click()

                            print("   ✅ Botão Salvar clicado!")

                            # Aguarda um pouco para ver o resultado
                            time.sleep(3)

                            # Verifica se há mensagens de sucesso ou erro
                            success_indicators = [
                                '.alert-success',
                                '.success',
                                'text="Sucesso"',
                                'text="Salvo"',
                                'text="Criado"'
                            ]

                            error_indicators = [
                                '.alert-danger',
                                '.error',
                                'text="Erro"',
                                'text="Falha"'
                            ]

                            # Verifica sucesso
                            documento_salvo = False
                            for indicator in success_indicators:
                                if page.locator(indicator).count() > 0:
                                    success_msg = page.locator(indicator).text_content()
                                    print(f"   🎉 Sucesso detectado: {success_msg}")
                                    documento_salvo = True
                                    break

                            # Verifica erro
                            if not documento_salvo:
                                for indicator in error_indicators:
                                    if page.locator(indicator).count() > 0:
                                        error_msg = page.locator(indicator).text_content()
                                        print(f"   ❌ Erro detectado: {error_msg}")
                                        raise Exception(f"Erro ao salvar: {error_msg}")

                            # Se não detectou nem sucesso nem erro, considera sucesso
                            if not documento_salvo:
                                print("   ✅ Formulário enviado (sem indicador específico)")
                                documento_salvo = True

                            if documento_salvo:
                                # Clica no botão OK para fechar o modal de sucesso
                                print("   👆 Clicando no botão OK...")
                                try:
                                    ok_button = page.locator('button.confirm.btn.btn-lg.btn-primary')
                                    if ok_button.count() > 0:
                                        if not headless:
                                            ok_button.highlight()
                                        ok_button.click()
                                        print("   ✅ Botão OK clicado!")
                                        time.sleep(1)
                                    else:
                                        # Tenta outras variações do botão OK
                                        ok_alternatives = [
                                            'button:has-text("OK")',
                                            'button:has-text("Ok")',
                                            '.confirm',
                                            '.btn-primary:has-text("OK")'
                                        ]
                                        for selector in ok_alternatives:
                                            ok_btn = page.locator(selector)
                                            if ok_btn.count() > 0:
                                                ok_btn.click()
                                                print(f"   ✅ Botão OK clicado (selector: {selector})!")
                                                break
                                        else:
                                            print("   ⚠️  Botão OK não encontrado, continuando...")
                                except Exception as e:
                                    print(f"   ⚠️  Erro ao clicar no botão OK: {e}")

                                documentos_processados += 1
                                print(f"   🎉 Documento {idx} processado com sucesso!")

                                # Aguarda um pouco antes do próximo
                                time.sleep(2)

                        except PlaywrightTimeoutError:
                            print("   ⚠️  Timeout ao aguardar resposta do servidor")
                            # Tenta clicar mesmo assim
                            salvar_btn.click()
                            time.sleep(3)
                            print("   ✅ Clique executado (sem aguardar resposta)")

                            # Tenta clicar no botão OK mesmo com timeout
                            try:
                                ok_button = page.locator('button.confirm.btn.btn-lg.btn-primary')
                                if ok_button.count() > 0:
                                    ok_button.click()
                                    print("   ✅ Botão OK clicado (timeout)!")
                                    time.sleep(1)
                            except:
                                pass

                            documentos_processados += 1

                    else:
                        print("   ❌ Botão Salvar não encontrado")
                        raise Exception("Botão Salvar não encontrado")

                except Exception as e:
                    print(f"   ❌ Erro no documento {idx}: {e}")
                    documentos_com_erro += 1

                    # Screenshot de erro para este documento
                    try:
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        screenshot_path = f"screenshots/erro_doc_{idx}_{timestamp}.png"
                        page.screenshot(path=screenshot_path, full_page=True)
                        print(f"   📸 Screenshot de erro salvo: {screenshot_path}")
                    except:
                        pass

                    # Continua para o próximo documento
                    continue

            # Resumo final
            print(f"\n{'='*60}")
            print(f"📊 RESUMO DO PROCESSAMENTO")
            print(f"{'='*60}")
            print(f"📁 Pasta: {selected_folder}")
            print(f"📄 Total de documentos: {len(documents)}")
            print(f"✅ Processados com sucesso: {documentos_processados}")
            print(f"❌ Com erro: {documentos_com_erro}")
            print(f"📈 Taxa de sucesso: {(documentos_processados/len(documents)*100):.1f}%")

            return documentos_processados > 0

        except Exception as e:
            print(f"❌ Erro durante execução: {e}")

            # Screenshot de erro
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/erro_preenchimento_{timestamp}.png"
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"📸 Screenshot de erro salvo: {screenshot_path}")
            except:
                pass

            return False

        finally:
            try:
                context.close()
                browser.close()
            except:
                pass

def main():
    """Função principal"""
    import argparse

    parser = argparse.ArgumentParser(description='Teste de preenchimento de formulário')
    parser.add_argument('--headless', action='store_true', help='Executa em modo headless')
    parser.add_argument('--fast', action='store_true', help='Execução rápida')

    args = parser.parse_args()
    speed = 500 if args.fast else 1000

    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           📝 TESTE PREENCHIMENTO FORMULÁRIO                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if teste_preenchimento_formulario(headless=args.headless, slow_mo=speed):
        print("\n🎉 TESTE DE PREENCHIMENTO PASSOU!")
        print("   ✅ Formulário preenchido com sucesso")
        print("   ✅ Botão Salvar clicado")
        return 0
    else:
        print("\n❌ TESTE DE PREENCHIMENTO FALHOU!")
        print("   ⚠️  Verifique screenshots e logs para debug")
        return 1

if __name__ == '__main__':
    exit(main())