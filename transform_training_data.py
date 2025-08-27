import json

def transform_prompts(input_file, output_file):
    """
    Transform prompts_nosuffix.json to new format:
    1. Combine "prompt" and "output" as "content" (output after prompt)
    2. Rename <FIM_PREFIX> to <fim-prefix>
    3. Rename <FIM_MIDDLE> to <fim-suffix><fim-middle>
    """
    
    # Read the input JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    transformed_data = []
    
    for item in data:
        # Combine prompt and output
        prompt = item.get('prompt', '')
        output = item.get('output', '')
        content = prompt + output
        
        # Apply tag transformations
        content = content.replace('<FIM_PREFIX>', '<fim-prefix>')
        content = content.replace('<FIM_MIDDLE>', '<fim-suffix><fim-middle>')
        
        # Create new item with transformed content
        new_item = {
            'content': content
        }
        
        # Preserve any other fields that might exist
        for key, value in item.items():
            if key not in ['prompt', 'output']:
                new_item[key] = value
        
        transformed_data.append(new_item)
    
    # Write the transformed data to output file in JSONL format
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in transformed_data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')
    
    print(f"Transformation complete! Output saved to {output_file}")
    print(f"Processed {len(transformed_data)} items")

if __name__ == "__main__":
    #input_file = "prompts_nosuffix.json"
    input_file = "prompts_origin_starcoder2_format.json"
    output_file = "prompts_transformed_ver2.jsonl"
    
    try:
        transform_prompts(input_file, output_file)
    except FileNotFoundError:
        print(f"Error: {input_file} not found in current directory")
    except json.JSONDecodeError:
        print(f"Error: {input_file} is not a valid JSON file")
    except Exception as e:
        print(f"Error: {e}")