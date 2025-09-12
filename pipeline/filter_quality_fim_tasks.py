import json
import re
from typing import List, Dict, Set

def extract_fim_parts(content: str) -> Dict[str, str]:
    """Extract prefix, suffix, and middle from FIM content"""
    parts = {}
    
    # Extract prefix
    prefix_match = re.search(r'<fim_prefix>(.*?)<fim_suffix>', content, re.DOTALL)
    if prefix_match:
        parts['prefix'] = prefix_match.group(1)
    
    # Extract suffix (usually empty in our case)
    suffix_match = re.search(r'<fim_suffix>(.*?)<fim_middle>', content, re.DOTALL)
    if suffix_match:
        parts['suffix'] = suffix_match.group(1)
    
    # Extract middle
    middle_match = re.search(r'<fim_middle>(.*?)$', content, re.DOTALL)
    if middle_match:
        parts['middle'] = middle_match.group(1)
    
    return parts

def is_meaningful_code_completion(middle: str, prefix: str) -> bool:
    """Judge if the middle part represents a meaningful, feasible auto-completion"""
    
    if not middle or not middle.strip():
        return False
    
    middle_stripped = middle.strip()
    
    # Reject if middle is too short (less than 5 characters after stripping)
    if len(middle_stripped) < 5:
        return False
    
    # Reject if middle is only symbols/punctuation
    if re.match(r'^[\s\{\}\[\]\(\);,\.]+$', middle_stripped):
        return False
    
    # Reject if middle is just a closing brace or return statement without content
    if re.match(r'^[\s}]+$', middle_stripped) or middle_stripped == 'return;':
        return False
    
    # Reject incomplete or meaningless fragments
    meaningless_patterns = [
        r'^[;,]+$',                    # Just punctuation
        r'^\s*\)\s*[;{]*\s*$',        # Just closing parentheses
        r'^\s*else\s*$',               # Standalone else
        r'^\s*\+\+\s*$',               # Just increment
        r'^\s*--\s*$',                 # Just decrement
    ]
    
    for pattern in meaningless_patterns:
        if re.match(pattern, middle_stripped):
            return False
    
    # Reject if middle is only preprocessor directives (except meaningful ones)
    if middle_stripped.startswith('#') and not any(keyword in middle_stripped for keyword in ['#include', '#define', '#ifndef', '#ifdef']):
        return False
    
    # Reject if middle contains only comments
    lines = middle.split('\n')
    non_comment_lines = [l for l in lines if l.strip() and not l.strip().startswith('//') and not l.strip().startswith('/*') and not l.strip().startswith('*')]
    if not non_comment_lines:
        return False
    
    # Reject if middle is just namespace declaration without meaningful content
    if re.match(r'^\s*namespace\s+\w+\s*$', middle_stripped):
        return False
    
    # Accept meaningful C++ constructs
    meaningful_patterns = [
        r'\w+\s*\([^)]*\)',  # Function calls
        r'class\s+\w+',      # Class definitions
        r'struct\s+\w+',     # Struct definitions
        r'\w+\s*=\s*\w+',    # Assignments
        r'if\s*\(',          # Control structures
        r'for\s*\(',
        r'while\s*\(',
        r'return\s+',        # Return statements
        r'#include\s*[<"]',  # Include statements
        r'using\s+namespace', # Using declarations
        r'public:', r'private:', r'protected:', # Access specifiers
        r'\w+::\w+',         # Scope resolution
    ]
    
    for pattern in meaningful_patterns:
        if re.search(pattern, middle_stripped):
            return True
    
    # Check for meaningful variable/function declarations
    if re.search(r'\b(int|double|float|char|bool|void|const|static|virtual|inline)\b', middle_stripped):
        return True
    
    # Check for C++ keywords that indicate meaningful code
    cpp_keywords = ['const', 'static', 'virtual', 'override', 'public', 'private', 'protected', 
                   'class', 'struct', 'enum', 'typedef', 'template', 'typename', 'namespace']
    if any(keyword in middle_stripped for keyword in cpp_keywords):
        return True
    
    # Accept if contains tbricks-specific patterns (domain-specific meaningful code)
    if re.search(r'\bTB[A-Z]+\b', middle_stripped) or 'tbricks::' in middle_stripped:
        return True
    
    return False

def has_logical_context_flow(prefix: str, middle: str, suffix: str) -> bool:
    """Check if the middle logically follows from the prefix context"""
    
    prefix_lines = prefix.strip().split('\n')
    if not prefix_lines:
        return False
    
    last_prefix_line = prefix_lines[-1].strip()
    middle_stripped = middle.strip()
    
    # Check for logical continuations
    logical_continuations = [
        # After includes, expect more includes, namespace, or declarations
        (r'#include\s*[<"]', lambda m: '#include' in m or 'namespace' in m or 'using' in m),
        
        # After namespace declaration, expect opening brace or content
        (r'namespace\s+\w+', lambda m: '{' in m or any(kw in m for kw in ['class', 'struct', 'enum', 'void', 'int'])),
        
        # After class/struct declaration, expect opening brace or inheritance
        (r'(class|struct)\s+\w+', lambda m: '{' in m or ':' in m or 'public' in m or 'private' in m),
        
        # After function signature, expect opening brace or implementation
        (r'\w+\s*\([^)]*\)\s*(const)?\s*$', lambda m: '{' in m or any(kw in m for kw in ['return', 'if', 'for', 'while'])),
        
        # After access specifiers, expect declarations
        (r'(public|private|protected)\s*:', lambda m: any(kw in m for kw in ['void', 'int', 'double', 'virtual', 'static', 'const'])),
    ]
    
    for pattern, check_func in logical_continuations:
        if re.search(pattern, last_prefix_line):
            if check_func(middle_stripped):
                return True
    
    return True  # Default to accepting if no specific pattern matched

