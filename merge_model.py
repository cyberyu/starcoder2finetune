# load the base and fine-tuned model
import argparse
import multiprocessing
import os
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import transformers
from accelerate import PartialState
from datasets import load_dataset
from peft import LoraConfig
from transformers import (
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    logging,
    set_seed,
)

from peft import PeftModel, PeftConfig


nf4_config = BitsAndBytesConfig(
   load_in_4bit=True,
   bnb_4bit_quant_type="nf4",
   bnb_4bit_use_double_quant=True,
   bnb_4bit_compute_dtype=torch.bfloat16
)

#config = PeftConfig.from_pretrained("/usr/project/starcoder2/finetune_starcoder2_underscore/checkpoint-10000")

# base_model = "/usr/project/refact/dockercode2_back/starcoder2_7b_22k_ft_80EM_underscore/"

base_model = 'bigcode/starcoder2-7b'
model = AutoModelForCausalLM.from_pretrained(
    base_model,
    #quantization_config=nf4_config,
    device_map="cuda:0",
    # offload_folder="offload",
    # offload_state_dict=True, 
    torch_dtype=torch.float16
)
model = PeftModel.from_pretrained(model, "/mnt/teamssd/compressed_LLM_tbricks/finetune_starcoder2_combinedThree/checkpoint-40000/")
model = model.merge_and_unload()

merged_model_path= f"/mnt/teamssd/compressed_LLM_tbricks/starcoder2_7b_22k_ft_80EM_triple_trained_new"
model.save_pretrained(merged_model_path)


tokenizer = AutoTokenizer.from_pretrained("/mnt/teamssd/compressed_LLM_tbricks/finetune_starcoder2_combinedThree/checkpoint-40000/")
tokenizer.save_pretrained(merged_model_path)
