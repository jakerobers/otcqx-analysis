import sys
import os
import argparse
import csv
from tqdm import tqdm
from sklearn.cluster import KMeans
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from otcqx_analysis import process_and_cluster_companies
from cache_utils import make_llm_call_with_cache, cache_data

def scrape(input_file):
    pass

async def dox(input_file):
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        company_names = [row['Security Name'] for row in reader]

        # Fetch company descriptions
        descriptions = []
        for company_name in tqdm(company_names, desc="Fetching Descriptions"):
            description_data = await make_llm_call_with_cache('company_description', company_name)
            descriptions.append(description_data['description'])

        # Embed company descriptions
        embeddings = []
        for description in tqdm(descriptions, desc="Embedding Descriptions"):
            embedding_data = await make_llm_call_with_cache('embedding', {'text': description, 'name': ''})
            embeddings.append(embedding_data['embedding'])

        # Cluster the embeddings
        kmeans = KMeans(n_clusters=5, random_state=0)
        clusters = kmeans.fit_predict(np.array(embeddings))

        for company_name, cluster in zip(company_names, clusters):
            print(f"Company: {company_name}, Cluster: {cluster}")

import asyncio

async def main():
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape company data')
    scrape_parser.add_argument('-i', '--input', required=True, help='Input file path')

    args = parser.parse_args()

    if args.command == 'scrape':
        scrape(args.input)
    elif args.command == 'dox':
        await dox(args.input)
    else:
        return
        # TODO: Implement better clustering algorithm
        process_and_cluster_companies()

if __name__ == "__main__":
    asyncio.run(main())
