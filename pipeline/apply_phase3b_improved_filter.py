#!/usr/bin/env python3
"""
Phase 3B: Improved Length-Based Quality Filter

Based on the validation analysis showing that Phase 3A was too restrictive:
- Prefix alignment: 23.7 → 0.0 (major decrease) 
- Overall alignment: 31.7 → 11.8 (substantial decrease)

New approach: Adaptive filtering that respects the characteristics of auto-extracted data
while still improving quality through semantic and contextual filtering.
"""

import json
import re
from datetime import datetime

def extract_fim_components(content):
    """Extract fim_prefix and fim_middle content from FIM task"""
    try:
        # Extract fim_prefix
        prefix_match = re.search(r'<fim_prefix>(.*?)<fim_suffix>', content, re.DOTALL)
        prefix = prefix_match.group(1).strip() if prefix_match else ""
        
        # Extract fim_middle  
        middle_match = re.search(r'<fim_middle>(.*?)(?:<|$)', content, re.DOTALL)
        middle = middle_match.group(1).strip() if middle_match else ""
        
        return prefix, middle
    except:
        return "", ""

def calculate_length_quality_score(prefix, middle):
    """Calculate length-based quality score (0.0-1.0, higher is better)"""
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
    optimal_ratio = None
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

def should_reject_improved(prefix, middle):
    """Improved rejection criteria based on analysis of Phase 3A issues"""
    
    if not prefix or not middle:
        return True, "missing_components"
    
    prefix_len = len(prefix)
    middle_len = len(middle)
    ratio = middle_len / prefix_len if prefix_len > 0 else float('inf')
    
    # RELAXED CRITERIA based on validation analysis:
    
    # 1. More permissive prefix length (was 100, now 50)
    # Analysis showed 100 was too restrictive for auto-extracted data
    if prefix_len < 50:
        return True, "prefix_too_short"
    
    # 2. Keep reasonable upper bound for prefix
    if prefix_len > 5000:
        return True, "prefix_too_long"
    
    # 3. More permissive middle length (was 10, now 8)
    if middle_len < 8:
        return True, "middle_too_short"
        
    # 4. Keep reasonable upper bound for middle  
    if middle_len > 400:
        return True, "middle_too_long"
    
    # 5. ADAPTIVE RATIO LIMITS based on prefix length
    # Key insight: Shorter prefixes naturally have higher ratios
    
    if prefix_len <= 150:
        # Short prefixes: allow higher ratios
        max_ratio = 1.2
    elif prefix_len <= 300:
        # Medium prefixes: moderate ratios
        max_ratio = 0.8  
    elif prefix_len <= 500:
        # Longer prefixes: stricter ratios
        max_ratio = 0.6
    else:
        # Very long prefixes: strict ratios
        max_ratio = 0.4
    
    if ratio > max_ratio:
        return True, f"ratio_too_large_{int(max_ratio*100)}"
    
    # 6. Minimum ratio check (avoid tiny completions)
    if ratio < 0.01:
        return True, "ratio_too_small"
    
    # 7. SEMANTIC QUALITY CHECKS
    # Avoid incomplete tokens/words
    if middle.strip() and middle.strip()[-1].isalnum() and ' ' not in middle.strip():
        # Single incomplete word
        if len(middle.strip()) < 15:  # Allow longer single tokens
            return True, "incomplete_word"
    
    # 8. CONTEXTUAL QUALITY
    # Very short prefix with very long middle (suspicious)
    if prefix_len < 80 and middle_len > 200:
        return True, "short_prefix_very_long_middle"
    
    # 9. WHITESPACE QUALITY
    # Avoid completions that are mostly whitespace
    middle_stripped = middle.strip()
    if len(middle_stripped) < len(middle) * 0.3:  # More than 70% whitespace
        return True, "mostly_whitespace"
    
    return False, "acceptable"

