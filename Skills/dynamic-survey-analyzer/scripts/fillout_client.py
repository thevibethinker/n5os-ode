#!/usr/bin/env python3
"""Fillout API client for multi-account form access and quantitative analysis.

Supports listing forms, fetching form structure, retrieving submissions,
auto-detecting account for a formId, and generating statistical analysis.
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests


# API Configuration
BASE_URL = "https://api.fillout.com/v1/api/"
ACCOUNTS = {
    "personal": os.environ.get("FILLOUT_SECRET_PERSONAL"),
    "careerspan": os.environ.get("FILLOUT_SECRET_CAREERSPAN"),
}


def _get_headers(api_key: str) -> Dict[str, str]:
    """Build headers for Fillout API requests."""
    return {"Authorization": f"Bearer {api_key}"}


def list_forms(account: Optional[str] = None) -> Dict[str, Any]:
    """List all forms from specified account(s)."""
    if account and account not in ACCOUNTS:
        print(f"Error: Unknown account '{account}'. Available: {list(ACCOUNTS.keys())}")
        sys.exit(1)

    results = {}
    accounts_to_check = [account] if account else [k for k, v in ACCOUNTS.items() if v]

    for acct in accounts_to_check:
        api_key = ACCOUNTS[acct]
        if not api_key:
            print(f"Warning: No API key configured for account '{acct}'")
            continue

        try:
            resp = requests.get(f"{BASE_URL}forms", headers=_get_headers(api_key))
            resp.raise_for_status()
            data = resp.json()

            # Fillout API returns an array directly
            forms = data if isinstance(data, list) else data.get("forms", [])

            if forms:
                results[acct] = {
                    "account": acct,
                    "count": len(forms),
                    "forms": [
                        {
                            "id": f.get("formId"),
                            "title": f.get("name"),
                            "theme": f.get("theme", {}).get("color", "#000000"),
                            "status": "published" if f.get("isPublished") else "draft",
                        }
                        for f in forms
                    ]
                }
        except requests.RequestException as e:
            print(f"Error listing forms for {acct}: {e}")

    return results


def get_form_structure(form_id: str, account: Optional[str] = None) -> Dict[str, Any]:
    """Get form structure including question details."""
    # First, detect account if not provided
    detected_account = account
    if not detected_account:
        detected_account = _detect_account(form_id)

    if not detected_account:
        print(f"Error: Could not find form '{form_id}' in any account")
        sys.exit(1)

    api_key = ACCOUNTS[detected_account]
    if not api_key:
        print(f"Error: No API key configured for account '{detected_account}'")
        sys.exit(1)

    resp = requests.get(
        f"{BASE_URL}forms/{form_id}",
        headers=_get_headers(api_key)
    )
    resp.raise_for_status()
    return resp.json()


def get_submissions(
    form_id: str,
    account: Optional[str] = None,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Get all submissions for a form.

    Note: API limit parameter is capped at 100 due to Fillout API constraints.
    For more than 100 responses, implement pagination.
    """
    if account:
        if account not in ACCOUNTS or not ACCOUNTS[account]:
            print(f"Error: Unknown or unconfigured account '{account}'")
            sys.exit(1)
        api_key = ACCOUNTS[account]
    else:
        api_key = _detect_account(form_id)

    if not api_key:
        print(f"Error: Could not find form '{form_id}' in any account")
        sys.exit(1)

    params = {"limit": limit}
    if filters:
        params.update(filters)

    resp = requests.get(
        f"{BASE_URL}forms/{form_id}/submissions",
        headers=_get_headers(api_key),
        params=params,
    )
    resp.raise_for_status()
    return resp.json()


def _detect_account(form_id: str) -> Optional[str]:
    """Auto-detect which account contains given formId and return its name."""
    for acct, api_key in ACCOUNTS.items():
        if not api_key:
            continue
        try:
            resp = requests.get(
                f"{BASE_URL}forms/{form_id}",
                headers=_get_headers(api_key),
                timeout=10,
            )
            if resp.status_code == 200:
                return acct  # Return account name
        except requests.RequestException:
            continue
    return None


