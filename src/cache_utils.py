import hashlib
import json
import os

async def make_llm_call_with_cache(identifier, key, fetch_data_async, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    hash_key = hashlib.sha256(f"{identifier}:{key}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)
    data = None
    if not os.path.exists(cache_path):
        data = await fetch_data_async()
        cache_data(key, data, cache_dir)
    else:
        with open(cache_path, 'r') as f:
            data = json.load(f)
    return data

def cache_data(key, data, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    hash_key = hashlib.sha256(key.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    with open(cache_path, 'w') as f:
        json.dump(data, f)
