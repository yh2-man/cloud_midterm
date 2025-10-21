from flask import Flask, request, jsonify, send_file
from pathlib import Path
import json, os

app = Flask(__name__)

# 데이터 파일 경로 설정 및 초기화
# 경로: /app/data/expenses.json
DATA_PATH = Path("/app/data/expenses.json")
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
if not DATA_PATH.exists():
    DATA_PATH.write_text("[]", encoding="utf-8")

# --- 헬퍼 함수 ---
def load_data():
    """expenses.json 파일에서 데이터를 불러옵니다."""
    try:
        with DATA_PATH.open('r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # 파일이 없거나 JSON 형식 오류 발생 시 빈 리스트 반환
        return []

def save_data(data):
    """데이터를 expenses.json 파일에 저장합니다."""
    # ensure_ascii=False를 사용하여 한글이 깨지지 않도록 합니다.
    with DATA_PATH.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# --- API 엔드포인트 ---

@app.get("/healthz")
def healthz():
    """헬스 체크 엔드포인트"""
    return "ok", 200

@app.get("/api/records")
def get_records():
    """저장된 모든 지출 기록을 JSON으로 반환합니다."""
    return jsonify(load_data())

@app.post("/api/records")
def add_record():
    """새로운 지출 기록을 추가하고 저장합니다."""
    record = request.get_json()
    
    # 1. 유효성 검사 (필수 필드 확인)
    if not record or 'title' not in record or 'amount' not in record or 'date' not in record:
        return jsonify({"error": "필수 항목(title, amount, date)이 누락되었습니다."}), 400

    try:
        title = str(record['title']).strip()
        amount = int(record['amount'])
        date = str(record['date'])
    except ValueError:
        return jsonify({"error": "금액(amount)은 유효한 정수여야 합니다."}), 400
    
    # 2. 유효성 검사 (값 확인)
    if not title:
        return jsonify({"error": "항목명은 비워둘 수 없습니다."}), 400
    if amount < 0:
        return jsonify({"error": "금액은 0 이상이어야 합니다."}), 400
    if not date:
        return jsonify({"error": "날짜는 비워둘 수 없습니다."}), 400

    new_record = {
        "title": title,
        "amount": amount,
        "date": date
    }

    # 3. 데이터 저장
    data = load_data()
    data.append(new_record)
    save_data(data)

    # 201 Created 상태 코드와 함께 새로 저장된 레코드를 반환
    return jsonify(new_record), 201

@app.get("/api/summary")
def get_summary():
    """총 기록 수(count)와 총 지출 금액(total)을 계산하여 반환합니다."""
    data = load_data()
    
    # 모든 amount를 합산
    total = sum(item.get('amount', 0) for item in data)
    
    summary = {
        "count": len(data),
        "total": total
    }
    return jsonify(summary)

@app.get("/api/download")
def download_json():
    """expenses.json 파일을 클라이언트에게 다운로드합니다."""
    return send_file(
        str(DATA_PATH),
        mimetype='application/json',
        as_attachment=True,
        download_name='expenses.json' # 다운로드 시 파일 이름 설정
    )

if __name__ == "__main__":
    # 적절한 포트(예: 5000)로 0.0.0.0 에서 실행
    app.run(host="0.0.0.0", port=5000)