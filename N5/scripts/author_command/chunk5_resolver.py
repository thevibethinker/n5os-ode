#!/usr/bin/env python3
"""
Chunk 5: Conflict Resolution and Suggestion Engine

Preemptive scan for existing commands, suggest adaptations.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import os
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path
import difflib

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

logger = logging.getLogger('chunk5_resolver')


class ConflictResolver:
    """Resolves conflicts with existing commands and suggests adaptations"""
    
    def __init__(self):
        self.similarity_matches = []
        self.conflict_resolution_time = 0.0
        self.adaptation_suggestions = []
        self.user_resolution_iterations = 0
    
    def resolve_conflicts(self, validated_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve conflicts with existing commands and suggest adaptations
        
        Args:
            validated_command: Validated command from Chunk 4
            
        Returns:
            Dict containing resolved command and telemetry
        """
        logger.info("Starting conflict resolution process")
        start_time = time.time()
        
        # Load existing commands
        existing_commands = self._load_existing_commands()
        
        # Preemptive scan for similar commands
        similar_commands = self._scan_similar_commands(validated_command, existing_commands)
        
        # Generate adaptation suggestions
        adaptations = self._generate_adaptations(validated_command, similar_commands)
        
        # Apply conflict resolution
        resolved_command = self._apply_conflict_resolution(validated_command, adaptations)
        
        self.conflict_resolution_time = time.time() - start_time
        
        logger.info(f"Conflict resolution completed in {self.conflict_resolution_time:.2f}s")
        logger.info(f"Similar commands found: {len(similar_commands)}")
        logger.info(f"Adaptation suggestions generated: {len(adaptations)}")
        logger.info(f"Final command name: {resolved_command.get('name', 'unknown')}")
        
        return {
            'resolved_command': resolved_command,
            'conflict_analysis': {
                'similar_commands': similar_commands,
                'adaptation_suggestions': adaptations,
                'resolution_strategy': 'rename_and_enhance' if adaptations else 'proceed_as_is'
            },
            'telemetry': {
                'similarity_matches': len(similar_commands),
                'conflict_resolution_time': self.conflict_resolution_time,
                'adaptation_suggestions_generated': len(adaptations),
                'user_resolution_iterations': self.user_resolution_iterations
            }
        }
    
    def _load_existing_commands(self) -> List[Dict[str, Any]]:
        """Load existing commands from N5 OS registry"""
        logger.info("Loading existing commands from registry")
        
        existing_commands = []
        
        # Try to load from executables.db if it exists
        commands_file = Path('/home/workspace/executables.db')
        if commands_file.exists():
            try:
                with open(commands_file, 'r') as f:
                    for line in f:
                        if line.strip():
                            existing_commands.append(json.loads(line))
            except Exception as e:
                logger.warning(f"Error loading executables.db: {e}")
        
        # Also scan for existing scripts
        scripts_dir = Path('/home/workspace/N5/scripts')
        if scripts_dir.exists():
            for script_file in scripts_dir.glob('*.py'):
                if script_file.name.startswith('n5_'):
                    existing_commands.append({
                        'name': script_file.stem,
                        'description': f"Existing N5 script: {script_file.name}",
                        'type': 'script',
                        'path': str(script_file)
                    })
        
        logger.info(f"Loaded {len(existing_commands)} existing commands")
        return existing_commands
    
    def _scan_similar_commands(self, new_command: Dict[str, Any], 
                              existing_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scan for similar existing commands"""
        logger.info("Scanning for similar existing commands")
        
        similar_commands = []
        new_name = new_command.get('name', '').lower()
        new_description = new_command.get('description', '').lower()
        new_parameters = [p.get('name', '') for p in new_command.get('parameters', [])]
        
        for existing in existing_commands:
            existing_name = existing.get('name', '').lower()
            existing_description = existing.get('description', '').lower()
            
            # Name similarity
            name_similarity = difflib.SequenceMatcher(None, new_name, existing_name).ratio()
            
            # Description similarity
            desc_similarity = difflib.SequenceMatcher(None, new_description, existing_description).ratio()
            
            # Parameter overlap
            existing_params = existing.get('parameters', [])
            if isinstance(existing_params, list):
                existing_param_names = [p.get('name', '') for p in existing_params]
            else:
                existing_param_names = []
            
            param_overlap = len(set(new_parameters) & set(existing_param_names))
            
            # Calculate overall similarity score
            similarity_score = (name_similarity * 0.4 + desc_similarity * 0.4 + 
                              (param_overlap / max(len(new_parameters), 1)) * 0.2)
            
            if similarity_score > 0.3:  # Similarity threshold
                similar_commands.append({
                    'existing_command': existing,
                    'similarity_score': similarity_score,
                    'name_similarity': name_similarity,
                    'description_similarity': desc_similarity,
                    'parameter_overlap': param_overlap,
                    'conflict_type': self._classify_conflict_type(similarity_score, name_similarity)
                })
        
        # Sort by similarity score
        similar_commands.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        self.similarity_matches = similar_commands
        logger.info(f"Found {len(similar_commands)} similar commands")
        
        return similar_commands
    
    def _classify_conflict_type(self, similarity_score: float, name_similarity: float) -> str:
        """Classify the type of conflict"""
        if name_similarity > 0.8:
            return 'name_collision'
        elif similarity_score > 0.7:
            return 'high_similarity'
        elif similarity_score > 0.5:
            return 'moderate_similarity'
        else:
            return 'low_similarity'
    
    def _generate_adaptations(self, new_command: Dict[str, Any], 
                            similar_commands: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate adaptation suggestions based on conflicts"""
        logger.info("Generating adaptation suggestions")
        
        adaptations = []
        
        for similar in similar_commands:
            conflict_type = similar.get('conflict_type', '')
            existing_cmd = similar.get('existing_command', {})
            
            if conflict_type == 'name_collision':
                # Suggest name modifications
                adaptations.append({
                    'type': 'rename',
                    'description': f"Rename to avoid collision with existing command '{existing_cmd.get('name', '')}'",
                    'suggestions': [
                        f"{new_command.get('name', '')}_v2",
                        f"{new_command.get('name', '')}_enhanced",
                        f"advanced_{new_command.get('name', '')}"
                    ]
                })
            
            elif conflict_type in ['high_similarity', 'moderate_similarity']:
                # Suggest feature differentiation
                adaptations.append({
                    'type': 'differentiate',
                    'description': f"Differentiate from similar command '{existing_cmd.get('name', '')}'",
                    'suggestions': [
                        "Add unique parameters not present in existing command",
                        "Focus on different use cases or workflows",
                        "Enhance with additional validation or error handling",
                        "Consider integrating with existing command instead of creating new one"
                    ]
                })
        
        # General adaptations if no specific conflicts
        if not similar_commands:
            adaptations.append({
                'type': 'enhancement',
                'description': "General enhancements for better integration",
                'suggestions': [
                    "Add --help option for better discoverability",
                    "Include version information",
                    "Add --verbose flag for detailed output"
                ]
            })
        
        self.adaptation_suggestions = adaptations
        return adaptations
    
    def _apply_conflict_resolution(self, command: Dict[str, Any], 
                                 adaptations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply conflict resolution based on adaptations"""
        logger.info("Applying conflict resolution")
        
        resolved_command = command.copy()
        
        if not adaptations:
            logger.info("No conflicts detected - proceeding with original command")
            return resolved_command
        
        # Apply automatic resolutions
        for adaptation in adaptations:
            adaptation_type = adaptation.get('type', '')
            
            if adaptation_type == 'rename' and adaptations[0].get('suggestions'):
                # Auto-rename to first suggestion
                new_name = adaptations[0]['suggestions'][0]
                resolved_command['name'] = new_name
                resolved_command['original_name'] = command.get('name', '')
                logger.info(f"Auto-renamed command from '{command.get('name', '')}' to '{new_name}'")
            
            elif adaptation_type == 'enhancement':
                # Apply general enhancements
                parameters = resolved_command.get('parameters', [])
                
                # Add help parameter if not present
                has_help = any(p.get('name') == 'help' for p in parameters)
                if not has_help:
                    parameters.append({
                        'name': 'help',
                        'type': 'boolean',
                        'required': False,
                        'description': 'Show help information',
                        'default': False
                    })
                
                # Add verbose parameter if not present
                has_verbose = any(p.get('name') == 'verbose' for p in parameters)
                if not has_verbose:
                    parameters.append({
                        'name': 'verbose',
                        'type': 'boolean',
                        'required': False,
                        'description': 'Enable verbose output',
                        'default': False
                    })
                
                resolved_command['parameters'] = parameters
                logger.info("Applied general enhancements (help and verbose parameters)")
        
        # Add conflict resolution metadata
        resolved_command['conflict_resolution'] = {
            'resolved_at': datetime.now().isoformat(),
            'adaptations_applied': len(adaptations),
            'original_command': command.get('name', ''),
            'resolution_strategy': 'auto_rename_enhance'
        }
        
        return resolved_command


async def main():
    """CLI interface for Chunk 5"""
    if len(sys.argv) != 2:
        print("Usage: python chunk5_resolver.py <validated_command.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            command_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    validated_command = command_data.get('validated_command', {})
    resolver = ConflictResolver()
    result = resolver.resolve_conflicts(validated_command)
    
    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())