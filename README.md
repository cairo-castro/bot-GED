# 🤖 Bot GED EMSERH

Bot automatizado para upload em lote de documentos médicos no sistema GED (Gestão Eletrônica de Documentos) da EMSERH - Empresa Maranhense de Serviços Hospitalares.

## 🚀 Características

- **Processamento em Lote**: Processa todos os arquivos de uma pasta automaticamente
- **13 Tipos de Documentos**: Suporte completo para todas as categorias do GED EMSERH
- **Interface Interativa**: Menu bash para testes e operações
- **Modos de Operação**: Visual, headless e com screenshots para debug
- **Mapeamento Automático**: Tipos de documento mapeados por pasta
- **Formulário Inteligente**: Preenchimento automático com validação
- **Screenshots Automáticos**: Captura de tela em cada etapa para debug
- **Relatórios Detalhados**: Resumo completo de sucessos e falhas

## 📋 Pré-requisitos

- Python 3.11+
- Playwright (instalado automaticamente)
- Sistema operacional: Windows ou Linux
- Acesso ao sistema GED EMSERH

## 🛠️ Instalação Rápida

1. **Clone o projeto**:
```bash
git clone https://github.com/cairo-castro/bot-GED.git
cd bot-GED
```

2. **Execute o configurador automático**:
```bash
chmod +x config_ambiente.py
python config_ambiente.py
```

3. **Configure suas credenciais**:
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais do GED EMSERH
```

4. **Teste a instalação**:
```bash
./iniciar_bot.sh
# Escolha opção 1: Teste rápido
```

## 📁 Estrutura de Documentos GED EMSERH

Organize seus documentos nas 13 pastas oficiais do sistema:

```
documentos/
├── POLITICAS/                          # Políticas institucionais
├── DIRETRIZ/                           # Diretrizes
├── FLUXOGRAMA/                         # Fluxogramas de processo
├── INSTRUMENTAL/                       # Instrumentais
├── MANUAL/                             # Manuais
├── MAPEAMENTO_DE_PROCESSO/             # Mapeamentos de processo
├── NORMA_E_ROTINA/                     # Normas e rotinas
├── NORMA_ZERO/                         # Normas zero
├── PLANO_DE_CONTINGENCIA/              # Planos de contingência
├── PROCEDIMENTO_OPERACIONAL_PADRAO/    # POPs
├── PROTOCOLO/                          # Protocolos
├── REGIMENTO/                          # Regimentos
└── REGULAMENTO/                        # Regulamentos
```

**Tipos de arquivo suportados**: `.pdf`, `.docx`, `.doc`, `.jpg`, `.jpeg`, `.png`

## ⚙️ Configuração (.env)

```env
# Sistema GED EMSERH
SITE_BASE_URL=https://gpc-hml.emserh.ma.gov.br
SITE_USER=52290832391
SITE_PASS=123456

# Configurações opcionais
MAX_WORKERS=5
DEFAULT_WAIT_TIME=30
RETRY_ATTEMPTS=3
```

## 🚦 Como Usar

### Menu Interativo (Recomendado)
```bash
./iniciar_bot.sh
```

**Opções disponíveis:**
1. 🧪 **Teste rápido** - Verificar configuração
2. 🔐 **Testar login** - Validar credenciais EMSERH
3. 👁️ **Modo visual** - Ver bot em ação (debug)
4. 📸 **Teste com screenshots** - Capturar cada etapa
5. 📝 **Testar preenchimento** - Escolher pasta e processar
6. ✅ **Validação completa** - Teste completo do sistema
7. 🚀 **Processar documentos** - Processamento em produção
8. ⚙️ **Configurar ambiente** - Reinstalar dependências
9. 📚 **Mostrar ajuda** - Documentação e dicas

### Uso Direto
```bash
# Testar pasta específica
SELECTED_FOLDER="POLITICAS" python teste_preenchimento_formulario.py

# Modo headless (mais rápido)
SELECTED_FOLDER="POLITICAS" python teste_preenchimento_formulario.py --headless

