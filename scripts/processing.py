import json
import re

def preprocess_text(text):
    """
    Cleans and anonymizes individual message text. 
    (개별 메시지 텍스트를 정제하고 비식별화합니다.)
    """
    # 1. Filter out Euro exchange info (only if both '유로' and '환전' exist)
    # ('유로'와 '환전'이 모두 포함된 경우만 제거)
    if '유로' in text and '환전' in text:
        return ""
        
    # 1-2. Filter out URLs (링크 제거)
    if re.search(r'http[s]?://', text):
        return ""

    # 2. Anonymize personal info: Phone and Email (개인정보 비식별화: 전화번호 및 이메일)
    text = re.sub(r'\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}', '[PHONE]', text)
    text = re.sub(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', '[EMAIL]', text)

    # 3. Remove chat slang, emojis, and special characters (채팅 용어, 이모지 및 특수문자 제거)
    # Remove Korean consonants/vowels (ㄱ-ㅎ, ㅏ-ㅣ 제거)
    text = re.sub(r'[ㄱ-ㅎㅏ-ㅣ]{1,}', '', text)
    # Remove Unicode Emojis and miscellaneous symbols (유니코드 이모지 및 기타 기호 제거)
    text = re.sub(r'[^\w\s,.!?]', '', text) 
    
    return text.strip()

def process_jsonl(input_file, output_file):
    """
    Loads the grouped chat data, cleans it, and converts it to ChatML format.
    (그룹화된 채팅 데이터를 불러와 정제한 후 ChatML 포맷으로 변환합니다.)
    """
    with open(input_file, 'r', encoding='utf-8') as f, \
         open(output_file, 'w', encoding='utf-8') as out_f:
        
        for line in f:
            data = json.loads(line)
            user_msgs = data.get("user", [])
            assistant_msgs = data.get("assistant", [])

            # Join individual messages into a single string (개별 메시지들을 하나의 문자열로 결합)
            cleaned_user = " ".join([preprocess_text(m) for m in user_msgs if preprocess_text(m)])
            cleaned_assistant = " ".join([preprocess_text(m) for m in assistant_msgs if preprocess_text(m)])

            # Skip if either user or assistant content is empty (사용자나 답변 내용이 비어있으면 제외)
            if not cleaned_user or not cleaned_assistant:
                continue

            # Format for LLM training: ChatML/OpenAI format (LLM 학습용 포맷인 ChatML/OpenAI 형태로 구성)
            formatted_data = {
                "messages": [
                    {"role": "user", "content": cleaned_user},
                    {"role": "assistant", "content": cleaned_assistant}
                ]
            }

            out_f.write(json.dumps(formatted_data, ensure_ascii=False) + '\n')

if __name__ == "__main__":
    # Define file paths (파일 경로 정의)
    input_path = 'data/processed/chat_turns.jsonl'
    output_path = 'data/processed/processed_data.jsonl'
    
    process_jsonl(input_path, output_path)
    print(f"Preprocessing complete! Saved to: {output_path}")