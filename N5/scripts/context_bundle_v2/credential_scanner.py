#!/usr/bin/env python3
"""
Credential Scanner for Context Bundles v2.0
Identifies sensitive credentials in files and data structures.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
import yaml


@dataclass
class CredentialFinding:
    """Represents a found credential."""
    credential_type: str
    location: str
    line_number: Optional[int] = None
    sensitive: bool = True


class CredentialScanner:
    """Scans for credentials in various content sources."""
    
    def __init__(self):
        self.patterns = {
            'api_key': re.compile(
                r'(?i)(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,64})["\']?'
            ),
            'password': re.compile(
                r'(?i)(password|passwd|pwd)["\']?\s*[:=]\s*["\']?([^"\'\s]{8,128})["\']?'
            ),
            'token': re.compile(
                r'(?i)(token|access_token|auth_token)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,64})["\']?'
            ),
            'secret': re.compile(
                r'(?i)(secret|client_secret)["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{20,64})["\']?'
            ),
            'convo_id': re.compile(
                r'(?i)con_[a-zA-Z0-9]{16}'
            ),
            'email': re.compile(
                r'(?i)[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            ),
        }
    
    def scan_text(self, text: str, mask: bool = True) -> List[CredentialFinding]:
        """
        Scan text for credential patterns.
        
        Args:
            text: Text content to scan
            mask: Whether to mask sensitive values (default: True)
        
        Returns:
            List of credential findings
        """
        findings = []
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for cred_type, pattern in self.patterns.items():
                for match in pattern.finditer(line):
                    location = f"line {line_num}"
                    if mask:
                        # Truncate sensitive values
                        value = match.group(2) if len(match.groups()) > 1 else match.group(0)
                        if cred_type != 'convo_id':  # Don't mask conversation IDs
                            masked = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                            location = f"{location}: {cred_type}={masked}"
                    
                    findings.append(CredentialFinding(
                        credential_type=cred_type,
                        location=location,
                        line_number=line_num
                    ))
        
        return findings
    
    def scan_file(self, file_path: Union[str, Path], mask: bool = True) -> List[CredentialFinding]:
        """
        Scan a file for credentials.
        
        Args:
            file_path: Path to file to scan
            mask: Whether to mask sensitive values
        
        Returns:
            List of credential findings
        """
        path = Path(file_path)
        if not path.exists():
            return []
        
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            return self.scan_text(content, mask=mask)
        except Exception:
            return []
    
    def scan_yaml_file(self, file_path: Union[str, Path], mask: bool = True) -> List[CredentialFinding]:
        """
        Scan a YAML file for credentials with additional YAML-aware parsing.
        
        Args:
            file_path: Path to YAML file
            mask: Whether to mask sensitive values
        
        Returns:
            List of credential findings
        """
        findings = []
        path = Path(file_path)
        
        if not path.exists():
            return findings
        
        try:
            # Raw text scan
            content = path.read_text(encoding='utf-8')
            findings.extend(self.scan_text(content, mask=mask))
            
            # Also scan keys/values in YAML structure
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
                if data:
                    findings.extend(self._scan_yaml_data(data))
                    
        except Exception:
            pass
        
        return findings
    
    def scan_context_bundle(self, bundle_path: Union[str, Path], mask: bool = True) -> List[CredentialFinding]:
        """
        Scan a context bundle file for credentials.
        
        Args:
            bundle_path: Path to context bundle file
            mask: Whether to mask sensitive values
        
        Returns:
            List of credential findings
        """
        return self.scan_yaml_file(bundle_path, mask=mask)
    
    def _scan_yaml_data(self, data: Any, prefix: str = "") -> List[CredentialFinding]:
        """Recursively scan YAML data structure."""
        findings = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                key_path = f"{prefix}.{key}" if prefix else key
                findings.extend(self._scan_yaml_value(key_path, str(value)))
                findings.extend(self._scan_yaml_data(value, key_path))
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                findings.extend(self._scan_yaml_data(item, f"{prefix}[{idx}]"))
        elif isinstance(data, (str, int, float, bool)):
            findings.extend(self._scan_yaml_value(prefix, str(data)))
        
        return findings
    
    def _scan_yaml_value(self, key_path: str, value: str) -> List[CredentialFinding]:
        """Scan a single YAML key-value pair."""
        findings = []
        
        # Check if the key name suggests it contains credentials
        suspicious_keys = ['token', 'key', 'secret', 'password', 'cred', 'auth', 'api', 'private']
        
        key_lower = key_path.lower()
        for keyword in suspicious_keys:
            if keyword in key_lower:
                # Value might be a credential
                value_str = str(value)
                if len(value_str) > 10 and not value_str.startswith('${'):
                    masked = f"{value_str[:4]}...{value_str[-4:]}" if len(value_str) > 8 else "***"
                    findings.append(CredentialFinding(
                        credential_type='suspicious_value',
                        location=f"{key_path}={masked}",
                        sensitive=True
                    ))
                break
        
        return findings


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python credential_scanner.py <file_path>")
        sys.exit(1)
    
    scanner = CredentialScanner()
    findings = scanner.scan_file(sys.argv[1], mask=True)
    
    if findings:
        print(f"\nFound {len(findings)} potential credential(s):\n")
        for finding in findings:
            print(f"  {finding.credential_type}: {finding.location}")
        print(f"\n⚠️  {len(findings)} credential(s) detected - review for security")
    else:
        print("✓ No credentials found")

