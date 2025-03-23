import hashlib
import json
import os

from llm_fetchers import EmbeddingFetcher, DetermineFinancialLink

async def make_llm_call_with_cache(identifier, input_data, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    key = json.dumps(input_data, sort_keys=True)
    hash_key = hashlib.sha256(f"{identifier}:{key}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    if os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            return json.load(f)

    if identifier == 'embedding':
        fetcher = EmbeddingFetcher(api_key=os.getenv('OPENAI_API_KEY'))
    elif identifier == 'fin_link_decision':
        fetcher = DetermineFinancialLink(model_name='gpt-4o')
    else:
        raise ValueError(f"Unknown identifier: {identifier}")

    data = await fetcher.fetch(input_data)
    cache_data(f"{identifier}:{key}", data, cache_dir)
    return data

def cache_data(key, data, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    hash_key = hashlib.sha256(key.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    with open(cache_path, 'w') as f:
        json.dump(data, f)
