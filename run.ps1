Write-Host "🟢 Claude Router 환경 세팅 시작..."

# -----------------------------
# 1. .claude 설정 생성
# -----------------------------
New-Item -ItemType Directory -Path .claude -Force | Out-Null
$settingsFile = ".claude/settings.local.json"
New-Item -ItemType File -Path $settingsFile -Force | Out-Null
$json = @"
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
"@
Set-Content -Path $settingsFile -Value $json -Encoding UTF8
Write-Host "✅ .claude/settings.local.json 생성 완료"

# -----------------------------
# 2. Python 패키지 설치
# -----------------------------
Write-Host "📦 Python 패키지 설치 중..."
pip install -r requirements.txt
Write-Host "✅ Python 패키지 설치 완료"

# -----------------------------
# 3. Ollama 서비스 확인
# -----------------------------
Write-Host "🔍 Ollama 서비스 확인 중..."
try {
    Invoke-WebRequest http://localhost:11434/api/version | Out-Null
    Write-Host "✅ Ollama 서비스 확인 완료"
} catch {
    Write-Error "❌ Ollama가 실행되지 않았습니다. 먼저 Ollama를 시작해주세요: ollama serve"
    exit 1
}

# -----------------------------
# 4. GPT-OSS 모델 확인
# -----------------------------
Write-Host "🔍 GPT-OSS:20b 모델 확인 중..."
if (!(ollama list | Select-String "gpt-oss:20b")) {
    Write-Error "❌ GPT-OSS:20b 모델이 설치되지 않았습니다. 먼저 모델을 설치해주세요: ollama pull gpt-oss:20b"
    exit 1
}
Write-Host "✅ GPT-OSS:20b 모델 확인 완료"

# -----------------------------
# 5. 포트 4000 확인 및 기존 서비스 종료
# -----------------------------
Write-Host "🔍 포트 4000 확인 중..."
$connections = Get-NetTCPConnection -LocalPort 4000 -ErrorAction SilentlyContinue
if ($connections) {
    Write-Host "⚠️  포트 4000이 이미 사용 중입니다. 기존 서비스를 종료합니다..."
    $connections | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }
    Start-Sleep -Seconds 2
    Write-Host "✅ 기존 서비스 종료 완료"
}

# -----------------------------
# 6. Claude Router 백그라운드 실행
# -----------------------------
Write-Host "🚀 Claude Router 백그라운드에서 실행 중..."
$logFile = "claude-router.log"
$process = Start-Process "python" -ArgumentList "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "4000", "--reload" -RedirectStandardOutput $logFile -RedirectStandardError $logFile -NoNewWindow -PassThru
Start-Sleep -Seconds 2

try {
    Invoke-WebRequest http://localhost:4000/health | Out-Null
    Write-Host "✅ Claude Router 시작 완료 (PID: $($process.Id))"
    Write-Host "   - Claude Router: http://localhost:4000"
    Write-Host "   - Ollama: http://localhost:11434"
    Write-Host "   - 로그 파일: $logFile"
    Write-Host ""
    Write-Host "📋 상태 확인: Invoke-WebRequest http://localhost:4000/health"
    Write-Host "📋 로그 확인: Get-Content -Path $logFile -Wait"
    Write-Host "🛑 종료: Stop-Process -Id $($process.Id)"
    Write-Host ""
    Write-Host "🎉 모든 서비스가 준비되었습니다!"
} catch {
    Write-Error "❌ Claude Router 시작 실패"
    Stop-Process -Id $($process.Id) -ErrorAction SilentlyContinue
    exit 1
}
