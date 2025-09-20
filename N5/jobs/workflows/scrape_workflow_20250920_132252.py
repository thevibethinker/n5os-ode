#!/usr/bin/env python3
"""
N5 OS Jobs Scrape Workflow - Domain Logic Module
Pure domain workflow logic for job scraping operations.

This module contains the core business logic for scraping jobs from companies,
extracted from the command authoring framework to enable reusability and
modular composition. Follows N5 OS principles and LADDER methodology.
"""

import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import os
import sys

# Add N5 to path for imports
sys.path.append('/home/workspace')

# Import existing jobs modules
from N5.jobs.modules.orchestrate import scrape_flow
from N5.jobs.modules.ats_detector import detect_ats
from N5.jobs.modules.ats_scraper import scrape_jobs
from N5.jobs.modules.dedup import deduplicate
from N5.jobs.modules.bs_filter import filter_job
from N5.jobs.modules.description_enricher import enrich_description
from N5.jobs.modules.list_writer import append_job
from N5.jobs.modules.fallback_scraper import FallbackScraper


class ScrapeWorkflow:
    """
    Pure domain workflow for job scraping operations.
    
    Encapsulates all business logic for validating inputs, executing scraping,
    and managing the complete workflow lifecycle without CLI-specific concerns.
    """
    
    def __init__(self, workflow_id: Optional[str] = None):
        """
        Initialize workflow with optional ID for tracking.
        
        Args:
            workflow_id: Optional workflow identifier. If not provided, generates UUID.
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.start_time = datetime.utcnow()
        self.logger = logging.getLogger(f'scrape_workflow.{self.workflow_id[:8]}')
        
        # Internal state for workflow execution
        self._stages = {}
        self._errors = []
        self._warnings = []
    
    def validate_inputs(self, companies_file: str, roles: List[str] = None) -> Dict[str, Any]:
        """
        Validate workflow inputs with comprehensive checks.
        
        Args:
            companies_file: Path to companies list file
            roles: Optional role filters
            
        Returns:
            Validation result with status and details
        """
        stage_name = 'input_validation'
        self._log_stage_start(stage_name)
        
        validation_result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'companies': [],
            'role_filters': roles or []
        }
        
        # Validate companies file
        companies_path = Path(companies_file)
        if not companies_path.exists():
            validation_result['valid'] = False
            validation_result['errors'].append(f"Companies file not found: {companies_file}")
        elif not companies_path.is_file():
            validation_result['valid'] = False
            validation_result['errors'].append(f"Companies path is not a file: {companies_file}")
        else:
            try:
                with open(companies_path, 'r') as f:
                    companies = [line.strip() for line in f if line.strip()]
                
                if not companies:
                    validation_result['valid'] = False
                    validation_result['errors'].append("Companies file is empty")
                else:
                    validation_result['companies'] = companies
                    self.logger.info(f"Found {len(companies)} companies to process")
                    
                    # Validate each company name
                    for company in companies:
                        if len(company) < 2:
                            validation_result['warnings'].append(f"Short company name: {company}")
                        if not company.replace('-', '').replace('_', '').replace(' ', '').isalnum():
                            validation_result['warnings'].append(f"Non-standard company name: {company}")
                            
            except Exception as e:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Error reading companies file: {str(e)}")
        
        # Validate role filters
        if roles:
            for role in roles:
                if not role.strip():
                    validation_result['warnings'].append("Empty role filter found")
                elif len(role.strip()) < 2:
                    validation_result['warnings'].append(f"Very short role filter: {role}")
        
        # Check output directory permissions
        output_dir = Path('/home/workspace/N5/jobs/lists')
        if not output_dir.exists():
            validation_result['valid'] = False
            validation_result['errors'].append(f"Output directory does not exist: {output_dir}")
        elif not os.access(output_dir, os.W_OK):
            validation_result['valid'] = False
            validation_result['errors'].append(f"No write permission for output directory: {output_dir}")
        
        # Store validation results in internal state
        self._errors.extend(validation_result['errors'])
        self._warnings.extend(validation_result['warnings'])
        
        self._log_stage_complete(stage_name, {
            'companies_count': len(validation_result.get('companies', [])),
            'role_filters_count': len(validation_result.get('role_filters', [])),
            'errors_count': len(validation_result['errors']),
            'warnings_count': len(validation_result['warnings'])
        })
        
        return validation_result
    
    def simulate_execution(self, companies: List[str], role_filters: List[str]) -> Dict[str, Any]:
        """
        Simulate workflow execution for planning and estimation.
        
        Args:
            companies: List of companies to scrape
            role_filters: Role filters to apply
            
        Returns:
            Simulation results with estimates and risk assessment
        """
        stage_name = 'simulation'
        self._log_stage_start(stage_name)
        
        simulation_result = {
            'estimated_operations': 0,
            'estimated_duration_minutes': 0,
            'risk_assessment': 'low',
            'companies_to_process': [],
            'expected_outputs': [],
            'resource_requirements': {}
        }
        
        # Estimate operations and duration based on company count
        total_companies = len(companies)
        estimated_ops = total_companies * 5  # Rough estimate: 5 ops per company
        estimated_duration = total_companies * 2  # Rough estimate: 2 minutes per company
        
        simulation_result.update({
            'estimated_operations': estimated_ops,
            'estimated_duration_minutes': estimated_duration,
            'companies_count': total_companies,
            'role_filters': role_filters,
            'resource_requirements': {
                'network_requests': estimated_ops * 10,
                'disk_space_mb': total_companies * 5,
                'memory_mb': 100
            }
        })
        
        # Risk assessment based on scale
        if total_companies > 20:
            simulation_result['risk_assessment'] = 'high'
        elif total_companies > 10:
            simulation_result['risk_assessment'] = 'medium'
        
        # Create preview of companies to process (limited for performance)
        for company in companies[:5]:
            simulation_result['companies_to_process'].append({
                'company': company,
                'estimated_jobs': 'unknown',
                'ats_detectable': 'will_check'
            })
        
        self._log_stage_complete(stage_name, simulation_result)
        return simulation_result
    
    def execute_scraping(self, companies: List[str], role_filters: List[str], target_list: str = "jobs-scraped") -> Dict[str, Any]:
        """
        Execute the complete scraping workflow for given companies and roles.
        
        Args:
            companies: List of companies to scrape
            role_filters: Role filters to apply
            target_list: Target list name for output
            
        Returns:
            Execution results with detailed metrics and per-company breakdown
        """
        stage_name = 'execution'
        self._log_stage_start(stage_name)
        
        execution_result = {
            'success': True,
            'companies_processed': 0,
            'companies_failed': 0,
            'total_jobs_found': 0,
            'jobs_added': 0,
            'jobs_rejected': 0,
            'errors': [],
            'per_company_results': {}
        }
        
        try:
            # Process each company using existing orchestration logic
            for i, company in enumerate(companies):
                company_start_time = time.time()
                self.logger.info(f"Processing company {i+1}/{len(companies)}: {company}")
                
                try:
                    # Delegate to existing scrape_flow logic
                    single_company_result = scrape_flow([company], role_filters, target_list)
                    
                    # Aggregate results
                    execution_result['companies_processed'] += 1
                    execution_result['total_jobs_found'] += single_company_result.get('new_jobs', 0)
                    execution_result['jobs_added'] += single_company_result.get('new_jobs', 0)
                    execution_result['jobs_rejected'] += single_company_result.get('rejected', 0)
                    
                    company_duration = time.time() - company_start_time
                    execution_result['per_company_results'][company] = {
                        'success': True,
                        'duration_seconds': company_duration,
                        'jobs_found': single_company_result.get('new_jobs', 0),
                        'jobs_rejected': single_company_result.get('rejected', 0),
                        'errors': single_company_result.get('errors', [])
                    }
                    
                    # Handle company-level warnings
                    if single_company_result.get('errors'):
                        for error in single_company_result['errors']:
                            self._warnings.append(f"Company {company}: {error}")
                    
                except Exception as company_error:
                    execution_result['companies_failed'] += 1
                    error_msg = f"Failed to process {company}: {str(company_error)}"
                    execution_result['errors'].append(error_msg)
                    self._errors.append(error_msg)
                    
                    execution_result['per_company_results'][company] = {
                        'success': False,
                        'error': str(company_error),
                        'duration_seconds': time.time() - company_start_time
                    }
                
                # Progress logging at intervals
                if (i + 1) % 5 == 0 or i == len(companies) - 1:
                    self.logger.info(f"Progress: {i+1}/{len(companies)} companies processed")
            
        except Exception as e:
            execution_result['success'] = False
            execution_result['errors'].append(f"Critical execution error: {str(e)}")
            self._errors.append(f"Critical execution error: {str(e)}")
        
        self._log_stage_complete(stage_name, {
            'companies_processed': execution_result['companies_processed'],
            'companies_failed': execution_result['companies_failed'],
            'jobs_added': execution_result['jobs_added'],
            'jobs_rejected': execution_result['jobs_rejected']
        })
        
        return execution_result
    
    def run_workflow(self, companies_file: str, role_filters: List[str] = None, target_list: str = "jobs-scraped", dry_run: bool = False) -> Dict[str, Any]:
        """
        Execute the complete scrape workflow from start to finish.
        
        Args:
            companies_file: Path to companies list file
            role_filters: Optional role filters to apply
            target_list: Target list name for output
            dry_run: Whether to simulate only without actual scraping
            
        Returns:
            Complete workflow results including validation, simulation, and execution
        """
        workflow_result = {
            'workflow_id': self.workflow_id,
            'success': True,
            'dry_run': dry_run,
            'start_time': self.start_time.isoformat() + 'Z',
            'stages': {},
            'errors': [],
            'warnings': []
        }
        
        try:
            # Stage 1: Validate inputs
            validation_result = self.validate_inputs(companies_file, role_filters or [])
            workflow_result['stages']['validation'] = validation_result
            
            if not validation_result['valid']:
                workflow_result['success'] = False
                workflow_result['errors'] = validation_result['errors']
                return self._finalize_workflow_result(workflow_result)
            
            companies = validation_result['companies']
            role_filters = role_filters or []
            
            # Stage 2: Simulate execution
            simulation_result = self.simulate_execution(companies, role_filters)
            workflow_result['stages']['simulation'] = simulation_result
            
            # If dry run, stop here
            if dry_run:
                return self._finalize_workflow_result(workflow_result)
            
            # Stage 3: Execute scraping
            execution_result = self.execute_scraping(companies, role_filters, target_list)
            workflow_result['stages']['execution'] = execution_result
            workflow_result['success'] = execution_result['success']
            
        except Exception as e:
            workflow_result['success'] = False
            workflow_result['errors'].append(f"Workflow error: {str(e)}")
            self._errors.append(f"Workflow error: {str(e)}")
        
        return self._finalize_workflow_result(workflow_result)
    
    def _log_stage_start(self, stage: str) -> None:
        """Internal method to log stage start."""
        self._stages[stage] = {
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'status': 'in_progress'
        }
        self.logger.info(f"Stage started: {stage}")
    
    def _log_stage_complete(self, stage: str, metrics: Dict[str, Any] = None) -> None:
        """Internal method to log stage completion."""
        if stage in self._stages:
            self._stages[stage]['end_time'] = datetime.utcnow().isoformat() + 'Z'
            self._stages[stage]['status'] = 'completed'
            if metrics:
                self._stages[stage]['metrics'] = metrics
        self.logger.info(f"Stage completed: {stage}")
    
    def _finalize_workflow_result(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to finalize workflow results."""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()
        
        workflow_result.update({
            'end_time': end_time.isoformat() + 'Z',
            'duration_seconds': duration,
            'errors': self._errors,
            'warnings': self._warnings,
            'internal_stages': self._stages
        })
        
        return workflow_result


