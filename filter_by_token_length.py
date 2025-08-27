import json

def filter_jsonl_by_token_length(input_file, output_file, max_tokens=500):
    kept = 0
    discarded = 0
    with open(input_file, 'r', encoding='utf-8') as fin, \
         open(output_file, 'w', encoding='utf-8') as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            content = obj.get("content", "")
            token_count = len(content.split())
            if token_count < max_tokens:
                json.dump(obj, fout, ensure_ascii=False)
                fout.write('\n')
                kept += 1
            else:
                discarded += 1
    print(f"Kept {kept} items, discarded {discarded} items (>{max_tokens} tokens)")

if __name__ == "__main__":
    input_file = "prompts_transformed.jsonl"
    output_file = "prompts_transformed_filtered.jsonl"
    filter_jsonl_by_token_length(input_file, output_file)