def calculate_quality_score(parts: Dict[str, str]) -> float:
    """Calculate a quality score for the FIM task (0-1, higher is better)"""
    
    prefix = parts.get('prefix', '')
    middle = parts.get('middle', '')
    suffix = parts.get('suffix', '')
    
    score = 0.0
    
    # Essential: Check if prefix starts with complete code lines
    if not starts_with_complete_code_line(prefix):
        return 0.0  # Immediate rejection for incomplete prefix
    
    # Base score for having meaningful completion
    if is_meaningful_code_completion(middle, prefix):
        score += 0.4
    
    # Bonus for logical context flow
    if has_logical_context_flow(prefix, middle, suffix):
        score += 0.2
    
    # Bonus for appropriate length (not too short, not too long)
    middle_len = len(middle.strip())
    if 10 <= middle_len <= 200:
        score += 0.2
    elif 5 <= middle_len <= 300:
        score += 0.1
    
    # Bonus for containing domain-specific (tbricks) content
    if 'tbricks' in middle.lower() or re.search(r'\bTB[A-Z]+\b', middle):
        score += 0.1
    
    # Bonus for containing meaningful C++ constructs
    meaningful_constructs = ['class', 'struct', 'namespace', 'public:', 'private:', 'virtual', 'const']
    if any(construct in middle for construct in meaningful_constructs):
        score += 0.1
    
    return min(score, 1.0)

def filter_quality_fim_tasks(input_file: str, output_file: str, quality_threshold: float = 0.5):
    """Filter FIM tasks based on quality assessment"""
    
    print(f"Reading FIM tasks from {input_file}...")
    print(f"Quality threshold: {quality_threshold}")
    
    good_count = 0
    rejected_count = 0
    total_count = 0
    
    # Process line by line and write good tasks immediately to avoid memory issues
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(infile, 1):
            if line.strip():
                total_count += 1
                try:
                    task = json.loads(line)
                    content = task.get('content', '')
                    
                    # Extract FIM parts
                    parts = extract_fim_parts(content)
                    
                    if not all(key in parts for key in ['prefix', 'middle']):
                        rejected_count += 1
                        continue
                    
                    # Calculate quality score
                    quality_score = calculate_quality_score(parts)
                    
                    if quality_score >= quality_threshold:
                        # Add quality score to the task
                        task['quality_score'] = quality_score
                        task['quality_phase'] = 'phase1_context_quality'
                        outfile.write(json.dumps(task, ensure_ascii=False) + '\n')
                        good_count += 1
                    else:
                        rejected_count += 1
                        
                    # Progress report
                    if line_num % 100000 == 0:
                        print(f"Processed {line_num:,} tasks. Accepted: {good_count:,}, Rejected: {rejected_count:,}")
                        
                except json.JSONDecodeError as e:
                    print(f"JSON decode error at line {line_num}: {e}")
                    rejected_count += 1
                    continue
                except Exception as e:
                    print(f"Error at line {line_num}: {e}")
                    rejected_count += 1
                    continue
    
    print(f"\nFiltering complete!")
    print(f"Total tasks processed: {total_count:,}")
    print(f"Good tasks accepted: {good_count:,}")
    print(f"Tasks rejected: {rejected_count:,}")
    print(f"Acceptance rate: {good_count/total_count*100:.2f}%")
    
    print(f"\nSaved {good_count:,} high-quality FIM tasks to {output_file}.")
    
    return good_count, rejected_count

def analyze_sample_tasks(input_file: str, num_samples: int = 10):
    """Analyze a few sample tasks to show the filtering criteria in action"""
    
    print(f"\nAnalyzing {num_samples} sample tasks from {input_file}:")
    print("=" * 80)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= num_samples:
                break
                
            if line.strip():
                task = json.loads(line)
                content = task.get('content', '')
                parts = extract_fim_parts(content)
                
                if 'middle' in parts and 'prefix' in parts:
                    quality_score = calculate_quality_score(parts)
                    
                    print(f"\nSample {i+1}:")
                    print(f"Prefix (last 50 chars): ...{parts['prefix'][-50:]}")
                    print(f"Middle: {parts['middle']}")
                    print(f"Quality Score: {quality_score:.2f}")
                    print(f"Accept: {'YES' if quality_score >= 0.5 else 'NO'}")
                    print("-" * 40)

