import base64
import logging
import hashlib
import json
import os

from fetchers import EmbeddingFetcher, GetCompanyDescription, URLFetcher, HTTPFetcher, IsFinancialReport, PDFFetcher

logger = logging.getLogger(__name__)

async def make_inference(identifier, input_data, cache_dir='cache', use_cache=True):
    os.makedirs(cache_dir, exist_ok=True)
    input_data['_key'] = identifier
    key = json.dumps(input_data, sort_keys=True)
    hash_key = hashlib.sha256(key.encode()).hexdigest()
    cache_path = os.path.join(cache_dir, f"{hash_key}.json")
    print(cache_path)
    if use_cache and os.path.exists(cache_path):
        with open(cache_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Cached inference: {identifier}; {cache_path}; input_data: {input_data}")
        return data

    if identifier == 'embedding':
        fetcher = EmbeddingFetcher(api_key=os.getenv('OPENAI_API_KEY'))
    elif identifier == 'company_description':
        fetcher = GetCompanyDescription(model_name='gpt-4o')
    elif identifier == 'url_fetch':
        fetcher = URLFetcher()
    elif identifier == 'http_fetch':
        fetcher = HTTPFetcher()
    elif identifier == 'fetch_pdf':
        fetcher = PDFFetcher()
    elif identifier == 'is_financial_report':
        fetcher = IsFinancialReport()
    else:
        logger.error(f"Could not find fetcher for identifier: {identifier}")
        return

    logger.info(f"Inference request: {identifier}, input_data: {input_data}")
    data = await fetcher.fetch(input_data)
    cache_data(data, input_data, cache_path)
    return data

def cache_data(data, input_data, cache_path):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    data_to_cache = {**input_data, **data}
    with open(cache_path, 'w') as f:
        json.dump(data_to_cache, f)
