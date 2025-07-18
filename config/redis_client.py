import redis
import os
from urllib.parse import urlparse

redis_parsed = urlparse(os.environ['REDIS_URL'])
redis_client = redis.from_url(
	url=os.environ['REDIS_URL'],
    decode_responses=True
)

# Test: Connection test to catch config errors early
# try:
#     redis_client.ping()
#     print("✅ Connected to Redis.")
# except redis.exceptions.RedisError as e:
#     print("❌ Redis connection failed:", str(e))