# 🤖 Guia Completo - Bot de Upload EMSERH

## 📋 Índice

1. [Pré-requisitos](#-pré-requisitos)
2. [Instalação](#-instalação)
3. [Configuração](#-configuração)
4. [Como Usar](#-como-usar)
5. [Modos de Execução](#-modos-de-execução)
6. [Testes Disponíveis](#-testes-disponíveis)
7. [Estrutura de Documentos](#-estrutura-de-documentos)
8. [Solução de Problemas](#-solução-de-problemas)

---

## 🔧 Pré-requisitos

### Sistema Operacional
- ✅ **Linux** (Ubuntu/Debian recomendado)
- ✅ **WSL2** (Windows Subsystem for Linux)
- ⚠️ **Windows** (parcialmente suportado)

### Software Necessário
- **Python 3.9+** (recomendado: 3.11+)
- **MariaDB/MySQL** (com usuário root configurado)
- **Git** (para clonar o projeto)

---

## 🚀 Instalação

### Opção 1: Instalação Automática (Linux)

```bash
# 1. Clone o projeto
git clone <seu-repositorio>
cd bot

# 2. Execute o instalador automático
chmod +x install.sh
./install.sh
```

### Opção 2: Instalação Manual

```bash
# 1. Crie ambiente virtual Python
python3 -m venv venv
source venv/bin/activate

# 2. Instale dependências
pip install -r requirements.txt

# 3. Instale browser do Playwright
playwright install chromium

# 4. Execute setup do projeto
python setup.py
```

---

## ⚙️ Configuração

### 1. Configure o Banco de Dados

**Opção A: Usuário root com senha**
```bash
mysql -u root -p < setup_database.sql
```

**Opção B: Script interativo**
```bash
python criar_banco_manual.py
```

### 2. Configure Credenciais

Edite o arquivo `.env`:
```env
# Banco de Dados
DB_HOST=localhost
DB_USER=medbot_user
DB_PASS=MedBot2024!
DB_NAME=uploads_db

# Site EMSERH
SITE_USER=52290832391
SITE_PASS=123456
SITE_BASE_URL=https://gpc-hml.emserh.ma.gov.br

# Configurações
DOCUMENTS_BASE_PATH=./documentos
MAX_WORKERS=5
```

### 3. Organize Documentos

```
documentos/
├── atestados/          # Atestados médicos
│   ├── arquivo1.pdf
│   └── arquivo2.jpg
├── prontuarios/        # Prontuários
│   └── prontuario1.pdf
└── exames/            # Exames e laudos
    └── exame1.pdf
```

---

## 🎯 Como Usar

### Teste Rápido do Sistema
```bash
source venv/bin/activate
python teste_rapido.py
```

### Validação Completa
```bash
python main.py --test-only
```

### Processamento de Documentos
```bash
# Execução normal
python main.py

# Com configurações específicas
python main.py --workers 3 --documents /caminho/documentos

# Forçar nova varredura
python main.py --force-rescan
```

---

## 👁️ Modos de Execução

### 1. Modo Visual (Ver Bot em Ação)

```bash
# Visualização normal
python teste_visual_ged.py

# Execução rápida
python teste_visual_ged.py --fast

# Velocidade personalizada
python teste_visual_ged.py --speed 500

# Modo headless mesmo assim
python teste_visual_ged.py --headless
```

### 2. Modo Debug com Screenshots

```bash
# Testa login + navegação + screenshots
python teste_fluxo_ged.py

# Login simples
python teste_login_emserh.py
```

### 3. Modo Produção

```bash
# Processamento completo
python main.py

# Com logging detalhado
python main.py --log-level DEBUG
```

---

## 🧪 Testes Disponíveis

| Script | Descrição | Visual | Screenshots |
|--------|-----------|--------|-------------|
| `teste_rapido.py` | ✅ Teste básico de configuração | ❌ | ❌ |
| `teste_login_emserh.py` | 🔐 Teste específico de login | ❌ | ❌ |
| `teste_fluxo_ged.py` | 📁 Teste completo com screenshots | ❌ | ✅ |
| `teste_visual_ged.py` | 👁️ Teste visual interativo | ✅ | ❌ |
| `main.py --test-only` | 🔍 Validação completa do sistema | ❌ | ❌ |

### Executando Testes

```bash
# Ativar ambiente
source venv/bin/activate

# Teste básico
python teste_rapido.py

# Teste visual (recomendado para debug)
python teste_visual_ged.py

# Teste com screenshots
python teste_fluxo_ged.py

# Validação completa
python main.py --test-only
```

---

## 📁 Estrutura de Documentos

### Tipos Suportados
- **PDF**: `.pdf`
- **Imagens**: `.jpg`, `.jpeg`, `.png`, `.tiff`, `.tif`
- **DICOM**: `.dcm`

### Organização por Pasta

```
documentos/
├── atestados/          # → Fluxo de atestados médicos
├── prontuarios/        # → Fluxo de prontuários
├── exames/            # → Fluxo de exames/laudos
└── [tipo_customizado]/ # → Detecta automaticamente
```

### Nomenclatura de Arquivos
- ✅ `atestado_001.pdf`
- ✅ `prontuario-paciente-123.pdf`
- ✅ `exame_sangue_2024.jpg`
- ❌ `arquivo<>inválido?.pdf` (caracteres especiais)

---

## 🔧 Solução de Problemas

### ❌ Erro de Conexão com Banco

```bash
# Verifica se MariaDB está rodando
sudo systemctl status mariadb

# Testa conexão manual
mysql -u medbot_user -pMedBot2024! uploads_db -e "SELECT 1;"

# Recria banco se necessário
mysql -u root -p < setup_database.sql
```

### ❌ Erro de Login no Site

1. **Verifica credenciais no `.env`**
2. **Testa login manual**: `python teste_login_emserh.py`
3. **Modo visual para debug**: `python teste_visual_ged.py`
4. **Verifica screenshots**: pasta `screenshots/`

### ❌ Dependências Não Instaladas

```bash
# Reinstala dependências
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Verifica instalação
python -c "import playwright, mysql.connector, pandas; print('OK')"
```

### ❌ Erro de Permissões

```bash
# Linux: Instala dependências do sistema
sudo apt update
sudo apt install -y python3-venv python3-pip mariadb-server

# Permissões de arquivos
chmod +x *.py
chmod +x install.sh
```

### ❌ Browser Não Abre (Modo Visual)

```bash
# Instala dependências gráficas (Linux)
sudo apt install -y xvfb

# Testa headless primeiro
python teste_visual_ged.py --headless

# Se WSL2, configura X11
export DISPLAY=:0
```

---

## 📊 Relatórios e Logs

### Localização dos Arquivos

```
logs/
├── main.log              # Log principal
├── worker_0.log          # Log do worker 0
├── worker_1.log          # Log do worker 1
└── ...

screenshots/
├── login_error_*.png     # Screenshots de erro
├── 01_apos_login_*.png   # Screenshots do fluxo
└── ...

relatorio_uploads_*.csv   # Relatório final
```

### Analisando Relatórios

```bash
# Ver últimos logs
tail -f logs/main.log

# Estatísticas rápidas
python -c "
import pandas as pd
df = pd.read_csv('relatorio_uploads_*.csv')
print(df['Status'].value_counts())
"
```

---

## 🚀 Comandos Úteis

### Execução Rápida
```bash
# Ativar ambiente + teste
source venv/bin/activate && python teste_visual_ged.py

# Processamento completo
source venv/bin/activate && python main.py

# Debug com logs
source venv/bin/activate && python main.py --log-level DEBUG
```

### Limpeza
```bash
# Limpa logs antigos
rm -rf logs/* screenshots/*

# Limpa registros pendentes no banco
mysql -u medbot_user -pMedBot2024! uploads_db -e "DELETE FROM uploads WHERE status='pendente';"
```

### Backup
```bash
# Backup do banco
mysqldump -u medbot_user -pMedBot2024! uploads_db > backup.sql

# Backup dos documentos
tar -czf documentos_backup.tar.gz documentos/
```

---

## 🆘 Suporte

### Verificação Rápida
1. **Sistema**: `python teste_rapido.py`
2. **Login**: `python teste_login_emserh.py`
3. **Visual**: `python teste_visual_ged.py`
4. **Completo**: `python main.py --test-only`

### Logs Importantes
- 📋 **Configuração**: `logs/main.log`
- 🔧 **Processamento**: `logs/worker_*.log`
- 📸 **Visual**: `screenshots/`

### Contato
- 📧 Issues: Criar issue no repositório
- 📚 Documentação: Este arquivo
- 🐛 Debug: Screenshots + logs

---

**Desenvolvido para EMSERH - Sistema GPC** 🏥
*Bot automatizado para upload de documentos médicos*