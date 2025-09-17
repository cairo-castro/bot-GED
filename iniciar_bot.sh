#!/bin/bash

# Script de início rápido para o bot EMSERH
# Facilita execução com diferentes opções

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
print_header() {
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║               🤖 BOT UPLOAD EMSERH                          ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verifica se ambiente virtual existe
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Ambiente virtual não encontrado!"
        print_info "Execute: python config_ambiente.py"
        exit 1
    fi
}

# Ativa ambiente virtual
activate_venv() {
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        print_success "Ambiente virtual ativado"
    else
        print_error "Não foi possível ativar ambiente virtual"
        exit 1
    fi
}

# Menu principal
show_menu() {
    echo
    echo "🎯 Escolha uma opção:"
    echo
    echo "  1) 🧪 Teste rápido (verificar configuração)"
    echo "  2) 🔐 Testar login no site"
    echo "  3) 👁️  Modo visual (ver bot em ação)"
    echo "  4) 📸 Teste com screenshots"
    echo "  5) 📝 Testar preenchimento de formulário"
    echo "  6) ✅ Validação completa"
    echo "  7) 🚀 Processar documentos"
    echo "  8) ⚙️  Configurar ambiente"
    echo "  9) 📚 Mostrar ajuda"
    echo "  10) 🚪 Sair"
    echo
}

# Executa teste rápido
run_quick_test() {
    print_info "Executando teste rápido..."
    python teste_rapido.py
}

# Executa teste de login
run_login_test() {
    print_info "Testando login no site EMSERH..."
    python teste_login_emserh.py
}

# Executa modo visual
run_visual_mode() {
    echo
    echo "Opções do modo visual:"
    echo "  1) Normal (1000ms entre ações)"
    echo "  2) Rápido (200ms entre ações)"
    echo "  3) Personalizado"
    echo "  4) Headless (sem interface)"
    echo "  5) Versão melhorada (recomendada)"
    echo
    read -p "Escolha (1-5): " visual_option

    case $visual_option in
        1)
            print_info "Executando modo visual normal..."
            python teste_visual_melhorado.py
            ;;
        2)
            print_info "Executando modo visual rápido..."
            python teste_visual_melhorado.py --fast
            ;;
        3)
            read -p "Velocidade em ms (ex: 500): " speed
            read -p "Tempo de espera em segundos (ex: 30): " wait_time
            print_info "Executando modo visual personalizado..."
            python teste_visual_melhorado.py --speed $speed --wait-time ${wait_time:-30}
            ;;
        4)
            print_info "Executando modo headless..."
            python teste_visual_melhorado.py --headless --fast
            ;;
        5)
            print_info "Executando versão melhorada (modo visual padrão)..."
            python teste_visual_melhorado.py --wait-time 30
            ;;
        *)
            print_error "Opção inválida"
            ;;
    esac
}

# Executa teste com screenshots
run_screenshot_test() {
    print_info "Executando teste com screenshots..."
    python teste_fluxo_ged.py
    echo
    print_info "Screenshots salvos em: screenshots/"
    ls -la screenshots/ | tail -5
}

