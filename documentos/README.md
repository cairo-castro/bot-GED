# 📁 Estrutura de Documentos - Sistema GPC EMSERH

Organize seus documentos médicos da seguinte forma:

## 📋 Tipos de Documentos Suportados

```
documentos/
├── POLITICAS/                          # ✅ Políticas institucionais
├── DIRETRIZ/                          # Diretrizes médicas
├── FLUXOGRAMA/                        # Fluxogramas de processos
├── INSTRUMENTAL/                      # Documentos instrumentais
├── MANUAL/                           # Manuais de procedimentos
├── MAPEAMENTO_DE_PROCESSO/           # Mapeamentos de processo
├── NORMA_E_ROTINA/                   # Normas e rotinas
├── NORMA_ZERO/                       # Normas zero
├── PLANO_DE_CONTINGENCIA/            # Planos de contingência
├── PROCEDIMENTO_OPERACIONAL_PADRAO/  # POPs
├── PROTOCOLO/                        # Protocolos médicos
├── REGIMENTO/                        # Regimentos
├── REGULAMENTO/                      # Regulamentos
├── atestados/                        # Atestados médicos (exemplo)
├── exames/                          # Exames (exemplo)
└── prontuarios/                     # Prontuários (exemplo)
```

## 📝 Tipos de Arquivo Suportados

- `.pdf` - Documentos PDF
- `.docx` - Documentos Word
- `.jpg`, `.jpeg` - Imagens JPEG
- `.png` - Imagens PNG
- `.tiff`, `.tif` - Imagens TIFF

## 🎯 Como Funciona

### Mapeamento Automático
O sistema automaticamente detecta o tipo de documento baseado na pasta:

| Pasta | Tipo no Sistema | Exemplo |
|-------|----------------|---------|
| `POLITICAS` | Políticas | POL 001 POLITICA INSTITUCIONAL... |
| `DIRETRIZ` | Diretriz | DIR 001 Diretriz de Atendimento... |
| `PROTOCOLO` | Protocolo | PROT 001 Protocolo de Emergência... |
| `MANUAL` | Manual | MAN 001 Manual de Procedimentos... |

### Nomenclatura Recomendada
```
POLITICAS/
├── POL_001_POLITICA_INSTITUCIONAL.docx
├── POL_002_SEGURANCA_PACIENTE.docx
└── POL_003_QUALIDADE_ASSISTENCIAL.pdf

PROTOCOLO/
├── PROT_001_EMERGENCIA_CARDIACA.pdf
├── PROT_002_PROCEDIMENTO_CIRURGICO.docx
└── PROT_003_MEDICACAO_ALTA_VIGILANCIA.pdf
```

## 🚀 Processamento

### Ordem de Prioridade
1. **POLITICAS** (primeira pasta a ser processada)
2. **PROTOCOLO**
3. **PROCEDIMENTO_OPERACIONAL_PADRAO**
4. **DIRETRIZ**
5. Demais tipos em ordem alfabética

### Execução
```bash
# Ativar ambiente
source venv/bin/activate

# Modo visual (ver bot funcionando)
python teste_visual_melhorado.py

# Processamento completo
python main.py

# Com configurações específicas
python main.py --workers 3
```

## 📊 Estatísticas Atuais

```
POLITICAS: 5 documentos (.docx)
DIRETRIZ: 0 documentos
PROTOCOLO: 0 documentos
... (outras pastas vazias)
```

## 🔧 Configuração do Sistema

O bot está configurado para:
- **Site**: https://gpc-hml.emserh.ma.gov.br
- **Usuário**: 52290832391
- **Fluxo**: Login → GED → Nova Solicitação → Upload

### Próximos Passos de Desenvolvimento
1. ✅ Login e navegação
2. ✅ Abertura do modal de solicitação
3. 🚧 Preenchimento do formulário por tipo
4. 🚧 Upload do arquivo
5. 🚧 Confirmação de envio

## 💡 Dicas

### Para Adicionar Documentos
1. Coloque arquivos na pasta correspondente ao tipo
2. Use nomenclatura clara e padronizada
3. Evite caracteres especiais nos nomes

### Para Testar
```bash
# Teste visual para ver o bot em ação
python teste_visual_melhorado.py

# Teste específico de uma pasta
python main.py --documents documentos/POLITICAS
```

### Para Monitorar
- **Logs**: `logs/main.log`
- **Screenshots**: `screenshots/`
- **Relatórios**: `relatorio_uploads_*.csv`

---

**Sistema configurado para GPC EMSERH** 🏥
*Gestão de Processos e Contratos*