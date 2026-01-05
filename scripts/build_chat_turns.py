import json
import os
from datetime import datetime, timedelta

# ======================
# PATH SETTINGS (경로 설정)
# ======================
INPUT_PATH = "data/processed/messages_raw.json"
OUTPUT_PATH = "data/processed/chat_turns.jsonl"

# Ensure output directory exists (출력 디렉토리 생성)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ======================
# QUESTION DETECTION RULES (질문 판별 규칙)
# ======================

# Sentence endings that usually indicate questions
# (질문을 나타내는 문장 끝 표현)
QUESTION_ENDINGS = [
    "나요", "인가요", "되나요", "할까요",
    "어디", "어떻게", "왜", "뭐", "무엇"
]

# Phrases expressing uncertainty or request for help
# (모르겠음 / 요청 의도를 나타내는 표현)
QUESTION_INTENT_PHRASES = [
    "모르겠", "헷갈", "이해가 안",
    "알려주", "어떻게 해야",
    "추천"
]

def is_question(text: str) -> bool:
    """
    Determine whether a message is a question
    (해당 메시지가 질문인지 판별)
    """
    text = text.strip()

    # Explicit question mark
    # (물음표 포함 여부)
    if "?" in text:
        return True

    # Question-like sentence endings
    # (질문형 어미 검사)
    for ending in QUESTION_ENDINGS:
        if text.endswith(ending):
            return True

    # Question intent expressions
    # (질문 의도 표현 포함 여부)
    for phrase in QUESTION_INTENT_PHRASES:
        if phrase in text:
            return True

    return False

# ======================
# ANSWER-LIKE MESSAGE FILTER (답변형 발화 판별)
# ======================
def is_answer_like(text: str) -> bool:
    """
    Check whether a message looks like an answer
    (해당 메시지가 답변처럼 보이는지 판별)
    """
    text = text.strip()

    # Exclude very short messages
    # (너무 짧은 메시지 제외)
    if len(text) < 5:
        return False

    # Exclude questions
    # (질문형 메시지 제외)
    if is_question(text):
        return False

    return True

# ======================
# TIME UTILITIES (시간 처리 함수)
# ======================
def parse_datetime(msg):
    """
    Convert message date and time to datetime object
    (메시지의 날짜/시간을 datetime 객체로 변환)
    """
    date = msg.get("date", "").strip()
    time = msg.get("time", "").strip()

    return datetime.strptime(
        f"{date} {time}",
        "%Y-%m-%d %H:%M"
    )

# Maximum time window to accept answers after a question
# (질문 이후 답변을 허용하는 최대 시간)
MAX_HOURS = 6

# ======================
# LOAD DATA (데이터 로드)
# ======================
with open(INPUT_PATH, "r", encoding="utf-8") as f:
    messages = json.load(f)

# ======================
# PRE-PARSE DATETIME (사전 datetime 변환)
# ======================
# Parse datetime once to avoid repeated strptime calls
# (strptime 반복 호출 방지를 위해 datetime을 미리 변환)
for msg in messages:
    try:
        msg["_dt"] = parse_datetime(msg)
    except Exception:
        msg["_dt"] = None

# ======================
# BUILD CHAT TURNS (턴 묶기 로직)
# ======================
turns = []
i = 0
n = len(messages)

while i < n:
    msg = messages[i]

    # Skip messages without valid datetime or not questions
    # (datetime 없거나 질문이 아니면 스킵)
    if msg["_dt"] is None or not is_question(msg["content"]):
        i += 1
        continue

    # Initialize question turn
    # (질문 턴 시작)
    question_time = msg["_dt"]
    user_contents = [msg["content"]]
    assistant_contents = []

    j = i + 1
    while j < n:
        next_msg = messages[j]

        # Skip messages with invalid datetime
        # (datetime 없는 메시지는 건너뜀)
        if next_msg["_dt"] is None:
            j += 1
            continue

        # Stop if time window exceeded
        # (시간 제한 초과 시 중단)
        if next_msg["_dt"] - question_time > timedelta(hours=MAX_HOURS):
            break

        # Stop if another question appears
        # (다음 질문 등장 시 중단)
        if is_question(next_msg["content"]):
            break

        # Collect answer-like messages
        # (답변처럼 보이는 메시지만 수집)
        if is_answer_like(next_msg["content"]):
            assistant_contents.append(next_msg["content"])

        j += 1

    # Save only turns with at least one answer
    # (답변이 있는 경우만 저장)
    if assistant_contents:
        turns.append({
            "user": user_contents,
            "assistant": assistant_contents
        })

    # Move pointer forward to avoid infinite loop
    # (무한 루프 방지를 위해 인덱스 이동)
    i = j

# ======================
# SAVE OUTPUT (결과 저장)
# ======================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for turn in turns:
        f.write(json.dumps(turn, ensure_ascii=False) + "\n")

print(f"✅ Done. Generated {len(turns)} chat turns.")
print(f"📄 Output saved to: {OUTPUT_PATH}")
