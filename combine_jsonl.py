import json

def combine_jsonl_files(file1, file2, output_file):
    """
    Combine two JSONL files into a single JSONL file.
    """
    
    combined_count = 0
    
    with open(output_file, 'w', encoding='utf-8') as outf:
        # Read and write from first file
        try:
            with open(file1, 'r', encoding='utf-8') as f1:
                for line in f1:
                    line = line.strip()
                    if line:  # Skip empty lines
                        outf.write(line + '\n')
                        combined_count += 1
            print(f"Added {combined_count} items from {file1}")
        except FileNotFoundError:
            print(f"Warning: {file1} not found, skipping...")
        
        file1_count = combined_count
        
        # Read and write from second file
        try:
            with open(file2, 'r', encoding='utf-8') as f2:
                for line in f2:
                    line = line.strip()
                    if line:  # Skip empty lines
                        outf.write(line + '\n')
                        combined_count += 1
            print(f"Added {combined_count - file1_count} items from {file2}")
        except FileNotFoundError:
            print(f"Warning: {file2} not found, skipping...")
    
    print(f"Combined {combined_count} total items into {output_file}")

if __name__ == "__main__":
    file1 = "nextline_fim.jsonl"
    file2 = "prompts_transformed.jsonl"
    output_file = "combined_training_data.jsonl"
    
    try:
        combine_jsonl_files(file1, file2, output_file)
    except Exception as e:
        print(f"Error: {e}")
