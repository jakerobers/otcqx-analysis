import csv
import hashlib
import json
from tqdm import tqdm
from openai import OpenAI
from sklearn.cluster import KMeans
from cache_utils import get_cached_data, cache_data
import numpy as np
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def get_company_embeddings(company_names):
    os.makedirs('cache', exist_ok=True)

    embeddings = []
    for name in tqdm(company_names, desc="Generating Embeddings"):
        async def fetch_embedding():
            response = client.embeddings.create(input=name, model="text-embedding-3-small")
            return {'name': name, 'embedding': response.data[0].embedding}

        cached = await get_cached_data(name, fetch_embedding)
        embeddings.append(cached['embedding'])
    return np.array(embeddings)

def process_and_cluster_companies():
    # Read the CSV file
    with open('data/Stock_Screener.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        companies = [
            {
                'Security Name': row['Security Name'],
                'Symbol': row['Symbol'],
                'Sec Type': row['Sec Type'],
                'Country': row['Country'],
                'State': row['State']
            }
            for row in reader
        ]
        company_names = [company['Security Name'] for company in companies]

    # Get embeddings for each company name
    embeddings = get_company_embeddings(company_names)

    # Cluster the companies using KMeans
    with tqdm(total=1, desc="Clustering") as pbar:
        kmeans = KMeans(n_clusters=5, random_state=0).fit(embeddings)
        pbar.update(1)
    labels = kmeans.labels_

    # Save the results to a new CSV file
    with open('data/Clustered_Companies.csv', 'w', newline='') as csvfile:
        fieldnames = ['Security Name', 'Symbol', 'Sec Type', 'Country', 'State', 'Cluster']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for company, label in zip(companies, labels):
            writer.writerow({
                'Security Name': company['Security Name'],
                'Symbol': company['Symbol'],
                'Sec Type': company['Sec Type'],
                'Country': company['Country'],
                'State': company['State'],
                'Cluster': label
            })
