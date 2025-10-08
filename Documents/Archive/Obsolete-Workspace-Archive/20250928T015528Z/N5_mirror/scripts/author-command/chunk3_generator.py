#!/usr/bin/env python3
"""
Chunk 3: Command Structure Generator

Transforms scoped workflow into draft command JSON structure.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

# Configure logging (only to file when running as CLI)
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[logging.FileHandler('/home/workspace/command_authoring.log', mode='a')]
    )
else:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s',
        handlers=[
            logging.FileHandler('/home/workspace/command_authoring.log', mode='a'),
            logging.StreamHandler(sys.stdout)
        ]
    )

logger = logging.getLogger('chunk3_generator')


class CommandDraft:
    """Represents a draft command structure"""
    
    def __init__(self, name: str, description: str, workflow: str, parameters: List[Dict], 
                 examples: List[str], validation_rules: List[str], side_effects: List[str],
                 permissions: List[str], version: str = "0.1.0"):
        self.name = name
        self.description = description
        self.workflow = workflow
        self.parameters = parameters
        self.examples = examples
        self.validation_rules = validation_rules
        self.side_effects = side_effects
        self.permissions = permissions
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'workflow': self.workflow,
            'parameters': self.parameters,
            'examples': self.examples,
            'validation_rules': self.validation_rules,
            'side_effects': self.side_effects,
            'permissions': self.permissions,
            'generated_at': datetime.now().isoformat(),
            'source': 'conversation_analysis'
        }


class CommandStructureGenerator:
    """Generates command structures from workflow analysis"""
    
    def __init__(self):
        self.generation_time = 0.0
        self.command_complexity = 0
        self.schema_compliance_score = 0.0
        self.generation_errors = []
    
    def generate_command(self, workflow_scope: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a command structure from workflow scope
        
        Args:
            workflow_scope: Dict containing workflow analysis from Chunk 2
            
        Returns:
            Dict containing draft command and telemetry
        """
        logger.info("Starting command structure generation")
        start_time = time.time()
        
        try:
            # Extract workflow components
            intent = workflow_scope.get('intent', 'general_workflow')
            steps = workflow_scope.get('steps', [])
            caveats = workflow_scope.get('caveats', [])
            tools_used = workflow_scope.get('tools_used', [])
            complexity = workflow_scope.get('complexity', 'medium')
            
            # Generate command components
            command_name = self._generate_command_name(intent, tools_used)
            description = self._generate_description(intent, steps, tools_used)
            workflow_type = self._determine_workflow_type(intent, tools_used)
            parameters = self._extract_parameters(steps, caveats)
            examples = self._generate_examples(command_name, parameters)
            validation_rules = self._generate_validation_rules(caveats, parameters)
            side_effects = self._identify_side_effects(steps, caveats)
            permissions = self._determine_permissions(steps, tools_used)
            
            # Create command draft
            command_draft = CommandDraft(
                name=command_name,
                description=description,
                workflow=workflow_type,
                parameters=parameters,
                examples=examples,
                validation_rules=validation_rules,
                side_effects=side_effects,
                permissions=permissions
            )
            
            # Calculate complexity metrics
            self.command_complexity = len(steps) + len(parameters) + len(validation_rules)
            
            # Mock schema validation
            self.schema_compliance_score = self._validate_schema_compliance(command_draft.to_dict())
            
            draft_dict = command_draft.to_dict()
            
        except Exception as e:
            logger.error(f"Failed to generate command structure: {e}")
            self.generation_errors.append(str(e))
            draft_dict = {}
        
        self.generation_time = time.time() - start_time
        
        logger.info(f"Command generation completed in {self.generation_time:.2f}s")
        logger.info(f"Command complexity score: {self.command_complexity}")
        logger.info(f"Schema compliance: {self.schema_compliance_score:.2f}")
        if self.generation_errors:
            logger.warning(f"Generation errors: {len(self.generation_errors)}")
        
        return {
            'command_draft': draft_dict,
            'telemetry': {
                'generation_time': self.generation_time,
                'command_complexity': self.command_complexity,
                'schema_compliance_score': self.schema_compliance_score,
                'generation_errors': len(self.generation_errors),
                'error_details': self.generation_errors
            }
        }
    
    def _generate_command_name(self, intent: str, tools_used: List[str]) -> str:
        """Generate a unique command name based on intent and tools"""
        # Clean intent for naming
        clean_intent = re.sub(r'[^\w]', '_', intent.lower())
        
        # Use primary tool if available
        if tools_used:
            primary_tool = tools_used[0].replace('_', '-')
            return f"{primary_tool}-{clean_intent}"
        
        return f"workflow-{clean_intent}"
    
    def _generate_description(self, intent: str, steps: List[str], tools_used: List[str]) -> str:
        """Generate command description"""
        tool_list = ', '.join(tools_used[:3])  # Limit to first 3 tools
        
        if tool_list:
            return f"Automated {intent} workflow using {tool_list}"
        else:
            return f"Automated {intent} workflow with {len(steps)} steps"
    
    def _determine_workflow_type(self, intent: str, tools_used: List[str]) -> str:
        """Determine workflow category"""
        intent_lower = intent.lower()
        
        if 'analysis' in intent_lower or 'search' in intent_lower:
            return 'analysis'
        elif 'create' in intent_lower or 'generate' in intent_lower:
            return 'creation'
        elif 'process' in intent_lower or 'convert' in intent_lower:
            return 'processing'
        else:
            return 'automation'
    
    def _extract_parameters(self, steps: List[str], caveats: List[str]) -> List[Dict]:
        """Extract command parameters from steps and caveats"""
        parameters = []
        param_names = set()
        
        # Common parameter patterns
        file_patterns = ['file', 'path', 'input', 'output', 'directory']
        text_patterns = ['text', 'content', 'message', 'description']
        option_patterns = ['mode', 'type', 'format', 'level']
        
        for step in steps + caveats:
            step_lower = step.lower()
            
            # Look for file-related parameters
            for pattern in file_patterns:
                if pattern in step_lower and f"{pattern}_path" not in param_names:
                    parameters.append({
                        'name': f"{pattern}_path",
                        'type': 'string',
                        'required': True,
                        'description': f"Path to the {pattern} for processing"
                    })
                    param_names.add(f"{pattern}_path")
                    break
            
            # Look for text parameters
            for pattern in text_patterns:
                if pattern in step_lower and pattern not in param_names:
                    parameters.append({
                        'name': pattern,
                        'type': 'string',
                        'required': True,
                        'description': f"The {pattern} to process"
                    })
                    param_names.add(pattern)
                    break
            
            # Look for option parameters
            for pattern in option_patterns:
                if pattern in step_lower and pattern not in param_names:
                    parameters.append({
                        'name': pattern,
                        'type': 'string',
                        'required': False,
                        'description': f"Optional {pattern} specification",
                        'default': 'default'
                    })
                    param_names.add(pattern)
                    break
        
        # Ensure at least one parameter
        if not parameters:
            parameters.append({
                'name': 'input',
                'type': 'string',
                'required': True,
                'description': 'Primary input for the workflow'
            })
        
        return parameters
    
    def _generate_examples(self, command_name: str, parameters: List[Dict]) -> List[str]:
        """Generate usage examples"""
        examples = []
        
        if parameters:
            # Create basic example
            param_args = []
            for param in parameters:
                if param.get('required', False):
                    param_args.append(f"--{param['name']} <value>")
                else:
                    param_args.append(f"[--{param['name']} <value>]")
            
            example_cmd = f"python3 {command_name}.py {' '.join(param_args)}"
            examples.append(example_cmd)
            
            # Create specific example with mock values
            specific_args = []
            for param in parameters[:2]:  # Limit to first 2 params
                if param['name'].endswith('_path'):
                    specific_args.append(f"--{param['name']} /home/workspace/example.txt")
                elif param['name'] == 'text':
                    specific_args.append(f"--{param['name']} \"Sample text content\"")
                else:
                    specific_args.append(f"--{param['name']} example_value")
            
            if specific_args:
                specific_cmd = f"python3 {command_name}.py {' '.join(specific_args)}"
                examples.append(specific_cmd)
        
        return examples
    
    def _generate_validation_rules(self, caveats: List[str], parameters: List[Dict]) -> List[str]:
        """Generate validation rules based on caveats and parameters"""
        rules = []
        
        # Extract validation requirements from caveats
        for caveat in caveats:
            caveat_lower = caveat.lower()
            
            if 'file' in caveat_lower and 'exist' in caveat_lower:
                rules.append("Validate that all file paths exist and are accessible")
            
            if 'permission' in caveat_lower:
                rules.append("Check file permissions for read/write operations")
            
            if 'missing' in caveat_lower:
                rules.append("Handle missing dependencies gracefully")
            
            if 'error' in caveat_lower:
                rules.append("Provide clear error messages for all failure cases")
        
        # Add parameter-specific validation
        for param in parameters:
            param_name = param['name']
            if param_name.endswith('_path'):
                rules.append(f"Validate {param_name} is a valid file path")
            elif param.get('required', False):
                rules.append(f"Ensure {param_name} parameter is provided")
        
        # Ensure minimum validation rules
        if not rules:
            rules.extend([
                "Validate all required parameters are provided",
                "Check for file system permissions",
                "Ensure input data is in expected format"
            ])
        
        return rules
    
    def _identify_side_effects(self, steps: List[str], caveats: List[str]) -> List[str]:
        """Identify potential side effects of the command"""
        side_effects = []
        
        for step in steps:
            step_lower = step.lower()
            
            if 'write' in step_lower or 'create' in step_lower or 'modify' in step_lower:
                side_effects.append("writes:file")
            
            if 'delete' in step_lower or 'remove' in step_lower:
                side_effects.append("modifies:file")
            
            if 'execute' in step_lower or 'run' in step_lower:
                side_effects.append("executes:command")
        
        for caveat in caveats:
            caveat_lower = caveat.lower()
            
            if 'atomic' in caveat_lower:
                side_effects.append("atomic:operations")
            
            if 'backup' in caveat_lower:
                side_effects.append("creates:backup")
        
        # Default side effects if none identified
        if not side_effects:
            side_effects.extend(["reads:file", "writes:file"])
        
        return side_effects
    
    def _determine_permissions(self, steps: List[str], tools_used: List[str]) -> List[str]:
        """Determine required permissions"""
        permissions = []
        
        # Check for file system operations
        for step in steps:
            step_lower = step.lower()
            
            if 'file' in step_lower or 'path' in step_lower:
                permissions.append("filesystem:read")
                
                if 'write' in step_lower or 'create' in step_lower:
                    permissions.append("filesystem:write")
        
        # Check for external tool usage
        if tools_used:
            permissions.append("tools:execute")
        
        # Default permissions
        if not permissions:
            permissions.append("filesystem:read")
        
        return permissions
    
    def _validate_schema_compliance(self, command_dict: Dict[str, Any]) -> float:
        """Mock schema validation - return compliance score"""
        required_fields = ['name', 'version', 'description', 'workflow', 'parameters']
        compliance = 0.0
        
        for field in required_fields:
            if field in command_dict and command_dict[field]:
                compliance += 0.2
        
        # Additional checks
        if command_dict.get('examples'):
            compliance += 0.1
        
        if command_dict.get('validation_rules'):
            compliance += 0.1
            
        if command_dict.get('side_effects'):
            compliance += 0.1
            
        if command_dict.get('permissions'):
            compliance += 0.1
        
        return min(compliance, 1.0)  # Cap at 1.0


def main():
    """CLI interface for Chunk 3"""
    if len(sys.argv) != 2:
        print("Usage: python chunk3_generator.py <scoped_workflow.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            workflow_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    # Extract workflow scope from the input
    if 'workflow_scope' in workflow_data:
        workflow_scope = workflow_data['workflow_scope']
    else:
        workflow_scope = workflow_data
    
    generator = CommandStructureGenerator()
    result = generator.generate_command(workflow_scope)
    
    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()