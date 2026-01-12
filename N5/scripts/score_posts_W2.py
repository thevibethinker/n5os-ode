#!/usr/bin/env python3
"""
W2 Worker: Score and categorize LinkedIn posts for Content Library ingestion.
Criteria: Originality (1-5), Evergreen (1-5)
Composite = Originality * 0.6 + Evergreen * 0.4
Categories: TOP (≥4.0), MAYBE (3.5-3.9), SKIP (<3.5)
"""
import json
from pathlib import Path
from datetime import datetime

INPUT_DIR = Path("/home/.z/workspaces/con_zTfB7kehxEEHmaoC/worker_updates")
OUTPUT_DIR = Path("/home/.z/workspaces/con_JMLoHaeJEiPz7N71")

def load_jsonl(filepath):
    items = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    return items

def score_post(post):
    """
    Score a post on originality and evergreen dimensions.
    Returns (originality_score, evergreen_score, topic, content_type)
    """
    text = post.get('text', '').lower()
    title = post.get('title', '').lower()
    is_reshare = post.get('is_reshare', False)
    word_count = post.get('word_count', 0)
    date = post.get('date', '')
    source_id = post.get('id', '')
    
    # Empty posts
    if word_count == 0 or not text.strip():
        return 1, 1, "empty", "empty", "SKIP"
    
    # Reshares get low originality
    if is_reshare:
        return 1, 3, "reshare", "reshare", "SKIP"
    
    originality = 3  # Default
    evergreen = 3    # Default
    topic = "general"
    content_type = "thought-piece"
    
    full_text = (text + " " + title).lower()
    
    # === ORIGINALITY SCORING ===
    
    # High originality indicators
    high_orig_patterns = [
        "i believe", "in my opinion", "i think", "my view", "my take",
        "here's the thing", "unpopular opinion", "hot take",
        "let me be blunt", "the real", "actually", "here's why",
        "paradox", "insight", "framework", "model", "thesis",
        "i've been thinking", "counterintuitive", "nuanced"
    ]
    
    # Low originality indicators
    low_orig_patterns = [
        "congratulations", "congrats", "excited to announce",
        "thrilled to share", "pleased to announce", "proud to",
        "join me", "save the date", "link in", "register",
        "delighted to", "i'm hiring", "we're hiring"
    ]
    
    # Check patterns
    high_orig_count = sum(1 for p in high_orig_patterns if p in full_text)
    low_orig_count = sum(1 for p in low_orig_patterns if p in full_text)
    
    # Adjust originality
    originality += min(high_orig_count, 2)  # Up to +2 for novel insights
    originality -= min(low_orig_count, 2)   # Down for announcements
    
    # Long-form, substantive content gets boost
    if word_count > 300:
        originality += 1
    if word_count > 500:
        originality += 0.5
    
    # Promotional about others without insight
    if "check out" in full_text or "details below" in full_text:
        if high_orig_count < 2:
            originality -= 1
    
    # === EVERGREEN SCORING ===
    
    # Time-bound indicators (reduce evergreen)
    time_bound = [
        "deadline", "this week", "tomorrow", "today", "next month",
        "registration", "register now", "save the date",
        "application deadline", "applications close",
        "joining", "starting", "event link", "upcoming"
    ]
    
    # Evergreen indicators
    timeless = [
        "why", "how to", "framework", "principle", "always",
        "never", "truth", "pattern", "lesson", "insight",
        "fundamentally", "the real", "problem", "solution",
        "strategy", "approach", "mindset"
    ]
    
    time_bound_count = sum(1 for p in time_bound if p in full_text)
    timeless_count = sum(1 for p in timeless if p in full_text)
    
    evergreen += min(timeless_count, 2)
    evergreen -= min(time_bound_count, 2)
    
    # Old posts about specific deadlines/events are dated
    if date and date < "2024-01-01":
        if time_bound_count > 0:
            evergreen -= 1
    
    # === TOPIC DETECTION ===
    topic_patterns = {
        "ai-job-search": ["ai", "chatgpt", "auto-apply", "automation", "llm"],
        "hiring-market": ["hiring", "recruiting", "job market", "employers", "talent"],
        "career-advice": ["career", "job search", "resume", "interview", "coach"],
        "startup-life": ["founder", "startup", "building", "co-founder", "venture"],
        "ai-productivity": ["zo computer", "productivity", "ai tools", "workflow"],
        "careerspan": ["careerspan", "apply ai", "applyai"],
        "thought-leadership": ["industry", "trend", "future", "prediction", "paradigm"],
        "networking": ["intro", "connect", "meet", "networking", "event"]
    }
    
    for t, patterns in topic_patterns.items():
        if any(p in full_text for p in patterns):
            topic = t
            break
    
    # === CONTENT TYPE DETECTION ===
    if any(p in full_text for p in ["how to", "here's how", "step", "guide", "framework"]):
        content_type = "how-to"
    elif any(p in full_text for p in ["opinion", "i think", "my view", "i believe", "hot take"]):
        content_type = "opinion"
    elif any(p in full_text for p in ["excited to announce", "thrilled", "congrats", "proud to"]):
        content_type = "announcement"
    elif any(p in full_text for p in ["story", "origin", "journey", "experience", "learned"]):
        content_type = "story"
    else:
        content_type = "thought-piece"
    
    # Clamp scores
    originality = max(1, min(5, originality))
    evergreen = max(1, min(5, evergreen))
    
    # Calculate composite
    composite = round(originality * 0.6 + evergreen * 0.4, 1)
    
    # Determine category
    if composite >= 4.0:
        category = "TOP"
    elif composite >= 3.5:
        category = "MAYBE"
    else:
        category = "SKIP"
    
    return originality, evergreen, topic, content_type, category


