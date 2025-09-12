import os
import re
import json

def get_code_files(root_dir):
    code_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for f in filenames:
            if f.endswith(('.h', '.cpp', '.hpp')):
                code_files.append(os.path.join(dirpath, f))
    return code_files

def is_code_line(line):
    stripped = line.strip()
    if not stripped:
        return False
    if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('*/'):
        return False
    if '| Templates *' in line or 'open the template in the editor. */ /* *' in line:
        return False
    return True

def has_real_code(lines):
    """Check if lines contain at least one or two lines of real C++ code (not just comments, brackets, or control chars)"""
    real_code_count = 0
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Skip comments
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*') or stripped.startswith('*/'):
            continue
        # Skip lines that are only brackets, semicolons, or other control characters
        if re.match(r'^[\s{}\[\]();,\.]*$', stripped):
            continue
        # Skip preprocessor directives (unless they're meaningful like #include)
        if stripped.startswith('#') and not stripped.startswith('#include'):
            continue
        # This looks like real code
        real_code_count += 1
        if real_code_count >= 1:  # At least 1 line of real code
            return True
    return False

def clean_input_context(context_lines):
    # Remove leading blank lines and comments from context
    while context_lines and (not context_lines[0].strip() or context_lines[0].strip().startswith('/*') or context_lines[0].strip().startswith('//') or context_lines[0].strip().startswith('*')):
        context_lines = context_lines[1:]
    # Remove all comment lines from context
    context_lines = [l for l in context_lines if not (l.strip().startswith('/*') or l.strip().startswith('//') or l.strip().startswith('*'))]
    return context_lines

def clean_output_lines(output_lines):
    # Remove output lines that are only a dangling '{'
    cleaned = [l for l in output_lines if l.strip() != '{']
    # If last line is a dangling '{', remove it
    while cleaned and cleaned[-1].strip() == '{':
        cleaned = cleaned[:-1]
    # If output is a single line ending with '{', remove the trailing '{'
    if cleaned and len(cleaned) == 1 and cleaned[0].strip().endswith('{'):
        cleaned[0] = cleaned[0].rstrip(' {').rstrip()
    # Remove leading spaces from each output line
    cleaned = [l.lstrip() for l in cleaned]
    # Remove lines that are only a single '}'
    cleaned = [l for l in cleaned if l.strip() != '}']
    # Remove trailing '}' if it is unpaired (appears more times than '{')
    open_brackets = sum(l.count('{') for l in cleaned)
    close_brackets = sum(l.count('}') for l in cleaned)
    while cleaned and close_brackets > open_brackets and cleaned[-1].strip() == '}':
        cleaned = cleaned[:-1]
        close_brackets -= 1
    return cleaned

def has_invalid_preprocessor_structure(context_lines):
    """
    Check if the context has invalid preprocessor structure
    (e.g., #else without #ifdef, unmatched directives)
    """
    stack = []
    for line in context_lines:
        stripped = line.strip()
        if stripped.startswith('#'):
            if re.match(r'#\s*if(def|ndef)?\b', stripped):
                stack.append('if')
            elif stripped.startswith('#else'):
                if not stack:
                    return True  # #else without corresponding #if
            elif stripped.startswith('#elif'):
                if not stack:
                    return True  # #elif without corresponding #if
            elif stripped.startswith('#endif'):
                if not stack:
                    return True  # #endif without corresponding #if
                stack.pop()
    
    # If stack is not empty, we have unmatched #if directives
    # This is actually okay for prefix context as long as there's no orphaned #else
    return False