# Executa teste de preenchimento de formulário
run_form_filling_test() {
    echo
    echo "📝 TESTE DE PREENCHIMENTO DE FORMULÁRIO"
    echo

    # Lista pastas disponíveis
    print_info "Pastas de documentos disponíveis:"
    echo
    local counter=1
    declare -a folders

    for folder in documentos/*/; do
        if [ -d "$folder" ] && [ "$(basename "$folder")" != "atestados" ] && [ "$(basename "$folder")" != "exames" ] && [ "$(basename "$folder")" != "prontuarios" ]; then
            folder_name=$(basename "$folder")
            folders[$counter]="$folder_name"

            # Conta arquivos na pasta
            file_count=$(find "$folder" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.doc" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l)

            echo "  $counter) $folder_name ($file_count arquivos)"
            ((counter++))
        fi
    done

    echo "  $counter) Voltar ao menu principal"
    echo

    read -p "Escolha uma pasta (1-$counter): " folder_choice

    if [ "$folder_choice" -eq "$counter" ]; then
        return
    fi

    if [ "$folder_choice" -ge 1 ] && [ "$folder_choice" -lt "$counter" ]; then
        selected_folder="${folders[$folder_choice]}"
        print_info "Pasta selecionada: $selected_folder"

        # Verifica se há arquivos na pasta
        file_count=$(find "documentos/$selected_folder" -type f \( -name "*.pdf" -o -name "*.docx" -o -name "*.doc" -o -name "*.jpg" -o -name "*.jpeg" -o -name "*.png" \) | wc -l)

        if [ "$file_count" -eq 0 ]; then
            print_warning "Pasta '$selected_folder' não tem documentos válidos"
            print_info "Adicione arquivos (.pdf, .docx, .doc, .jpg, .png) na pasta e tente novamente"
            return
        fi

        echo
        echo "Opções de teste:"
        echo "  1) Modo visual (ver preenchimento)"
        echo "  2) Modo headless (rápido)"
        echo "  3) Com screenshots detalhados"
        echo
        read -p "Escolha o modo (1-3): " test_mode

        case $test_mode in
            1)
                print_info "Executando teste visual para pasta: $selected_folder"
                SELECTED_FOLDER="$selected_folder" python teste_preenchimento_formulario.py
                ;;
            2)
                print_info "Executando teste headless para pasta: $selected_folder"
                SELECTED_FOLDER="$selected_folder" python teste_preenchimento_formulario.py --headless
                ;;
            3)
                print_info "Executando teste com screenshots para pasta: $selected_folder"
                SELECTED_FOLDER="$selected_folder" python teste_preenchimento_com_screenshots.py
                echo
                print_info "Screenshots salvos em: screenshots/"
                ls -la screenshots/ | tail -5
                ;;
            *)
                print_error "Opção inválida"
                ;;
        esac
    else
        print_error "Opção inválida"
    fi
}

# Executa validação completa
run_validation() {
    print_info "Executando validação completa..."
    python main.py --test-only
}

# Executa processamento
run_processing() {
    echo
    echo "Opções de processamento:"
    echo "  1) Normal (5 workers)"
    echo "  2) Personalizado"
    echo "  3) Force rescan"
    echo "  4) Debug mode"
    echo
    read -p "Escolha (1-4): " proc_option

    case $proc_option in
        1)
            print_info "Executando processamento normal..."
            python main.py
            ;;
        2)
            read -p "Número de workers (1-10): " workers
            read -p "Caminho dos documentos (Enter para padrão): " docs_path

            cmd="python main.py --workers $workers"
            if [ ! -z "$docs_path" ]; then
                cmd="$cmd --documents $docs_path"
            fi

            print_info "Executando: $cmd"
            eval $cmd
            ;;
        3)
            print_info "Executando com force rescan..."
            python main.py --force-rescan
            ;;
        4)
            print_info "Executando modo debug..."
            python main.py --log-level DEBUG
            ;;
        *)
            print_error "Opção inválida"
            ;;
    esac
}

# Configura ambiente
run_config() {
    print_info "Executando configurador de ambiente..."
    python config_ambiente.py
}

# Mostra ajuda
show_help() {
    echo
    echo "📚 AJUDA - Bot Upload EMSERH"
    echo
    echo "🎯 Scripts disponíveis:"
    echo "  • teste_rapido.py        - Teste básico de configuração"
    echo "  • teste_login_emserh.py  - Teste de login específico"
    echo "  • teste_visual_ged.py    - Modo visual interativo"
    echo "  • teste_fluxo_ged.py     - Teste com screenshots"
    echo "  • main.py               - Processamento principal"
    echo "  • config_ambiente.py    - Configurador de ambiente"
    echo
    echo "📁 Estrutura de documentos:"
    echo "  documentos/"
    echo "  ├── atestados/     - Atestados médicos"
    echo "  ├── prontuarios/   - Prontuários de pacientes"
    echo "  └── exames/        - Exames e laudos"
    echo
    echo "🔧 Arquivos importantes:"
    echo "  • .env              - Configurações (credenciais)"
    echo "  • GUIA_COMPLETO.md  - Documentação completa"
    echo "  • logs/             - Logs de execução"
    echo "  • screenshots/      - Capturas de tela"
    echo
    echo "💡 Dicas:"
    echo "  • Configure o .env antes de usar"
    echo "  • Use modo visual para debug"
    echo "  • Verifique logs em caso de erro"
    echo "  • Screenshots são salvos automaticamente"
    echo
}

# Função principal
main() {
    print_header

    # Verifica ambiente virtual
    check_venv
    activate_venv

    while true; do
        show_menu
        read -p "Escolha uma opção (1-10): " choice

        case $choice in
            1)
                run_quick_test
                ;;
            2)
                run_login_test
                ;;
            3)
                run_visual_mode
                ;;
            4)
                run_screenshot_test
                ;;
            5)
                run_form_filling_test
                ;;
            6)
                run_validation
                ;;
            7)
                run_processing
                ;;
            8)
                run_config
                ;;
            9)
                show_help
                ;;
            10)
                print_success "Até logo!"
                exit 0
                ;;
            *)
                print_error "Opção inválida. Escolha entre 1-10."
                ;;
        esac

        echo
        read -p "Pressione Enter para continuar..."
    done
}

# Verifica se está no diretório correto
if [ ! -f "main.py" ]; then
    print_error "Execute este script no diretório do bot (onde está o main.py)"
    exit 1
fi

# Executa função principal
main