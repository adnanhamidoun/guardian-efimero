#!/bin/bash
# Quick Setup & Run Guide for Guardian Efímero Streamlit
# Run this to get up and running quickly

set -e  # Exit on any error

echo "🛡️  Guardian Efímero - Quick Setup"
echo "================================="
echo ""

# Step 1: Check Python
echo "1️⃣  Checking Python..."
python --version
echo ""

# Step 2: Install dependencies
echo "2️⃣  Installing dependencies..."
pip install -r requirements.txt -q
echo "✅ Dependencies installed"
echo ""

# Step 3: Check Azure CLI
echo "3️⃣  Checking Azure CLI..."
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not found. Please install from https://learn.microsoft.com/en-us/cli/azure/"
    exit 1
fi
az --version | head -n 1
echo ""

# Step 4: Check Azure login
echo "4️⃣  Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "⚠️  Not logged in to Azure"
    echo "Running: az login"
    az login
fi
CURRENT_SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✅ Logged in to: $CURRENT_SUBSCRIPTION"
echo ""

# Step 5: Optional - Check Ollama
echo "5️⃣  Checking Ollama (optional)..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama available at localhost:11434"
else
    echo "⚠️  Ollama not available - will use heuristics"
    echo "   (Optional) To enable AI: install from https://ollama.ai"
fi
echo ""

# Step 6: Run Streamlit
echo "6️⃣  Starting Streamlit app..."
echo "   🌐 App will open at http://localhost:8501"
echo ""
streamlit run app.py