def main():
    # Load data
    posts = load_jsonl(INPUT_DIR / "posts.jsonl")
    articles = load_jsonl(INPUT_DIR / "articles.jsonl")
    
    print(f"Loaded {len(posts)} posts and {len(articles)} articles")
    
    top_posts = []
    maybe_posts = []
    skip_count = 0
    empty_count = 0
    
    topic_counts = {}
    
    # Process posts
    for post in posts:
        originality, evergreen, topic, content_type, category = score_post(post)
        
        if post.get('word_count', 0) == 0:
            empty_count += 1
            skip_count += 1
            continue
        
        result = {
            "source_id": post["id"],
            "date": post.get("date", ""),
            "text": post.get("text", ""),
            "originality_score": originality,
            "evergreen_score": evergreen,
            "composite_score": round(originality * 0.6 + evergreen * 0.4, 1),
            "topic": topic,
            "content_type": content_type,
            "category": category
        }
        
        if category == "TOP":
            top_posts.append(result)
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        elif category == "MAYBE":
            maybe_posts.append(result)
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        else:
            skip_count += 1
    
    # Process articles (all are original long-form, auto-include as TOP)
    for article in articles:
        text = article.get("text", "")
        title = article.get("title", "")
        
        # Articles get high scores by default
        originality = 5  # Original long-form
        evergreen = 4    # Generally evergreen thought leadership
        
        # Topic detection for articles
        full_text = (text + " " + title).lower()
        if "auto-apply" in full_text or "job search" in full_text:
            topic = "ai-job-search"
        elif "ghost job" in full_text:
            topic = "hiring-market"
        elif "niche" in full_text and "social" in full_text:
            topic = "thought-leadership"
        else:
            topic = "career-advice"
        
        result = {
            "source_id": article["id"],
            "date": article.get("date", ""),
            "text": text,
            "title": title,
            "originality_score": originality,
            "evergreen_score": evergreen,
            "composite_score": round(originality * 0.6 + evergreen * 0.4, 1),
            "topic": topic,
            "content_type": "thought-piece",
            "category": "TOP"
        }
        top_posts.append(result)
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    # Sort by composite score descending
    top_posts.sort(key=lambda x: x["composite_score"], reverse=True)
    maybe_posts.sort(key=lambda x: x["composite_score"], reverse=True)
    
    # Write outputs
    with open(OUTPUT_DIR / "top_posts_candidates.jsonl", 'w') as f:
        for p in top_posts:
            f.write(json.dumps(p) + "\n")
    
    with open(OUTPUT_DIR / "maybe_posts.jsonl", 'w') as f:
        for p in maybe_posts:
            f.write(json.dumps(p) + "\n")
    
    # Generate summary
    total_reviewed = len(posts) + len(articles)
    summary = f"""---
created: {datetime.now().strftime('%Y-%m-%d')}
last_edited: {datetime.now().strftime('%Y-%m-%d')}
version: 1.0
provenance: con_JMLoHaeJEiPz7N71
---

# W2 Selection Summary: LinkedIn Posts for Content Library

## Overview

| Metric | Count |
|--------|-------|
| **Total Reviewed** | {total_reviewed} |
| **Posts** | {len(posts)} |
| **Articles** | {len(articles)} |
| **Empty Posts** | {empty_count} |

## Selection Results

| Category | Count | Percentage |
|----------|-------|------------|
| **TOP** (≥4.0) | {len(top_posts)} | {len(top_posts)*100/total_reviewed:.1f}% |
| **MAYBE** (3.5-3.9) | {len(maybe_posts)} | {len(maybe_posts)*100/total_reviewed:.1f}% |
| **SKIP** (<3.5) | {skip_count} | {skip_count*100/total_reviewed:.1f}% |

## TOP Posts (Auto-Ingest)

| ID | Date | Score | Topic | Type |
|----|------|-------|-------|------|
"""
    
    for p in top_posts[:25]:  # Show first 25
        summary += f"| {p['source_id']} | {p['date']} | {p['composite_score']} | {p['topic']} | {p['content_type']} |\n"
    
    if len(top_posts) > 25:
        summary += f"| ... | ... | ... | ({len(top_posts) - 25} more) | ... |\n"
    
    summary += f"""
## MAYBE Posts (For V's Review)

| ID | Date | Score | Topic | Type |
|----|------|-------|-------|------|
"""
    
    for p in maybe_posts[:15]:
        summary += f"| {p['source_id']} | {p['date']} | {p['composite_score']} | {p['topic']} | {p['content_type']} |\n"
    
    if len(maybe_posts) > 15:
        summary += f"| ... | ... | ... | ({len(maybe_posts) - 15} more) | ... |\n"
    
    summary += f"""
## Topic Distribution (Selected Posts)

| Topic | Count |
|-------|-------|
"""
    for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        summary += f"| {topic} | {count} |\n"
    
    summary += f"""
## Scoring Criteria Applied

**Originality (weight: 0.6)**
- High: Novel insights, unique framing, personal frameworks, substantive analysis
- Low: Reshares, congratulatory posts, announcements, promotional content

**Evergreen (weight: 0.4)**
- High: Timeless principles, frameworks, lessons learned, enduring advice
- Low: Time-bound events, deadlines, announcements with specific dates

## Notes

1. All 3 articles auto-included as TOP (original long-form content)
2. {empty_count} empty posts skipped (word_count=0)
3. Posts with high insight density scored higher on originality
4. Event promotions and congratulatory posts deprioritized
"""
    
    with open(OUTPUT_DIR / "selection_summary.md", 'w') as f:
        f.write(summary)
    
    print(f"\n=== W2 RESULTS ===")
    print(f"Total reviewed: {total_reviewed}")
    print(f"TOP: {len(top_posts)}")
    print(f"MAYBE: {len(maybe_posts)}")
    print(f"SKIP: {skip_count}")
    print(f"\nTopic distribution:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
        print(f"  {topic}: {count}")
    print(f"\nOutputs written to: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()

