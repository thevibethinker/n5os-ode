#!/usr/bin/env python3
"""
N5 OS Jobs Workflow Validation Utilities
Input validation and sanitization utilities for job processing workflows.

This module provides reusable validation functions for companies, role filters,
file paths, and other common workflow inputs with comprehensive error reporting.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


class ValidationResult:
    """
    Container for validation results with structured error reporting.
    """
    
    def __init__(self):
        self.valid = True
        self.errors = []
        self.warnings = []
        self.data = {}
    
    def add_error(self, message: str, field: str = None) -> None:
        """Add a validation error."""
        self.valid = False
        error = {'message': message}
        if field:
            error['field'] = field
        self.errors.append(error)
    
    def add_warning(self, message: str, field: str = None) -> None:
        """Add a validation warning."""
        warning = {'message': message}
        if field:
            warning['field'] = field
        self.warnings.append(warning)
    
    def set_data(self, key: str, value: Any) -> None:
        """Set validated data."""
        self.data[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            'valid': self.valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'data': self.data
        }


def validate_companies_file(file_path: str) -> ValidationResult:
    """
    Validate companies file and extract company list.
    
    Args:
        file_path: Path to companies file
        
    Returns:
        ValidationResult with companies list or validation errors
    """
    result = ValidationResult()
    
    # Check if file exists and is accessible
    path_obj = Path(file_path)
    
    if not path_obj.exists():
        result.add_error(f"Companies file not found: {file_path}", 'companies_file')
        return result
    
    if not path_obj.is_file():
        result.add_error(f"Path is not a file: {file_path}", 'companies_file')
        return result
    
    if not os.access(path_obj, os.R_OK):
        result.add_error(f"No read permission for file: {file_path}", 'companies_file')
        return result
    
    # Read and validate file contents
    try:
        with open(path_obj, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Extract and clean company names
        companies = []
        for line_num, line in enumerate(lines, 1):
            cleaned = line.strip()
            if not cleaned:
                continue  # Skip empty lines
            
            if cleaned.startswith('#'):
                continue  # Skip comment lines
            
            # Validate individual company name
            company_validation = validate_company_name(cleaned)
            if company_validation['valid']:
                companies.append(cleaned)
            else:
                for error in company_validation['errors']:
                    result.add_warning(f"Line {line_num}: {error['message']}", 'companies_file')
        
        if not companies:
            result.add_error("No valid companies found in file", 'companies_file')
        else:
            result.set_data('companies', companies)
            result.set_data('companies_count', len(companies))
    
    except UnicodeDecodeError:
        result.add_error(f"File encoding error - file must be UTF-8: {file_path}", 'companies_file')
    except IOError as e:
        result.add_error(f"Error reading file: {str(e)}", 'companies_file')
    except Exception as e:
        result.add_error(f"Unexpected error processing file: {str(e)}", 'companies_file')
    
    return result


def validate_company_name(company: str) -> Dict[str, Any]:
    """
    Validate a single company name.
    
    Args:
        company: Company name to validate
        
    Returns:
        Dictionary with validation result
    """
    result = ValidationResult()
    
    if not company or not company.strip():
        result.add_error("Company name cannot be empty", 'company_name')
        return result.to_dict()
    
    cleaned = company.strip()
    
    # Length checks
    if len(cleaned) < 2:
        result.add_error(f"Company name too short: '{cleaned}'", 'company_name')
    
    if len(cleaned) > 100:
        result.add_warning(f"Company name very long: '{cleaned[:50]}...'", 'company_name')
    
    # Character validation - allow alphanumeric, spaces, hyphens, underscores, dots
    valid_chars = re.compile(r'^[a-zA-Z0-9\s\-_.&]+$')
    if not valid_chars.match(cleaned):
        result.add_warning(f"Company name contains unusual characters: '{cleaned}'", 'company_name')
    
    # Check for suspicious patterns
    if cleaned.lower() in ['test', 'example', 'sample', 'demo']:
        result.add_warning(f"Company name appears to be a placeholder: '{cleaned}'", 'company_name')
    
    result.set_data('company_name', cleaned)
    return result.to_dict()


def validate_role_filters(roles: List[str]) -> ValidationResult:
    """
    Validate role filter list.
    
    Args:
        roles: List of role filter strings
        
    Returns:
        ValidationResult with validated role filters
    """
    result = ValidationResult()
    
    if not roles:
        result.set_data('role_filters', [])
        return result
    
    validated_roles = []
    
    for i, role in enumerate(roles):
        if not role or not role.strip():
            result.add_warning(f"Empty role filter at position {i}", 'role_filters')
            continue
        
        cleaned = role.strip()
        
        # Length validation
        if len(cleaned) < 2:
            result.add_warning(f"Very short role filter: '{cleaned}'", 'role_filters')
        
        if len(cleaned) > 50:
            result.add_warning(f"Very long role filter: '{cleaned[:30]}...'", 'role_filters')
        
        # Common role validation
        common_roles = [
            'engineer', 'developer', 'backend', 'frontend', 'fullstack', 'full-stack',
            'senior', 'junior', 'lead', 'principal', 'staff', 'architect',
            'manager', 'director', 'analyst', 'scientist', 'researcher',
            'designer', 'product', 'marketing', 'sales', 'support'
        ]
        
        # Check if it looks like a reasonable role filter
        role_lower = cleaned.lower()
        looks_valid = any(common_word in role_lower for common_word in common_roles)
        
        if not looks_valid and len(cleaned) > 10:
            result.add_warning(f"Role filter may be too specific: '{cleaned}'", 'role_filters')
        
        validated_roles.append(cleaned)
    
    result.set_data('role_filters', validated_roles)
    result.set_data('role_filters_count', len(validated_roles))
    
    return result


def validate_output_directory(directory_path: str) -> ValidationResult:
    """
    Validate output directory accessibility and permissions.
    
    Args:
        directory_path: Path to output directory
        
    Returns:
        ValidationResult with directory validation status
    """
    result = ValidationResult()
    
    path_obj = Path(directory_path)
    
    if not path_obj.exists():
        result.add_error(f"Output directory does not exist: {directory_path}", 'output_directory')
        return result
    
    if not path_obj.is_dir():
        result.add_error(f"Path is not a directory: {directory_path}", 'output_directory')
        return result
    
    if not os.access(path_obj, os.W_OK):
        result.add_error(f"No write permission for directory: {directory_path}", 'output_directory')
        return result
    
    if not os.access(path_obj, os.R_OK):
        result.add_error(f"No read permission for directory: {directory_path}", 'output_directory')
        return result
    
    # Check disk space (basic check)
    try:
        stat = os.statvfs(path_obj)
        free_bytes = stat.f_frsize * stat.f_bavail
        free_mb = free_bytes / (1024 * 1024)
        
        if free_mb < 100:  # Less than 100MB free
            result.add_warning(f"Low disk space: {free_mb:.1f} MB available", 'output_directory')
        
        result.set_data('free_space_mb', free_mb)
    except (OSError, AttributeError):
        # statvfs not available on all systems
        result.add_warning("Could not check disk space", 'output_directory')
    
    result.set_data('output_directory', str(path_obj.absolute()))
    return result


def validate_target_list_name(list_name: str) -> ValidationResult:
    """
    Validate target list name for job storage.
    
    Args:
        list_name: Name of the target list
        
    Returns:
        ValidationResult with validated list name
    """
    result = ValidationResult()
    
    if not list_name or not list_name.strip():
        result.add_error("Target list name cannot be empty", 'target_list')
        return result
    
    cleaned = list_name.strip()
    
    # Character validation - allow alphanumeric, hyphens, underscores
    valid_chars = re.compile(r'^[a-zA-Z0-9\-_]+$')
    if not valid_chars.match(cleaned):
        result.add_error(f"Target list name contains invalid characters: '{cleaned}'", 'target_list')
    
    # Length validation
    if len(cleaned) < 3:
        result.add_error(f"Target list name too short: '{cleaned}'", 'target_list')
    
    if len(cleaned) > 50:
        result.add_error(f"Target list name too long: '{cleaned}'", 'target_list')
    
    # Reserved names check
    reserved_names = ['test', 'temp', 'tmp', 'backup', 'config', 'system']
    if cleaned.lower() in reserved_names:
        result.add_warning(f"Target list name may be reserved: '{cleaned}'", 'target_list')
    
    result.set_data('target_list', cleaned)
    return result


def validate_scrape_workflow_inputs(companies_file: str, role_filters: List[str] = None, 
                                  target_list: str = "jobs-scraped", 
                                  output_dir: str = "/home/workspace/N5/jobs/lists") -> ValidationResult:
    """
    Comprehensive validation of all scrape workflow inputs.
    
    Args:
        companies_file: Path to companies file
        role_filters: Optional role filter list
        target_list: Target list name
        output_dir: Output directory path
        
    Returns:
        ValidationResult with all validation results combined
    """
    result = ValidationResult()
    
    # Validate companies file
    companies_validation = validate_companies_file(companies_file)
    if not companies_validation.valid:
        result.errors.extend(companies_validation.errors)
    result.warnings.extend(companies_validation.warnings)
    result.data.update(companies_validation.data)
    
    # Validate role filters
    if role_filters is None:
        role_filters = []
    roles_validation = validate_role_filters(role_filters)
    if not roles_validation.valid:
        result.errors.extend(roles_validation.errors)
    result.warnings.extend(roles_validation.warnings)
    result.data.update(roles_validation.data)
    
    # Validate target list name
    list_validation = validate_target_list_name(target_list)
    if not list_validation.valid:
        result.errors.extend(list_validation.errors)
    result.warnings.extend(list_validation.warnings)
    result.data.update(list_validation.data)
    
    # Validate output directory
    output_validation = validate_output_directory(output_dir)
    if not output_validation.valid:
        result.errors.extend(output_validation.errors)
    result.warnings.extend(output_validation.warnings)
    result.data.update(output_validation.data)
    
    # Overall validation status
    result.valid = (companies_validation.valid and list_validation.valid and 
                   roles_validation.valid and output_validation.valid)
    
    return result


# Convenience functions for common validation patterns
def quick_validate_companies(companies_file: str) -> Tuple[bool, List[str], List[str]]:
    """
    Quick validation returning simple tuple format.
    
    Args:
        companies_file: Path to companies file
        
    Returns:
        Tuple of (is_valid, companies_list, error_messages)
    """
    result = validate_companies_file(companies_file)
    companies = result.data.get('companies', [])
    errors = [error['message'] for error in result.errors]
    return result.valid, companies, errors


def sanitize_role_filters(roles: List[str]) -> List[str]:
    """
    Sanitize and clean role filter list.
    
    Args:
        roles: Raw role filter list
        
    Returns:
        Cleaned and validated role filter list
    """
    if not roles:
        return []
    
    result = validate_role_filters(roles)
    return result.data.get('role_filters', [])