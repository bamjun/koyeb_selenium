# Python 3.9을 기반 이미지로 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일을 복사
COPY requirements.txt requirements.txt

# Python 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드를 복사
COPY . .

# 애플리케이션 포트 설정
EXPOSE 8000

# Uvicorn을 사용해 FastAPI 애플리케이션 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
