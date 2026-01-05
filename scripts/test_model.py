import os
import json
import torch
from huggingface_hub import login
from transformers import pipeline

# 1. Hugging Face Login (Log in via code instead of terminal)
# (터미널 대신 코드에서 직접 허깅페이스 로그인 수행)
HF_TOKEN = "Your token"
login(token=HF_TOKEN)

# 2. Model Configuration (Llama-3.1-8B-Instruct)
model_id = "meta-llama/Llama-3.1-8B-Instruct"

print(f"--- Model Loading Started: {model_id} ---")

# Use bfloat16 and device_map="auto" for GPU memory efficiency
# (GPU 메모리 효율을 위해 bfloat16 및 자동 장치 할당 사용)
try:
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    # 3. Data Loading Test
    # Use absolute path to ensure the file is found regardless of where you run sbatch
    # (어디서 sbatch를 실행하든 파일을 찾을 수 있도록 절대 경로 구성)
    current_dir = os.path.dirname(os.path.abspath(__file__)) # .../scripts/
    root_dir = os.path.dirname(current_dir) # .../ (Root)
    data_path = os.path.join(root_dir, "data", "processed_data.jsonl")

    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            sample_data = json.loads(f.readline())
            user_content = sample_data["messages"][0]["content"]
            print(f"--- Data loaded from: {data_path} ---")
    else:
        print(f"--- File not found at: {data_path}. Using fallback message. ---")
        user_content = "Hello, this is a basic sentence for model testing."

    # 4. Model Inference (Run the model)
    # (모델 실행: 실제 인퍼런스 수행)
    print(f"\n[Input Sentence]: {user_content}")
    
    # Format message for Instruct model
    # (인스트럭트 모델 형식에 맞게 메시지 구성)
    messages = [{"role": "user", "content": user_content}]
    outputs = pipe(messages, max_new_tokens=256)
    
    print("\n[Model Response]:")
    # Extract only the assistant's response content
    # (어시스턴트의 답변 내용만 추출하여 출력)
    print(outputs[0]["generated_text"][-1]['content'])

except Exception as e:
    print(f"Error occurred: {e}")