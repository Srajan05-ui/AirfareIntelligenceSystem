import time
import random
import logging

logger = logging.getLogger(__name__)

class TokenBucket:
    def __init__(self, rate: float, capacity: float):
        """
        Token Bucket algorithm for rate limiting.
        :param rate: Tokens generated per second.
        :param capacity: Maximum tokens the bucket can hold.
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()

    def consume(self, tokens: float = 1.0) -> bool:
        """
        Consume tokens if available.
        """
        now = time.time()
        # Add generated tokens since last update
        self.tokens += (now - self.last_update) * self.rate
        if self.tokens > self.capacity:
            self.tokens = self.capacity
        self.last_update = now

        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_for_token(self):
        """
        Wait until a token is available, adding a random network jitter.
        """
        while not self.consume(1.0):
            time.sleep(0.1)
        
        # Add IP Jitter to prevent perfectly periodic requests
        jitter = random.uniform(0.05, 0.18) # 50ms - 180ms jitter
        time.sleep(jitter)

class PoliteScraper:
    def __init__(self, requests_per_second: float = 1.5, max_burst: int = 3):
        self.bucket = TokenBucket(rate=requests_per_second, capacity=max_burst)

    def __enter__(self):
        self.bucket.wait_for_token()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
