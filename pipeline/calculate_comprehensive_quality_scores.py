#!/usr/bin/env python3
"""
Comprehensive Quality Score Calculator for FIM Tasks

This script calculates and adds comprehensive quality scores to FIM tasks,
integrating all three phases of quality assessment:
- Phase 1: Context Quality (prefix completeness, meaningful completion)
- Phase 2: Middle Content Quality (pattern-based assessment)
- Phase 3: Length-Based Quality (adaptive ratio scoring)

Final output includes all individual scores plus a composite quality score.
"""

import json
import re
from datetime import datetime
from typing import Dict, Tuple

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

def calculate_phase1_score(parts: Dict[str, str]) -> float:
    """Calculate Phase 1 context quality score (0.0-1.0)"""
    prefix = parts.get('prefix', '')
    middle = parts.get('middle', '')
    suffix = parts.get('suffix', '')
    
    if not starts_with_complete_code_line(prefix):
        return 0.0
    
    score = 0.0
    
    # Base score for meaningful completion
    if is_meaningful_code_completion(middle, prefix):
        score += 0.4
    
    # Bonus for logical context flow
    if has_logical_context_flow(prefix, middle, suffix):
        score += 0.2
    
    # Bonus for appropriate length
    middle_len = len(middle.strip())
    if 10 <= middle_len <= 200:
        score += 0.2
    elif 5 <= middle_len <= 300:
        score += 0.1
    
    # Bonus for domain-specific content
    if 'tbricks' in middle.lower() or re.search(r'\bTB[A-Z]+\b', middle):
        score += 0.1
    
    # Bonus for meaningful C++ constructs
    meaningful_constructs = ['class', 'struct', 'namespace', 'public:', 'private:', 'virtual', 'const']
    if any(construct in middle for construct in meaningful_constructs):
        score += 0.1
    
    return min(score, 1.0)

def calculate_phase2_score(middle: str) -> float:
    """Calculate Phase 2 middle content quality score (0.0-1.0)"""
    if not middle:
        return 0.0
    
    content = middle.strip()
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

def calculate_phase3_score(prefix: str, middle: str) -> float:
    """Calculate Phase 3 length-based quality score (0.0-1.0)"""
    if not prefix or not middle:
        return 0.0
    
    prefix_len = len(prefix)
    middle_len = len(middle)
    ratio = middle_len / prefix_len if prefix_len > 0 else float('inf')
    
    score = 0.5  # Base score
    
    # Prefix length scoring
    if 200 <= prefix_len <= 1000:
        score += 0.2  # Optimal prefix length
    elif 100 <= prefix_len <= 2000:
        score += 0.1  # Good prefix length
    elif prefix_len < 50 or prefix_len > 5000:
        score -= 0.2  # Poor prefix length
    
    # Middle length scoring
    if 20 <= middle_len <= 150:
        score += 0.2  # Optimal middle length
    elif 10 <= middle_len <= 300:
        score += 0.1  # Good middle length
    elif middle_len < 8 or middle_len > 400:
        score -= 0.2  # Poor middle length
    
    # Ratio scoring (adaptive based on prefix length)
    if prefix_len <= 150:
        optimal_ratio = 0.4
        max_good_ratio = 0.8
    elif prefix_len <= 300:
        optimal_ratio = 0.3
        max_good_ratio = 0.6
    elif prefix_len <= 500:
        optimal_ratio = 0.25
        max_good_ratio = 0.4
    else:
        optimal_ratio = 0.2
        max_good_ratio = 0.3
    
    if ratio <= optimal_ratio:
        score += 0.1  # Good ratio
    elif ratio <= max_good_ratio:
        score += 0.05  # Acceptable ratio
    else:
        score -= 0.1  # Poor ratio
    
    return min(max(score, 0.0), 1.0)

def calculate_composite_score(phase1_score: float, phase2_score: float, phase3_score: float) -> float:
    """Calculate composite quality score weighted across all phases"""
    # Weighted average: Phase 1 is most important (context), then Phase 2 (content), then Phase 3 (length)
    weights = {'phase1': 0.5, 'phase2': 0.3, 'phase3': 0.2}
    
    composite = (
        weights['phase1'] * phase1_score +
        weights['phase2'] * phase2_score + 
        weights['phase3'] * phase3_score
    )
    
    return min(max(composite, 0.0), 1.0)

# Import helper functions from the original filter
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

def starts_with_complete_code_line(prefix: str) -> bool:
    """Check if prefix starts with complete code lines"""
    if not prefix or not prefix.strip():
        return False
    
    lines = prefix.split('\n')
    first_line = None
    for line in lines:
        stripped = line.strip()
        if stripped:
            first_line = stripped
            break
    
    if not first_line:
        return False
    
    # Check for excessive leading whitespace
    original_first_line = lines[0] if lines else ""
    leading_spaces = len(original_first_line) - len(original_first_line.lstrip())
    if leading_spaces > 4:
        return False
    
    # Accept meaningful starting patterns
    meaningful_starts = [
        r'^#include',          # Include statements
        r'^#pragma',           # Pragma directives
        r'^#ifndef',           # Header guards
        r'^#ifdef',
        r'^#define',
        r'^namespace\s+',      # Namespace declarations
        r'^using\s+',          # Using declarations
        r'^class\s+',          # Class declarations
        r'^struct\s+',         # Struct declarations
        r'^enum\s+',           # Enum declarations
    ]
    
    for pattern in meaningful_starts:
        if re.match(pattern, first_line):
            return True
    
    # Accept complete function declarations
    if re.match(r'^[\w:<>~]+.*\w+\s*\([^)]*\)', first_line):
        return True
    
    return False

