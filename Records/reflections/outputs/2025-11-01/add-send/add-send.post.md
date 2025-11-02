Here's a pattern I keep seeing:

# Send approval email to employer (V)
        try:
            from employer_email_templates import format_approval_request_email
            
            email_content = format_approval_request_email(
                candidate_id=candidate_id,
                job_title=job_title,
                candidate_summary=candidate_summary,
                rationale=f"MAYBE decision. Concerns: {rationale}",
                questions=questions,
                request_id=approval_request["request_id"]
            )
            
            # Import and use send_email_to_user
            import __main__
            if hasattr(__main__, 'send_email_to_user'):
                __main__.send_email_to_user(
                    subject=email_content.subject,
                    markdown_body=email_content.body_markdown
                )
                logger.info("✓ Sent approval request email to employer")
            else:
                logger.warning("[SIMULATION] send_email_to_user not available")
                logger.info(f"Would send: {email_content.subject}")
        except Exception as e:
            logger.error(f"Failed to send employer email: {e}")
            logger.info("Approval request saved but employer must be notified manually")

—
What stands out to you? What would you add?