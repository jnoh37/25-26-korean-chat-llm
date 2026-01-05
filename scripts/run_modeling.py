import os
import json
import torch
from huggingface_hub import login
from transformers import pipeline
from tqdm import tqdm

# 1. Hugging Face Login
# (허깅페이스 로그인)
HF_TOKEN = "Your token"
login(token=HF_TOKEN)

# 2. Model Configuration for Inference
# (추론을 위한 모델 설정)
model_id = "meta-llama/Llama-3.1-8B-Instruct"

print(f"--- Initialization: Loading {model_id} ---")
try:
    # Set up the text-generation pipeline
    # (텍스트 생성 파이프라인 설정)
    pipe = pipeline(
        "text-generation",
        model=model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto"
    )

    # 3. Path Configuration
    # (입출력 경로 설정)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir)
    input_path = os.path.join(root_dir, "data", "processed_data.jsonl")
    output_path = os.path.join(root_dir, "data", "modeling_results.jsonl")

    # 4. Batch Modeling (Full Inference)
    # (전체 데이터 모델링 시작)
    if not os.path.exists(input_path):
        print(f"Error: Dataset not found at {input_path}")
        exit()

    print(f"--- Modeling started. Dataset: {input_path} ---")
    
    with open(input_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Create modeling_results.jsonl
    # (모델링 결과 저장 파일 생성)
    with open(output_path, "w", encoding="utf-8") as out_f:
        # Loop through each conversation for modeling
        # (전체 대화를 돌며 모델링 수행)
        for line in tqdm(lines, desc="Running Llama Modeling"):
            data = json.loads(line)
            user_query = data["messages"][0]["content"]
            
            # Run Inference
            messages = [{"role": "user", "content": user_query}]
            outputs = pipe(messages, max_new_tokens=512)
            model_answer = outputs[0]["generated_text"][-1]['content']
            
            # Save the original input and the model's generated response
            # (입력값과 모델이 생성한 답변을 함께 저장)
            result_item = {
                "input": user_query,
                "modeling_output": model_answer
            }
            out_f.write(json.dumps(result_item, ensure_ascii=False) + "\n")

    print(f"--- Modeling completed! Results saved to: {output_path} ---")

except Exception as e:
    print(f"Modeling Error: {e}")