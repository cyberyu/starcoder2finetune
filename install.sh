#!/bin/bash

set -e

echo "=== Creating conda environment 'refact3_minimal' with Python 3.9.23 ==="
conda create -n refact3_minimal python=3.9.23 -y

echo "=== Activating environment ==="
source $(conda info --base)/etc/profile.d/conda.sh
conda activate refact3_minimal

echo "=== Upgrading pip ==="
pip install --upgrade pip

echo "=== Installing core packages for your test code ==="

# PyTorch ecosystem with CUDA 12.7 support
echo "Installing PyTorch with CUDA 12.7 support..."
pip install torch==2.6.0 torchvision==0.21.0 torchaudio==2.6.0 --index-url https://download.pytorch.org/whl/cu124

# Note: PyTorch doesn't have separate CUDA 12.7 wheels, but CUDA 12.4 wheels are compatible with CUDA 12.7

# Transformers ecosystem
echo "Installing transformers and related packages..."
pip install transformers==4.53.3
pip install tokenizers==0.21.2
pip install accelerate==1.7.0
pip install safetensors==0.5.3

# Datasets
echo "Installing datasets..."
pip install datasets==4.0.0

# Fine-tuning packages
echo "Installing PEFT and TRL..."
pip install peft==0.15.2
pip install trl

# Quantization
echo "Installing BitsAndBytes..."
pip install bitsandbytes==0.46.1

# Flash Attention for performance
echo "Installing Flash Attention..."
pip install flash_attn==2.7.4.post1 --no-build-isolation || echo "Flash Attention install failed, continuing..."

echo "=== Testing CUDA compatibility ==="
python << 'EOF'
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version detected by PyTorch: {torch.version.cuda}")
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print(f"Current CUDA device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name()}")
else:
    print("❌ CUDA not available - check your installation")
EOF

echo "=== Testing your specific imports ==="
python << 'EOF'
try:
    print("Testing imports from your code...")
    
    import argparse
    print("✅ argparse")
    
    import multiprocessing
    print("✅ multiprocessing")
    
    import os
    print("✅ os")
    
    from datasets import load_dataset
    print("✅ datasets.load_dataset")
    
    import torch
    print(f"✅ torch {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    
    import transformers
    print(f"✅ transformers {transformers.__version__}")
    
    from accelerate import PartialState
    print("✅ accelerate.PartialState")
    
    from peft import LoraConfig
    print("✅ peft.LoraConfig")
    
    from transformers import (
        AutoModelForCausalLM,
        BitsAndBytesConfig,
        logging,
        set_seed,
    )
    print("✅ transformers components")
    
    import datasets
    from datasets import Dataset, DatasetDict
    print(f"✅ datasets {datasets.__version__}")
    
    from trl import SFTTrainer, SFTConfig
    print("✅ trl.SFTTrainer, SFTConfig")
    
    print("\n🎉 All imports successful!")
    print(f"Python version: {__import__('sys').version}")
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA runtime version: {torch.version.cuda}")
    print(f"Transformers version: {transformers.__version__}")
    print(f"Datasets version: {datasets.__version__}")
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF

echo "=== Setup complete! ==="
echo "CUDA 12.7 compatibility notes:"
echo "- PyTorch CUDA 12.4 wheels are compatible with CUDA 12.7"
echo "- No need to install separate NVIDIA CUDA packages for basic usage"
echo "- Your system CUDA 12.7 runtime will be used"
echo ""
echo "Activate with: conda activate refact3_minimal"
