import re
import json
import os

# ======================
# PATH (경로 설정)
# ======================
INPUT_PATH = "data/raw/KakaoTalk_20251230_1037_23_449_group.txt"
OUTPUT_PATH = "data/processed/messages_raw.json"

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

# ======================
# REGEX (정규식)
# ======================
DATE_REGEX = re.compile(r"-+\s*(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일")
MSG_REGEX = re.compile(
    r"\[(.+?)\]\s*\[(오전|오후)\s*(\d{1,2}):(\d{2})\]\s*(.*)"
)

# ======================
# FILTER RULES (필터 규칙)
# ======================
MEDIA_ONLY = {"동영상", "사진", "이미지"}

def is_system_line(line: str) -> bool:
    """Check whether the line is a system message
    (시스템 메시지 여부 판단)
    """
    return (
        "님이 들어왔습니다" in line
        or "님이 나갔습니다" in line
    )

# ======================
# PARSER (파서 로직)
# ======================
messages = []
current_date = None
last_msg = None

with open(INPUT_PATH, "r", encoding="utf-8") as f:
    for raw_line in f:
        line = raw_line.rstrip()

        # ---- Date separator line (날짜 구분 라인) ----
        date_match = DATE_REGEX.search(line)
        if date_match:
            y, m, d = date_match.groups()
            current_date = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
            last_msg = None
            continue

        # ---- System line: user join/leave (시스템 라인: 입장/퇴장) ----
        if is_system_line(line):
            last_msg = None
            continue

        # ---- Message start line (메시지 시작 라인) ----
        msg_match = MSG_REGEX.match(line)
        if msg_match:
            speaker, ampm, h, m, content = msg_match.groups()

            # Remove Open Chat Bot messages (오픈채팅봇 메시지 제거)
            if speaker == "오픈채팅봇":
                last_msg = None
                continue

            # Convert time to 24-hour format (24시간 형식으로 변환)
            hour = int(h)
            if ampm == "오후" and hour != 12:
                hour += 12
            if ampm == "오전" and hour == 12:
                hour = 0
            time = f"{hour:02d}:{m}"

            # Remove media-only messages (미디어 단독 메시지 제거)
            if content.strip() in MEDIA_ONLY:
                last_msg = None
                continue

            msg = {
                "date": current_date,
                "speaker": speaker,
                "time": time,
                "content": content
            }
            messages.append(msg)
            last_msg = msg
            continue

        # ---- Continuation line (줄바꿈 이어지는 메시지) ----
        if last_msg and line.strip():
            # Skip system text inside continuation
            # (continuation 중 시스템 메시지 제거)
            if is_system_line(line):
                continue
            last_msg["content"] += "\n" + line

# ======================
# SAVE OUTPUT (결과 저장)
# ======================
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(messages, f, ensure_ascii=False, indent=2)

print(f"Parsing completed: {len(messages)} messages")
