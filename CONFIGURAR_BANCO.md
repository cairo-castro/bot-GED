# 🗄️ Configuração do Banco de Dados

## Opção 1: Executar com usuário root do MySQL

Se você tem acesso root ao MySQL/MariaDB, execute:

```bash
# Se você sabe a senha do root
mysql -u root -p < setup_database.sql

# Ou se o root não tem senha
mysql -u root < setup_database.sql
```

## Opção 2: Executar via sudo (se configurado com socket auth)

```bash
sudo mysql < setup_database.sql
```

## Opção 3: Manual via linha de comando

Entre no MySQL como administrador e execute os comandos:

```sql
-- Cria o banco
CREATE DATABASE uploads_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Cria usuário com senha segura
CREATE USER 'medbot_user'@'localhost' IDENTIFIED BY 'MedBot2024!';

-- Concede permissões
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, ALTER, INDEX ON uploads_db.* TO 'medbot_user'@'localhost';

-- Atualiza privilégios
FLUSH PRIVILEGES;
```

## Opção 4: Usando outro usuário admin

Se você tem outro usuário com privilégios administrativos:

```bash
mysql -u SEU_USUARIO_ADMIN -p < setup_database.sql
```

## Verificar se funcionou

Teste a conexão:

```bash
mysql -u medbot_user -pMedBot2024! -D uploads_db -e "SELECT 'Conexão OK!' AS status;"
```

## Credenciais Criadas

- **Usuário**: `medbot_user`
- **Senha**: `MedBot2024!`
- **Banco**: `uploads_db`
- **Host**: `localhost`

## Segurança

✅ **Usuário específico**: Não usa root
✅ **Permissões limitadas**: Apenas no banco uploads_db
✅ **Senha forte**: Contém maiúsculas, números e símbolos
✅ **Acesso local**: Apenas localhost

## Após configurar o banco

1. Teste com o nosso script:
```bash
source venv/bin/activate
python run_tests.py
```

2. Se o teste passar, execute:
```bash
python main.py --test-only
```

## Problemas comuns

**Erro de acesso negado**: Verifique se você tem privilégios administrativos
**Usuário já existe**: Normal, o script usa IF NOT EXISTS
**Banco já existe**: Normal, o script usa IF NOT EXISTS