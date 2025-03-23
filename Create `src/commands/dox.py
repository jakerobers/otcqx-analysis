import csv
import asyncio
from sklearn.cluster import KMeans
import numpy as np
from make_inference import make_inference

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
