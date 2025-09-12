#!/usr/bin/env python3
"""
FIM Dataset Quality Pipeline Summary

This script provides a comprehensive summary of the quality-enhanced FIM dataset
and demonstrates how to use the quality scores for different applications.
"""

import json
import re
from collections import defaultdict, Counter

def analyze_final_dataset():
    """Analyze the final dataset with comprehensive quality scores"""
    
    print("🎯 FIM DATASET QUALITY ANALYSIS")
    print("=" * 60)
    
    filename = "prompts_codebricks_final_with_quality_scores.jsonl"
    
    stats = {
        'total': 0,
        'quality_tiers': defaultdict(int),
        'score_distributions': {
            'phase1': [],
            'phase2': [], 
            'phase3': [],
            'composite': []
        },
        'length_stats': {
            'prefix_lengths': [],
            'middle_lengths': [],
            'ratios': []
        },
        'quality_features': {
            'complete_prefix': 0,
            'meaningful_completion': 0,
            'logical_flow': 0
        }
    }
    
    print(f"📊 Analyzing: {filename}")
    print(f"Processing dataset...")
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                if line_num > 200000:  # Sample first 200K for quick analysis
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                stats['total'] += 1
                
                try:
                    data = json.loads(line)
                    
                    # Quality tier distribution
                    tier = data.get('quality_tier', 'unknown')
                    stats['quality_tiers'][tier] += 1
                    
                    # Score distributions
                    scores = data.get('quality_scores', {})
                    for phase, phase_key in [
                        ('phase1', 'phase1_context_quality'),
                        ('phase2', 'phase2_middle_quality'), 
                        ('phase3', 'phase3_length_quality'),
                        ('composite', 'composite_quality')
                    ]:
                        if phase_key in scores:
                            stats['score_distributions'][phase].append(scores[phase_key])
                    
                    # Length statistics
                    metrics = data.get('quality_metrics', {})
                    if 'prefix_length' in metrics:
                        stats['length_stats']['prefix_lengths'].append(metrics['prefix_length'])
                    if 'middle_length' in metrics:
                        stats['length_stats']['middle_lengths'].append(metrics['middle_length'])
                    if 'ratio' in metrics:
                        stats['length_stats']['ratios'].append(metrics['ratio'])
                    
                    # Quality features
                    if metrics.get('has_complete_prefix', False):
                        stats['quality_features']['complete_prefix'] += 1
                    if metrics.get('has_meaningful_completion', False):
                        stats['quality_features']['meaningful_completion'] += 1
                    if metrics.get('has_logical_flow', False):
                        stats['quality_features']['logical_flow'] += 1
                
                except json.JSONDecodeError:
                    continue
                
                if line_num % 50000 == 0:
                    print(f"  Processed {line_num:,} tasks...")
    
    except FileNotFoundError:
        print(f"❌ File {filename} not found!")
        return
    
    # Display comprehensive analysis
    total = stats['total']
    print(f"\n📈 DATASET OVERVIEW")
    print("-" * 40)
    print(f"Sample size analyzed: {total:,} tasks")
    
    print(f"\n🏆 QUALITY TIER DISTRIBUTION:")
    print("-" * 40)
    tier_order = ['high_quality', 'medium_quality', 'acceptable_quality', 'low_quality']
    for tier in tier_order:
        count = stats['quality_tiers'].get(tier, 0)
        pct = count / total * 100 if total > 0 else 0
        print(f"{tier.replace('_', ' ').title():<18} {count:,} ({pct:.1f}%)")
    
    print(f"\n📊 QUALITY SCORE STATISTICS:")
    print("-" * 40)
    
    import statistics
    for phase, scores in stats['score_distributions'].items():
        if scores:
            mean = statistics.mean(scores)
            median = statistics.median(scores)
            stdev = statistics.stdev(scores) if len(scores) > 1 else 0
            print(f"{phase.capitalize():<12} Mean: {mean:.3f} ± {stdev:.3f}, Median: {median:.3f}")
    
    print(f"\n📏 LENGTH CHARACTERISTICS:")
    print("-" * 40)
    
    for metric, values in stats['length_stats'].items():
        if values:
            mean = statistics.mean(values)
            median = statistics.median(values)
            min_val = min(values)
            max_val = max(values)
            
            metric_name = metric.replace('_', ' ').title()
            print(f"{metric_name:<15} Mean: {mean:.1f}, Median: {median:.1f}, Range: {min_val}-{max_val}")
    
    print(f"\n✨ QUALITY FEATURES:")
    print("-" * 40)
    
    features = [
        ('Complete Prefix', stats['quality_features']['complete_prefix']),
        ('Meaningful Completion', stats['quality_features']['meaningful_completion']),
        ('Logical Flow', stats['quality_features']['logical_flow'])
    ]
    
    for feature_name, count in features:
        pct = count / total * 100 if total > 0 else 0
        print(f"{feature_name:<20} {count:,} ({pct:.1f}%)")

