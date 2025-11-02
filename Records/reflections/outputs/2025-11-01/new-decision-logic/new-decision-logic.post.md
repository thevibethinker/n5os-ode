Here's a pattern I keep seeing:

# === MAKE DECISION ===
    
    # Initialize defaults
    decision = "PASS"
    confidence = "medium"
    narrative = "Insufficient evidence of consulting-relevant capabilities for this role."
    
    # Immediate disqualifiers
    if ai_result['likelihood'] == 'high':
        decision = "PASS"
        confidence = "high"
        narrative = "Resume appears AI-generated with generic language and low specificity. Not a genuine candidate."
    
    # Check for direct target company match (HIGHEST PRIORITY)
    elif has_target_company:
        decision = "STRONG_INTERVIEW"
        confidence = "high"
        narrative = "Former employee at target company. Direct experience makes this a strong fit worth immediate conversation."
    
    # Elite consulting background + major impact
    elif has_consulting and has_major_impact and has_elite:
        decision = "STRONG_INTERVIEW"
        confidence = "high"
        narrative = f"Elite consulting background with 0M+ business impact. Strong traditional candidate."
    
    # Solid consulting background
    elif has_consulting and (has_elite or has_major_impact):
        decision = "STRONG_INTERVIEW"
        confidence = "medium"
        narrative = "Solid consulting background with strong supporting signals. Worth prioritizing."
    
    # Strong bundle (multiple strengths, minimal concerns)
    elif len(strengths) >= 3 and len(concerns) <= 1 and has_any_business_signal:
        decision = "STRONG_INTERVIEW"
        confidence = "medium"
        narrative = "Compelling combination of signals. Strong candidate worth interviewing."
    
    # Consulting experience alone
    elif has_consulting:
        decision = "INTERVIEW"
        confidence = "medium"
        narrative = "Consulting background. Standard interview to assess depth and fit."
    
    # Elite + analytical strength
    elif has_elite and analytical_strength >= 0.7:
        decision = "INTERVIEW"
        confidence = "medium"
        narrative = "Promising candidate with elite background and transferable skills. Worth exploring fit."
    
    # Maybe: elite + clarifiable gaps
    elif has_elite and len(clarifications) > 0 and len(clarifications) <= 3:
        decision = "MAYBE"
        confidence = "low"
        narrative = "Intriguing elite background but key gaps. Worth clarifying before deciding."
    
    # Maybe: major impact + analytical
    elif has_major_impact and analytical_strength >= 0.6 and len(clarifications) <= 3:
        decision = "MAYBE"
        confidence = "low"
        narrative = "Strong business outcomes but unclear consulting readiness. Clarification needed."
    
    # Backup list: too many questions
    elif len(clarifications) > 3:
        decision = "BACKUP_LIST"
        confidence = "low"
        narrative = "Too many fundamental gaps to clarify efficiently. Consider if shortlist insufficient."
    
    # Pass: role mismatch
    elif has_role_mismatch and not has_any_business_signal:
        decision = "PASS"
        confidence = "high"
        narrative = "Role mismatch for consulting position. Not a fit."
    
    # Pass: default (weak signals)
    else:
        if not has_elite and not has_impact:
            confidence = "high"
            narrative = "No compelling signals for consulting role. Not a fit."

—
What stands out to you? What would you add?