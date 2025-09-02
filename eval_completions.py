# filepath: eval_completions.py
import pandas as pd
from typing import List, Dict
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import numpy as np
import os
import json
import re

def edit_distance(s1: str, s2: str) -> int:
    # Simple Levenshtein distance implementation
    if len(s1) < len(s2):
        return edit_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def normalized_edit_distance(s1: str, s2: str) -> float:
    """
    Returns the normalized Levenshtein distance between two strings.
    Normalized by the length of the ground truth (s1), or 1 if both are empty.
    """
    if not s1 and not s2:
        return 0.0
    dist = edit_distance(s1, s2)
    norm = max(len(s1), 1)
    return dist / norm

def subsume_match(gt: str, pred: str) -> int:
    """
    Returns 1 if either string subsumes the other (is a substring), else 0.
    """
    gt = gt.strip()
    pred = pred.strip()
    return int(gt in pred or pred in gt)

def extract_fim_middle(text: str) -> str:
    """
    If text contains <fim-prefix>**<fim-suffix>**<fim-middle>, return content after <fim-middle>.
    Otherwise, return text as is.
    """
    if not isinstance(text, str):
        return text
    match = re.search(r'<fim-middle>(.*)', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text

def truncate_to_1_line(text: str) -> str:
    """Extracts the first non-empty line from the text."""
    if not isinstance(text, str):
        return ''
    lines = [line for line in text.splitlines() if line.strip()]
    return lines[0] if lines else ''

def truncate_to_n_lines(text: str, n: int) -> str:
    """Extracts the first n non-empty lines from the text."""
    if not isinstance(text, str):
        return ''
    lines = [line for line in text.splitlines() if line.strip()]
    return '\n'.join(lines[:n])

def evaluate_completions(df: pd.DataFrame, output_col: str = 'output_after_fim_middle', completion_col: str = 'prediction_after_fim_middle', n: int = 1) -> Dict[str, float]:
    # All metrics should use the filtered df only
    if completion_col not in df.columns or output_col not in df.columns:
        return None
    gt = df[output_col].astype(str).str.strip().apply(lambda x: truncate_to_n_lines(x, n))
    pred = df[completion_col].astype(str).str.strip().apply(lambda x: truncate_to_n_lines(x, n))
    # Metrics (all uncommented)
    exact_matches = (gt == pred)
    accuracy = exact_matches.mean()
    edit_distances = [edit_distance(g, p) for g, p in zip(gt, pred)]
    mean_edit_distance = float(np.mean(edit_distances))
    norm_edit_distances = [normalized_edit_distance(g, p) for g, p in zip(gt, pred)]
    mean_normalized_edit_distance = float(np.mean(norm_edit_distances))
    smoothie = SmoothingFunction().method4
    bleu_scores = [sentence_bleu([g.split()], p.split(), smoothing_function=smoothie) for g, p in zip(gt, pred)]
    mean_bleu = float(np.mean(bleu_scores))
    subsume_matches = [subsume_match(g, p) for g, p in zip(gt, pred)]
    mean_subsume_match = float(np.mean(subsume_matches))
    return {
        'count': len(df),
        'evaluated_rows': len(df),
        'accuracy': float(accuracy),
        'mean_edit_distance': mean_edit_distance,
        'mean_normalized_edit_distance': mean_normalized_edit_distance,
        'mean_bleu': mean_bleu,
        'mean_subsume_match': mean_subsume_match
    }

def find_column_case_insensitive(columns, *candidates):
    """
    Returns the first matching column name (case-insensitive) from candidates, or None if not found.
    """
    lower_columns = {col.lower(): col for col in columns}
    for cand in candidates:
        if cand.lower() in lower_columns:
            return lower_columns[cand.lower()]
    return None

def evaluate_completions_data(data, output_col: str = 'output_after_fim_middle', completion_col: str = 'prediction_after_fim_middle', n: int = 1) -> Dict[str, float]:
    """
    Accepts either a pandas DataFrame or a list of dicts (from JSON).
    Returns only the count of non-empty completions as evaluated_rows.
    Handles completion column name variations (completion, completions, case-insensitive).
    """
    if isinstance(data, pd.DataFrame):
        df = data
    elif isinstance(data, list):
        if not data:
            return None
        df = pd.DataFrame(data)
    else:
        return None
    output_col_name = find_column_case_insensitive(df.columns, output_col)
    prediction_col_name = find_column_case_insensitive(df.columns, completion_col)
    if not prediction_col_name or not output_col_name:
        return None
    mask = (df[prediction_col_name].astype(str).str.strip().str.len() > 0)
    filtered_df = df[mask].copy()
    if filtered_df.empty:
        return None
    return evaluate_completions(filtered_df, output_col, completion_col, n)

def extract_evaluation_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame filtered to rows where either 'completion' or 'completions' column exists and is non-empty.
    Uses a lambda with apply for filtering. Adds debug prints for shape before and after filtering.
    """
    print(f"[DEBUG] DataFrame shape before filtering: {df.shape}")
    completion_col = find_column_case_insensitive(df.columns, 'prediction_after_fim_middle')
    completions_col = find_column_case_insensitive(df.columns, 'predictions_after_fim_middle')
    if not completion_col and not completions_col:
        print("[DEBUG] No 'completion' or 'completions' column found.")
        return df.iloc[0:0]  # Return empty DataFrame if neither column exists
    def is_non_empty(row):
        val1 = str(row[completion_col]).strip() if completion_col and pd.notna(row[completion_col]) else ''
        val2 = str(row[completions_col]).strip() if completions_col and pd.notna(row[completions_col]) else ''
        return len(val1) > 0 or len(val2) > 0
    filtered_df = df[df.apply(is_non_empty, axis=1)].copy()
    print(f"[DEBUG] DataFrame shape after filtering: {filtered_df.shape}")
    return filtered_df

def try_load_json_or_jsonl(file_path):
    """
    Tries to load a file as JSON. If it fails with JSONDecodeError, tries as JSONL.
    Returns a list of dicts (records).
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            if isinstance(data, dict):
                return [data]
            return data
        except json.JSONDecodeError:
            # Try as JSONL
            f.seek(0)
            return [json.loads(line) for line in f if line.strip()]

def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python eval_completions.py <file> [N]")
        sys.exit(1)
    file_path = sys.argv[1]
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    output_col = 'output_after_fim_middle'
    completion_col = 'prediction_after_fim_middle'
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        df = pd.read_csv(file_path)
        df = extract_evaluation_results(df)
        results = evaluate_completions_data(df, output_col, completion_col, N)
    elif ext == '.json' or ext == '.jsonl':
        data = try_load_json_or_jsonl(file_path)
        df = pd.DataFrame(data)
        df = extract_evaluation_results(df)
        results = evaluate_completions_data(df, output_col, completion_col, N)
    else:
        print(f"Unsupported file type: {ext}")
        sys.exit(1)
    if results is None:
        print(f"Required columns not found in {file_path}, skipping evaluation.")
    else:
        print(f"Results for first {N} line(s): {results}")

if __name__ == "__main__":
    main()
