# SynthNet Deployment Guide

## 📦 Release Artifacts

### Available Downloads
- **`synthnet-mcp-ecosystem-v1.0.0.tar.gz`** (92KB) - Complete MCP server ecosystem
- **`synthnet-n8n-templates-v1.0.0.tar.gz`** (3KB) - n8n workflow templates
- **Source Code** - Full repository with documentation

## 🚀 Deployment Options

### Option 1: Full Git Clone (Recommended)
```bash
git clone https://github.com/asshat1981ar/synthnet.git
cd synthnet
chmod +x mcp_servers/setup_mcp_servers.sh
./mcp_servers/setup_mcp_servers.sh
```

### Option 2: Package Deployment
```bash
# Download and extract MCP ecosystem
wget https://github.com/asshat1981ar/synthnet/releases/download/v1.0.0/synthnet-mcp-ecosystem-v1.0.0.tar.gz
tar -xzf synthnet-mcp-ecosystem-v1.0.0.tar.gz

# Download and extract n8n templates
wget https://github.com/asshat1981ar/synthnet/releases/download/v1.0.0/synthnet-n8n-templates-v1.0.0.tar.gz
tar -xzf synthnet-n8n-templates-v1.0.0.tar.gz

# Setup permissions
chmod +x *.sh
./setup_mcp_servers.sh
```

## 🔧 Quick Start Commands

### Deploy Complete Ecosystem
```bash
./mcp_servers/deploy_synthnet_ecosystem.sh deploy
```

### Start All MCP Servers
```bash
./mcp_servers/start_all_mcp_servers.sh
```

### Test Individual Server
```bash
python3 mcp_servers/semantic_cot_reasoning_engine.py
```

## 🌐 Server Endpoints

After deployment, MCP servers will be available at:
- **Semantic CoT Engine**: `http://localhost:8771/mcp`
- **n8n-MCP Bridge**: `http://localhost:8773/mcp`
- **Android Hub**: `http://localhost:8768/mcp`
- **Testing Ecosystem**: `http://localhost:8770/mcp`
- **Architecture Intelligence**: `http://localhost:8769/mcp`
- **GitHub Tools**: `http://localhost:8774/mcp`
- **Plus 7 additional servers on ports 8775-8781**

## 📋 System Requirements

### Minimal Requirements
- Python 3.8+
- 50MB disk space
- Android/Termux or Linux environment

### Optional Dependencies
- `networkx>=3.0` (has fallback)
- `numpy>=1.20.0` (has fallback)
- `aiohttp>=3.8.0` (has fallback)
- `websockets>=10.0` (has fallback)

## 🔍 Verification

### Health Check
```bash
curl http://localhost:8771/health
```

### List Available Tools
```bash
curl -X POST http://localhost:8771/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/list"}'
```

## 🛠️ Troubleshooting

### Common Issues
1. **Port conflicts**: Modify port numbers in server files
2. **Permission errors**: Run `chmod +x *.sh`
3. **Python path issues**: Use `python3` explicitly

### Debug Mode
```bash
export DEBUG=1
./mcp_servers/start_all_mcp_servers.sh
```

## 📖 Documentation

- **Main README**: [README.md](./README.md)
- **Release Notes**: [RELEASE_NOTES.md](./RELEASE_NOTES.md)
- **MCP Server Docs**: [mcp_servers/README.md](./mcp_servers/README.md)

## 🔗 Integration Examples

### With Claude Desktop
Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "synthnet-semantic": {
      "command": "python3",
      "args": ["/path/to/synthnet/mcp_servers/semantic_cot_reasoning_engine.py"]
    }
  }
}
```

### With n8n
Import workflow templates from `n8n_templates/` directory into your n8n instance.

---
🔗 **Support**: [GitHub Issues](https://github.com/asshat1981ar/synthnet/issues)