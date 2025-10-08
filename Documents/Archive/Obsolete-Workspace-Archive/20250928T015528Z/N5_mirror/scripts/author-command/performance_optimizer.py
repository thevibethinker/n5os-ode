#!/usr/bin/env python3
"""
Performance Optimizer for Command Authoring System

Implements caching, profiling, and performance improvements.
"""

import json
import logging
import os
import pickle
import time
from functools import wraps
from pathlib import Path
from typing import Dict, List, Any, Callable, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger('performance_optimizer')


class CacheManager:
    """Manages caching for expensive operations"""
    
    def __init__(self, cache_dir: str = "/home/workspace/N5/runtime/cache/command_authoring"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = timedelta(hours=24)  # 24 hour default TTL
    
    def _get_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments"""
        # Create a hash of the function name and arguments
        key_data = {
            'func': func_name,
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path for a cache key"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_cache_valid(self, cache_path: Path, ttl: timedelta) -> bool:
        """Check if cache file is valid (exists and not expired)"""
        if not cache_path.exists():
            return False
        
        # Check if cache has expired
        cache_time = datetime.fromtimestamp(cache_path.stat().st_mtime)
        if datetime.now() - cache_time > ttl:
            return False
        
        return True
    
    def get_cached_result(self, func_name: str, args: tuple, kwargs: dict, ttl: Optional[timedelta] = None) -> Optional[Any]:
        """Get cached result if available and valid"""
        if ttl is None:
            ttl = self.default_ttl
        
        cache_key = self._get_cache_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        if self._is_cache_valid(cache_path, ttl):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    logger.debug(f"Cache hit for {func_name}")
                    return cached_data['result']
            except Exception as e:
                logger.warning(f"Failed to load cache for {func_name}: {e}")
        
        return None
    
    def cache_result(self, func_name: str, args: tuple, kwargs: dict, result: Any):
        """Cache function result"""
        cache_key = self._get_cache_key(func_name, args, kwargs)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            cached_data = {
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'func_name': func_name
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(cached_data, f)
            
            logger.debug(f"Cached result for {func_name}")
            
        except Exception as e:
            logger.warning(f"Failed to cache result for {func_name}: {e}")
    
    def clear_cache(self, pattern: Optional[str] = None):
        """Clear cache files, optionally matching a pattern"""
        if pattern:
            cache_files = list(self.cache_dir.glob(f"*{pattern}*"))
        else:
            cache_files = list(self.cache_dir.glob("*.cache"))
        
        for cache_file in cache_files:
            try:
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")
        
        logger.info(f"Cleared {len(cache_files)} cache files")


class PerformanceProfiler:
    """Profiles function execution for performance analysis"""
    
    def __init__(self):
        self.profile_data = {}
    
    def record_execution(self, func_name: str, duration: float, success: bool, args_count: int = 0):
        """Record function execution metrics"""
        if func_name not in self.profile_data:
            self.profile_data[func_name] = {
                'total_calls': 0,
                'total_time': 0.0,
                'avg_time': 0.0,
                'min_time': float('inf'),
                'max_time': 0.0,
                'success_count': 0,
                'error_count': 0,
                'args_counts': []
            }
        
        data = self.profile_data[func_name]
        data['total_calls'] += 1
        data['total_time'] += duration
        data['avg_time'] = data['total_time'] / data['total_calls']
        data['min_time'] = min(data['min_time'], duration)
        data['max_time'] = max(data['max_time'], duration)
        data['args_counts'].append(args_count)
        
        if success:
            data['success_count'] += 1
        else:
            data['error_count'] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'functions': {},
            'summary': {
                'total_functions': len(self.profile_data),
                'total_calls': sum(data['total_calls'] for data in self.profile_data.values()),
                'total_time': sum(data['total_time'] for data in self.profile_data.values()),
                'slowest_functions': [],
                'most_called_functions': []
            }
        }
        
        for func_name, data in self.profile_data.items():
            report['functions'][func_name] = {
                'total_calls': data['total_calls'],
                'total_time': round(data['total_time'], 4),
                'avg_time': round(data['avg_time'], 4),
                'min_time': round(data['min_time'], 4),
                'max_time': round(data['max_time'], 4),
                'success_rate': data['success_count'] / data['total_calls'] if data['total_calls'] > 0 else 0,
                'avg_args_count': sum(data['args_counts']) / len(data['args_counts']) if data['args_counts'] else 0
            }
        
        # Find slowest functions by average time
        sorted_by_avg_time = sorted(
            report['functions'].items(),
            key=lambda x: x[1]['avg_time'],
            reverse=True
        )
        report['summary']['slowest_functions'] = sorted_by_avg_time[:5]
        
        # Find most called functions
        sorted_by_calls = sorted(
            report['functions'].items(),
            key=lambda x: x[1]['total_calls'],
            reverse=True
        )
        report['summary']['most_called_functions'] = sorted_by_calls[:5]
        
        return report


# Global instances
cache_manager = CacheManager()
profiler = PerformanceProfiler()


def cached(ttl: Optional[timedelta] = None):
    """Decorator to cache function results"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check cache first
            cached_result = cache_manager.get_cached_result(func.__name__, args, kwargs, ttl)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_manager.cache_result(func.__name__, args, kwargs, result)
            
            return result
        
        return wrapper
    return decorator


def profile_performance(func: Callable) -> Callable:
    """Decorator to profile function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        success = True
        
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            profiler.record_execution(
                func.__name__,
                duration,
                success,
                len(args) + len(kwargs)
            )
    
    return wrapper


class PerformanceOptimizer:
    """Main performance optimization coordinator"""
    
    def __init__(self):
        self.cache_manager = cache_manager
        self.profiler = profiler
    
    def optimize_conversation_parsing(self):
        """Apply optimizations to conversation parsing"""
        # Import here to avoid circular imports
        from chunk1_parser import ConversationParser
        
        # Patch parsing method with caching and profiling
        original_parse = ConversationParser.parse_conversation
        
        @cached(ttl=timedelta(hours=1))
        @profile_performance
        def optimized_parse_conversation(self, conversation_path: str):
            return original_parse(self, conversation_path)
        
        ConversationParser.parse_conversation = optimized_parse_conversation
        logger.info("Applied optimizations to conversation parsing")
    
    def optimize_llm_scoping(self):
        """Apply optimizations to LLM scoping"""
        from chunk2_scoper import LLMScopingAgent
        
        # Cache LLM results since they're expensive
        original_scope = LLMScopingAgent.scope_workflow
        
        @cached(ttl=timedelta(hours=6))  # Cache LLM results longer
        @profile_performance
        async def optimized_scope_workflow(self, parsed_data):
            return await original_scope(self, parsed_data)
        
        LLMScopingAgent.scope_workflow = optimized_scope_workflow
        logger.info("Applied optimizations to LLM scoping")
    
    def optimize_all_components(self):
        """Apply optimizations to all components"""
        try:
            self.optimize_conversation_parsing()
            self.optimize_llm_scoping()
            
            logger.info("Performance optimizations applied to all components")
            
        except Exception as e:
            logger.error(f"Failed to apply optimizations: {e}")
    
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and provide recommendations"""
        report = self.profiler.get_performance_report()
        
        # Add recommendations based on performance data
        recommendations = []
        
        for func_name, metrics in report['functions'].items():
            if metrics['avg_time'] > 1.0:
                recommendations.append(f"Consider optimizing {func_name} - average time {metrics['avg_time']:.2f}s")
            
            if metrics['success_rate'] < 0.95:
                recommendations.append(f"Improve error handling in {func_name} - success rate {metrics['success_rate']:.1%}")
        
        # Check cache hit rates
        cache_files = list(self.cache_manager.cache_dir.glob("*.cache"))
        if len(cache_files) > 100:
            recommendations.append("Consider cleaning old cache files to improve performance")
        
        report['recommendations'] = recommendations
        return report
    
    def cleanup_cache(self, max_age_hours: int = 168):  # 7 days default
        """Clean up old cache files"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        for cache_file in self.cache_manager.cache_dir.glob("*.cache"):
            try:
                file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if file_time < cutoff_time:
                    cache_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                logger.warning(f"Failed to clean cache file {cache_file}: {e}")
        
        logger.info(f"Cleaned {cleaned_count} old cache files")
        return cleaned_count


def main():
    """CLI interface for performance optimizer"""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    optimizer = PerformanceOptimizer()
    
    if len(sys.argv) < 2:
        print("Usage: python performance_optimizer.py <command>")
        print("Commands:")
        print("  optimize    - Apply performance optimizations")
        print("  analyze     - Analyze current performance")
        print("  cleanup     - Clean up old cache files")
        print("  clear-cache - Clear all cache files")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == 'optimize':
        optimizer.optimize_all_components()
        print("Performance optimizations applied")
    
    elif command == 'analyze':
        report = optimizer.analyze_performance()
        
        print("=== Performance Analysis ===")
        print(f"Functions analyzed: {report['summary']['total_functions']}")
        print(f"Total function calls: {report['summary']['total_calls']}")
        print(f"Total execution time: {report['summary']['total_time']:.2f}s")
        
        if report['summary']['slowest_functions']:
            print(f"\nSlowest functions:")
            for func_name, metrics in report['summary']['slowest_functions'][:3]:
                print(f"  {func_name}: {metrics['avg_time']:.2f}s avg ({metrics['total_calls']} calls)")
        
        if report['recommendations']:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"  {i}. {rec}")
        
        # Save detailed report
        report_path = Path("/home/workspace/N5/tmp_execution/performance_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nDetailed report saved to: {report_path}")
    
    elif command == 'cleanup':
        cleaned = optimizer.cleanup_cache()
        print(f"Cleaned {cleaned} old cache files")
    
    elif command == 'clear-cache':
        optimizer.cache_manager.clear_cache()
        print("All cache files cleared")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()