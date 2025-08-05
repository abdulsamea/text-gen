import asyncio
import random

class RetryHandler:
    @staticmethod
    async def run_with_exponential_backoff(
        func, max_retries=5, base_delay=1, max_delay=60, *args, **kwargs
    ):
        """
        Calls func(*args, **kwargs) retrying with exponential backoff up to max_retries.
        On failure, raises last exception.
        """
        for attempt in range(1, max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    raise
                delay = min(max_delay, base_delay * 2 ** (attempt - 1))
                jitter = random.uniform(0.5, 1.5)
                sleep_time = delay * jitter
                print(f"RetryHandler attempt {attempt} failed: {e}, retrying in {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)
