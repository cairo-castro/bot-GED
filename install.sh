#!/bin/bash

# Script de instalação para o Robô de Upload de Documentos Médicos
# Compatível com Ubuntu/Debian e CentOS/RHEL

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                                                              ║"
echo "║               🏥 INSTALAÇÃO DO ROBÔ DE UPLOAD                ║"
echo "║                                                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Detecta o sistema operacional
if command -v apt-get >/dev/null 2>&1; then
    DISTRO="debian"
    INSTALL_CMD="apt-get install -y"
    UPDATE_CMD="apt-get update"
elif command -v yum >/dev/null 2>&1; then
    DISTRO="redhat"
    INSTALL_CMD="yum install -y"
    UPDATE_CMD="yum update"
else
    echo "❌ Sistema operacional não suportado"
    exit 1
fi

echo "🔍 Sistema detectado: $DISTRO"

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 1. Atualiza sistema
echo "📦 Atualizando sistema..."
sudo $UPDATE_CMD

# 2. Instala Python 3.11+ se necessário
echo "🐍 Verificando Python..."
if command_exists python3.11; then
    PYTHON_CMD="python3.11"
    echo "✅ Python 3.11 encontrado"
elif command_exists python3.10; then
    PYTHON_CMD="python3.10"
    echo "✅ Python 3.10 encontrado (compatível)"
elif command_exists python3.9; then
    PYTHON_CMD="python3.9"
    echo "⚠️  Python 3.9 encontrado (pode ter limitações)"
else
    echo "📥 Instalando Python 3..."
    if [ "$DISTRO" = "debian" ]; then
        sudo $INSTALL_CMD python3 python3-pip python3-venv
    else
        sudo $INSTALL_CMD python3 python3-pip
    fi
    PYTHON_CMD="python3"
fi

# 3. Instala MariaDB/MySQL se necessário
echo "🗄️  Verificando MariaDB/MySQL..."
if command_exists mysql; then
    echo "✅ MySQL/MariaDB já instalado"
else
    echo "📥 Instalando MariaDB..."
    if [ "$DISTRO" = "debian" ]; then
        sudo $INSTALL_CMD mariadb-server mariadb-client
    else
        sudo $INSTALL_CMD mariadb-server mariadb
    fi

    echo "🔧 Iniciando MariaDB..."
    sudo systemctl start mariadb
    sudo systemctl enable mariadb

    echo "⚠️  Execute 'sudo mysql_secure_installation' para configurar segurança"
fi

# 4. Instala dependências do sistema
echo "🔧 Instalando dependências do sistema..."
if [ "$DISTRO" = "debian" ]; then
    sudo $INSTALL_CMD wget curl unzip xvfb libx11-6 libx11-xcb1 libxcb1 \
        libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 \
        libxi6 libxrandr2 libxrender1 libxss1 libxtst6 libnss3 \
        libgconf-2-4 libgtk-3-0 libgdk-pixbuf2.0-0 libxinerama1 \
        libatk-bridge2.0-0 libdrm2 libgtk-3-0 libasound2
else
    sudo $INSTALL_CMD wget curl unzip xorg-x11-server-Xvfb libX11 \
        libXcomposite libXcursor libXdamage libXext libXi libXtst \
        nss gtk3 alsa-lib
fi

# 5. Cria ambiente virtual Python
echo "🌍 Criando ambiente virtual Python..."
$PYTHON_CMD -m venv venv

# Ativa ambiente virtual
source venv/bin/activate

# 6. Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# 7. Instala dependências Python
echo "📚 Instalando dependências Python..."
pip install -r requirements.txt

# 8. Instala browsers do Playwright
echo "🎭 Instalando browsers do Playwright..."
playwright install chromium

# 9. Executa setup do projeto
echo "⚙️  Executando setup do projeto..."
python setup.py

# 10. Executa testes
echo "🧪 Executando testes do sistema..."
python run_tests.py

echo ""
echo "🎉 INSTALAÇÃO CONCLUÍDA!"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Configure o banco de dados:"
echo "   sudo mysql -u root -p"
echo "   CREATE DATABASE uploads_db;"
echo "   CREATE USER 'bot_user'@'localhost' IDENTIFIED BY 'sua_senha';"
echo "   GRANT ALL PRIVILEGES ON uploads_db.* TO 'bot_user'@'localhost';"
echo "   FLUSH PRIVILEGES;"
echo ""
echo "2. Configure suas credenciais no arquivo .env"
echo ""
echo "3. Organize seus documentos na pasta 'documentos/'"
echo ""
echo "4. Execute testes:"
echo "   source venv/bin/activate"
echo "   python main.py --test-only"
echo ""
echo "5. Inicie o processamento:"
echo "   python main.py"
echo ""
echo "💡 Para mais informações, consulte o README.md"