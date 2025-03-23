import sys
import os
import argparse
import csv
import asyncio
from sklearn.cluster import KMeans
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from otcqx_analysis import process_and_cluster_companies
from make_inference import make_inference, cache_data

async def get_url(company_name):
    """
    Fetches the URL for a given company's financial documents.

    :param company_name: Name of the company to search for.
    """
    input_data = {'company_name': company_name}
    url_data = await make_inference('url_fetch', input_data)
    current_url = url_data['url']
    print(f"Visited URL: {current_url}")


async def dox(input_file, output_file):
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        company_names = [row['Security Name'] for row in reader]

        # Fetch company descriptions in batches of 20
        descriptions = []
        batch_size = 20
        semaphore = asyncio.Semaphore(batch_size)

        async def fetch_description(company_name):
            async with semaphore:
                description_data = await make_inference('company_description', company_name)
                return description_data['description']

        tasks = [fetch_description(company_name) for company_name in company_names]
        descriptions = await asyncio.gather(*tasks)

        # Embed company descriptions in batches of 20
        embeddings = []
        embed_semaphore = asyncio.Semaphore(batch_size)

        async def embed_description(description):
            async with embed_semaphore:
                embedding_data = await make_inference('embedding', {'text': description})
                return embedding_data['embedding']

        embed_tasks = [embed_description(description) for description in descriptions]
        embeddings = await asyncio.gather(*embed_tasks)

        # Cluster the embeddings
        kmeans = KMeans(n_clusters=13, random_state=0)
        clusters = kmeans.fit_predict(np.array(embeddings))

        # Organize companies by cluster
        cluster_dict = {i: [] for i in range(kmeans.n_clusters)}
        for company_name, cluster in zip(company_names, clusters):
            cluster_dict[cluster].append(company_name)

        # Write to output file in CSV format
        with open(output_file, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow([f"Cluster {i}" for i in range(kmeans.n_clusters)])
            max_length = max(len(names) for names in cluster_dict.values())
            for i in range(max_length):
                row = [cluster_dict[cluster][i] if i < len(cluster_dict[cluster]) else '' for cluster in range(kmeans.n_clusters)]
                csv_writer.writerow(row)


async def infer_financial_page(company_name):
    """
    Infers the financial reporting page (e.g., investor relations) of the company.

    :param company_name: Name of the company to search for.
    """
    # Stub implementation
    print(f"Inferred financial page for {company_name}")

async def infer_financial_report_url(company_name):
    """
    Infers the financial report URL (e.g., a URL to a PDF document of a specific 10-K report).

    :param company_name: Name of the company to search for.
    """
    # Stub implementation
    print(f"Inferred financial report URL for {company_name}")
async def main():
    parser = argparse.ArgumentParser(description="OTCQX Analysis Tool")
    subparsers = parser.add_subparsers(dest='command')


    # Dox command
    dox_parser = subparsers.add_parser('dox', help='Categorizes a list of companies by industry')
    dox_parser.add_argument('-i', '--input', required=True, help='Input file path')
    dox_parser.add_argument('-o', '--output', required=True, help='Output file path')

    # Infer financial page command
    infer_fin_page_parser = subparsers.add_parser('infer-fin-page', help='Infer the financial reporting page of the company')
    infer_fin_page_parser.add_argument('-c', '--company', required=True, help='Company name')

    # Infer financial report URL command
    infer_fin_report_url_parser = subparsers.add_parser('infer-fin-report-url', help='Infer the financial report URL of the company')
    infer_fin_report_url_parser.add_argument('-c', '--company', required=True, help='Company name')
    get_url_parser = subparsers.add_parser('get-url', help='Fetch the URL for a company\'s financial documents')
    get_url_parser.add_argument('-c', '--company', required=True, help='Company name')

    args = parser.parse_args()

    if args.command == 'dox':
        await dox(args.input, args.output)
    elif args.command == 'infer-fin-page':
        await infer_financial_page(args.company)
    elif args.command == 'infer-fin-report-url':
        await infer_financial_report_url(args.company)
    elif args.command == 'get-url':
        await get_url(args.company)

if __name__ == "__main__":
    asyncio.run(main())