def process_dataset_with_comprehensive_scores():
    """Process dataset and add comprehensive quality scores"""
    
    # Use the final filtered dataset as input
    input_file = "prompts_codebricks_filtered_phase3b_improved.jsonl"
    output_file = "prompts_codebricks_final_with_quality_scores.jsonl"
    
    print("🎯 COMPREHENSIVE QUALITY SCORE CALCULATOR")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Start:  {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    stats = {
        'total': 0,
        'processed': 0,
        'phase1_scores': [],
        'phase2_scores': [],
        'phase3_scores': [],
        'composite_scores': []
    }
    
    try:
        with open(input_file, 'r', encoding='utf-8') as infile, \
             open(output_file, 'w', encoding='utf-8') as outfile:
            
            for line_num, line in enumerate(infile, 1):
                
                # Progress update
                if line_num % 50000 == 0:
                    print(f"Processed: {line_num:,} tasks")
                
                line = line.strip()
                if not line:
                    continue
                
                stats['total'] += 1
                
                try:
                    data = json.loads(line)
                    content = data.get('content', '')
                    
                    # Extract FIM parts
                    parts = extract_fim_parts(content)
                    
                    if not all(key in parts for key in ['prefix', 'middle']):
                        continue
                    
                    prefix = parts['prefix']
                    middle = parts['middle']
                    
                    # Calculate all quality scores
                    phase1_score = calculate_phase1_score(parts)
                    phase2_score = calculate_phase2_score(middle)
                    phase3_score = calculate_phase3_score(prefix, middle)
                    composite_score = calculate_composite_score(phase1_score, phase2_score, phase3_score)
                    
                    # Add comprehensive quality information to task
                    data['quality_scores'] = {
                        'phase1_context_quality': phase1_score,
                        'phase2_middle_quality': phase2_score,
                        'phase3_length_quality': phase3_score,
                        'composite_quality': composite_score
                    }
                    
                    # Add detailed metrics
                    data['quality_metrics'] = {
                        'prefix_length': len(prefix),
                        'middle_length': len(middle),
                        'ratio': len(middle) / len(prefix) if len(prefix) > 0 else 0.0,
                        'has_complete_prefix': starts_with_complete_code_line(prefix),
                        'has_meaningful_completion': is_meaningful_code_completion(middle, prefix),
                        'has_logical_flow': has_logical_context_flow(prefix, middle, parts.get('suffix', ''))
                    }
                    
                    # Add quality tier classification
                    if composite_score >= 0.8:
                        quality_tier = 'high_quality'
                    elif composite_score >= 0.6:
                        quality_tier = 'medium_quality'
                    elif composite_score >= 0.4:
                        quality_tier = 'acceptable_quality'
                    else:
                        quality_tier = 'low_quality'
                    
                    data['quality_tier'] = quality_tier
                    
                    # Track statistics
                    stats['phase1_scores'].append(phase1_score)
                    stats['phase2_scores'].append(phase2_score)
                    stats['phase3_scores'].append(phase3_score)
                    stats['composite_scores'].append(composite_score)
                    stats['processed'] += 1
                    
                    # Write enhanced task
                    outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                    
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error processing line {line_num}: {e}")
                    continue
    
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Calculate and display final statistics
    print("\n" + "=" * 60)
    print("COMPREHENSIVE QUALITY ANALYSIS COMPLETE")
    print("=" * 60)
    
    processed = stats['processed']
    print(f"Total tasks processed: {processed:,}")
    
    if processed > 0:
        # Score statistics
        import statistics
        
        def calc_stats(scores, name):
            mean = statistics.mean(scores)
            median = statistics.median(scores)
            stdev = statistics.stdev(scores) if len(scores) > 1 else 0
            return mean, median, stdev
        
        print(f"\n📊 QUALITY SCORE STATISTICS:")
        print("-" * 40)
        
        for score_type, scores in [
            ('Phase 1 (Context)', stats['phase1_scores']),
            ('Phase 2 (Content)', stats['phase2_scores']),
            ('Phase 3 (Length)', stats['phase3_scores']),
            ('Composite', stats['composite_scores'])
        ]:
            mean, median, stdev = calc_stats(scores, score_type)
            print(f"{score_type:<18} Mean: {mean:.3f} ± {stdev:.3f}, Median: {median:.3f}")
        
        # Quality tier distribution
        print(f"\n🏆 QUALITY TIER DISTRIBUTION:")
        print("-" * 40)
        
        high_quality = sum(1 for s in stats['composite_scores'] if s >= 0.8)
        medium_quality = sum(1 for s in stats['composite_scores'] if 0.6 <= s < 0.8)
        acceptable_quality = sum(1 for s in stats['composite_scores'] if 0.4 <= s < 0.6)
        low_quality = sum(1 for s in stats['composite_scores'] if s < 0.4)
        
        print(f"High Quality (≥0.8):     {high_quality:,} ({high_quality/processed*100:.1f}%)")
        print(f"Medium Quality (0.6-0.8): {medium_quality:,} ({medium_quality/processed*100:.1f}%)")
        print(f"Acceptable (0.4-0.6):     {acceptable_quality:,} ({acceptable_quality/processed*100:.1f}%)")
        print(f"Low Quality (<0.4):       {low_quality:,} ({low_quality/processed*100:.1f}%)")
    
    print(f"\nEnhanced dataset saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    process_dataset_with_comprehensive_scores()
