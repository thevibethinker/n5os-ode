#!/usr/bin/env python3
"""
Systematic Pangram testing to identify AI detection signals.
Builds a database of what passes vs fails.
"""

import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get("PANGRAM_API_KEY")
ENDPOINT = "https://text.api.pangram.com/v3"

def test_pangram(text: str, label: str, category: str) -> dict:
    """Test a sample and return results."""
    try:
        resp = requests.post(
            ENDPOINT,
            headers={"x-api-key": API_KEY, "Content-Type": "application/json"},
            json={"text": text},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()
        
        result = {
            "label": label,
            "category": category,
            "text": text,
            "char_count": len(text),
            "word_count": len(text.split()),
            "fraction_ai": data.get("fraction_ai", 0),
            "fraction_human": data.get("fraction_human", 0),
            "prediction": data.get("prediction_short", ""),
            "passed": data.get("fraction_ai", 1) < 0.3,
            "windows": data.get("windows", [])
        }
        return result
    except Exception as e:
        return {"label": label, "category": category, "error": str(e)}


# Test samples organized by category
SAMPLES = {
    # ===== V's ACTUAL X POSTS (should pass) =====
    "v_x_posts": [
        ("toxic_trait", "My toxic trait is not shutting the fuck up about products I love until it has subsumed all around me (Borg-as-a-Service?)"),
        ("founder_math", "Founder math is wild. You'll spend $8K/month on tools. $25K on a booth at a conference. $50K on a fractional CMO. But the first five people who will build your company? 'Can we just post for free?' Your first five hires are your foundation. Act like it."),
        ("blessed_are", "Blessed are the try-hard, type-A sons-of-bitches for they shall inherit the Earth"),
        ("millennial_urge", "the millennial urge to put song lyrics on social media as a way of signaling emotional state"),
        ("hot_take", "Hot take: The 'AI won't replace X' framing is cope. It's already replacing BAD ones."),
        ("zocialism", "I knew if Zocialism was to start anywhere, it would be in Brooklyn #LFZ"),
        ("startups_chores", "Startups ain't shit but chores and tricks"),
        ("power_user", "I'm a Howie power user, and I fucking love it. Genuinely great AI product that consciously trades flash for substance."),
        ("missed_point", "The degree to which you've missed the point is staggering. Like your understanding couldn't hit the broadside of a barn with a bazooka at 10 paces."),
        ("dei_question", "So when Musk does it, it isn't DEI and it's smart, but when others do, it is DEI and it's bad?"),
        ("chuffed", "Absolutely fucking chuffed to support the good folks over at @zocomputer"),
        ("10pm_ai", "For the record, 'I am aware' is not a message you want to receive from your AI at 10PM on a Tuesday! If anyone needs me, I'll be in the bathroom dunking all my devices in the tub 😰"),
    ],
    
    # ===== V-VOICE EMAILS (mixed results expected) =====
    "v_voice_emails": [
        ("warm_intro", "Hi Jabari — one of the founders of Zo Computer. I've built my entire personal operating system on it — 250k+ lines of code. It's essentially a computer in the cloud you can prompt and set to work on your behalf."),
        ("meeting_request", "Can we do 20 minutes Thursday to discuss the project?"),
        ("follow_up_bump", "Following up on the Careerspan demo. Let me know by Friday if you're in."),
        ("cold_outreach", "Marcus — V here, founder of Careerspan. Your work on talent ops caught my attention. I think we have overlap on AI-assisted hiring. 15 minutes next week?"),
        ("status_update", "Update: Issues 1-3 resolved. Issue 4 pending legal review. ETA Friday."),
        ("delay_notify", "The integration is delayed. Hit an API rate limit issue. New ETA: Monday. I'm caching responses to prevent recurrence."),
        ("disagreement", "I see it differently. The data shows retention drops 40% after week 2. What am I missing?"),
        ("critique", "Strong direction. One fix: cut the intro by half. The real hook is in paragraph 2."),
    ],
    
    # ===== GENERIC AI WRITING (should fail) =====
    "generic_ai": [
        ("corporate_jargon", "It is essential to leverage innovative solutions in order to facilitate comprehensive digital transformation. Furthermore, our robust methodology enables organizations to streamline their operations and empower stakeholders through cutting-edge technology paradigms."),
        ("generic_follow_up", "I hope this email finds you well. I wanted to follow up on our previous conversation and see if you had any questions about our proposal. Please let me know if there's anything else I can help with."),
        ("smooth_prose", "The implementation of artificial intelligence in modern business processes has fundamentally transformed how organizations approach problem-solving. By utilizing machine learning algorithms, companies can now analyze vast amounts of data to make more informed decisions."),
        ("listicle_intro", "In today's fast-paced digital landscape, staying ahead of the curve is more important than ever. Here are five key strategies that successful companies are using to drive innovation and maintain competitive advantage."),
        ("thought_leadership", "As we navigate an increasingly complex business environment, it's crucial that leaders develop a nuanced understanding of emerging technologies and their potential impact on organizational strategy."),
        ("generic_pitch", "Our platform offers a comprehensive suite of tools designed to help businesses of all sizes optimize their workflows and improve operational efficiency. With our intuitive interface and powerful features, you'll be able to achieve your goals faster than ever before."),
    ],
    
    # ===== HEDGING PATTERNS (should fail) =====
    "hedging": [
        ("maybe_potentially", "I think maybe we could potentially explore this opportunity if you're interested."),
        ("permission_hedge", "If you don't mind, and if it's not too much trouble, I was wondering if you might be able to help?"),
        ("softener_stack", "I just wanted to quickly check in about a slightly small ask I basically have."),
        ("escape_hatch", "Let me know if you're interested, no rush, no worries if not, totally understand if you're busy."),
        ("throat_clearing", "I hope this email finds you well. I wanted to reach out because I thought I'd follow up on our previous conversation."),
    ],
    
    # ===== STRUCTURAL VARIATIONS =====
    "structural": [
        ("short_punchy", "Try Speechify. Changed how I consume content."),
        ("medium_specific", "Just spent 4 hours on API docs. Found the bug in line 3. Classic."),
        ("question_mid", "Built the dashboard. You know what's missing? A way to export. Adding that next."),
        ("numbers_concrete", "3 calls today. 2 warm leads. 1 verbal commitment. Not bad for a Tuesday."),
        ("em_dash_pivot", "Thought I was done — turns out the edge cases had edge cases."),
    ],
}


def run_tests():
    """Run all tests and output results."""
    results = []
    
    for category, samples in SAMPLES.items():
        print(f"\n{'='*60}")
        print(f"TESTING: {category.upper()}")
        print('='*60)
        
        for label, text in samples:
            result = test_pangram(text, label, category)
            results.append(result)
            
            if "error" in result:
                print(f"  ❌ {label}: ERROR - {result['error']}")
            else:
                status = "✓ PASS" if result["passed"] else "✗ FAIL"
                ai_pct = result["fraction_ai"] * 100
                print(f"  {status} {label}: {ai_pct:.1f}% AI ({result['word_count']} words)")
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY BY CATEGORY")
    print('='*60)
    
    for category in SAMPLES.keys():
        cat_results = [r for r in results if r.get("category") == category and "error" not in r]
        passed = sum(1 for r in cat_results if r["passed"])
        total = len(cat_results)
        avg_ai = sum(r["fraction_ai"] for r in cat_results) / total if total > 0 else 0
        print(f"  {category}: {passed}/{total} passed, avg AI: {avg_ai*100:.1f}%")
    
    # Save detailed results
    output_path = "/home/workspace/Integrations/Pangram/test_results.json"
    with open(output_path, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "threshold": 0.3,
            "results": results
        }, f, indent=2)
    print(f"\nDetailed results saved to: {output_path}")
    
    return results


if __name__ == "__main__":
    run_tests()

