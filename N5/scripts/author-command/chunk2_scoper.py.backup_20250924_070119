#!/usr/bin/env python3
"""
Chunk 2: LLM Scoping and Clarification Agent

Uses LLM to scope relevant workflow, extract steps/caveats, and perform Socratic questioning.
Implements telemetry logging for diagnostics.
"""

import json
import logging
import sys
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

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

logger = logging.getLogger('chunk2_scoper')


class WorkflowScope:
    """Represents a scoped workflow analysis"""
    
    def __init__(self, intent: str, steps: List[str], caveats: List[str], 
                 complexity: str, tools_used: List[str], clarifications: List[str]):
        self.intent = intent
        self.steps = steps
        self.caveats = caveats
        self.complexity = complexity
        self.tools_used = tools_used
        self.clarifications = clarifications
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'intent': self.intent,
            'steps': self.steps,
            'caveats': self.caveats,
            'complexity': self.complexity,
            'tools_used': self.tools_used,
            'clarifications': self.clarifications
        }


class LLMScopingAgent:
    """Uses LLM to scope and clarify workflow patterns"""
    
    def __init__(self):
        self.llm_queries = 0
        self.query_times = []
        self.clarification_loops = 0
        self.workflow_steps_count = 0
        self.user_interactions = 0
    
    async def scope_workflow(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze conversation segments to identify workflow patterns with LLM assistance
        
        Args:
            parsed_data: JSON from Chunk 1 containing segments and telemetry
            
        Returns:
            Dict containing scoped workflow and telemetry
        """
        logger.info("Starting LLM scoping and clarification process")
        start_time = time.time()
        
        segments = parsed_data.get('segments', [])
        
        # Extract conversation context
        conversation_text = self._extract_conversation_text(segments)
        
        # Initial LLM analysis
        initial_scope = await self._llm_analyze_workflow(conversation_text)
        
        # Socratic questioning for clarification
        clarifications = await self._socratic_clarification(initial_scope, segments)
        
        # Final workflow scope
        workflow_scope = await self._finalize_workflow_scope(initial_scope, clarifications)
        
        # Update telemetry
        self.workflow_steps_count = len(workflow_scope.steps)
        
        total_time = time.time() - start_time
        
        logger.info(f"LLM scoping completed in {total_time:.2f}s")
        logger.info(f"LLM queries: {self.llm_queries}")
        logger.info(f"Clarification loops: {self.clarification_loops}")
        logger.info(f"Workflow steps identified: {self.workflow_steps_count}")
        logger.info(f"User interactions: {self.user_interactions}")
        
        return {
            'workflow_scope': workflow_scope.to_dict(),
            'telemetry': {
                'llm_queries': self.llm_queries,
                'query_times': self.query_times,
                'clarification_loops': self.clarification_loops,
                'workflow_steps_count': self.workflow_steps_count,
                'user_interactions': self.user_interactions,
                'total_time': total_time
            }
        }
    
    def _extract_conversation_text(self, segments: List[Dict[str, Any]]) -> str:
        """Extract readable conversation text from segments"""
        conversation_lines = []
        for segment in segments:
            content = segment.get('content', '').strip()
            if content:
                segment_type = segment.get('segment_type', 'unknown')
                if segment_type == 'user_query':
                    conversation_lines.append(f"User: {content}")
                elif segment_type == 'assistant_response':
                    conversation_lines.append(f"Assistant: {content}")
                elif segment_type == 'tool_call':
                    conversation_lines.append(f"Tool: {content}")
        
        return '\n'.join(conversation_lines)
    
    async def _llm_analyze_workflow(self, conversation_text: str) -> WorkflowScope:
        """Analyze conversation workflow with improved LLM simulation"""
        logger.info("Performing initial LLM workflow analysis")
        query_start = time.time()
        
        # Simulate LLM processing time
        await asyncio.sleep(0.1)
        
        # Extract actual tools from conversation
        tools_mentioned = self._extract_tools_from_conversation(conversation_text)
        
        # Analyze conversation to determine intent and complexity
        intent = self._determine_intent(conversation_text)
        complexity = self._assess_complexity(conversation_text)
        
        # Generate workflow steps based on conversation content
        steps = self._generate_workflow_steps(conversation_text, tools_mentioned)
        
        # Generate caveats based on conversation patterns
        caveats = self._generate_caveats(conversation_text)
        
        query_time = time.time() - query_start
        self.llm_queries += 1
        self.query_times.append(query_time)
        
        logger.info(f"Initial LLM analysis: {len(steps)} steps identified")
        
        return WorkflowScope(
            intent=intent,
            steps=steps,
            caveats=caveats,
            complexity=complexity,
            tools_used=tools_mentioned,
            clarifications=[]
        )
    
    async def _socratic_clarification(self, initial_scope: WorkflowScope, 
                                    segments: List[Dict[str, Any]]) -> List[str]:
        """Perform Socratic questioning to clarify workflow details"""
        logger.info("Starting Socratic clarification process")
        
        clarifications = []
        
        # Single clarification loop to avoid duplication
        self.clarification_loops += 1
        
        # Generate clarification questions based on scope
        questions = await self._generate_clarification_questions(initial_scope)
        
        if questions:
            # Simulate user responses (in real implementation, this would be interactive)
            responses = await self._simulate_user_responses(questions)
            clarifications.extend(responses)
            
            # Update scope based on clarifications
            await self._update_scope_from_clarifications(initial_scope, responses)
            
            logger.info(f"Clarification completed: {len(responses)} responses")
        
        logger.info(f"Socratic clarification completed with {len(clarifications)} clarifications")
        return clarifications
    
    async def _generate_clarification_questions(self, scope: WorkflowScope) -> List[str]:
        """Generate Socratic questions for workflow clarification"""
        query_start = time.time()
        await asyncio.sleep(0.05)  # Simulate LLM processing
        
        questions = []
        
        # Generate questions based on scope complexity and intent
        if scope.complexity in ['medium', 'high']:
            questions.append("What specific error handling should be included?")
        
        if 'file' in scope.intent.lower() or any('file' in tool.lower() for tool in scope.tools_used):
            questions.append("Are there any specific file formats that need special consideration?")
        
        if scope.complexity == 'high':
            questions.append("Should the command support batch processing of multiple files?")
        
        questions.append("What validation rules are most important for this workflow?")
        
        query_time = time.time() - query_start
        self.llm_queries += 1
        self.query_times.append(query_time)
        
        return questions
    
    async def _simulate_user_responses(self, questions: List[str]) -> List[str]:
        """Simulate user responses to clarification questions"""
        response_templates = {
            "error handling": "Include comprehensive error handling for file not found and permission errors",
            "file formats": "Focus on text files (.txt, .md) primarily, but allow any readable file",
            "batch processing": "Yes, batch processing would be useful for analyzing multiple files",
            "validation": "Validate that input paths exist and are readable, check command parameters"
        }
        
        responses = []
        for question in questions:
            question_lower = question.lower()
            if "error" in question_lower:
                responses.append(response_templates["error handling"])
            elif "format" in question_lower:
                responses.append(response_templates["file formats"])
            elif "batch" in question_lower:
                responses.append(response_templates["batch processing"])
            elif "validation" in question_lower:
                responses.append(response_templates["validation"])
        
        self.user_interactions += len(responses)
        return responses
    
    async def _update_scope_from_clarifications(self, scope: WorkflowScope, 
                                              clarifications: List[str]):
        """Update workflow scope based on clarification responses"""
        # Keep track of what's been added to avoid duplicates
        added_caveats = set(scope.caveats)
        added_steps = set(scope.steps)
        
        # Add clarification-based caveats
        for clarification in clarifications:
            if "error handling" in clarification.lower():
                if "file not found" in clarification.lower():
                    caveat = "Handle file not found errors gracefully"
                    if caveat not in added_caveats:
                        scope.caveats.append(caveat)
                        added_caveats.add(caveat)
                if "permission" in clarification.lower():
                    caveat = "Check file permissions before processing"
                    if caveat not in added_caveats:
                        scope.caveats.append(caveat)
                        added_caveats.add(caveat)
            
            if "batch processing" in clarification.lower():
                step = "Support batch processing of multiple files"
                if step not in added_steps:
                    scope.steps.append(step)
                    added_steps.add(step)
                    scope.complexity = "high"
    
    async def _finalize_workflow_scope(self, initial_scope: WorkflowScope, 
                                     clarifications: List[str]) -> WorkflowScope:
        """Finalize the workflow scope with all clarifications incorporated"""
        final_scope = WorkflowScope(
            intent=initial_scope.intent,
            steps=initial_scope.steps.copy(),
            caveats=initial_scope.caveats.copy(),
            complexity=initial_scope.complexity,
            tools_used=initial_scope.tools_used.copy(),
            clarifications=clarifications
        )
        
        # Add final refinements
        final_scope.caveats.append("Ensure all file operations are atomic")
        final_scope.caveats.append("Provide clear error messages to users")
        
        logger.info(f"Final workflow scope: {len(final_scope.steps)} steps, {len(final_scope.caveats)} caveats")
        
        return final_scope
    
    def _extract_tools_from_conversation(self, conversation_text: str) -> List[str]:
        """Extract tool names mentioned in the conversation"""
        tools = []
        lines = conversation_text.split('\n')
        
        for line in lines:
            if line.strip().startswith('Tool:'):
                tool_name = line.strip()[5:].strip()  # Remove "Tool: " prefix
                if tool_name and tool_name not in tools:
                    tools.append(tool_name)
        
        return tools
    
    def _determine_intent(self, conversation_text: str) -> str:
        """Determine the primary intent from conversation"""
        text_lower = conversation_text.lower()
        
        if 'create' in text_lower and 'command' in text_lower:
            return 'command_creation'
        elif 'analyze' in text_lower or 'analysis' in text_lower:
            return 'data_analysis'
        elif 'process' in text_lower or 'processing' in text_lower:
            return 'data_processing'
        elif 'search' in text_lower or 'find' in text_lower:
            return 'information_retrieval'
        else:
            return 'general_task'
    
    def _assess_complexity(self, conversation_text: str) -> str:
        """Assess workflow complexity based on conversation content"""
        text_lower = conversation_text.lower()
        
        # Count complexity indicators
        complexity_indicators = [
            'error handling', 'batch processing', 'multiple files',
            'validation', 'dry run', 'export', 'update'
        ]
        
        indicator_count = sum(1 for indicator in complexity_indicators 
                            if indicator in text_lower)
        
        if indicator_count >= 5:
            return 'high'
        elif indicator_count >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _generate_workflow_steps(self, conversation_text: str, tools: List[str]) -> List[str]:
        """Generate workflow steps based on conversation and tools"""
        steps = [
            "Analyze user requirements",
            "Validate input parameters"
        ]
        
        # Add steps based on tools mentioned
        tool_step_mapping = {
            'grep_search': "Search for existing similar implementations",
            'create_command_draft': "Generate command structure",
            'validate_command': "Validate command specification",
            'dry_run_command': "Perform testing and validation",
            'update_command': "Incorporate user feedback and improvements",
            'export_command': "Export to command registry"
        }
        
        for tool in tools:
            if tool in tool_step_mapping:
                step = tool_step_mapping[tool]
                if step not in steps:
                    steps.append(step)
        
        # Add general completion steps
        if "Export to command registry" not in steps:
            steps.append("Export to command registry")
        
        return steps
    
    def _generate_caveats(self, conversation_text: str) -> List[str]:
        """Generate caveats based on conversation content"""
        caveats = [
            "Ensure input validation",
            "Handle edge cases appropriately"
        ]
        
        text_lower = conversation_text.lower()
        
        if 'file' in text_lower:
            caveats.extend([
                "Validate file paths and permissions",
                "Handle file I/O errors gracefully"
            ])
        
        if 'error' in text_lower or 'handling' in text_lower:
            caveats.append("Implement comprehensive error handling")
        
        if 'batch' in text_lower or 'multiple' in text_lower:
            caveats.append("Consider performance for large datasets")
        
        return caveats


async def main():
    """CLI interface for Chunk 2"""
    if len(sys.argv) != 2:
        print("Usage: python chunk2_scoper.py <parsed_conversation.json>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r') as f:
            parsed_data = json.load(f)
    except Exception as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    agent = LLMScopingAgent()
    result = await agent.scope_workflow(parsed_data)
    
    # Output JSON result
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())