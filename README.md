# Claude Router

Claude Router is a proxy server that connects Claude Code with local Ollama installations using GPT-OSS models.

## Prerequisites

### 1. Ollama Installation
Install Ollama on your system:

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download/windows

### 2. Start Ollama Service
```bash
ollama serve
```

### 3. Install Required Model
```bash
ollama pull gpt-oss:20b
```

## Setup & Run

### 1. Clone and Setup
```bash
git clone <repository-url>
cd claude-router
chmod +x run.sh
```

### 2. Run the Router
```bash
./run.sh
```

This will:
- Generate `.claude/settings.local.json` configuration
- Install Python dependencies  
- Verify Ollama service and model
- Start the router on localhost:4000

## Configuration

The router automatically generates `.claude/settings.local.json`:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "http://localhost:4000",
    "ANTHROPIC_API_KEY": "any-key",
    "ANTHROPIC_MODEL": "gpt-oss"
  },
  "allowedTools": ["*"],
  "hasTrustDialogAccepted": true,
  "hasCompletedProjectOnboarding": true
}
```

## Environment Variables

- `OLLAMA_URL`: Ollama API endpoint (default: "http://localhost:11434/api/chat")
- `MODEL_NAME`: Ollama model to use (default: "gpt-oss:20b")
- `PROXY_HOST`: Router host (default: "0.0.0.0")
- `PROXY_PORT`: Router port (default: 4000)

## API Endpoints

- `POST /v1/messages` - Anthropic Messages API compatible endpoint
- `GET /health` - Health check
- `GET /` - Service information

## Usage

1. Start Ollama service: `ollama serve`
2. Install model: `ollama pull gpt-oss:20b`  
3. Run router: `./run.sh`
4. Use Claude Code normally - it will route through local setup

## Troubleshooting

### Common Issues

1. **Ollama not running**: Make sure `ollama serve` is running
2. **Model not found**: Run `ollama pull gpt-oss:20b`
3. **Connection errors**: Verify Ollama at localhost:11434

### Check Status
```bash
# Verify Ollama
curl http://localhost:11434/api/version

# List models  
ollama list

# Test router
curl http://localhost:4000/health
```