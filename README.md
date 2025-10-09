https://huggingface.co/docs/peft/main/en/developer_guides/model_merging

vllm serve starcoder2_7b_triple_Train_w8a8_optimal

🎯 Running FIM validation on 1000 test cases...
✅ Loaded 1000 test cases
Progress: 50/1000 | Success: 64.0% | Avg: 2119ms
Progress: 100/1000 | Success: 60.0% | Avg: 2289ms
Progress: 150/1000 | Success: 64.0% | Avg: 2129ms
Progress: 200/1000 | Success: 62.5% | Avg: 2174ms
Progress: 250/1000 | Success: 62.4% | Avg: 2175ms
Progress: 300/1000 | Success: 63.7% | Avg: 2125ms
Progress: 350/1000 | Success: 62.9% | Avg: 2194ms
Progress: 400/1000 | Success: 63.7% | Avg: 2191ms
Progress: 450/1000 | Success: 63.3% | Avg: 2197ms
Progress: 500/1000 | Success: 64.6% | Avg: 2156ms
Progress: 550/1000 | Success: 65.1% | Avg: 2121ms
Progress: 600/1000 | Success: 64.5% | Avg: 2121ms
Progress: 650/1000 | Success: 64.9% | Avg: 2091ms
Progress: 700/1000 | Success: 64.4% | Avg: 2092ms
Progress: 750/1000 | Success: 64.0% | Avg: 2094ms
Progress: 800/1000 | Success: 63.5% | Avg: 2099ms
Progress: 850/1000 | Success: 63.2% | Avg: 2104ms
Progress: 900/1000 | Success: 63.2% | Avg: 2094ms
Progress: 950/1000 | Success: 63.4% | Avg: 2081ms
Progress: 1000/1000 | Success: 63.3% | Avg: 2076ms

============================================================
📊 VALIDATION RESULTS
============================================================
✅ Success: 633/1000 (63.3%)
❌ Failed: 367/1000
⚡ Avg response: 2076ms
⏱️ Total time: 1314.4s
🤖 Model: starcoder2_7b_triple_Train_w8a8_optimal
👍 GOOD - Backend functional
✅ Validation completed!

************************************************************************************************
vllm serve starcoder2_7b_22k_ft_80EM_SingleLine_trained

🎯 Running FIM validation on 1000 test cases...
✅ Loaded 1000 test cases
Progress: 50/1000 | Success: 78.0% | Avg: 2350ms
Progress: 100/1000 | Success: 73.0% | Avg: 2514ms
Progress: 150/1000 | Success: 76.0% | Avg: 2413ms
Progress: 200/1000 | Success: 75.0% | Avg: 2450ms
Progress: 250/1000 | Success: 76.4% | Avg: 2405ms
Progress: 300/1000 | Success: 77.0% | Avg: 2386ms
Progress: 350/1000 | Success: 78.9% | Avg: 2324ms
Progress: 400/1000 | Success: 80.0% | Avg: 2296ms
Progress: 450/1000 | Success: 79.6% | Avg: 2312ms
Progress: 500/1000 | Success: 81.0% | Avg: 2270ms
Progress: 550/1000 | Success: 81.5% | Avg: 2257ms
Progress: 600/1000 | Success: 81.3% | Avg: 2260ms
Progress: 650/1000 | Success: 81.2% | Avg: 2265ms
Progress: 700/1000 | Success: 81.1% | Avg: 2268ms
Progress: 750/1000 | Success: 81.2% | Avg: 2266ms
Progress: 800/1000 | Success: 80.9% | Avg: 2274ms
Progress: 850/1000 | Success: 81.2% | Avg: 2268ms
Progress: 900/1000 | Success: 80.8% | Avg: 2280ms
Progress: 950/1000 | Success: 80.9% | Avg: 2294ms
Progress: 1000/1000 | Success: 80.8% | Avg: 2312ms

============================================================
📊 VALIDATION RESULTS
============================================================
✅ Success: 808/1000 (80.8%)
❌ Failed: 192/1000
⚡ Avg response: 2312ms
⏱️ Total time: 1868.0s
🤖 Model: starcoder2_7b_22k_ft_80EM_SingleLine_trained
🎉 EXCELLENT - WebIDE pipeline working well!
✅ Validation completed!
************************************************************************************************
vllm serve starcoder2_7b_22k_ft_80EM_combined_trained

🎯 Running FIM validation on 1000 test cases...
✅ Loaded 1000 test cases
Progress: 50/1000 | Success: 70.0% | Avg: 2632ms
Progress: 100/1000 | Success: 62.0% | Avg: 2973ms
Progress: 150/1000 | Success: 66.7% | Avg: 2974ms
Progress: 200/1000 | Success: 66.5% | Avg: 3091ms
Progress: 250/1000 | Success: 68.4% | Avg: 3070ms
Progress: 300/1000 | Success: 69.0% | Avg: 3100ms
Progress: 350/1000 | Success: 69.1% | Avg: 3130ms
Progress: 400/1000 | Success: 69.5% | Avg: 3135ms
Progress: 450/1000 | Success: 69.8% | Avg: 3111ms
Progress: 500/1000 | Success: 70.8% | Avg: 3048ms
Progress: 550/1000 | Success: 70.5% | Avg: 3057ms
Progress: 600/1000 | Success: 69.8% | Avg: 3079ms
Progress: 650/1000 | Success: 70.2% | Avg: 3062ms
Progress: 700/1000 | Success: 70.0% | Avg: 3067ms
Progress: 750/1000 | Success: 70.0% | Avg: 3064ms
Progress: 800/1000 | Success: 69.8% | Avg: 3068ms
Progress: 850/1000 | Success: 69.3% | Avg: 3089ms
Progress: 900/1000 | Success: 69.2% | Avg: 3086ms
Progress: 950/1000 | Success: 69.4% | Avg: 3078ms
Progress: 1000/1000 | Success: 69.2% | Avg: 3083ms

============================================================
📊 VALIDATION RESULTS
============================================================
✅ Success: 692/1000 (69.2%)
❌ Failed: 308/1000
⚡ Avg response: 3083ms
⏱️ Total time: 2133.2s
🤖 Model: starcoder2_7b_22k_ft_80EM_combined_trained
👍 GOOD - Backend functional
✅ Validation completed!
************************************************************************************************
vllm serve starcoder2_7b_22k_ft_80EM_triple_trained

🎯 Running FIM validation on 1000 test cases...
✅ Loaded 1000 test cases
Progress: 50/1000 | Success: 64.0% | Avg: 3019ms
Progress: 100/1000 | Success: 59.0% | Avg: 3207ms
Progress: 150/1000 | Success: 62.0% | Avg: 3018ms
Progress: 200/1000 | Success: 61.0% | Avg: 3049ms
Progress: 250/1000 | Success: 61.2% | Avg: 3027ms
Progress: 300/1000 | Success: 62.3% | Avg: 2973ms