def starts_with_complete_code_line(prefix: str) -> bool:
    """Check if prefix starts with complete code lines based on analysis of reference file patterns"""
    if not prefix or not prefix.strip():
        return False
    
    # Get the first meaningful line (skip empty lines)
    lines = prefix.split('\n')
    first_line = None
    for line in lines:
        stripped = line.strip()
        if stripped:
            first_line = stripped
            break
    
    if not first_line:
        return False
    
    # REJECT: If the original first line (before stripping) has excessive leading whitespace
    # This indicates the context starts in the middle of a code block, which is poor for FIM
    original_first_line = lines[0] if lines else ""
    leading_spaces = len(original_first_line) - len(original_first_line.lstrip())
    if leading_spaces > 4:  # More than one level of indentation suggests starting mid-block
        return False
    
    # REJECT: Lines that start with meaningless delimiters or incomplete control structures
    # These make poor auto-completion contexts as identified by the user
    
    # Reject if starts with incomplete control structures without proper context
    incomplete_control_patterns = [
        r'^if\s*\(',           # Standalone if statements
        r'^else\s*$',          # Standalone else
        r'^else\s*if\s*\(',    # Standalone else if
        r'^for\s*\(',          # Standalone for loops
        r'^while\s*\(',        # Standalone while loops
        r'^switch\s*\(',       # Standalone switch
        r'^catch\s*\(',        # Standalone catch
        r'^try\s*$',           # Standalone try
        r'^return\s*[^;]*$',   # Incomplete return statements
    ]
    
    for pattern in incomplete_control_patterns:
        if re.match(pattern, first_line):
            return False
    
    # REJECT: Lines that are only closing braces or meaningless punctuation
    if re.match(r'^[\s{}\[\]();,\.]*$', first_line):
        return False
    
    # REJECT: Single words or identifiers without context
    if re.match(r'^\w+$', first_line):
        return False
    
    # BOOST: #include patterns (51.3% in reference, only 1.7% in generated)
    if first_line.startswith('#include') and (first_line.endswith('.h"') or first_line.endswith('.hpp"') or first_line.endswith('>') or '"' in first_line):
        return True
    
    # BOOST: OTHER_PREPROCESSOR patterns like #pragma (45.0% in reference, only 0.2% in generated)
    if first_line.startswith('#pragma'):
        return True
    
    # Accept other meaningful preprocessor directives
    if first_line.startswith('#ifndef') or first_line.startswith('#ifdef') or first_line.startswith('#define'):
        return True
    
    # Accept namespace and using statements (present in reference)
    if first_line.startswith('namespace ') or first_line.startswith('using '):
        return True
    
    # Accept complete class/struct declarations
    if first_line.startswith('class ') or first_line.startswith('struct ') or first_line.startswith('enum '):
        return True
    
    # Accept complete function declarations/definitions (must have both function name and parentheses)
    if re.match(r'^[\w:<>~]+.*\w+\s*\([^)]*\)', first_line):
        return True
    
    # REDUCE: function calls/statements without proper context (2.6% vs 33.6%)
    if (re.match(r'^[A-Z_]+\(', first_line) or  # TEST_, EXPECT_, etc.
        first_line.startswith('auto ') or 
        first_line.startswith('const ') or
        first_line.startswith('static ')):
        return False
    
    # REDUCE: method_definition patterns without class context (0.4% vs 15.6%)
    if '::' in first_line and '(' in first_line and not first_line.startswith('#'):
        return False
    
    # REDUCE: variable_declaration patterns without class/function context (0% vs 13.1%)
    if re.match(r'^(const\s+)?(static\s+)?(virtual\s+)?[\w:<>]+\s+\w+\s*[=;]', first_line):
        return False
    
    # REDUCE: access_specifier without proper context
    if first_line.rstrip(':') in ['public', 'private', 'protected']:
        return False
    
    # Accept complete statements that provide meaningful context
    # These should be complete logical units that a developer can reasonably continue
    meaningful_complete_patterns = [
        r'^#\w+',              # Preprocessor directives
        r'^\w+\s+\w+.*[;{]$',  # Complete declarations or definitions
        r'^typedef\s+',        # Type definitions
        r'^template\s*<',      # Template declarations
        r'^\w+::\w+',          # Scoped identifiers (when not in function calls)
    ]
    
    for pattern in meaningful_complete_patterns:
        if re.match(pattern, first_line):
            return True
    
    # Reject everything else to be more conservative
    # This ensures we only get high-quality FIM tasks with meaningful starting context
    return False

if __name__ == '__main__':
    # Process the full dataset
    input_file = 'prompts_codebricks_autogenerated_underscore.jsonl'
    output_file = 'prompts_codebricks_filtered_improved.jsonl'
    
    print("Processing full dataset...")
    print("This may take several minutes due to the large file size...")
    
    # First, analyze some samples to show the process
    print("Analyzing sample tasks...")
    analyze_sample_tasks(input_file, num_samples=10)
    
    # Then filter all tasks
    good_count, rejected_count = filter_quality_fim_tasks(
        input_file=input_file,
        output_file=output_file,
        quality_threshold=0.5
    )
