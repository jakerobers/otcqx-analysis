import logging
import hashlib
import json
import os

from fetchers import EmbeddingFetcher, DetermineFinancialLink, GetCompanyDescription, URLFetcher

# Set up logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    filename='logs/llm_calls.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def make_inference(identifier, input_data, cache_dir='cache', use_cache=True):
    os.makedirs(cache_dir, exist_ok=True)
    key = json.dumps(input_data, sort_keys=True)
    hash_key = hashlib.sha256(f"{identifier}:{key}".encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            data = json.load(f)
            if '_key' not in data:
                data['_key'] = identifier
                with open(cache_path, 'w') as wf:
                    json.dump(data, wf)
            logging.info(f"Cached inference: {identifier}, input_data: {input_data}")
            return data

    if identifier == 'embedding':
        fetcher = EmbeddingFetcher(api_key=os.getenv('OPENAI_API_KEY'))
    elif identifier == 'fin_link_decision':
        fetcher = DetermineFinancialLink(model_name='gpt-4o')
    elif identifier == 'company_description':
        fetcher = GetCompanyDescription(model_name='gpt-4o')
    elif identifier == 'url_fetch':
        fetcher = URLFetcher(browser_context=input_data['browser_context'])
    else:
        raise ValueError(f"Unknown identifier: {identifier}")

    logging.info(f"Inference request: {identifier}, input_data: {input_data}")
    data = await fetcher.fetch(input_data)
    data['_key'] = identifier
    cache_data(key, data, cache_dir)
    return data

def cache_data(key, data, cache_dir='cache'):
    os.makedirs(cache_dir, exist_ok=True)
    hash_key = hashlib.sha256(key.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    with open(cache_path, 'w') as f:
        json.dump(data, f)