# Com screenshots detalhados
SELECTED_FOLDER="POLITICAS" python teste_preenchimento_com_screenshots.py
```

### Argumentos Disponíveis

| Argumento | Descrição | Padrão |
|-----------|-----------|--------|
| `--documents` `-d` | Caminho para documentos | `./documentos` |
| `--workers` `-w` | Número de workers paralelos | `5` |
| `--force-rescan` | Força nova varredura | `False` |
| `--test-only` | Apenas testa configurações | `False` |
| `--log-level` | Nível de logging | `INFO` |
| `--no-log-file` | Não salva logs em arquivo | `False` |

## 📊 Relatórios

O sistema gera automaticamente:

- **CSV com todos os arquivos**: Status, data de envio, erros
- **Screenshots de erro**: Capturas automáticas para debug
- **Logs detalhados**: Por worker e geral

Exemplo de relatório:
```csv
Nome do Arquivo,Caminho Completo,Tipo de Documento,Status,Data/Hora Envio,Mensagem de Erro
atestado001.pdf,/documentos/atestados/atestado001.pdf,atestados,enviado,2024-01-15 10:30:15,
exame002.pdf,/documentos/exames/exame002.pdf,exames,erro,2024-01-15 10:32:22,Elemento não encontrado
```

## 🔧 Personalização de Fluxos

Para adicionar novos tipos de documento, crie um arquivo em `flows/`:

```python
# flows/novo_tipo.py
from .base_flow import BaseFlow

class NovoTipoFlow(BaseFlow):
    def navigate_to_upload_page(self) -> bool:
        # Lógica específica de navegação
        pass

    def upload_file(self, file_path: str) -> bool:
        # Lógica específica de upload
        pass
```

E registre em `flows/__init__.py`.

## 📈 Performance

- **Processamento**: ~50-100 arquivos por hora (depende do site)
- **Paralelização**: 5 workers simultâneos por padrão
- **Retry**: 3 tentativas com backoff exponencial
- **Timeout**: 30s por upload

## 🐛 Solução de Problemas

### Erro de Conexão com Banco
```bash
# Verificar se MariaDB está rodando
systemctl status mariadb

# Testar conexão manual
mysql -h localhost -u bot_user -p uploads_db
```

### Erro de Login no Site
1. Verifique credenciais no `.env`
2. Analise screenshots em `screenshots/`
3. Verifique se não há captcha/2FA ativo

### Documentos Não Encontrados
```bash
# Verificar estrutura de pastas
ls -la documentos/
```

### Performance Baixa
- Reduza número de workers se o site for lento
- Aumente timeout para sites instáveis
- Verifique conectividade de rede

## 📝 Logs

Os logs são salvos em:
- `logs/main.log` - Log principal
- `logs/worker_X.log` - Log por worker
- `screenshots/` - Capturas de erro

## 🔒 Segurança

- **Credenciais**: Nunca commitadas (use .env)
- **Headless**: Navegador invisível por padrão
- **Isolamento**: Cada worker em processo separado
- **Timeout**: Previne travamentos indefinidos

## 📞 Suporte

Para problemas ou melhorias:

1. Verifique os logs em `logs/`
2. Analise screenshots de erro
3. Execute com `--test-only` para validar config
4. Use `--log-level DEBUG` para mais detalhes

## 🏗️ Arquitetura

```
main.py              # Orchestrator principal
├── controller.py    # Coordenação de processos paralelos
├── worker.py        # Processamento individual
├── db.py           # Gerenciamento de banco
└── flows/          # Fluxos específicos por tipo
    ├── base_flow.py    # Classe base
    ├── atestados.py    # Fluxo para atestados
    ├── prontuarios.py  # Fluxo para prontuários
    └── exames.py       # Fluxo para exames
```

## 📄 Licença

Este projeto é para uso interno e automação de processos legítimos.

---

**Desenvolvido para automação eficiente e confiável de uploads médicos** 🏥🤖