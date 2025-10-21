FROM python:3.11

# 작업 디렉토리를 /app으로 설정

WORKDIR /app

# 의존성 파일 복사 및 설치

COPY api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# 애플리케이션 코드 복사

COPY api/ /app/

# Flask 앱이 리슨하는 포트 노출

EXPOSE 5000

# 컨테이너 시작 시 Flask 앱 실행

CMD ["python", "app.py"]