def detect_account(form_id: str) -> Dict[str, Any]:
    """Detect and return which account owns the given formId."""
    account = _detect_account(form_id)
    return {
        "form_id": form_id,
        "account": account if account else "not_found",
        "has_access": account is not None,
    }


def _parse_scale_value(value: Any, question_id: str) -> Optional[float]:
    """Parse scale/likert questions to numeric values.

    Handles emoji-based scales and text labels.
    """
    if value is None or value == "":
        return None

    # If already numeric, return it
    if isinstance(value, (int, float)):
        return float(value)

    value_str = str(value).strip()

    # Emoji to score mapping (common patterns)
    emoji_scores = {
        "😞": 1, "😐": 2, "🙂": 3, "😊": 4, "🤩": 5,
        "🙁": 1, "😕": 2, "😐": 3, "🙂": 4, "😄": 5,
        "❌": 1, "🔹": 2, "✅": 3,
        "1️⃣": 1, "2️⃣": 2, "3️⃣": 3, "4️⃣": 4, "5️⃣": 5,
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    }

    # Try direct emoji match
    for emoji, score in emoji_scores.items():
        if emoji in value_str:
            return float(score)

    # Try to extract numeric value
    try:
        return float(value_str)
    except ValueError:
        pass

    # Text to score mapping (lowercase)
    text_scores = {
        "strongly disagree": 1,
        "disagree": 2,
        "neutral": 3,
        "agree": 4,
        "strongly agree": 5,
        "very low": 1,
        "low": 2,
        "medium": 3,
        "high": 4,
        "very high": 5,
    }

    lower = value_str.lower()
    for text, score in text_scores.items():
        if text in lower:
            return float(score)

    return None


def _get_question_type(question: Dict[str, Any]) -> str:
    """Normalize question type to standard categories."""
    raw_type = question.get("type", "").lower()

    type_mapping = {
        "multiplechoice": "multiple_choice",
        "checkboxes": "multiple_choice",  # Treated as multi-select
        "shortanswer": "text",
        "longanswer": "text",
        "numberinput": "scale",
        "rating": "scale",
        "likertscale": "scale",
        "dateinput": "date",
        "fileupload": "file",
    }

    return type_mapping.get(raw_type, raw_type)


def _extract_responses(
    submissions: List[Dict[str, Any]],
    question_id: str,
    question_type: str,
) -> List[Any]:
    """Extract all responses for a question from submissions.

    Handles both direct 'questions' array and nested 'answers.questions' structure.
    """
    responses = []

    for sub in submissions:
        try:
            # Try direct questions array first (actual Fillout API structure)
            questions_list = sub.get("questions", [])
            if not questions_list:
                # Fallback to nested structure
                questions_list = sub.get("answers", {}).get("questions", [])

            for q in questions_list:
                if q.get("id") == question_id:
                    value = q.get("value")
                    # Handle multi-select (checkboxes)
                    if question_type == "multiple_choice" and isinstance(value, list):
                        # Expand to individual entries
                        responses.extend(value)
                    else:
                        responses.append(value)
                    break
        except (KeyError, TypeError):
            continue

    return responses