def filter_phase3b():
    """Apply improved Phase 3B filtering"""
    
    input_file = "prompts_codebricks_filtered_middle_quality.jsonl"
    output_file = "prompts_codebricks_filtered_phase3b_improved.jsonl"
    
    print("🚀 PHASE 3B: IMPROVED LENGTH-BASED QUALITY FILTER")
    print("=" * 60)
    print(f"Input:  {input_file}")
    print(f"Output: {output_file}")
    print(f"Start:  {datetime.now().strftime('%H:%M:%S')}")
    
    print(f"\n🔧 IMPROVED FILTERING CRITERIA:")
    print(f"  PREFIX:   50 ≤ length ≤ 5000 characters (relaxed from 100)")
    print(f"  MIDDLE:   8 ≤ length ≤ 400 characters (relaxed from 10)")
    print(f"  ADAPTIVE RATIOS:")
    print(f"    Short prefix (≤150):   ratio ≤ 1.2")
    print(f"    Medium prefix (150-300): ratio ≤ 0.8") 
    print(f"    Long prefix (300-500):   ratio ≤ 0.6")
    print(f"    Very long prefix (500+): ratio ≤ 0.4")
    print(f"  SEMANTIC: Avoid incomplete words, mostly whitespace")
    print()
    
    stats = {
        'total': 0,
        'kept': 0,
        'rejected': 0,
        'reasons': {}
    }
    
    prefix_lengths = []
    middle_lengths = []
    ratios = []
    
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
                    
                    # Extract components
                    prefix, middle = extract_fim_components(content)
                    should_reject, reason = should_reject_improved(prefix, middle)
                    
                    if should_reject:
                        stats['rejected'] += 1
                        stats['reasons'][reason] = stats['reasons'].get(reason, 0) + 1
                    else:
                        stats['kept'] += 1
                        
                        # Calculate and add Phase 3B quality information
                        length_quality_score = calculate_length_quality_score(prefix, middle)
                        data['quality_phase3b'] = 'passed_length_based_filter'
                        data['quality_length_reason'] = reason
                        data['quality_length_score'] = length_quality_score
                        data['quality_prefix_length'] = len(prefix)
                        data['quality_middle_length'] = len(middle)
                        data['quality_ratio'] = len(middle) / len(prefix) if len(prefix) > 0 else 0.0
                        
                        outfile.write(json.dumps(data, ensure_ascii=False) + '\n')
                        
                        # Track accepted statistics
                        prefix_lengths.append(len(prefix))
                        middle_lengths.append(len(middle))
                        if len(prefix) > 0:
                            ratios.append(len(middle) / len(prefix))
                        
                except json.JSONDecodeError:
                    stats['rejected'] += 1
                    stats['reasons']['json_error'] = stats['reasons'].get('json_error', 0) + 1
                    continue
    
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Final results
    print("\n" + "=" * 60) 
    print("PHASE 3B FILTERING RESULTS")
    print("=" * 60)
    
    total = stats['total']
    kept = stats['kept'] 
    rejected = stats['rejected']
    acceptance_rate = (kept / total * 100) if total > 0 else 0
    
    print(f"Total processed:     {total:,}")
    print(f"Tasks kept:          {kept:,} ({acceptance_rate:.1f}%)")
    print(f"Tasks rejected:      {rejected:,} ({rejected/total*100:.1f}%)")
    
    print(f"\nRejection reasons:")
    print("-" * 40)
    for reason, count in sorted(stats['reasons'].items(), key=lambda x: x[1], reverse=True):
        pct = (count / total * 100) if total > 0 else 0
        print(f"{reason:<30} {count:>8,} ({pct:>5.1f}%)")
    
    # Statistics of accepted data
    if prefix_lengths:
        import numpy as np
        
        print(f"\n📊 ACCEPTED DATA CHARACTERISTICS:")
        print("-" * 40)
        print(f"Prefix lengths:")
        print(f"  Mean: {np.mean(prefix_lengths):.1f} ± {np.std(prefix_lengths):.1f}")
        print(f"  Range: {min(prefix_lengths)}-{max(prefix_lengths)}")
        print(f"  Median: {np.median(prefix_lengths):.1f}")
        
        print(f"\nMiddle lengths:")
        print(f"  Mean: {np.mean(middle_lengths):.1f} ± {np.std(middle_lengths):.1f}")
        print(f"  Range: {min(middle_lengths)}-{max(middle_lengths)}")
        print(f"  Median: {np.median(middle_lengths):.1f}")
        
        if ratios:
            print(f"\nMiddle/Prefix ratios:")
            print(f"  Mean: {np.mean(ratios):.3f} ± {np.std(ratios):.3f}")
            print(f"  Range: {min(ratios):.3f}-{max(ratios):.3f}")
            print(f"  Median: {np.median(ratios):.3f}")
    
    # Dataset progression summary
    print(f"\n📈 DATASET PROGRESSION:")
    print("-" * 40)
    print(f"Phase 1:  5.48M → 1.61M (29.3% acceptance)")
    print(f"Phase 2:  1.61M → 1.43M (89.0% acceptance)")
    print(f"Phase 3A: 1.43M → 968K (67.6% acceptance) ⚠️ Over-filtered")
    print(f"Phase 3B: 1.43M → {kept/1000:.0f}K ({acceptance_rate:.1f}% acceptance) ✅ Improved")
    
    cumulative_rate = (kept / 5483908) * 100 if kept > 0 else 0
    print(f"Overall:  5.48M → {kept/1000:.0f}K ({cumulative_rate:.1f}% total acceptance)")
    
    # Comparison with Phase 3A
    phase3a_size = 967985
    improvement = kept - phase3a_size
    print(f"\n🔄 PHASE 3B vs PHASE 3A:")
    print(f"  Size change: {phase3a_size/1000:.0f}K → {kept/1000:.0f}K ({improvement:+,} tasks)")
    print(f"  Acceptance: 67.6% → {acceptance_rate:.1f}% ({acceptance_rate-67.6:+.1f}% points)")
    
    print(f"\nOutput saved to: {output_file}")
    print(f"End time: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    filter_phase3b()
