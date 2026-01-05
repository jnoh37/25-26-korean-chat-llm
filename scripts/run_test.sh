#!/bin/bash
#SBATCH -p GPU              # Partition name (파티션 이름)
#SBATCH -N 1                # Number of nodes (노드 수)
#SBATCH -t 0-01:00          # Maximum wall time: 1 hour (최대 실행 시간: 1시간)
#SBATCH -o slurm.%j.out     # Standard output log (표준 출력 로그 파일)
#SBATCH -e slurm.%j.err     # Standard error log (에러 로그 파일)
#SBATCH --gres=gpu:1        # Request 1 GPU (GPU 1개 요청)

# 1. Load Anaconda Environment Settings
# (아나콘다 환경 설정 불러오기)
if [ -f "/usr/local/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/usr/local/anaconda3/etc/profile.d/conda.sh"
else
    export PATH="/usr/local/anaconda3/bin:$PATH"
fi

# 2. Activate Virtual Environment
# (가상환경 활성화)
conda activate my_env

# 3. Execute the Python Script
# (파이썬 코드 실행)
echo "Job started at: $(date)"
python test_model.py
echo "Job finished at: $(date)"