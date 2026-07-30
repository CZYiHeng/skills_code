# -*- coding: utf-8 -*-
import argparse
import sys
from pathlib import Path

import pandas as pd


def read_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path)
    if suffix in (".xls", ".xlsx"):
        return pd.read_excel(path)
    raise ValueError(f"unsupported file format: {suffix}")


def write_file(df: pd.DataFrame, path: Path) -> None:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        df.to_csv(path, index=False)
    elif suffix in (".xls", ".xlsx"):
        df.to_excel(path, index=False)
    elif suffix == ".json":
        df.to_json(path, orient="records", force_ascii=False, indent=2)
    else:
        raise ValueError(f"unsupported output format: {suffix}")


def clean(df: pd.DataFrame, drop_dup: bool, drop_na: bool) -> pd.DataFrame:
    result = df.copy()
    if drop_dup:
        before = len(result)
        result = result.drop_duplicates()
        print(f"[clean] removed {before - len(result)} duplicate rows")
    if drop_na:
        before = len(result)
        result = result.dropna()
        print(f"[clean] removed {before - len(result)} rows with missing values")
    return result


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    summary = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "non_null": df.notna().sum(),
        "null_count": df.isna().sum(),
        "unique": df.nunique(),
    })
    numeric = df.select_dtypes(include="number").describe().T
    if not numeric.empty:
        summary = summary.join(numeric[["mean", "std", "min", "max"]])
    return summary


def filter_rows(df: pd.DataFrame, column: str, op: str, value: str) -> pd.DataFrame:
    if column not in df.columns:
        raise ValueError(f"column not found: {column}")
    series = df[column]
    target = pd.to_numeric(series, errors="coerce") if op in (">", ">=", "<", "<=") else series
    if op == "==":
        return df[series.astype(str) == value]
    if op == "!=":
        return df[series.astype(str) != value]
    if op == "contains":
        return df[series.astype(str).str.contains(value, na=False)]
    target_value = float(value)
    if op == ">":
        return df[target > target_value]
    if op == ">=":
        return df[target >= target_value]
    if op == "<":
        return df[target < target_value]
    if op == "<=":
        return df[target <= target_value]
    raise ValueError(f"unsupported operator: {op}")


def main() -> int:
    parser = argparse.ArgumentParser(description="simple CSV/Excel data processor")
    parser.add_argument("input", type=Path, help="input file (.csv/.xlsx/.xls)")
    parser.add_argument("-o", "--output", type=Path, help="output file for cleaned data")
    parser.add_argument("-s", "--summary", type=Path, help="output file for summary stats")
    parser.add_argument("--drop-duplicates", action="store_true", help="remove duplicate rows")
    parser.add_argument("--drop-na", action="store_true", help="remove rows with missing values")
    parser.add_argument("--filter-column", help="column name to filter on")
    parser.add_argument("--filter-op", choices=["==", "!=", ">", ">=", "<", "<=", "contains"], help="filter operator")
    parser.add_argument("--filter-value", help="filter value")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        return 1

    try:
        df = read_file(args.input)
    except Exception as exc:
        print(f"error: failed to read file: {exc}", file=sys.stderr)
        return 1

    print(f"[load] {args.input} -> {len(df)} rows, {len(df.columns)} columns")

    if args.filter_column:
        df = filter_rows(df, args.filter_column, args.filter_op, args.filter_value)
        print(f"[filter] -> {len(df)} rows")

    df = clean(df, args.drop_duplicates, args.drop_na)

    if args.output:
        write_file(df, args.output)
        print(f"[save] cleaned data -> {args.output}")

    if args.summary:
        summary = summarize(df)
        write_file(summary, args.summary)
        print(f"[save] summary     -> {args.summary}")
        print()
        print(summary.to_string())

    return 0


if __name__ == "__main__":
    sys.exit(main())
