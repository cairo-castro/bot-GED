# 📋 Mapeamento de Tipos de Documentos - GPC EMSERH

## 🎯 Mapeamento Pasta → Tipo no Sistema

| Pasta | Tipo no Dropdown | Descrição |
|-------|------------------|-----------|
| `POLITICAS` | Políticas | Políticas institucionais |
| `DIRETRIZ` | Diretriz | Diretrizes médicas e assistenciais |
| `FLUXOGRAMA` | Fluxograma | Fluxogramas de processos |
| `INSTRUMENTAL` | Instrumental | Documentos instrumentais |
| `MANUAL` | Manual | Manuais de procedimentos |
| `MAPEAMENTO_DE_PROCESSO` | Mapeamento de Processo | Mapeamentos de processo |
| `NORMA_E_ROTINA` | Norma e Rotina | Normas e rotinas operacionais |
| `NORMA_ZERO` | Norma Zero | Normas zero |
| `PLANO_DE_CONTINGENCIA` | Plano de Contingência | Planos de contingência |
| `PROCEDIMENTO_OPERACIONAL_PADRAO` | Procedimento Operacional Padrão | POPs |
| `PROTOCOLO` | Protocolo | Protocolos médicos |
| `REGIMENTO` | Regimento | Regimentos |
| `REGULAMENTO` | Regulamento | Regulamentos |

## 🚀 Implementação no Bot

### Função de Mapeamento
```python
def get_document_type_from_folder(folder_name: str) -> str:
    """Mapeia nome da pasta para tipo no sistema"""

    mapping = {
        'POLITICAS': 'Políticas',
        'DIRETRIZ': 'Diretriz',
        'FLUXOGRAMA': 'Fluxograma',
        'INSTRUMENTAL': 'Instrumental',
        'MANUAL': 'Manual',
        'MAPEAMENTO_DE_PROCESSO': 'Mapeamento de Processo',
        'NORMA_E_ROTINA': 'Norma e Rotina',
        'NORMA_ZERO': 'Norma Zero',
        'PLANO_DE_CONTINGENCIA': 'Plano de Contingência',
        'PROCEDIMENTO_OPERACIONAL_PADRAO': 'Procedimento Operacional Padrão',
        'PROTOCOLO': 'Protocolo',
        'REGIMENTO': 'Regimento',
        'REGULAMENTO': 'Regulamento'
    }

    return mapping.get(folder_name.upper(), folder_name)
```

## 📝 Campos do Formulário

### Campos Obrigatórios
1. **Título**: Nome do documento (extraído do arquivo)
2. **Tipo de Documento**: Seleção do dropdown (baseado na pasta)
3. **Onde se aplica**: A definir (pode ser padrão)
4. **Perfil**: A definir (pode ser padrão)
5. **Justificativa**: Texto padrão ou baseado no tipo

### Valores Padrão Sugeridos
```python
default_values = {
    'onde_se_aplica': 'Geral',  # ou valor específico
    'perfil': 'Administrativo',  # ou valor específico
    'justificativa_template': 'Upload automático de {tipo_documento} para organização e padronização dos processos institucionais.'
}
```

## 🎯 Próximos Passos de Desenvolvimento

### 1. Preenchimento Automático do Formulário
- [x] Modal detectado e aberto
- [ ] Preencher campo "Título" com nome do arquivo
- [ ] Selecionar "Tipo de Documento" baseado na pasta
- [ ] Definir valores padrão para "Onde se aplica" e "Perfil"
- [ ] Gerar justificativa automática

### 2. Upload do Arquivo
- [ ] Localizar campo de upload de arquivo
- [ ] Fazer upload do documento
- [ ] Aguardar confirmação

### 3. Finalização
- [ ] Clicar em "Salvar"
- [ ] Verificar sucesso/erro
- [ ] Atualizar banco de dados

## 📊 Prioridade de Processamento

1. **POLITICAS** (5 documentos prontos)
2. **PROTOCOLO**
3. **PROCEDIMENTO_OPERACIONAL_PADRAO**
4. **DIRETRIZ**
5. Demais tipos em ordem alfabética

## 🔧 Teste Atual

### Status do Fluxo
- ✅ Login no sistema
- ✅ Navegação para GED
- ✅ Clique em "Nova Solicitação"
- ✅ Modal aberto com formulário
- 🚧 Preenchimento automático (próximo passo)

### Comando de Teste
```bash
# Ver bot em ação até o modal
python teste_visual_melhorado.py

# Próximo: implementar preenchimento
```