# Backward compatibility function
def scrape_jobs_workflow(companies: List[str], role_filters: List[str], target_list: str) -> Dict:
    """
    Orchestrate job scraping from companies with filters.
    Use fallback scraper if ATS scraping fails.
    """
    all_new_jobs = []
    rejected_count = 0
    errors = []

    for company in companies:
        try:
            ats_info = detect_ats(company)
            if not ats_info:
                # Use fallback scraper with guessed careers url
                fallback_url = f"https://{company.lower()}.com/careers"
                fallback_scraper = FallbackScraper(fallback_url)
                raw_jobs = fallback_scraper.scrape_jobs()
            else:
                raw_jobs = scrape_jobs(ats_info['careers_url'], role_filters)

            deduped = deduplicate(raw_jobs, f"/home/workspace/N5/jobs/lists/{target_list}.jsonl")

            for job in deduped:
                filter_result = filter_job(job)
                if filter_result['verdict'] == 'pass':
                    desc = enrich_description(job['url'])
                    job['description'] = desc
                    append_job(job, target_list)
                    all_new_jobs.append(job)
                else:
                    rejected_count += 1
        except Exception as e:
            errors.append(f"Error with {company}: {str(e)}")

    return {"new_jobs": len(all_new_jobs), "rejected": rejected_count, "errors": errors}


# Factory function for workflow instantiation
def create_scrape_workflow(workflow_id: Optional[str] = None) -> ScrapeWorkflow:
    """
    Factory function to create a new scrape workflow instance.
    
    Args:
        workflow_id: Optional workflow identifier
        
    Returns:
        New ScrapeWorkflow instance
    """
    return ScrapeWorkflow(workflow_id)


# Convenience function for direct workflow execution
def run_scrape_workflow(companies_file: str, role_filters: List[str] = None, target_list: str = "jobs-scraped", dry_run: bool = False, workflow_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function to create and run a scrape workflow in one call.
    
    Args:
        companies_file: Path to companies list file
        role_filters: Optional role filters to apply
        target_list: Target list name for output
        dry_run: Whether to simulate only without actual scraping
        workflow_id: Optional workflow identifier
        
    Returns:
        Complete workflow results
    """
    workflow = create_scrape_workflow(workflow_id)
    return workflow.run_workflow(companies_file, role_filters, target_list, dry_run)


if __name__ == "__main__":
    # Simple smoke test
    result = scrape_jobs_workflow(["stripe"], ["backend"], "jobs-scraped")
    print(result)
