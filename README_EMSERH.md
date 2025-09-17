# 🏥 Bot de Upload EMSERH - Sistema GPC

Automação completa para upload de documentos médicos no sistema GPC da EMSERH (Empresa Maranhense de Serviços Hospitalares).

## ✨ Recursos Principais

- 🤖 **Automação Completa**: Login + navegação + upload automatizado
- 👁️ **Modo Visual**: Ver o bot em ação (ideal para debug)
- 📸 **Screenshots Automáticos**: Capturas de erro para diagnóstico
- 🔄 **Retry Inteligente**: Tentativas automáticas com backoff exponencial
- 📊 **Relatórios Detalhados**: CSV com estatísticas de upload
- 🎯 **Interface Simples**: Scripts interativos para facilitar uso

## 🚀 Início Rápido

### 1. Configure o Ambiente
```bash
# Configure automaticamente
python config_ambiente.py

# OU manualmente
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 2. Configure Credenciais
Edite o arquivo `.env`:
```env
# Site EMSERH
SITE_USER=52290832391
SITE_PASS=123456
SITE_BASE_URL=https://gpc-hml.emserh.ma.gov.br

# Banco de Dados (já configurado)
DB_USER=medbot_user
DB_PASS=MedBot2024!
DB_NAME=uploads_db
```

### 3. Execute o Bot
```bash
# Script interativo (RECOMENDADO)
./iniciar_bot.sh

# OU comandos diretos
source venv/bin/activate
python teste_visual_ged.py  # Ver bot em ação
```

## 👁️ Modo Visual - Ver Bot em Ação

```bash
# Ativar ambiente
source venv/bin/activate

# Modo visual normal (1000ms entre ações)
python teste_visual_ged.py

# Modo rápido (200ms entre ações)
python teste_visual_ged.py --fast

# Velocidade personalizada
python teste_visual_ged.py --speed 500

# Modo headless (sem interface)
python teste_visual_ged.py --headless
```

### 📺 O que você verá:
1. ✅ Navegador abrindo e indo para página de login
2. ✅ Campos sendo preenchidos automaticamente
3. ✅ Login sendo realizado
4. ✅ Navegação para página GED
5. ✅ Clique no botão "Nova Solicitação"
6. ✅ Modal abrindo com formulário

## 🧪 Testes Disponíveis

| Script | Descrição | Visual | Tempo |
|--------|-----------|--------|-------|
| `teste_rapido.py` | Teste básico de configuração | ❌ | ~10s |
| `teste_login_emserh.py` | Teste específico de login | ❌ | ~15s |
| `teste_visual_ged.py` | **Ver bot em ação** | ✅ | ~30s |
| `teste_fluxo_ged.py` | Teste com screenshots | ❌ | ~20s |

### Executar Testes
```bash
# Ativar ambiente
source venv/bin/activate

# Teste básico
python teste_rapido.py

# Ver bot funcionando (RECOMENDADO)
python teste_visual_ged.py

# Teste com capturas de tela
python teste_fluxo_ged.py
```

## 📁 Estrutura de Documentos

```
documentos/
├── atestados/          # Atestados médicos
│   ├── atestado001.pdf
│   └── atestado002.jpg
├── prontuarios/        # Prontuários de pacientes
│   └── prontuario001.pdf
└── exames/            # Exames e laudos
    └── exame001.pdf
```

**Tipos suportados**: PDF, JPG, JPEG, PNG, TIFF, DICOM

## 🎯 Scripts Interativos

### Script Principal (Recomendado)
```bash
./iniciar_bot.sh
```

**Opções disponíveis**:
1. 🧪 Teste rápido
2. 🔐 Testar login
3. 👁️ Modo visual
4. 📸 Screenshots
5. ✅ Validação completa
6. 🚀 Processar documentos
7. ⚙️ Configurar ambiente
8. 📚 Ajuda

### Configurador de Ambiente
```bash
python config_ambiente.py
```

## 🔧 Configuração Manual

### Banco de Dados
```bash
# Com usuário root
mysql -u root -p < setup_database.sql

# Script interativo
python criar_banco_manual.py
```

### Teste de Configuração
```bash
source venv/bin/activate
python teste_rapido.py
```

## 📊 Fluxo Atual Implementado

✅ **Login no Sistema**
- Site: https://gpc-hml.emserh.ma.gov.br/login
- Usuário: 52290832391
- Senha: 123456

✅ **Navegação GED**
- Acesso: https://gpc-hml.emserh.ma.gov.br/ged
- Clique: Botão "Nova Solicitação" (`#btnNovaSolicitacao`)

✅ **Modal Aberto**
- Formulário com campos:
  - Título
  - Tipo de Documento (dropdown)
  - Onde se aplica (dropdown)
  - Perfil (dropdown)
  - Justificativa
  - Botão Salvar

🚧 **Próximos Passos** (em desenvolvimento):
- Preenchimento automático do formulário
- Upload do arquivo
- Confirmação de envio

## 📸 Screenshots e Logs

```
logs/
├── main.log              # Log principal
└── worker_*.log          # Logs dos workers

screenshots/
├── 01_apos_login_*.png   # Após login
├── 02_pagina_ged_*.png   # Página GED
└── 03_apos_clique_*.png  # Modal aberto
```

## 🆘 Solução de Problemas

### ❌ Erro de Login
```bash
# Teste login específico
python teste_login_emserh.py

# Modo visual para debug
python teste_visual_ged.py
```

### ❌ Banco de Dados
```bash
# Teste conexão
mysql -u medbot_user -pMedBot2024! uploads_db -e "SELECT 1;"

# Reconfigurar banco
mysql -u root -p < setup_database.sql
```

### ❌ Dependências
```bash
# Reinstalar
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium
```

### 🐧 Linux/WSL
```bash
# Dependências gráficas
sudo apt install xvfb

# WSL - configurar X11
export DISPLAY=:0
```

## 💡 Dicas de Uso

### Para Desenvolvimento
- Use `python teste_visual_ged.py` para ver o que está acontecendo
- Screenshots são salvos automaticamente em caso de erro
- Logs detalhados em `logs/main.log`

### Para Produção
- Use `python main.py` para processamento completo
- Configure `MAX_WORKERS` no `.env` baseado na capacidade do servidor
- Monitor logs em tempo real: `tail -f logs/main.log`

### Para Debug
- Modo visual: `python teste_visual_ged.py`
- Screenshots: `python teste_fluxo_ged.py`
- Logs debug: `python main.py --log-level DEBUG`

## 📞 Suporte

1. **Configuração**: Execute `python config_ambiente.py`
2. **Teste Rápido**: Execute `python teste_rapido.py`
3. **Visual Debug**: Execute `python teste_visual_ged.py`
4. **Documentação**: Ver `GUIA_COMPLETO.md`

---

**Desenvolvido para EMSERH** 🏥
*Sistema GPC - Gestão de Processos e Contratos*