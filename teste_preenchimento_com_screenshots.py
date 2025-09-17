#!/usr/bin/env python3
"""
Teste de preenchimento com screenshots em cada etapa
"""

import os
import time
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from datetime import datetime
from pathlib import Path

load_dotenv()

def teste_com_screenshots():
    """Executa teste capturando screenshots de cada etapa"""

    site_url = os.getenv('SITE_BASE_URL')
    usuario = os.getenv('SITE_USER')
    senha = os.getenv('SITE_PASS')

    # Pega primeiro documento da pasta POLITICAS
    politicas_path = Path('documentos/POLITICAS')
    document_name = None

    for file_path in politicas_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in {'.pdf', '.docx', '.doc'}:
            document_name = file_path.name
            break

    if not document_name:
        print("❌ Nenhum documento encontrado")
        return False

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={'width': 1920, 'height': 1080})
            page = context.new_page()

            print(f"📄 Processando: {document_name}")

            # Login
            print("🔐 Fazendo login...")
            page.goto(f"{site_url}/login", wait_until="networkidle")
            page.locator('#usuario').fill(usuario)
            page.locator('#password').fill(senha)

            with page.expect_navigation():
                page.locator('input[type="submit"][value="Entrar"]').click()

            page.screenshot(path=f"screenshots/01_apos_login_{timestamp}.png", full_page=True)
            print("📸 Screenshot 1: Após login")

            # Navegar para GED
            print("📁 Navegando para GED...")
            page.goto(f"{site_url}/ged", wait_until="networkidle")
            page.screenshot(path=f"screenshots/02_pagina_ged_{timestamp}.png", full_page=True)
            print("📸 Screenshot 2: Página GED")

            # Abrir modal
            print("➕ Abrindo modal...")
            page.locator('#btnNovaSolicitacao').click()
            time.sleep(2)
            page.screenshot(path=f"screenshots/03_modal_aberto_{timestamp}.png", full_page=True)
            print("📸 Screenshot 3: Modal aberto")

            # Preencher título
            print("📝 Preenchendo título...")
            page.locator('input[name="titulo"]').fill(document_name)
            page.screenshot(path=f"screenshots/04_titulo_preenchido_{timestamp}.png", full_page=True)
            print("📸 Screenshot 4: Título preenchido")

            # Selecionar tipo
            print("🔽 Selecionando tipo...")
            page.locator('select[name="tipo_documento"]').select_option(label="POLÍTICAS")
            page.screenshot(path=f"screenshots/05_tipo_selecionado_{timestamp}.png", full_page=True)
            print("📸 Screenshot 5: Tipo selecionado")

            # Selecionar público alvo
            print("🎯 Selecionando público alvo...")
            page.locator('select[name="publico_alvo"]').select_option(value="2")
            page.screenshot(path=f"screenshots/06_publico_selecionado_{timestamp}.png", full_page=True)
            print("📸 Screenshot 6: Público alvo selecionado")

            # Selecionar perfil
            print("👤 Selecionando perfil...")
            page.locator('select[name="perfil"]').select_option(value="1")
            page.screenshot(path=f"screenshots/07_perfil_selecionado_{timestamp}.png", full_page=True)
            print("📸 Screenshot 7: Perfil selecionado")

            # Preencher justificativa
            print("📋 Preenchendo justificativa...")
            page.locator('textarea[name="justificativa"]').fill(document_name)
            page.screenshot(path=f"screenshots/08_justificativa_preenchida_{timestamp}.png", full_page=True)
            print("📸 Screenshot 8: Justificativa preenchida")

            # Formulário completo antes de salvar
            page.screenshot(path=f"screenshots/09_formulario_completo_{timestamp}.png", full_page=True)
            print("📸 Screenshot 9: Formulário completo")

            # Clicar em Salvar
            print("💾 Clicando em Salvar...")
            page.locator('#btnModalDocumento').click()
            time.sleep(3)
            page.screenshot(path=f"screenshots/10_apos_salvar_{timestamp}.png", full_page=True)
            print("📸 Screenshot 10: Após salvar")

            print(f"\n✅ Teste concluído! Screenshots salvos com timestamp: {timestamp}")
            return True

        except Exception as e:
            print(f"❌ Erro: {e}")
            try:
                page.screenshot(path=f"screenshots/erro_teste_{timestamp}.png", full_page=True)
            except:
                pass
            return False

        finally:
            try:
                context.close()
                browser.close()
            except:
                pass

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           📸 TESTE COM SCREENSHOTS DETALHADOS               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)

    if teste_com_screenshots():
        print("\n🎉 TODAS AS ETAPAS FUNCIONARAM!")
        print("📁 Verifique a pasta screenshots/ para ver o processo completo")
    else:
        print("\n❌ Erro durante execução")
        print("📁 Verifique screenshot de erro na pasta screenshots/")