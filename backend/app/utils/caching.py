import logging
from functools import lru_cache
import time
from typing import Dict, Any, Callable, TypeVar, Tuple, List, Optional, Union
import hashlib
import json
import os
import pickle
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
import base64
import redis

# Type variables for generics
T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("cache_utils")

# Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class CacheManager:
    def __init__(self):
        self.redis = redis_client
        
    @lru_cache(maxsize=1000)
    def get_from_memory_cache(self, key: str) -> Optional[Any]:
        """Get data from in-memory cache"""
        return None  # Default return, actual data is handled by lru_cache decorator

    def get_from_redis(self, key: str) -> Optional[Any]:
        """Get data from Redis cache"""
        try:
            data = self.redis.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None

    def set_in_redis(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set data in Redis cache with expiration"""
        try:
            self.redis.setex(key, expire_seconds, json.dumps(value))
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False

    def get_cached_data(self, key: str, fetch_func, expire_seconds: int = 3600) -> Any:
        """Get data from cache or fetch and cache it"""
        # Try memory cache first
        data = self.get_from_memory_cache(key)
        if data:
            logger.debug(f"Cache hit (memory): {key}")
            return data

        # Try Redis cache
        data = self.get_from_redis(key)
        if data:
            logger.debug(f"Cache hit (Redis): {key}")
            # Update memory cache
            self.get_from_memory_cache.cache_clear()
            return data

        # Fetch data if not in cache
        data = fetch_func()
        if data:
            # Store in both caches
            self.set_in_redis(key, data, expire_seconds)
            self.get_from_memory_cache.cache_clear()
            logger.debug(f"Cache miss, data fetched and cached: {key}")
        return data

    def invalidate_cache(self, key: str) -> None:
        """Invalidate cache for given key"""
        try:
            self.redis.delete(key)
            self.get_from_memory_cache.cache_clear()
            logger.debug(f"Cache invalidated: {key}")
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")

cache_manager = CacheManager()

class PerformanceMetrics:
    """Utility to track and report algorithm performance metrics."""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
    
    def record(self, operation: str, execution_time: float):
        """Record the execution time for an operation."""
        if operation not in self.metrics:
            self.metrics[operation] = []
        self.metrics[operation].append(execution_time)
    
    def get_average(self, operation: str) -> Optional[float]:
        """Get the average execution time for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return None
        return sum(self.metrics[operation]) / len(self.metrics[operation])
    
    def get_summary(self) -> Dict[str, Dict[str, float]]:
        """Get a summary of all metrics."""
        summary = {}
        for operation, times in self.metrics.items():
            if not times:
                continue
            summary[operation] = {
                'average': sum(times) / len(times),
                'min': min(times),
                'max': max(times),
                'count': len(times)
            }
        return summary
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {}
        
    def export_to_csv(self, filepath: str):
        """Export metrics to a CSV file."""
        import csv
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Operation', 'Average Time', 'Min Time', 'Max Time', 'Count'])
            
            for operation, metrics in self.get_summary().items():
                writer.writerow([
                    operation,
                    metrics['average'],
                    metrics['min'],
                    metrics['max'],
                    metrics['count']
                ])
        
        logger.info(f"Metrics exported to {filepath}")
    
    def generate_chart(self, chart_type: str = 'bar') -> str:
        """Generate a chart of the performance metrics.
        
        Args:
            chart_type: Type of chart ('bar', 'line', 'pie')
            
        Returns:
            Base64 encoded PNG image
        """
        plt.figure(figsize=(10, 6))
        summary = self.get_summary()
        operations = list(summary.keys())
        avg_times = [data['average'] for data in summary.values()]
        
        if chart_type == 'bar':
            plt.bar(operations, avg_times)
        elif chart_type == 'line':
            for op in operations:
                plt.plot(self.metrics[op], label=op)
            plt.legend()
        elif chart_type == 'pie':
            plt.pie(avg_times, labels=operations, autopct='%1.1f%%')
        
        plt.title('Operation Performance Metrics')
        plt.xlabel('Operations')
        plt.ylabel('Average Execution Time (s)')
        
        # Save to in-memory file
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str


# Create a singleton instance
performance_metrics = PerformanceMetrics()


def timed(operation_name: str):
    """Decorator to time function execution and record metrics."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            performance_metrics.record(operation_name, execution_time)
            return result
        return wrapper
    return decorator


@lru_cache(maxsize=128)
def memoized_function(func: Callable[..., T], *args, **kwargs) -> T:
    """Memoize a function with LRU cache."""
    return func(*args, **kwargs)


class CacheBase:
    """Base class for cache implementations."""
    
    def _get_key(self, *args, **kwargs) -> str:
        """Generate a unique key from function arguments."""
        key_dict = {'args': args, 'kwargs': kwargs}
        key_str = json.dumps(key_dict, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache."""
        raise NotImplementedError
    
    def set(self, key: str, value: Any):
        """Set a value in the cache."""
        raise NotImplementedError
    
    def clear(self):
        """Clear the cache."""
        raise NotImplementedError


class MemoryCache(CacheBase):
    """In-memory cache with optional size limit and eviction policies."""
    
    def __init__(self, max_size: int = 1000, eviction_policy: str = 'lru'):
        """
        Initialize memory cache.
        
        Args:
            max_size: Maximum number of items in cache
            eviction_policy: Policy for evicting items when cache is full ('lru', 'fifo', 'random')
        """
        self.max_size = max_size
        self.eviction_policy = eviction_policy
        self.cache: Dict[str, Tuple[Any, datetime]] = {}
        self.access_count: Dict[str, int] = {}
        self.last_accessed: Dict[str, datetime] = {}
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            self.hits += 1
            self.access_count[key] = self.access_count.get(key, 0) + 1
            self.last_accessed[key] = datetime.now()
            logger.debug(f"Cache hit for key: {key}")
            return value
        
        self.misses += 1
        logger.debug(f"Cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any):
        """Set a value in the cache with current timestamp."""
        # If cache is full, evict an item
        if len(self.cache) >= self.max_size and key not in self.cache:
            self._evict_item()
        
        self.cache[key] = (value, datetime.now())
        self.access_count[key] = self.access_count.get(key, 0)
        self.last_accessed[key] = datetime.now()
        logger.debug(f"Added key to cache: {key}")
    
    def _evict_item(self):
        """Evict an item based on the chosen policy."""
        if not self.cache:
            return
        
        if self.eviction_policy == 'lru':
            # Least recently used
            oldest_key = min(self.last_accessed.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.access_count[oldest_key]
            del self.last_accessed[oldest_key]
        
        elif self.eviction_policy == 'fifo':
            # First in, first out
            oldest_key = min(self.cache.items(), key=lambda x: x[1][1])[0]
            del self.cache[oldest_key]
            del self.access_count[oldest_key]
            del self.last_accessed[oldest_key]
        
        elif self.eviction_policy == 'random':
            # Random eviction
            import random
            key_to_remove = random.choice(list(self.cache.keys()))
            del self.cache[key_to_remove]
            del self.access_count[key_to_remove]
            del self.last_accessed[key_to_remove]
    
    def clear(self):
        """Clear the cache."""
        self.cache = {}
        self.access_count = {}
        self.last_accessed = {}
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_ratio = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'eviction_policy': self.eviction_policy
        }


class DiskCache(CacheBase):
    """Persistent disk cache for expensive computations."""
    
    def __init__(self, cache_name: str, expiry_hours: int = 24):
        self.cache_file = os.path.join(CACHE_DIR, f"{cache_name}.pickle")
        self.expiry_hours = expiry_hours
        self.cache = self._load_cache()
        self.hits = 0
        self.misses = 0
    
    def _load_cache(self) -> Dict[str, Tuple[Any, datetime]]:
        """Load cache from disk if it exists."""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, EOFError):
                logger.warning(f"Failed to load cache file: {self.cache_file}")
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to disk."""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Failed to save cache to {self.cache_file}: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache if it exists and is not expired."""
        if key in self.cache:
            value, timestamp = self.cache[key]
            if datetime.now() - timestamp < timedelta(hours=self.expiry_hours):
                self.hits += 1
                logger.debug(f"Disk cache hit for key: {key}")
                return value
            # Remove expired entry
            logger.debug(f"Removing expired entry for key: {key}")
            del self.cache[key]
            self._save_cache()
        
        self.misses += 1
        logger.debug(f"Disk cache miss for key: {key}")
        return None
    
    def set(self, key: str, value: Any):
        """Set a value in the cache with current timestamp."""
        self.cache[key] = (value, datetime.now())
        self._save_cache()
        logger.debug(f"Added key to disk cache: {key}")
    
    def clear(self):
        """Clear the cache."""
        self.cache = {}
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except OSError as e:
                logger.error(f"Failed to remove cache file {self.cache_file}: {e}")
    
    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics."""
        total_requests = self.hits + self.misses
        hit_ratio = self.hits / total_requests if total_requests > 0 else 0
        
        return {
            'size': len(self.cache),
            'hits': self.hits,
            'misses': self.misses,
            'hit_ratio': hit_ratio,
            'expiry_hours': self.expiry_hours
        }


def cached(expire_seconds: int = 3600):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            return cache_manager.get_cached_data(key, lambda: func(*args, **kwargs), expire_seconds)
        return wrapper
    return decorator


class CacheComparison:
    """Utility for comparing different cache implementations."""
    
    @staticmethod
    def compare_caches(test_func: Callable, inputs: List[Tuple], 
                      cache_configs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        Compare different cache configurations with the same workload.
        
        Args:
            test_func: Function to test
            inputs: List of input tuples to pass to the function
            cache_configs: List of cache configuration dictionaries
                           Each dict should have keys matching the kwargs for the cached decorator
        
        Returns:
            Dictionary of results for each cache configuration
        """
        results = {}
        
        for i, config in enumerate(cache_configs):
            cache_name = config.get('name', f"cache_{i}")
            
            # Create cached version of the function
            cached_func = cached(**config)(test_func)
            
            # Measure execution time
            start_time = time.time()
            for input_args in inputs:
                if isinstance(input_args, tuple):
                    cached_func(*input_args)
                else:
                    cached_func(input_args)
            total_time = time.time() - start_time
            
            # Collect stats
            cache_stats = cached_func.cache.get_stats()
            results[cache_name] = {
                'total_time': total_time,
                'config': config,
                'stats': cache_stats
            }
            
            # Clear cache for next test
            cached_func.cache.clear()
        
        return results


class PerformanceBenchmark:
    """Utility for benchmarking algorithm performance with various dataset sizes."""
    
    @staticmethod
    def benchmark(func: Callable, dataset_sizes: List[int], 
                  generate_dataset: Callable[[int], Tuple], 
                  repetitions: int = 3) -> Dict[int, Dict[str, float]]:
        """
        Benchmark a function with different dataset sizes.
        
        Args:
            func: The function to benchmark
            dataset_sizes: List of dataset sizes to test
            generate_dataset: Function that generates test data of a specified size
            repetitions: Number of times to repeat the test for each size
        
        Returns:
            Dictionary mapping dataset sizes to performance metrics
        """
        results = {}
        
        for size in dataset_sizes:
            size_results = []
            
            for _ in range(repetitions):
                test_data = generate_dataset(size)
                
                start_time = time.time()
                func(*test_data if isinstance(test_data, tuple) else (test_data,))
                execution_time = time.time() - start_time
                
                size_results.append(execution_time)
            
            results[size] = {
                'average': sum(size_results) / len(size_results),
                'min': min(size_results),
                'max': max(size_results),
                'data_points': size_results
            }
        
        return results
    
    @staticmethod
    def compare_algorithms(algorithms: Dict[str, Callable], dataset_sizes: List[int],
                         generate_dataset: Callable[[int], Tuple], 
                         repetitions: int = 3) -> Dict[str, Dict[int, Dict[str, float]]]:
        """
        Compare multiple algorithms across different dataset sizes.
        
        Args:
            algorithms: Dictionary mapping algorithm names to their functions
            dataset_sizes: List of dataset sizes to test
            generate_dataset: Function that generates test data of a specified size
            repetitions: Number of times to repeat the test for each size
            
        Returns:
            Dictionary mapping algorithm names to their benchmark results
        """
        results = {}
        
        for name, func in algorithms.items():
            logger.info(f"Benchmarking algorithm: {name}")
            algo_results = PerformanceBenchmark.benchmark(
                func, dataset_sizes, generate_dataset, repetitions
            )
            results[name] = algo_results
        
        return results
    
    @staticmethod
    def plot_comparison(benchmark_results: Dict[str, Dict[int, Dict[str, float]]],
                        metric: str = 'average', plot_type: str = 'line') -> str:
        """
        Generate a plot comparing algorithms.
        
        Args:
            benchmark_results: Results from compare_algorithms
            metric: Which metric to plot ('average', 'min', 'max')
            plot_type: Type of plot ('line', 'bar')
            
        Returns:
            Base64 encoded PNG image
        """
        plt.figure(figsize=(12, 8))
        
        for algo_name, algo_results in benchmark_results.items():
            sizes = sorted(algo_results.keys())
            times = [algo_results[size][metric] for size in sizes]
            
            if plot_type == 'line':
                plt.plot(sizes, times, marker='o', label=algo_name)
            elif plot_type == 'bar':
                bar_width = 0.35
                index = np.arange(len(sizes))
                plt.bar(index + bar_width * list(benchmark_results.keys()).index(algo_name), 
                        times, bar_width, label=algo_name)
        
        if plot_type == 'bar':
            plt.xticks(np.arange(len(sizes)) + bar_width/2, sizes)
        
        plt.title(f'Algorithm Performance Comparison ({metric})')
        plt.xlabel('Dataset Size')
        plt.ylabel(f'Execution Time ({metric})')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Save to in-memory file
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        
        # Convert to base64
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return img_str
    
    @staticmethod
    def identify_bottlenecks(func: Callable, test_data: Any, 
                           profiling_runs: int = 5) -> Dict[str, Any]:
        """
        Identify performance bottlenecks in a function using profiling.
        
        Args:
            func: Function to profile
            test_data: Data to use for profiling
            profiling_runs: Number of profiling runs
            
        Returns:
            Dictionary with profiling results
        """
        import cProfile
        import pstats
        from io import StringIO
        
        # Run profiler
        profiler = cProfile.Profile()
        for _ in range(profiling_runs):
            profiler.enable()
            if isinstance(test_data, tuple):
                func(*test_data)
            else:
                func(test_data)
            profiler.disable()
        
        # Get stats
        s = StringIO()
        stats = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        stats.print_stats(20)  # Print top 20 time-consuming functions
        
        # Extract function call data
        function_stats = []
        for func_tuple, (cc, nc, tt, ct, callers) in stats.stats.items():
            module_name, line_number, func_name = func_tuple
            function_stats.append({
                'module': module_name,
                'line': line_number,
                'function': func_name,
                'calls': nc,
                'time': ct,
                'time_per_call': ct/nc if nc > 0 else 0
            })
        
        # Sort by cumulative time
        function_stats.sort(key=lambda x: x['time'], reverse=True)
        
        return {
            'top_functions': function_stats[:20],
            'raw_stats': s.getvalue()
        } 