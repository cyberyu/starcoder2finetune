#!/usr/bin/env python3
"""
Package Version Checker for test.py Dependencies
This script prints detailed version information for all packages imported by test.py
"""

import sys
import os
import pkg_resources
import importlib
import traceback

def get_package_version(package_name):
    """Get version of a package using multiple methods"""
    try:
        # Method 1: Using pkg_resources
        return pkg_resources.get_distribution(package_name).version
    except:
        try:
            # Method 2: Using importlib and __version__
            module = importlib.import_module(package_name)
            return getattr(module, '__version__', 'Unknown')
        except:
            try:
                # Method 3: Using importlib.metadata (Python 3.8+)
                import importlib.metadata
                return importlib.metadata.version(package_name)
            except:
                return "Not found"

def check_cuda_info():
    """Check CUDA availability and version"""
    try:
        import torch
        print(f"PyTorch CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"CUDA version (PyTorch): {torch.version.cuda}")
            print(f"cuDNN version: {torch.backends.cudnn.version()}")
            print(f"Number of GPUs: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
    except Exception as e:
        print(f"Error checking CUDA info: {e}")

def get_dependency_tree(package_name):
    """Get dependencies of a package"""
    try:
        dist = pkg_resources.get_distribution(package_name)
        return [str(req) for req in dist.requires()]
    except:
        return []

# Direct imports from test.py
direct_imports = [
    'argparse',  # built-in
    'multiprocessing',  # built-in
    'os',  # built-in
    'datasets',
    'torch',
    'transformers',
    'accelerate',
    'peft',
    'trl'
]

# Additional related packages that might be dependencies
related_packages = [
    'numpy',
    'pandas',
    'pyarrow',
    'tokenizers',
    'safetensors',
    'huggingface-hub',
    'bitsandbytes',
    'scipy',
    'scikit-learn',
    'matplotlib',
    'tqdm',
    'requests',
    'packaging',
    'filelock',
    'fsspec',
    'typing-extensions',
    'psutil'
]

print("=" * 80)
print("PACKAGE VERSION REPORT for test.py")
print("=" * 80)
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print()

print("DIRECT IMPORTS FROM test.py:")
print("-" * 40)
for package in direct_imports:
    if package in ['argparse', 'multiprocessing', 'os']:
        print(f"{package:20} : Built-in module")
    else:
        version = get_package_version(package)
        print(f"{package:20} : {version}")
        
        # Show some key dependencies for ML packages
        if package in ['transformers', 'torch', 'datasets']:
            deps = get_dependency_tree(package)
            if deps:
                print(f"{'':20}   Dependencies: {', '.join(deps[:5])}")
                if len(deps) > 5:
                    print(f"{'':20}   ... and {len(deps)-5} more")

print()
print("RELATED/DEPENDENCY PACKAGES:")
print("-" * 40)
for package in related_packages:
    version = get_package_version(package)
    if version != "Not found":
        print(f"{package:20} : {version}")

print()
print("CUDA AND GPU INFORMATION:")
print("-" * 40)
check_cuda_info()

print()
print("DETAILED TRANSFORMERS INFORMATION:")
print("-" * 40)
try:
    import transformers
    print(f"Transformers version: {transformers.__version__}")
    print(f"Transformers file location: {transformers.__file__}")
    
    # Check if specific functions are available
    try:
        from transformers import top_k_top_p_filtering
        print("✓ top_k_top_p_filtering is available")
    except ImportError as e:
        print(f"✗ top_k_top_p_filtering not available: {e}")
    
    try:
        from transformers.generation.utils import top_k_top_p_filtering
        print("✓ top_k_top_p_filtering available from generation.utils")
    except ImportError as e:
        print(f"✗ top_k_top_p_filtering not available from generation.utils: {e}")
    
except Exception as e:
    print(f"Error importing transformers: {e}")

print()
print("DETAILED TRL INFORMATION:")
print("-" * 40)
try:
    import trl
    print(f"TRL version: {trl.__version__}")
    print(f"TRL file location: {trl.__file__}")
    
    # Check TRL imports
    try:
        from trl import SFTTrainer, SFTConfig
        print("✓ SFTTrainer and SFTConfig are available")
    except ImportError as e:
        print(f"✗ SFTTrainer/SFTConfig not available: {e}")
    
except Exception as e:
    print(f"Error importing trl: {e}")

print()
print("ENVIRONMENT INFORMATION:")
print("-" * 40)
print(f"CONDA_DEFAULT_ENV: {os.environ.get('CONDA_DEFAULT_ENV', 'Not set')}")
print(f"VIRTUAL_ENV: {os.environ.get('VIRTUAL_ENV', 'Not set')}")
print(f"PATH: {os.environ.get('PATH', 'Not set')[:200]}...")

print()
print("=" * 80)
print("END OF REPORT")
print("=" * 80)
