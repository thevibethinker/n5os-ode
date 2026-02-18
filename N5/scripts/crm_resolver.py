#!/usr/bin/env python3
"""Compatibility wrapper for CRM identity resolution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from crm_identity_resolver import CRMIdentityResolver


@dataclass
class MatchResult:
    person_id: int
    confidence: float
    match_type: str
    details: Dict[str, Any]


class IdentityResolver:
    def __init__(
        self,
        db_path: str = "/home/workspace/N5/data/n5_core.db",
        auto_link_threshold: float = 0.99,
    ):
        self.resolver = CRMIdentityResolver(
            auto_link_threshold=auto_link_threshold,
            db_path=db_path,
        )

    def resolve_person(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        company: Optional[str] = None,
    ) -> Optional[MatchResult]:
        result = self.resolver.auto_link(
            email=email,
            name=name,
            linkedin_url=linkedin_url,
            company=company,
        )
        if result.person_id is None:
            return None

        match_type = result.method.upper()
        return MatchResult(
            person_id=result.person_id,
            confidence=result.confidence,
            match_type=match_type,
            details={
                "name": result.full_name,
                "email": result.email,
                "markdown_path": result.markdown_path,
                "method": result.method,
            },
        )


if __name__ == "__main__":
    import sys

    resolver = IdentityResolver()
    email_arg = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] != "None" else None
    name_arg = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] != "None" else None
    linkedin_arg = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] != "None" else None
    company_arg = sys.argv[4] if len(sys.argv) > 4 and sys.argv[4] != "None" else None

    print(
        f"Resolving: email={email_arg}, name={name_arg}, linkedin={linkedin_arg}, company={company_arg}"
    )
    result = resolver.resolve_person(
        email=email_arg,
        name=name_arg,
        linkedin_url=linkedin_arg,
        company=company_arg,
    )
    if result:
        print(f"MATCH: {result}")
    else:
        print("NO MATCH")
