from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from typing import List, Callable, Any, TypeVar, Generic
import multiprocessing
import logging
from functools import partial

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')

class ParallelProcessor:
    def __init__(self, max_workers: int = None):
        """Initialize with optional max workers, defaults to CPU count"""
        self.max_workers = max_workers or multiprocessing.cpu_count()
        
    def process_in_parallel(self, items: List[T], process_func: Callable[[T], R], 
                          use_processes: bool = True) -> List[R]:
        """
        Process items in parallel using either processes or threads
        
        Args:
            items: List of items to process
            process_func: Function to process each item
            use_processes: If True, use ProcessPoolExecutor, else ThreadPoolExecutor
        """
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        
        try:
            with executor_class(max_workers=self.max_workers) as executor:
                results = list(executor.map(process_func, items))
                logger.info(f"Processed {len(results)} items in parallel using "
                          f"{'processes' if use_processes else 'threads'}")
                return results
        except Exception as e:
            logger.error(f"Parallel processing error: {str(e)}")
            raise

    def chunk_process(self, items: List[T], process_func: Callable[[List[T]], List[R]], 
                     chunk_size: int = 100) -> List[R]:
        """
        Process items in chunks for better memory management
        
        Args:
            items: List of items to process
            process_func: Function to process a chunk of items
            chunk_size: Size of each chunk
        """
        chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
        
        try:
            with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
                chunk_results = list(executor.map(process_func, chunks))
                # Flatten results
                results = [item for sublist in chunk_results for item in sublist]
                logger.info(f"Processed {len(results)} items in {len(chunks)} chunks")
                return results
        except Exception as e:
            logger.error(f"Chunk processing error: {str(e)}")
            raise

    @staticmethod
    def parallel_map(func: Callable[[T], R], items: List[T], 
                    chunk_size: int = None) -> List[R]:
        """
        Static method for simple parallel mapping
        """
        processor = ParallelProcessor()
        if chunk_size:
            chunk_func = lambda chunk: [func(item) for item in chunk]
            return processor.chunk_process(items, chunk_func, chunk_size)
        return processor.process_in_parallel(items, func)

# Example usage decorator
def parallel_execution(chunk_size: int = None):
    def decorator(func):
        def wrapper(items: List[Any], *args, **kwargs):
            process_func = partial(func, *args, **kwargs)
            return ParallelProcessor.parallel_map(process_func, items, chunk_size)
        return wrapper
    return decorator 