def demonstrate_quality_filtering():
    """Demonstrate how to filter dataset by quality scores"""
    
    print(f"\n🔍 QUALITY-BASED FILTERING EXAMPLES")
    print("=" * 60)
    
    filename = "prompts_codebricks_final_with_quality_scores.jsonl" 
    
    # Example 1: High-quality tasks only
    print(f"\n1️⃣ HIGH-QUALITY TASKS (Composite Score ≥ 0.9):")
    print("-" * 50)
    
    high_quality_count = 0
    sample_count = 0
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if sample_count >= 50000:  # Limit sample
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                sample_count += 1
                
                try:
                    data = json.loads(line)
                    scores = data.get('quality_scores', {})
                    composite = scores.get('composite_quality', 0)
                    
                    if composite >= 0.9:
                        high_quality_count += 1
                        
                        # Show first few examples
                        if high_quality_count <= 3:
                            content = data.get('content', '')
                            
                            # Extract middle for display
                            middle_match = re.search(r'<fim_middle>(.*?)$', content, re.DOTALL)
                            middle = middle_match.group(1)[:100] if middle_match else ""
                            
                            metrics = data.get('quality_metrics', {})
                            
                            print(f"   Example {high_quality_count}:")
                            print(f"     Composite Score: {composite:.3f}")
                            print(f"     Middle: {middle}{'...' if len(middle) >= 100 else ''}")
                            print(f"     Prefix Length: {metrics.get('prefix_length', 0)}")
                            print(f"     Middle Length: {metrics.get('middle_length', 0)}")
                            print()
                
                except json.JSONDecodeError:
                    continue
        
        pct = high_quality_count / sample_count * 100 if sample_count > 0 else 0
        print(f"   High-quality tasks: {high_quality_count:,} / {sample_count:,} ({pct:.1f}%)")
    
    except FileNotFoundError:
        print("   ❌ Dataset file not found")
    
    # Example 2: Balanced dataset creation
    print(f"\n2️⃣ BALANCED QUALITY DATASET:")
    print("-" * 50)
    print("   Code example for creating balanced training sets:")
    print("""
   # Filter by composite quality score
   def create_balanced_dataset(input_file, output_file, target_size=100000):
       quality_buckets = {'high': [], 'medium': [], 'low': []}
       
       with open(input_file, 'r') as f:
           for line in f:
               data = json.loads(line)
               composite = data['quality_scores']['composite_quality']
               
               if composite >= 0.8:
                   quality_buckets['high'].append(data)
               elif composite >= 0.6:
                   quality_buckets['medium'].append(data)
               else:
                   quality_buckets['low'].append(data)
       
       # Create balanced mix: 70% high, 25% medium, 5% low
       balanced_dataset = (
           quality_buckets['high'][:int(target_size * 0.7)] +
           quality_buckets['medium'][:int(target_size * 0.25)] +
           quality_buckets['low'][:int(target_size * 0.05)]
       )
       
       return balanced_dataset
    """)

