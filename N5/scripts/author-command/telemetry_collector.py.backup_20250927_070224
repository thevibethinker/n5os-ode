#!/usr/bin/env python3
"""
Telemetry Collector Module

Comprehensive diagnostics and monitoring for the command authoring system.
Collects structured logging, metrics, and performance data.
"""

import json
import logging
import time
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

logger = logging.getLogger('telemetry_collector')

class TelemetryCollector:
    """Comprehensive telemetry collection and reporting system"""
    def __init__(self):
        self.metrics = {
            'execution_times': [],
            'success_rates': {},
            'error_types': {},
            'component_health': {},
            'resource_usage': {},
            'user_interactions': 0
        }
        self.telemetry_file = Path('/home/workspace/command_authoring_telemetry.json')
        self.session_start = datetime.now()

    def record_execution_time(self, component: str, duration: float, success: bool):
        """Record execution time for a component"""
        logger.info(f"{component} execution: {duration:.2f}s ({'success' if success else 'failed'})")
        self.metrics['execution_times'].append({
            'component': component,
            'duration': duration,
            'timestamp': datetime.now().isoformat(),
            'success': success
        })
        if component not in self.metrics['success_rates']:
            self.metrics['success_rates'][component] = {'total': 0, 'successful': 0}
        self.metrics['success_rates'][component]['total'] += 1
        if success:
            self.metrics['success_rates'][component]['successful'] += 1

    def record_error(self, component: str, error_type: str, details: str):
        """Record an error with context"""
        logger.error(f"Error in {component}: {error_type} - {details}")
        if error_type not in self.metrics['error_types']:
            self.metrics['error_types'][error_type] = []
        self.metrics['error_types'][error_type].append({
            'component': component,
            'details': details,
            'timestamp': datetime.now().isoformat()
        })
        self.metrics['component_health'][component] = 'error'

    def record_user_interaction(self, interaction_type: str, details: Dict[str, Any]):
        """Record user interaction for analytics"""
        self.metrics['user_interactions'] += 1
        logger.info(f"User interaction: {interaction_type}")
        self.metrics['execution_times'].append({
            'component': f'user_{interaction_type}',
            'details': details,
            'timestamp': datetime.now().isoformat(),
            'success': True
        })

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            'session_duration': (datetime.now() - self.session_start).total_seconds(),
            'total_interactions': self.metrics['user_interactions'],
            'success_rates_summary': {},
            'performance_metrics': {},
            'error_summary': {}
        }
        for component, data in self.metrics['success_rates'].items():
            rate = data['successful'] / data['total'] if data['total'] > 0 else 0
            report['success_rates_summary'][component] = {
                'total_executions': data['total'],
                'successful': data['successful'],
                'success_rate': rate
            }
        execution_times = [m['duration'] for m in self.metrics['execution_times'] if m['success']]
        if execution_times:
            report['performance_metrics'] = {
                'average_execution_time': sum(execution_times) / len(execution_times),
                'max_execution_time': max(execution_times),
                'min_execution_time': min(execution_times),
                'total_executions': len(execution_times)
            }
        for error_type, errors in self.metrics['error_types'].items():
            report['error_summary'][error_type] = {
                'count': len(errors),
                'components': list(set(e['component'] for e in errors))
            }
        logger.info(f"Performance report generated: {json.dumps(report, indent=2)}")
        return report

    def save_telemetry_data(self):
        """Save telemetry data to persistent storage"""
        telemetry_data = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics,
            'performance_report': self.get_performance_report()
        }
        try:
            with open(self.telemetry_file, 'w') as f:
                json.dump(telemetry_data, f, indent=2)
            logger.info(f"Telemetry data saved to {self.telemetry_file}")
        except Exception as e:
            logger.error(f"Failed to save telemetry data: {e}")

    def load_telemetry_data(self) -> Optional[Dict[str, Any]]:
        """Load previous telemetry data"""
        if self.telemetry_file.exists():
            try:
                with open(self.telemetry_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load telemetry data: {e}")
        return None

class MetricsAggregator:
    """Aggregate metrics from multiple sources"""
    def __init__(self):
        self.aggregated_metrics = {}

    def aggregate_execution_metrics(self, telemetry_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate execution metrics across multiple sessions"""
        all_times = []
        component_stats = {}
        for data in telemetry_data:
            for item in data.get('metrics', {}).get('execution_times', []):
                component = item['component']
                duration = item['duration']
                success = item['success']
                if component not in component_stats:
                    component_stats[component] = {'times': [], 'success_count': 0, 'total_count': 0}
                component_stats[component]['times'].append(duration)
                component_stats[component]['total_count'] += 1
                if success:
                    component_stats[component]['success_count'] += 1
                if success:
                    all_times.append(duration)
        aggregated = {
            'total_successful_executions': len(all_times),
            'average_execution_time': sum(all_times) / len(all_times) if all_times else 0,
            'component_breakdown': {}
        }
        for component, stats in component_stats.items():
            if stats['times']:
                aggregated['component_breakdown'][component] = {
                    'avg_duration': sum(stats['times']) / len(stats['times']),
                    'max_duration': max(stats['times']),
                    'min_duration': min(stats['times']),
                    'success_rate': stats['success_count'] / stats['total_count'] if stats['total_count'] > 0 else 0
                }
        return aggregated

async def main():
    """Main telemetry collection demonstration"""
    collector = TelemetryCollector()
    for i in range(5):
        collector.record_execution_time('parser', 0.1 + i * 0.1, True)
        collector.record_execution_time('generator', 0.3 + i * 0.1, i > 1)
        if i % 2 == 0:
            collector.record_error('validator', 'file_not_found', f'Missing file in iteration {i}')
        await asyncio.sleep(0.1)
    performance_report = collector.get_performance_report()
    collector.save_telemetry_data()
    aggregator = MetricsAggregator()
    previous_data = collector.load_telemetry_data()
    if previous_data:
        aggregated = aggregator.aggregate_execution_metrics([previous_data])
        logger.info(f"Aggregated metrics: {json.dumps(aggregated, indent=2)}")
    logger.info("Telemetry collection completed successfully! ")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)sZ %(levelname)s %(name)s %(message)s'
    )
    import asyncio
    asyncio.run(main())
