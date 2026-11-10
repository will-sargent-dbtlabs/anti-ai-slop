#!/usr/bin/env python3
"""Strictly validate one Ringer review verdict and its quoted rewrite evidence."""
import argparse
import hashlib
import json
import pathlib
import stat
import sys

TOP = {"verdict", "blocking", "fix", "note", "unverifiable"}
SECTIONS = ("blocking", "fix", "note")
FINDING = {"line", "issue", "quote", "fix"}


def reject_constant(_):
    raise ValueError("non-finite JSON number")


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def validate(verdict_path, rewrite_path, rewrite_text=None, expected_sha256=None):
    for path in (verdict_path, rewrite_path):
        p = pathlib.Path(path)
        if p.is_symlink() or not stat.S_ISREG(p.lstat().st_mode):
            raise ValueError("input must be a regular non-symlink file")
    if rewrite_text is None:
        with open(rewrite_path, encoding="utf-8") as fh:
            rewrite_text = fh.read()
    if expected_sha256 and hashlib.sha256(rewrite_text.encode("utf-8")).hexdigest() != expected_sha256:
        raise ValueError("rewrite snapshot changed")
    lines = rewrite_text.splitlines()
    with open(verdict_path, encoding="utf-8") as fh:
        data = json.load(fh, parse_constant=reject_constant, object_pairs_hook=reject_duplicate_keys)
    if not isinstance(data, dict) or set(data) != TOP:
        raise ValueError("verdict must contain exactly the required fields")
    if data["verdict"] not in ("PASS", "FAIL") or not isinstance(data["verdict"], str):
        raise ValueError("verdict must be PASS or FAIL")
    for section in SECTIONS:
        items = data[section]
        if not isinstance(items, list):
            raise ValueError("{} must be an array".format(section))
        for item in items:
            if not isinstance(item, dict) or set(item) != FINDING:
                raise ValueError("finding has invalid fields")
            line = item["line"]
            if isinstance(line, bool) or not isinstance(line, int) or not 1 <= line <= len(lines):
                raise ValueError("finding line is outside rewrite")
            for key in ("issue", "quote", "fix"):
                if not isinstance(item[key], str) or not item[key].strip():
                    raise ValueError("finding {} must be a non-empty string".format(key))
            if item["quote"] not in lines[line - 1]:
                raise ValueError("finding quote does not occur on its stated line")
    if not isinstance(data["unverifiable"], list) or not all(
            isinstance(v, str) and v.strip() for v in data["unverifiable"]):
        raise ValueError("unverifiable must be an array of non-empty strings")
    if data["verdict"] == "PASS" and (data["blocking"] or data["fix"] or data["unverifiable"]):
        raise ValueError("PASS cannot contain blocking, fix, or unverifiable findings")
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rewrite", required=True)
    ap.add_argument("--rewrite-sha256")
    ap.add_argument("--verdict", required=True)
    args = ap.parse_args()
    try:
        validate(args.verdict, args.rewrite, expected_sha256=args.rewrite_sha256)
    except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as exc:
        print("Invalid review verdict: {}".format(str(exc)[:160]), file=sys.stderr)
        return 1
    print("valid review verdict")
    return 0


if __name__ == "__main__":
    sys.exit(main())
