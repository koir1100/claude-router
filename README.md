# Claude Router

Claude Router는 Claude Code를 로컬 Ollama 설치 및 GPT-OSS 모델과 연결하는 **범용 프록시 서버**입니다. 어떤 프로젝트에서든 Claude Code의 강력한 기능을 로컬 모델을 통해 사용할 수 있도록 지원합니다.

## ✨ 주요 기능

*   **범용 호환성**: Python, JavaScript, Go 등 모든 언어 및 프레임워크의 프로젝트에서 별도 설정 없이 동작합니다.
*   **로컬 LLM 연동**: 로컬에 설치된 Ollama와 `gpt-oss:20b` 같은 오픈소스 모델을 Claude Code의 브레인으로 사용합니다.
*   **Anthropic API 호환**: Anthropic Messages API와 완벽하게 호환되어 안정적으로 통신합니다.
*   **모든 도구 지원**: 파일 CRUD, 터미널 명령어 실행 등 Claude Code의 모든 도구를 지능적으로 변환하고 지원합니다.
*   **원클릭 실행**: `run.sh` 스크립트 하나로 의존성 설치, 환경 설정, 서비스 실행까지 한 번에 해결합니다.

## Prerequisites

### 1. Ollama 설치
시스템에 Ollama를 설치합니다.

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
[Ollama 공식 사이트](https://ollama.com/download/windows)에서 다운로드하여 설치합니다.

### 2. Ollama 서비스 시작
터미널에서 Ollama 서비스를 실행합니다.
```bash
ollama serve
```

### 3. 필요 모델 설치
Claude Router는 `gpt-oss:20b` 모델에 최적화되어 있습니다.
```bash
ollama pull gpt-oss:20b
```

## 🚀 시작하기

### 1. 리포지토리 클론 및 설정
```bash
git clone https://github.com/say828/claude-router.git
cd claude-router
chmod +x run.sh
```

### 2. 라우터 실행
`run.sh` 스크립트를 실행하면 필요한 모든 설정과 서비스가 자동으로 시작됩니다.
```bash
./run.sh
```

스크립트가 실행하는 작업은 다음과 같습니다:
- Claude Code 연동을 위한 `.claude/settings.local.json` 파일 생성
- 필요한 Python 패키지 설치
- Ollama 서비스 및 모델 준비 상태 확인
- `localhost:4000`에서 프록시 서버 시작

## 💻 사용 방법

1.  **Claude Router 실행**: `claude-router` 프로젝트에서 `./run.sh`를 실행해 프록시 서버를 켭니다 (최초 한 번만).
2.  **작업할 프로젝트로 이동**: `cd /path/to/your/awesome-project/`
3.  **해당 프로젝트에서 Claude Code 열기**: Claude Code가 자동으로 `localhost:4000` 프록시를 사용하며, 현재 프로젝트 구조에 맞춰 지능적으로 동작하기 시작합니다.

## 📂 프로젝트 구조

```
claude-router/
├── .claude/                    # Claude Code 설정
│   └── settings.local.json     # 자동 생성된 설정 파일
├── src/                        # 소스 코드
│   ├── main.py                # FastAPI 프록시 서버
│   ├── util.py                # 메시지/도구 변환 유틸리티
│   ├── type.py                # 데이터 클래스 및 타입
│   ├── const.py               # 상수 및 기본 설정
│   └── ...
├── test/                       # 테스트 파일
│   ├── test_tools.py          # 도구 호출 테스트
│   └── ...
├── run.sh                      # 자동 실행 스크립트
├── requirements.txt            # Python 의존성
├── Dockerfile                  # Docker 설정
├── CLAUDE.md                   # 개발자용 상세 문서
└── README.md                   # 이 파일
```

## ⚙️ Configuration

### Claude Code 설정
`run.sh` 실행 시 `.claude/settings.local.json` 파일이 아래와 같이 자동 생성되어 Claude Code와 연동됩니다.

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

### 환경 변수
필요시 아래 환경 변수를 사용하여 설정을 변경할 수 있습니다.
- `OLLAMA_URL`: Ollama API 엔드포인트 (기본값: "http://localhost:11434/api/chat")
- `MODEL_NAME`: 사용할 Ollama 모델 (기본값: "gpt-oss:20b")
- `PROXY_HOST`: 라우터 호스트 (기본값: "0.0.0.0")
- `PROXY_PORT`: 라우터 포트 (기본값: 4000)

## 🧪 테스트

프로젝트의 테스트를 실행하려면 아래 명령어를 사용하세요.

```bash
python -m pytest test/
```

## Troubleshooting

### 일반적인 문제
1.  **Ollama 미실행**: `ollama serve` 명령어로 Ollama가 실행 중인지 확인하세요.
2.  **모델 미설치**: `ollama pull gpt-oss:20b` 명령어로 모델을 설치했는지 확인하세요.
3.  **연결 오류**: `curl http://localhost:11434/api/version`으로 Ollama 서비스 상태를, `curl http://localhost:4000/health`로 라우터 상태를 확인하세요.
