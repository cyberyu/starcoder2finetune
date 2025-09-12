#!/usr/bin/env python3
"""
FIM Middle Content Quality Filter - Streamlined Version

Apply middle content filtering based on the analysis showing:
- 9.4% incomplete_comma patterns (vs 2.0% in reference) - eliminate these  
- 2.8% standalone_access_specifier - eliminate these
- 12.4% total rejection rate expected
- Target: ~1.41M high-quality tasks from 1.61M input
"""

import json
import re
from datetime import datetime

def extract_fim_middle(content):
    """Extract fim_middle content from FIM task"""
    try:
        match = re.search(r'<fim_middle>(.*?)(?:<|$)', content, re.DOTALL)
        return match.group(1).strip() if match else ""
    except:
        return ""

def calculate_middle_quality_score(middle_content):
    """Calculate quality score for middle content (0.0-1.0, higher is better)"""
    if not middle_content:
        return 0.0
    
    content = middle_content.strip()
    score = 0.6  # Base score for non-empty content
    
    # Bonus for appropriate length
    length = len(content)
    if 10 <= length <= 100:
        score += 0.2
    elif 5 <= length <= 200:
        score += 0.1
    
    # Bonus for complete constructs (not ending with problematic patterns)
    if not content.endswith((',', '::', '->', '.', '(')):
        score += 0.1
    
    # Bonus for meaningful C++ patterns
    meaningful_patterns = [
        r'\w+\s*\([^)]*\)',  # Function calls
        r'\w+\s*=\s*',       # Assignments
        r'return\s+',        # Return statements
        r'if\s*\(',          # Control structures
        r'for\s*\(',
        r'while\s*\(',
    ]
    
    for pattern in meaningful_patterns:
        if re.search(pattern, content):
            score += 0.05
            break
    
    # Penalty for purely symbolic content
    if re.match(r'^[{}\(\)\[\];,\s]*$', content):
        score -= 0.3
    
    return min(max(score, 0.0), 1.0)

def should_reject_middle(middle_content):
    """Check if middle content should be rejected based on quality analysis"""
    if not middle_content:
        return True, "empty"
    
    content = middle_content.strip()
    
    # Major problems identified in analysis:
    
    # 1. Incomplete comma patterns (9.4% vs 2.0% in reference)
    if content.endswith(','):
        return True, "incomplete_comma"
    
    # 2. Standalone access specifiers (2.8%, low quality)
    if re.match(r'^\s*(public|private|protected)\s*:\s*$', content):
        return True, "standalone_access_specifier" 
    
    # 3. Too short (minimal value)
    if len(content) <= 2:
        return True, "too_short"
    
    # 4. Pure symbols 
    if re.match(r'^[{}\(\)\[\];,\s]*$', content):
        return True, "pure_symbols"
    
    # 5. Incomplete scope operators
    if content.endswith(('::','->', '.', '(')) and len(content) < 15:
        return True, "incomplete_scope"
    
    return False, "acceptable"

def filter_dataset():
    """Apply middle content quality filtering"""
    
    input_file = "prompts_codebricks_filtered_improved.jsonl"
    output_file = "prompts_codebricks_filtered_middle_quality.jsonl"
    
    print("FIM Middle Content Quality Filter")
    print("=" * 50)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Start:  {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    stats = {
        'total': 0,
        'kept': 0,
        'rejected': 0,
        'reasons': {}
    }
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                
                # Progress update
                if line_num % 100000 == 0:
                    rate = (stats['kept'] / stats['total'] * 100) if stats['total'] > 0 else 0
                    print(f"Processed: {line_num:,} | Kept: {stats['kept']:,} | Rate: {rate:.1f}%")
                
                line = line.strip()
                if not line:
                    continue
                
                stats['total'] += 1
                
                try:
                    data = json.loads(line)
                    content = data.get('content', '')
                    
                    # Extract and check middle content
                    middle = extract_fim_middle(content)
                    should_reject, reason = should_reject_middle(middle)
                    
                    if should_reject:
                        stats['rejected'] += 1
                        stats['reasons'][reason] = stats['reasons'].get(reason, 0) + 1
                    else:
                        stats['kept'] += 1
                        # Calculate and add Phase 2 quality information
                        middle_quality_score = calculate_middle_quality_score(middle)
                        data['quality_phase2'] = 'passed_middle_content_filter'
                        data['quality_middle_reason'] = reason
                        data['quality_middle_score'] = middle_quality_score
                        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                        
                except json.JSONDecodeError:
                    stats['rejected'] += 1
                    stats['reasons']['json_error'] = stats['reasons'].get('json_error', 0) + 1
                    continue
    
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Final results
    print("\n" + "=" * 50) 
    print("FILTERING RESULTS")
    print("=" * 50)
    
    total = stats['total']
    kept = stats['kept'] 
    rejected = stats['rejected']
    acceptance_rate = (kept / total * 100) if total > 0 else 0
    
    print(f"Total processed:     {total:,}")
    print(f"Tasks kept:          {kept:,} ({acceptance_rate:.1f}%)")
    print(f"Tasks rejected:      {rejected:,} ({rejected/total*100:.1f}%)")
    
    print(f"\nRejection reasons:")
    print("-" * 30)
    for reason, count in sorted(stats['reasons'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        print(f"{reason:<20} {count:>8,} ({pct:>5.1f}%)")
    
    print(f"\nOutput saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    filter_dataset()
