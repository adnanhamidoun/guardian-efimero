#!/bin/bash
# Fix Installation Script for Guardian Efímero
# Instala dependencias de forma limpia sin conflictos

set -e

echo "🛡️  Guardian Efímero - Clean Installation"
echo "=========================================="
echo ""

# Step 1: Upgrade pip
echo "1️⃣  Upgrading pip..."
pip install --upgrade pip setuptools wheel
echo ""

# Step 2: Install dependencies (sin usar requirements.txt compilado)
echo "2️⃣  Installing dependencies..."
pip install --upgrade \
    azure-identity==1.25.1 \
    azure-mgmt-resourcegraph==8.0.1 \
    azure-mgmt-costmanagement==4.0.1 \
    pandas==2.3.3 \
    rich==14.2.0 \
    python-dotenv==1.2.1 \
    requests==2.32.5 \
    streamlit==1.41.1 \
    langchain-community==0.4.1 \
    langchain-ollama==1.0.1 \
    ollama==0.6.1 \
    pytest==7.4.4 \
    duckdb==1.4.3

echo "✅ Dependencies installed"
echo ""

# Step 3: Verify installation
echo "3️⃣  Verifying installation..."
python -c "import streamlit; import pandas; import azure.identity; print('✅ All packages imported successfully')"
echo ""

echo "🎉 Installation complete!"
echo ""
echo "Run: streamlit run app.py"
