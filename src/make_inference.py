import base64
import logging
import hashlib
import json
import os

from fetchers import EmbeddingFetcher, GetCompanyDescription, URLFetcher, HTTPFetcher, IsFinancialReport, PDFFetcher

logger = logging.getLogger(__name__)

async def make_inference(identifier, input_data, cache_dir='cache', use_cache=True):
    conn = sqlite3.connect('cache_data.db')
    cursor = conn.cursor()
    input_data['_key'] = identifier
    key = json.dumps(input_data, sort_keys=True)
    hash_key = hashlib.sha256(key.encode()).hexdigest()
    if use_cache:
        cursor.execute('SELECT data FROM cache_data WHERE key = ?', (hash_key,))
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
            logger.info(f"Cached inference: {identifier}; key: {hash_key}; input_data: {input_data}")
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
    cache_data(data, input_data, hash_key, cursor)
    conn.commit()
    conn.close()
    return data

def cache_data(data, input_data, hash_key, cursor):
    data_to_cache = json.dumps({**input_data, **data})
    strategy = input_data.get('_key', None)
    cursor.execute('''
    INSERT OR IGNORE INTO cache_data (key, strategy, data)
    VALUES (?, ?, ?)
    ''', (hash_key, strategy, data_to_cache))
