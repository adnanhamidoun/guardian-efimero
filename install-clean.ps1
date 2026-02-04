# Fix Installation Script for Guardian Efímero (Windows)
# Instala dependencias de forma limpia sin conflictos

Write-Host "🛡️  Guardian Efímero - Clean Installation (Windows)" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Upgrade pip
Write-Host "1️⃣  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip setuptools wheel | Out-Null
Write-Host ""

# Step 2: Install dependencies
Write-Host "2️⃣  Installing dependencies..." -ForegroundColor Yellow
$packages = @(
    "azure-identity==1.25.1",
    "azure-mgmt-resourcegraph==8.0.1",
    "azure-mgmt-costmanagement==4.0.1",
    "pandas==2.3.3",
    "rich==14.2.0",
    "python-dotenv==1.2.1",
    "requests==2.32.5",
    "streamlit==1.41.1",
    "langchain-community==0.4.1",
    "langchain-ollama==1.0.1",
    "ollama==0.6.1",
    "pytest==7.4.4",
    "duckdb==1.4.3"
)

foreach ($package in $packages) {
    Write-Host "  Installing $package..." -ForegroundColor Gray
    python -m pip install $package --upgrade | Out-Null
}

Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Step 3: Verify installation
Write-Host "3️⃣  Verifying installation..." -ForegroundColor Yellow
python -c "import streamlit; import pandas; import azure.identity; print('✅ All packages imported successfully')"
Write-Host ""

Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Run: streamlit run app.py" -ForegroundColor Cyan
