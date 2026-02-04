# 🚀 Quick Reference - Guardian Efímero Streamlit

## Start in 3 Steps

```bash
# 1. Install
pip install -r requirements.txt

# 2. Login to Azure (if not already)
az login

# 3. Run
streamlit run app.py
# 🌐 Opens at http://localhost:8501
```

---

## Common Commands

| Task | Command |
|------|---------|
| Run Streamlit | `streamlit run app.py` |
| Run with Make | `make streamlit` |
| Run quick setup | `bash quick-start.sh` (Linux/Mac) |
| Install deps | `pip install -r requirements.txt` |
| Run tests | `make test` |
| Full scan (CLI) | `make full_scan` |
| IA agent (CLI) | `make agente` |

---

## File Structure

```
guardian-efimero/
├── app.py                          # 🎯 Main Streamlit interface
├── src/
│   ├── cli_generator.py           # 📋 Generate az CLI commands
│   ├── detectores.py              # 🔍 Full scan (10 types)
│   ├── ia_agente.py               # 🤖 AI agent
│   ├── guardian.py                # Entry point
│   └── tools/arg_detector.py      # Azure Resource Graph queries
├── docs/
│   ├── STREAMLIT_APP_GUIDE.md     # 📚 Detailed guide
│   ├── UI_REFERENCE.md            # 🎨 Visual reference
│   └── vision.md                  # Vision document
├── requirements.txt               # Dependencies
├── Makefile                       # Make targets
└── quick-start.sh                 # Setup script
```

---

## Key Features

### 🔍 Scanning
- Detects 10 types of Azure resources (disks, IPs, SQL, VMs, storage, etc.)
- Real-time progress with spinner
- Metrics: total, types, savings, ambiguity

### 🤖 AI Recommendations
- Action: delete, snapshot, or keep
- Confidence: 0-100%
- Savings estimation
- Reason explanation
- Fallback to heuristics if Ollama unavailable

### ✅ Approval
- Checkbox-based selection
- "Select all" option
- Running totals
- % of total shown

### 📋 CLI Commands
- Auto-generated from selections
- Supports 10 resource types
- Ready to copy/paste
- Downloadable as script

---

## Generated Commands Examples

### Delete Disk
```bash
az disk delete --resource-group 'my-rg' --name 'unused-disk' --yes
```

### Delete Public IP
```bash
az network public-ip delete --resource-group 'my-rg' --name 'orphaned-ip' --yes
```

### Create Snapshot
```bash
az snapshot create --resource-group 'my-rg' --name 'disk-snapshot' --source 'my-disk'
```

### Delete Storage Account
```bash
az storage account delete --resource-group 'my-rg' --name 'oldstorageacct' --yes
```

### Delete VM
```bash
az vm delete --resource-group 'my-rg' --name 'stopped-vm' --yes
```

---

## Resource Types (10 Total)

| Typ | Delete Command | Typical Action |
|-----|---|---|
| **disk** | `az disk delete` | Delete if unused |
| **ip** | `az network public-ip delete` | Delete always |
| **sql** | `az sql db delete` | Delete |
| **vm** | `az vm delete` | Delete or restart |
| **storage** | `az storage account delete` | Delete |
| **appserviceplan** | `az appservice plan delete` | Delete |
| **nic** | `az network nic delete` | Delete |
| **keyvault** | `az keyvault delete` | Delete |
| **loadbalancer** | `az network lb delete` | Delete |
| **snapshot** | `az snapshot delete` | Delete if >90 days |

---

## Cost Estimates

| Resource | Monthly Cost | Notes |
|----------|---|---|
| Disk (per GB) | €0.08/GB | Size-dependent |
| Public IP | €3.00 | Fixed per IP |
| SQL Database | €45.00 | Estimate |
| VM (stopped) | €60.00 | Estimate |
| Storage Account | €10.00 | Estimate |
| App Service Plan | €5.00 | Estimate |
| Network Interface | €1.00 | Estimate |
| Key Vault | €0.50 | Estimate |
| Load Balancer | €2.00 | Estimate |
| Snapshot (per GB, 90d) | Variable | Based on size + days |

---

## Troubleshooting

### "Error connecting to Ollama"
✅ App falls back to heuristics automatically. No action needed.

### "Not logged in to Azure"
```bash
az login
az account set --subscription "<sub-id>"
```

### "Scan is frozen"
⏳ Scans take 1-2 minutes. Wait or check network.

### "No commands generated"
✓ Ensure at least 1 resource is selected (checkboxes)

### "Command needs parameters"
📝 Some commands (SQL) need extra info. Edit before running.

---

## Workflow

```
1. 🔍 SCAN           2. 🤖 ANALYZE        3. ✅ APPROVE        4. 📋 GENERATE
   ↓                    ↓                   ↓                    ↓
Click Scan         Click Get IA         Check boxes          Review commands
Wait 1-2 min       Read details         See totals           Copy to terminal
View table         Expand cards         Click Select All     Paste & run
```

---

## Important Notes

⚠️ **CRITICAL**:
- Commands are **NOT executed automatically**
- **ALWAYS review manually** before running
- **Backup first** before deleting resources
- **You are responsible** for what gets deleted
- Some commands may need **extra parameters**
- Use at **your own risk**

---

## Environment Setup

### Python Version
```bash
# Check version (3.10+ recommended)
python --version
```

### Virtual Environment
```bash
# Create
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Install Requirements
```bash
pip install -r requirements.txt
```

---

## Optional: Setup Ollama

For better AI recommendations:

```bash
# 1. Download from https://ollama.ai

# 2. Pull model
ollama pull llama3.2:1b

# 3. Run in separate terminal
ollama serve

# 4. Now Streamlit will use Ollama automatically
streamlit run app.py
```

---

## Useful Links

- 📚 [Detailed Guide](docs/STREAMLIT_APP_GUIDE.md)
- 🎨 [UI Reference](docs/UI_REFERENCE.md)
- 🏗️ [Implementation Details](STREAMLIT_IMPLEMENTATION.md)
- 📖 [Project Vision](docs/vision.md)
- 🔗 [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/reference-index)

---

## Support

**Issue?**
1. Check [Troubleshooting](#troubleshooting) section
2. Read [Detailed Guide](docs/STREAMLIT_APP_GUIDE.md)
3. Run: `az account show` (check Azure login)
4. Verify: Python 3.10+, pip packages installed

---

**Version**: 1.0 (Streamlit)
**Last Updated**: 2026-02-04
**Project**: Guardian Efímero - FinOps for Azure
