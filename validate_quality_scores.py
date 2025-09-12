#!/usr/bin/env python3
"""
Quality Score Validation Script

This script validates that quality scores have been correctly added to the FIM dataset
and provides analysis of the scoring distribution and sample tasks.
"""

import json
import re
from datetime import datetime
from collections import defaultdict

def validate_quality_scores(filename):
    """Validate quality scores in the dataset"""
    
    print(f"🔍 QUALITY SCORE VALIDATION")
    print("=" * 50)
    print(f"File: {filename}")
    print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
    print()
    
    stats = {
        'total_tasks': 0,
        'tasks_with_scores': 0,
        'score_ranges': defaultdict(int),
        'quality_tiers': defaultdict(int),
        'phase_scores': {
            'phase1': [],
            'phase2': [],
            'phase3': [],
            'composite': []
        },
        'sample_tasks': []
    }
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > 100000:  # Limit for quick validation
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                stats['total_tasks'] += 1
                
                try:
                    data = json.loads(line)
                    
                    # Check for quality scores
                    has_scores = 'quality_scores' in data
                    if has_scores:
                        stats['tasks_with_scores'] += 1
                        
                        scores = data['quality_scores']
                        
                        # Collect phase scores
                        if 'phase1_context_quality' in scores:
                            stats['phase_scores']['phase1'].append(scores['phase1_context_quality'])
                        if 'phase2_middle_quality' in scores:
                            stats['phase_scores']['phase2'].append(scores['phase2_middle_quality'])
                        if 'phase3_length_quality' in scores:
                            stats['phase_scores']['phase3'].append(scores['phase3_length_quality'])
                        if 'composite_quality' in scores:
                            composite = scores['composite_quality']
                            stats['phase_scores']['composite'].append(composite)
                            
                            # Categorize composite scores
                            if composite >= 0.8:
                                stats['score_ranges']['high'] += 1
                            elif composite >= 0.6:
                                stats['score_ranges']['medium'] += 1
                            elif composite >= 0.4:
                                stats['score_ranges']['acceptable'] += 1
                            else:
                                stats['score_ranges']['low'] += 1
                    
                    # Check for quality tier
                    if 'quality_tier' in data:
                        stats['quality_tiers'][data['quality_tier']] += 1
                    
                    # Collect sample tasks
                    if len(stats['sample_tasks']) < 10 and has_scores:
                        # Extract FIM parts for display
                        content = data.get('content', '')
                        prefix_match = re.search(r'<fim_prefix>(.*?)<fim_suffix>', content, re.DOTALL)
                        middle_match = re.search(r'<fim_middle>(.*?)$', content, re.DOTALL)
                        
                        sample = {
                            'line_num': line_num,
                            'prefix': prefix_match.group(1)[-100:] if prefix_match else "",
                            'middle': middle_match.group(1) if middle_match else "",
                            'scores': data.get('quality_scores', {}),
                            'metrics': data.get('quality_metrics', {}),
                            'tier': data.get('quality_tier', 'unknown')
                        }
                        stats['sample_tasks'].append(sample)
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    print(f"Error at line {line_num}: {e}")
                    continue
                
                # Progress update
                if line_num % 25000 == 0:
                    print(f"Validated {line_num:,} lines...")
    
    except FileNotFoundError:
        print(f"❌ File {filename} not found!")
        return
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return
    
    # Display validation results
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    
    total = stats['total_tasks']
    with_scores = stats['tasks_with_scores']
    
    print(f"Total tasks examined:     {total:,}")
    print(f"Tasks with quality scores: {with_scores:,} ({with_scores/total*100:.1f}%)")
    
    if with_scores > 0:
        print(f"\n📊 SCORE DISTRIBUTION:")
        print("-" * 30)
        
        for phase, scores in stats['phase_scores'].items():
            if scores:
                mean_score = sum(scores) / len(scores)
                min_score = min(scores)
                max_score = max(scores)
                print(f"{phase.capitalize():<12} Mean: {mean_score:.3f}, Range: {min_score:.3f}-{max_score:.3f}")
        
        print(f"\n🏆 QUALITY TIER DISTRIBUTION:")
        print("-" * 30)
        
        tier_order = ['high_quality', 'medium_quality', 'acceptable_quality', 'low_quality']
        for tier in tier_order:
            count = stats['quality_tiers'].get(tier, 0)
            pct = count / with_scores * 100 if with_scores > 0 else 0
            print(f"{tier.replace('_', ' ').title():<18} {count:,} ({pct:.1f}%)")
        
        print(f"\n📝 SAMPLE TASKS WITH SCORES:")
        print("-" * 50)
        
        for i, sample in enumerate(stats['sample_tasks'][:5], 1):
            print(f"\nSample {i} (Line {sample['line_num']}):")
            print(f"Tier: {sample['tier']}")
            print(f"Prefix (last 80 chars): ...{sample['prefix'][-80:]}")
            print(f"Middle: {sample['middle'][:100]}{'...' if len(sample['middle']) > 100 else ''}")
            
            scores = sample['scores']
            print(f"Scores: P1={scores.get('phase1_context_quality', 0):.3f}, "
                  f"P2={scores.get('phase2_middle_quality', 0):.3f}, "
                  f"P3={scores.get('phase3_length_quality', 0):.3f}, "
                  f"Composite={scores.get('composite_quality', 0):.3f}")
            
            metrics = sample['metrics']
            if metrics:
                print(f"Metrics: Prefix={metrics.get('prefix_length', 0)}, "
                      f"Middle={metrics.get('middle_length', 0)}, "
                      f"Ratio={metrics.get('ratio', 0):.3f}")
            print("-" * 40)
    
    print(f"\n✅ Validation complete at {datetime.now().strftime('%H:%M:%S')}")

def compare_quality_distributions():
    """Compare quality score distributions across different filtered versions"""
    
    files_to_compare = [
        "prompts_codebricks_filtered_improved.jsonl",
        "prompts_codebricks_filtered_middle_quality.jsonl", 
        "prompts_codebricks_filtered_phase3b_improved.jsonl",
        "prompts_codebricks_final_with_quality_scores.jsonl"
    ]
    
    print(f"\n🔄 QUALITY DISTRIBUTION COMPARISON")
    print("=" * 60)
    
    for filename in files_to_compare:
        print(f"\n📁 {filename}")
        try:
            # Quick sample to check what quality info is available
            with open(filename, 'r', encoding='utf-8') as f:
                sample_line = f.readline()
                if sample_line.strip():
                    data = json.loads(sample_line)
                    
                    quality_fields = []
                    for key in data.keys():
                        if 'quality' in key.lower():
                            quality_fields.append(key)
                    
                    if quality_fields:
                        print(f"   Quality fields: {', '.join(quality_fields)}")
                    else:
                        print(f"   No quality fields found")
        
        except FileNotFoundError:
            print(f"   ⚠️  File not found")
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    # First, validate the final file with comprehensive scores
    validate_quality_scores("prompts_codebricks_final_with_quality_scores.jsonl")
    
    # Then compare distributions across different versions
    compare_quality_distributions()