def extract_pairs_from_file(filepath, min_context=2, max_context=10, max_output=2):
    pairs = []
    seen_pairs = set()  # Deduplication set
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    code_indices = [i for i, l in enumerate(lines) if is_code_line(l)]
    
    # Strategy 1: Extract pairs with varying output lengths (1 line and 2 lines)
    for output_len in [1, 2]:  # Generate pairs for both 1-line and 2-line outputs
        for idx in range(len(code_indices) - output_len):
            for context_len in range(min_context, max_context+1):
                context_end = code_indices[idx]
                context_start = context_end - context_len + 1
                if context_start < 0:
                    continue
                context_lines = [lines[i].rstrip('\n') for i in range(context_start, context_end+1)]
                context_lines = clean_input_context(context_lines)
                # Check for invalid preprocessor structure (e.g., #else without #ifdef)
                if has_invalid_preprocessor_structure(context_lines):
                    continue
                output_lines = []
                for j in range(1, output_len+1):
                    if idx + j < len(code_indices):
                        output_lines.append(lines[code_indices[idx + j]].rstrip('\n'))
                output_lines = clean_output_lines(output_lines)
                if context_lines and output_lines:
                    # Ensure output contains at least one line of real C++ code
                    if not has_real_code(output_lines):
                        continue
                    # Avoid context/output that starts or ends with only brackets or is inside a comment block
                    if not re.match(r'^\s*[\}\];,]+\s*$', context_lines[-1]) and not any('| Templates *' in l or 'open the template in the editor. */ /* *' in l for l in context_lines + output_lines):
                        prefix = '\n'.join(context_lines)
                        middle = '\n'.join(output_lines)
                        # Create FIM format with underscore tags
                        fim_content = f"<fim_prefix>{prefix}<fim_suffix><fim_middle>{middle}"
                        pair_tuple = (prefix, middle)
                        if pair_tuple not in seen_pairs:
                            pairs.append({
                                'content': fim_content
                            })
                            seen_pairs.add(pair_tuple)
    
    # Strategy 2: Add overlapping sliding window pairs (with step size < context length)
    step_size = 2  # Step by 2 lines instead of full context length
    for idx in range(0, len(code_indices) - max_output, step_size):
        for context_len in range(min_context, max_context+1):
            context_end = code_indices[idx]
            context_start = context_end - context_len + 1
            if context_start < 0:
                continue
            context_lines = [lines[i].rstrip('\n') for i in range(context_start, context_end+1)]
            context_lines = clean_input_context(context_lines)
            # Check for invalid preprocessor structure (e.g., #else without #ifdef)
            if has_invalid_preprocessor_structure(context_lines):
                continue
            output_lines = []
            for j in range(1, max_output+1):
                if idx + j < len(code_indices):
                    output_lines.append(lines[code_indices[idx + j]].rstrip('\n'))
            output_lines = clean_output_lines(output_lines)
            if context_lines and output_lines:
                # Ensure output contains at least one line of real C++ code
                if not has_real_code(output_lines):
                    continue
                # Avoid context/output that starts or ends with only brackets or is inside a comment block
                if not re.match(r'^\s*[\}\];,]+\s*$', context_lines[-1]) and not any('| Templates *' in l or 'open the template in the editor. */ /* *' in l for l in context_lines + output_lines):
                    prefix = '\n'.join(context_lines)
                    middle = '\n'.join(output_lines)
                    # Create FIM format with underscore tags
                    fim_content = f"<fim_prefix>{prefix}<fim_suffix><fim_middle>{middle}"
                    pair_tuple = (prefix, middle)
                    if pair_tuple not in seen_pairs:
                        pairs.append({
                            'content': fim_content
                        })
                        seen_pairs.add(pair_tuple)
    
    return pairs

def main():
    root_dir = 'code'
    code_files = get_code_files(root_dir)
    all_pairs = []
    for f in code_files:
        pairs = extract_pairs_from_file(f)
        all_pairs.extend(pairs)
    with open('prompts_codebricks_autogenerated_underscore.jsonl', 'w', encoding='utf-8') as out:
        for pair in all_pairs:
            out.write(json.dumps(pair, ensure_ascii=False) + '\n')
    print(f"Extracted {len(all_pairs)} FIM pairs in underscore format.")

if __name__ == '__main__':
    main()
