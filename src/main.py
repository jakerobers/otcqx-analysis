import sys
import os
import argparse
import csv
import asyncio
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
            embedding_data = await make_llm_call_with_cache('embedding', {'text': description})
            embeddings.append(embedding_data['embedding'])

        # Cluster the embeddings
        kmeans = KMeans(n_clusters=5, random_state=0)
        clusters = kmeans.fit_predict(np.array(embeddings))

        # Organize companies by cluster
        cluster_dict = {i: [] for i in range(kmeans.n_clusters)}
        for company_name, cluster in zip(company_names, clusters):
            cluster_dict[cluster].append(company_name)

        # Write to stdout in CSV format
        csv_writer = csv.writer(sys.stdout)
        csv_writer.writerow([f"Cluster {i}" for i in range(kmeans.n_clusters)])
        max_length = max(len(names) for names in cluster_dict.values())
        for i in range(max_length):
            row = [cluster_dict[cluster][i] if i < len(cluster_dict[cluster]) else '' for cluster in range(kmeans.n_clusters)]
            csv_writer.writerow(row)


async def main():
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')

    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape company data')
    scrape_parser.add_argument('-i', '--input', required=True, help='Input file path')

    # Dox command
    dox_parser = subparsers.add_parser('dox', help='Categorizes a list of companies by industry')
    dox_parser.add_argument('-i', '--input', required=True, help='Input file path')

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