def _calculate_distribution(
    responses: List[Any],
    question_type: str,
) -> Dict[str, Any]:
    """Calculate frequency distribution for responses."""
    # Filter out None/empty values
    filtered = [r for r in responses if r is not None and r != ""]
    response_count = len(filtered)

    if not filtered:
        return {"response_count": 0, "distribution": {}, "percentage": {}}

    if question_type in ["scale", "number"]:
        # For numeric/scale questions, collect numeric values
        numeric_values = []
        for r in filtered:
            parsed = _parse_scale_value(r, "")
            if parsed is not None:
                numeric_values.append(parsed)

        if numeric_values:
            distribution = {}
            for val in sorted(set(numeric_values)):
                distribution[str(int(val))] = numeric_values.count(val)

            percentage = {k: round(v / len(numeric_values) * 100, 1) for k, v in distribution.items()}
            return {
                "response_count": len(numeric_values),
                "distribution": distribution,
                "percentage": percentage,
                "min": min(numeric_values),
                "max": max(numeric_values),
                "mean": round(sum(numeric_values) / len(numeric_values), 2),
                "median": sorted(numeric_values)[len(numeric_values) // 2],
            }
        else:
            return {"response_count": 0, "distribution": {}, "percentage": {}}

    # For categorical questions
    counter = Counter(filtered)
    distribution = {str(k): v for k, v in counter.items()}
    percentage = {k: round(v / response_count * 100, 1) for k, v in distribution.items()}

    return {
        "response_count": response_count,
        "distribution": distribution,
        "percentage": percentage,
    }


def _cross_tabulate(
    submissions: List[Dict[str, Any]],
    q1_id: str,
    q2_id: str,
) -> Dict[str, Any]:
    """Create cross-tabulation matrix between two questions."""
    matrix = {}
    paired_count = 0

    # Extract paired responses
    for sub in submissions:
        try:
            # Try direct questions array first (actual Fillout API structure)
            questions_list = sub.get("questions", [])
            if not questions_list:
                # Fallback to nested structure
                questions_list = sub.get("answers", {}).get("questions", [])

            val1, val2 = None, None

            for q in questions_list:
                if q.get("id") == q1_id:
                    val1 = q.get("value")
                    # Flatten lists for checkboxes
                    if isinstance(val1, list) and val1:
                        val1 = ", ".join(str(v) for v in val1)
                elif q.get("id") == q2_id:
                    val2 = q.get("value")
                    if isinstance(val2, list) and val2:
                        val2 = ", ".join(str(v) for v in val2)

            if val1 is not None and val2 is not None:
                paired_count += 1
                str_val1 = str(val1)
                str_val2 = str(val2)
                if str_val1 not in matrix:
                    matrix[str_val1] = {}
                matrix[str_val1][str_val2] = matrix[str_val1].get(str_val2, 0) + 1
        except (KeyError, TypeError):
            continue

    return {
        "q1": q1_id,
        "q2": q2_id,
        "paired_responses": paired_count,
        "matrix": matrix,
    }


def generate_analysis(
    form_id: str,
    account: Optional[str] = None,
    screening_question_id: Optional[str] = None,
    screening_exclude_value: Optional[str] = None,
    cross_tab_pairs: Optional[List[List[str]]] = None,
) -> Dict[str, Any]:
    """Generate comprehensive quantitative analysis for a form."""
    # Get form structure
    form_data = get_form_structure(form_id, account)
    questions = form_data.get("questions", [])

    # Get submissions
    submissions_data = get_submissions(form_id, account, limit=100)
    all_submissions = submissions_data.get("responses", [])

    # Apply screening filter if provided
    filtered_submissions = all_submissions
    if screening_question_id and screening_exclude_value:
        filtered_submissions = [
            s for s in all_submissions
            if any(
                q.get("id") == screening_question_id
                and q.get("value") != screening_exclude_value
                for q in s.get("questions", [])
            )
        ]

    # Build question summary
    question_summaries = {}
    question_types = {}

    for q in questions:
        q_id = q.get("id")
        q_type = _get_question_type(q)
        question_types[q_id] = q_type

        responses = _extract_responses(filtered_submissions, q_id, q_type)
        dist = _calculate_distribution(responses, q_type)

        question_summaries[q_id] = {
            "question_text": q.get("name", "Unknown"),
            "question_type": q_type,
            "response_count": dist.get("response_count", 0),
            "distribution": dist.get("distribution", {}),
            "percentage": dist.get("percentage", {}),
        }

        # Add numeric stats for scale questions
        if "mean" in dist:
            question_summaries[q_id]["stats"] = {
                "min": dist["min"],
                "max": dist["max"],
                "mean": dist["mean"],
                "median": dist["median"],
            }

    # Cross-tabulations
    cross_tabs = []
    if cross_tab_pairs:
        for q1_id, q2_id in cross_tab_pairs:
            if q1_id in question_types and q2_id in question_types:
                cross_tabs.append(_cross_tabulate(filtered_submissions, q1_id, q2_id))

    return {
        "form_id": form_id,
        "form_title": form_data.get("name", form_data.get("title", "Unknown")),
        "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        "total_submissions": len(all_submissions),
        "filtered_submissions": len(filtered_submissions),
        "screening_applied": screening_question_id is not None,
        "question_summaries": question_summaries,
        "cross_tabs": cross_tabs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Fillout API client for multi-account access and analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all forms from both accounts
  python3 fillout_client.py --list-forms

  # List forms from specific account
  python3 fillout_client.py --list-forms --account careerspan

  # Get form structure
  python3 fillout_client.py --form-structure jPQRwpT4nGus

  # Get all submissions
  python3 fillout_client.py --submissions jPQRwpT4nGus

  # Auto-detect account for a form
  python3 fillout_client.py --detect-account jPQRwpT4nGus

  # Generate full quantitative analysis
  python3 fillout_client.py --analyze jPQRwpT4nGus

  # Analyze with screening filter
  python3 fillout_client.py --analyze jPQRwpT4nGus \\
      --screening dGZw --screening-exclude "No"

  # Output analysis to file
  python3 fillout_client.py --analyze jPQRwpT4nGus -o analysis.json
        """
    )

    parser.add_argument(
        "--list-forms", "-l",
        action="store_true",
        help="List all forms from configured accounts",
    )
    parser.add_argument(
        "--form-structure",
        metavar="FORMID",
        help="Get structure for a specific form",
    )
    parser.add_argument(
        "--submissions",
        metavar="FORMID",
        help="Get all submissions for a form",
    )
    parser.add_argument(
        "--detect-account",
        metavar="FORMID",
        help="Auto-detect which account owns a form",
    )
    parser.add_argument(
        "--analyze",
        metavar="FORMID",
        help="Generate quantitative analysis for a form",
    )
    parser.add_argument(
        "--account", "-a",
        metavar="ACCOUNT",
        choices=list(ACCOUNTS.keys()),
        help="Specify account (default: auto-detect)",
    )
    parser.add_argument(
        "--screening",
        metavar="QUESTION_ID",
        help="Screening question ID to filter responses",
    )
    parser.add_argument(
        "--screening-exclude",
        metavar="VALUE",
        help="Value to exclude from analysis",
    )
    parser.add_argument(
        "--cross-tabs",
        nargs="+",
        metavar="Q1_ID:Q2_ID",
        help="Cross-tabulate question pairs (format: q1_id:q2_id)",
    )
    parser.add_argument(
        "--output", "-o",
        metavar="FILE",
        help="Output JSON to file instead of stdout",
    )

    args = parser.parse_args()

    # Check for required API keys
    if not any(ACCOUNTS.values()):
        print("Error: No Fillout API keys configured. Set FILLOUT_SECRET_PERSONAL and/or FILLOUT_SECRET_CAREERSPAN.")
        sys.exit(1)

    result = None

    if args.list_forms:
        result = list_forms(args.account)

    elif args.form_structure:
        result = get_form_structure(args.form_structure, args.account)

    elif args.submissions:
        result = get_submissions(args.submissions, args.account)

    elif args.detect_account:
        result = detect_account(args.detect_account)

    elif args.analyze:
        cross_tab_pairs = None
        if args.cross_tabs:
            cross_tab_pairs = [pair.split(":") for pair in args.cross_tabs if ":" in pair]

        result = generate_analysis(
            form_id=args.analyze,
            account=args.account,
            screening_question_id=args.screening,
            screening_exclude_value=args.screening_exclude,
            cross_tab_pairs=cross_tab_pairs,
        )

    else:
        parser.print_help()
        sys.exit(1)

    # Output result
    output_json = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output_json, encoding="utf-8")
        print(f"Output written to {args.output}")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