def show_pipeline_summary():
    """Show complete pipeline summary with quality metrics"""
    
    print(f"\n📋 COMPLETE FIM QUALITY PIPELINE SUMMARY")
    print("=" * 60)
    
    pipeline_stages = [
        {
            'stage': 'Phase 1: Context Quality Filtering',
            'input': '5.48M raw FIM tasks',
            'output': '1.61M tasks (29.3%)',
            'criteria': 'Complete prefix lines, meaningful completions',
            'quality_score': 'Phase 1 Context Quality (0.0-1.0)'
        },
        {
            'stage': 'Phase 2: Middle Content Filtering', 
            'input': '1.61M tasks',
            'output': '1.43M tasks (89.0%)',
            'criteria': 'Remove incomplete patterns, standalone specifiers',
            'quality_score': 'Phase 2 Middle Quality (0.0-1.0)'
        },
        {
            'stage': 'Phase 3B: Adaptive Length Filtering',
            'input': '1.43M tasks', 
            'output': '1.26M tasks (88.1%)',
            'criteria': 'Adaptive length ratios, semantic quality',
            'quality_score': 'Phase 3 Length Quality (0.0-1.0)'
        },
        {
            'stage': 'Quality Score Enhancement',
            'input': '1.26M tasks',
            'output': '1.26M tasks (100%)',
            'criteria': 'Add comprehensive quality metrics',
            'quality_score': 'Composite Quality Score (0.0-1.0)'
        }
    ]
    
    for i, stage in enumerate(pipeline_stages, 1):
        print(f"\n{i}. {stage['stage']}")
        print(f"   Input:  {stage['input']}")  
        print(f"   Output: {stage['output']}")
        print(f"   Criteria: {stage['criteria']}")
        print(f"   Score: {stage['quality_score']}")
    
    print(f"\n📊 FINAL DATASET CHARACTERISTICS:")
    print("-" * 40)
    print(f"   📁 File: prompts_codebricks_final_with_quality_scores.jsonl")
    print(f"   📈 Size: ~1.26M high-quality FIM tasks")
    print(f"   🎯 Quality: 91% high-quality (≥0.8 composite score)")
    print(f"   📋 Metrics: Complete quality scoring for all tasks")
    
    print(f"\n🔧 AVAILABLE QUALITY FIELDS:")
    print("-" * 40)
    
    quality_fields = [
        ('quality_scores.phase1_context_quality', 'Context & prefix quality (0.0-1.0)'),
        ('quality_scores.phase2_middle_quality', 'Middle content quality (0.0-1.0)'),
        ('quality_scores.phase3_length_quality', 'Length-based quality (0.0-1.0)'),
        ('quality_scores.composite_quality', 'Overall quality score (0.0-1.0)'),
        ('quality_tier', 'Quality category (high/medium/acceptable/low)'),
        ('quality_metrics.prefix_length', 'Character count of prefix'),
        ('quality_metrics.middle_length', 'Character count of middle'),
        ('quality_metrics.ratio', 'Middle/prefix length ratio'),
        ('quality_metrics.has_complete_prefix', 'Boolean: complete code start'),
        ('quality_metrics.has_meaningful_completion', 'Boolean: meaningful completion'),
        ('quality_metrics.has_logical_flow', 'Boolean: logical context flow')
    ]
    
    for field, description in quality_fields:
        print(f"   {field:<35} {description}")

if __name__ == "__main__":
    # Run complete analysis
    analyze_final_dataset()
    demonstrate_quality_filtering()
    show_pipeline_summary()
    
    print(f"\n✅ Quality-enhanced FIM dataset analysis complete!")
    print(f"💡 Use quality scores to create custom filtered datasets for specific use cases.")
