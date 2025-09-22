#!/usr/bin/env python3
"""
System Upgrades JSON Schema Validator
Handles validation of system upgrade data against JSON schema.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from jsonschema import validate, ValidationError, Draft7Validator
import jsonschema

logger = logging.getLogger(__name__)

class ValidationResult:
    """Represents the result of a validation operation."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None, warnings: List[str] = None):
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings = warnings or []
    
    def add_error(self, error: str):
        self.is_valid = False
        self.errors.append(error)
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def __bool__(self):
        return self.is_valid
    
    def __str__(self):
        status = "VALID" if self.is_valid else "INVALID"
        result = f"Validation Result: {status}\n"
        
        if self.errors:
            result += "\nErrors:\n"
            for error in self.errors:
                result += f"  • {error}\n"
        
        if self.warnings:
            result += "\nWarnings:\n"
            for warning in self.warnings:
                result += f"  • {warning}\n"
        
        return result

class SystemUpgradesValidator:
    """Validates system upgrade data against JSON schema."""
    
    def __init__(self, schema_path: Path):
        """
        Initialize validator.
        
        Args:
            schema_path: Path to JSON schema file
        """
        self.schema_path = Path(schema_path)
        with open(self.schema_path) as f:
            self.schema = json.load(f)
        
        # Create validator
        self.validator = Draft7Validator(self.schema)
    
    def validate_item(self, item: Dict[str, Any]) -> ValidationResult:
        """
        Validate a single system upgrade item.
        
        Args:
            item: System upgrade item to validate
            
        Returns:
            ValidationResult object with detailed error information
        """
        result = ValidationResult()
        
        try:
            # Basic validation against schema
            self.validator.validate(item)
            logger.debug("Item passed schema validation")
            
            # Additional custom validations
            self._validate_date_fields(item, result)
            self._validate_id_uniqueness(item, result)
            self._validate_fields_consistency(item, result)
            
        except ValidationError as e:
            result.add_error(f"Schema validation failed: {e.message}")
            result.add_error(f"Failed at path: {' -> '.join(str(p) for p in e.path)}")
            logger.error(f"Validation error for item {item.get('id', 'unknown')}: {e}")
            
        except Exception as e:
            result.add_error(f"Unexpected validation error: {str(e)}")
            logger.error(f"Unexpected validation error: {e}")
        
        return result
    
    def validate_jsonl_file(self, jsonl_path: Path) -> Tuple[ValidationResult, List[Dict[str, Any]]]:
        """
        Validate all items in a JSONL file.
        
        Args:
            jsonl_path: Path to JSONL file
            
        Returns:
            Tuple of (overall validation result, list of valid items)
        """
        overall_result = ValidationResult()
        valid_items = []
        seen_ids = set()
        
        try:
            jsonl_path = Path(jsonl_path)
            if not jsonl_path.exists():
                overall_result.add_warning(f"JSONL file does not exist: {jsonl_path}")
                return overall_result, valid_items
            
            with open(jsonl_path, 'r', encoding='utf-8') as f:
                line_num = 0
                for line in f:
                    line_num += 1
                    line = line.strip()
                    
                    if not line:
                        continue
                    
                    try:
                        item = json.loads(line)
                        item_result = self.validate_item(item)
                        
                        if item_result:
                            valid_items.append(item)
                            
                            # Check for duplicate IDs across items
                            item_id = item.get('id')
                            if item_id in seen_ids:
                                overall_result.add_error(f"Line {line_num}: Duplicate ID '{item_id}' found")
                            else:
                                seen_ids.add(item_id)
                        else:
                            overall_result.is_valid = False
                            overall_result.errors.extend([f"Line {line_num}: {error}" for error in item_result.errors])
                            overall_result.warnings.extend([f"Line {line_num}: {warning}" for warning in item_result.warnings])
                            
                    except json.JSONDecodeError as e:
                        overall_result.add_error(f"Line {line_num}: Invalid JSON - {str(e)}")
                    
        except Exception as e:
            overall_result.add_error(f"Failed to read JSONL file: {str(e)}")
        
        logger.info(f"Validated {line_num} lines, {len(valid_items)} valid items, {overall_result.errors.__len__()} errors")
        return overall_result, valid_items
    
    def _validate_date_fields(self, item: Dict[str, Any], result: ValidationResult):
        """Validate date field consistency."""
        created_at = item.get('created_at')
        updated_at = item.get('updated_at')
        
        if not created_at:
            result.add_error("created_at field is required")
            return
        
        try:
            created_dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            
            if updated_at:
                updated_dt = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                
                # Check if updated_at is before created_at (not allowed)
                if updated_dt < created_dt:
                    result.add_error("updated_at cannot be earlier than created_at")
                    
        except ValueError as e:
            result.add_error(f"Invalid date format: {str(e)}")
    
    def _validate_id_uniqueness(self, item: Dict[str, Any], result: ValidationResult):
        """Additional ID validation."""
        item_id = item.get('id')
        if not item_id:
            result.add_error("id field is required")
            return
        
        # Check ID format more strictly
        if not item_id.replace('-', '_').replace('.', '').isalnum():
            result.add_warning(f"ID '{item_id}' contains characters that may cause issues")
    
    def _validate_fields_consistency(self, item: Dict[str, Any], result: ValidationResult):
        """Check consistency between related fields."""
        status = item.get('status')
        category = item.get('category')
        
        # Check if status and category are consistent
        if status and category:
            if category == "Done" and status != "closed":
                result.add_warning(f"Item with category 'Done' should have status 'closed', got '{status}'")
            elif category in ["Planned", "In Progress"] and status == "closed":
                result.add_warning(f"Item with category '{category}' may not need status 'closed'")
        
        # Validate priority format
        priority = item.get('priority')
        if priority and priority not in ['L', 'M', 'H']:
            result.add_error(f"Invalid priority '{priority}', must be one of: L, M, H")


def validate_schema_against_data(schema_path: Path, data_path: Path) -> ValidationResult:
    """
    Convenience function to validate a JSONL file against a schema.
    
    Args:
        schema_path: Path to JSON schema
        data_path: Path to JSONL data file
        
    Returns:
        ValidationResult
    """
    validator = SystemUpgradesValidator(schema_path)
    result, _ = validator.validate_jsonl_file(data_path)
    return result