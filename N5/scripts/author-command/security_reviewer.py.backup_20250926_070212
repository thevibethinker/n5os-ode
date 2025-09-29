#!/usr/bin/env python3
"""
Security Reviewer for Command Authoring System

Performs comprehensive security analysis of all components.
Validates safety principles and identifies potential vulnerabilities.
"""

import ast
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

logger = logging.getLogger('security_reviewer')


class SecurityIssue:
    """Represents a security issue found during review"""
    
    def __init__(self, severity: str, category: str, description: str, 
                 file_path: str, line_number: int = None, suggestion: str = None):
        self.severity = severity  # 'critical', 'high', 'medium', 'low', 'info'
        self.category = category  # 'injection', 'path_traversal', 'code_execution', etc.
        self.description = description
        self.file_path = file_path
        self.line_number = line_number
        self.suggestion = suggestion
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'severity': self.severity,
            'category': self.category,
            'description': self.description,
            'file_path': self.file_path,
            'line_number': self.line_number,
            'suggestion': self.suggestion
        }


class SecurityReviewer:
    """Comprehensive security analysis for command authoring system"""
    
    def __init__(self, script_dir: str = "/home/workspace/N5/scripts/author-command"):
        self.script_dir = Path(script_dir)
        self.issues = []
        self.patterns = self._load_security_patterns()
    
    def _load_security_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load security check patterns"""
        return {
            'command_injection': [
                {
                    'pattern': r'os\.system\([^)]*["\'][^"\']*\+',
                    'severity': 'critical',
                    'description': 'Potential command injection via string concatenation'
                },
                {
                    'pattern': r'subprocess\.(call|run|Popen)\([^)]*["\'][^"\']*\+',
                    'severity': 'critical', 
                    'description': 'Potential command injection in subprocess call'
                },
                {
                    'pattern': r'shell=True',
                    'severity': 'high',
                    'description': 'Shell injection risk - avoid shell=True when possible'
                }
            ],
            'path_traversal': [
                {
                    'pattern': r'open\([^)]*\+[^)]*["\'][^"\']*\.\.[^"\']*["\']',
                    'severity': 'high',
                    'description': 'Potential path traversal vulnerability'
                },
                {
                    'pattern': r'(file_path|path|filename)[^=]*=[^=]*input\(',
                    'severity': 'medium',
                    'description': 'User input used directly for file paths'
                }
            ],
            'code_execution': [
                {
                    'pattern': r'eval\(',
                    'severity': 'critical',
                    'description': 'Use of eval() can lead to code injection'
                },
                {
                    'pattern': r'exec\(',
                    'severity': 'critical',
                    'description': 'Use of exec() can lead to code execution'
                },
                {
                    'pattern': r'__import__\([^)]*input\(',
                    'severity': 'critical',
                    'description': 'Dynamic import with user input'
                }
            ],
            'information_disclosure': [
                {
                    'pattern': r'print\([^)]*password|print\([^)]*secret|print\([^)]*token',
                    'severity': 'medium',
                    'description': 'Potential information disclosure in print statements'
                },
                {
                    'pattern': r'logger\.(info|debug|warning)\([^)]*password|secret|token',
                    'severity': 'medium',
                    'description': 'Potential secrets in log messages'
                }
            ],
            'unsafe_file_operations': [
                {
                    'pattern': r'open\([^)]*["\'][^"\']*["\'][^)]*["\']w',
                    'severity': 'low',
                    'description': 'File write operation - ensure proper validation'
                },
                {
                    'pattern': r'\.unlink\(\)|\.rmdir\(\)|\.remove\(\)',
                    'severity': 'medium',
                    'description': 'File deletion operation - ensure safety checks'
                }
            ]
        }
    
    def perform_comprehensive_review(self) -> Dict[str, Any]:
        """Perform comprehensive security review"""
        logger.info("Starting comprehensive security review")
        
        # Review all Python files in the directory
        python_files = list(self.script_dir.glob('*.py'))
        
        for file_path in python_files:
            self._review_file(file_path)
        
        # Check for configuration issues
        self._review_configuration()
        
        # Check file permissions
        self._review_file_permissions()
        
        # Generate report
        report = self._generate_security_report()
        
        logger.info(f"Security review completed: {len(self.issues)} issues found")
        return report
    
    def _review_file(self, file_path: Path):
        """Review a single Python file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern-based checks
            self._check_patterns(file_path, content)
            
            # AST-based analysis
            try:
                tree = ast.parse(content)
                self._analyze_ast(file_path, tree)
            except SyntaxError as e:
                self.issues.append(SecurityIssue(
                    severity='low',
                    category='syntax_error',
                    description=f'Syntax error prevents full analysis: {e}',
                    file_path=str(file_path),
                    suggestion='Fix syntax errors for complete security analysis'
                ))
            
        except Exception as e:
            logger.error(f"Failed to review file {file_path}: {e}")
    
    def _check_patterns(self, file_path: Path, content: str):
        """Check file content against security patterns"""
        lines = content.split('\n')
        
        for category, patterns in self.patterns.items():
            for pattern_info in patterns:
                pattern = pattern_info['pattern']
                severity = pattern_info['severity']
                description = pattern_info['description']
                
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        self.issues.append(SecurityIssue(
                            severity=severity,
                            category=category,
                            description=f"{description}: {line.strip()[:100]}",
                            file_path=str(file_path),
                            line_number=line_num,
                            suggestion=self._get_suggestion_for_pattern(category)
                        ))
    
    def _analyze_ast(self, file_path: Path, tree: ast.AST):
        """Analyze AST for security issues"""
        class SecurityAnalyzer(ast.NodeVisitor):
            def __init__(self, issues: List[SecurityIssue], file_path: str):
                self.issues = issues
                self.file_path = file_path
            
            def visit_Call(self, node):
                # Check for dangerous function calls
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['eval', 'exec']:
                        self.issues.append(SecurityIssue(
                            severity='critical',
                            category='code_execution',
                            description=f'Dangerous function call: {func_name}',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            suggestion='Use safer alternatives to eval/exec'
                        ))
                
                # Check subprocess calls
                elif isinstance(node.func, ast.Attribute):
                    if (isinstance(node.func.value, ast.Name) and 
                        node.func.value.id == 'subprocess' and
                        node.func.attr in ['call', 'run', 'Popen']):
                        
                        # Check for shell=True
                        for keyword in node.keywords:
                            if keyword.arg == 'shell' and isinstance(keyword.value, ast.Constant):
                                if keyword.value.value is True:
                                    self.issues.append(SecurityIssue(
                                        severity='high',
                                        category='command_injection',
                                        description='subprocess call with shell=True',
                                        file_path=self.file_path,
                                        line_number=node.lineno,
                                        suggestion='Use shell=False and pass command as list'
                                    ))
                
                self.generic_visit(node)
            
            def visit_Import(self, node):
                # Check for potentially dangerous imports
                for alias in node.names:
                    if alias.name in ['pickle', 'cPickle']:
                        self.issues.append(SecurityIssue(
                            severity='medium',
                            category='unsafe_deserialization',
                            description='Import of pickle module - ensure safe usage',
                            file_path=self.file_path,
                            line_number=node.lineno,
                            suggestion='Use safer serialization like JSON when possible'
                        ))
                
                self.generic_visit(node)
        
        analyzer = SecurityAnalyzer(self.issues, str(file_path))
        analyzer.visit(tree)
    
    def _get_suggestion_for_pattern(self, category: str) -> str:
        """Get security suggestion for pattern category"""
        suggestions = {
            'command_injection': 'Use parameterized commands and avoid shell=True',
            'path_traversal': 'Validate and sanitize file paths, use os.path.join()',
            'code_execution': 'Avoid eval/exec, use safer alternatives',
            'information_disclosure': 'Avoid logging sensitive information',
            'unsafe_file_operations': 'Add proper validation and error handling'
        }
        return suggestions.get(category, 'Follow security best practices')
    
    def _review_configuration(self):
        """Review configuration and setup files"""
        # Check for hardcoded credentials
        config_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']'
        ]
        
        for file_path in self.script_dir.glob('*.py'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                for pattern in config_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        self.issues.append(SecurityIssue(
                            severity='high',
                            category='hardcoded_credentials',
                            description='Potential hardcoded credentials found',
                            file_path=str(file_path),
                            suggestion='Use environment variables or secure config files'
                        ))
            except Exception:
                continue
    
    def _review_file_permissions(self):
        """Review file permissions for security issues"""
        for file_path in self.script_dir.glob('*'):
            try:
                stat_info = file_path.stat()
                mode = oct(stat_info.st_mode)[-3:]
                
                # Check for world-writable files
                if mode[-1] in ['2', '3', '6', '7']:
                    self.issues.append(SecurityIssue(
                        severity='medium',
                        category='file_permissions',
                        description=f'File is world-writable: {mode}',
                        file_path=str(file_path),
                        suggestion='Remove world-write permissions'
                    ))
                
                # Check for overly permissive directories
                if file_path.is_dir() and mode == '777':
                    self.issues.append(SecurityIssue(
                        severity='high',
                        category='file_permissions', 
                        description='Directory has overly permissive permissions (777)',
                        file_path=str(file_path),
                        suggestion='Use more restrictive directory permissions'
                    ))
                    
            except Exception:
                continue
    
    def _generate_security_report(self) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        
        # Categorize issues by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        category_counts = {}
        
        for issue in self.issues:
            severity_counts[issue.severity] += 1
            category_counts[issue.category] = category_counts.get(issue.category, 0) + 1
        
        # Calculate security score (100 - weighted penalty)
        penalty = (severity_counts['critical'] * 25 + 
                  severity_counts['high'] * 10 + 
                  severity_counts['medium'] * 5 + 
                  severity_counts['low'] * 1)
        
        security_score = max(0, 100 - penalty)
        
        # Determine overall security level
        if security_score >= 90:
            security_level = 'Excellent'
        elif security_score >= 75:
            security_level = 'Good'
        elif security_score >= 50:
            security_level = 'Fair'
        elif security_score >= 25:
            security_level = 'Poor'
        else:
            security_level = 'Critical'
        
        return {
            'review_timestamp': datetime.now().isoformat(),
            'total_issues': len(self.issues),
            'severity_breakdown': severity_counts,
            'category_breakdown': category_counts,
            'security_score': security_score,
            'security_level': security_level,
            'files_reviewed': len(list(self.script_dir.glob('*.py'))),
            'issues': [issue.to_dict() for issue in self.issues],
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on findings"""
        recommendations = []
        
        if any(issue.category == 'command_injection' for issue in self.issues):
            recommendations.append("Implement input validation and sanitization for all command parameters")
        
        if any(issue.category == 'path_traversal' for issue in self.issues):
            recommendations.append("Use os.path.join() and validate all file paths against allowed directories")
        
        if any(issue.category == 'code_execution' for issue in self.issues):
            recommendations.append("Remove all usage of eval() and exec() functions")
        
        if any(issue.category == 'hardcoded_credentials' for issue in self.issues):
            recommendations.append("Move all credentials to environment variables or secure configuration")
        
        if any(issue.category == 'file_permissions' for issue in self.issues):
            recommendations.append("Review and restrict file permissions to principle of least privilege")
        
        # General recommendations
        recommendations.extend([
            "Implement comprehensive input validation for all user inputs",
            "Add rate limiting for API calls and resource-intensive operations", 
            "Implement proper error handling that doesn't expose sensitive information",
            "Use secure logging practices that don't record sensitive data",
            "Regular security updates and dependency scanning"
        ])
        
        return recommendations


def main():
    """CLI interface for security reviewer"""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    reviewer = SecurityReviewer()
    report = reviewer.perform_comprehensive_review()
    
    # Print summary
    print(f"\n=== Security Review Report ===")
    print(f"Review completed: {report['review_timestamp']}")
    print(f"Files reviewed: {report['files_reviewed']}")
    print(f"Total issues: {report['total_issues']}")
    print(f"Security score: {report['security_score']}/100 ({report['security_level']})")
    
    print(f"\nSeverity breakdown:")
    for severity, count in report['severity_breakdown'].items():
        if count > 0:
            print(f"  {severity.title()}: {count}")
    
    print(f"\nCategory breakdown:")
    for category, count in report['category_breakdown'].items():
        print(f"  {category.replace('_', ' ').title()}: {count}")
    
    if report['issues']:
        print(f"\nTop Issues:")
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        sorted_issues = sorted(report['issues'], key=lambda x: severity_order.get(x['severity'], 5))
        
        for issue in sorted_issues[:10]:  # Show top 10 issues
            print(f"  [{issue['severity'].upper()}] {issue['description']}")
            print(f"    File: {issue['file_path']}")
            if issue['line_number']:
                print(f"    Line: {issue['line_number']}")
            if issue['suggestion']:
                print(f"    Suggestion: {issue['suggestion']}")
            print()
    
    print(f"\nRecommendations:")
    for i, recommendation in enumerate(report['recommendations'][:5], 1):
        print(f"  {i}. {recommendation}")
    
    # Save detailed report
    report_file = Path("/home/workspace/N5/tmp_execution/security_report.json")
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_file}")
    
    # Return appropriate exit code
    if report['security_score'] < 50:
        print("\nWARNING: Security score is below acceptable threshold!")
        sys.exit(1)
    else:
        print(f"\nSecurity review passed with score {report['security_score']}/100")
        sys.exit(0)


if __name__ == "__main__":
    main()