FROM python:3.11-slim

WORKDIR /app

# 필수 패키지 설치
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# 코드 복사 (바인드 마운트로도 덮어씌워짐)
COPY . /app

# Python 패키지 설치
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# .claude 설정 복사
RUN mkdir -p /app/.claude
COPY .claude/settings.local.json /app/.claude/settings.local.json

EXPOSE 4000

# uvicorn reload 옵션으로 main.py 변경 자동 반영
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "4000", "--reload"]
