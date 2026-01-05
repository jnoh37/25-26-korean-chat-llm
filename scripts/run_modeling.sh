#!/bin/bash
#SBATCH -p GPU
#SBATCH -N 1
#SBATCH -t 0-06:00
#SBATCH -o slurm_modeling.%j.out
#SBATCH -e slurm_modeling.%j.err
#SBATCH --gres=gpu:1

# 1. Environment Setup
if [ -f "/usr/local/anaconda3/etc/profile.d/conda.sh" ]; then
    . "/usr/local/anaconda3/etc/profile.d/conda.sh"
else
    export PATH="/usr/local/anaconda3/bin:$PATH"
fi

# 2. Activate Virtual Environment
conda activate my_env

# 3. Ensure tqdm is installed
pip install tqdm

# 4. Start Modeling Task
echo "Modeling task started at: $(date)"
python run_modeling.py
echo "Modeling task finished at: $(date)"