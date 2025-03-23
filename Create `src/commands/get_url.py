import csv
import asyncio
from make_inference import make_inference

async def get_url(input_file, limit=None):
    """
    Fetches the URLs for a list of companies' financial documents from a CSV file.

    :param input_file: Path to the input CSV file containing company names.
    :param limit: Optional limit on the number of companies to process.
    """
    with open(input_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        company_names = [row['Security Name'] for row in reader]

    if limit is not None:
        company_names = company_names[:limit]

    for company_name in company_names:
        input_data = {'company_name': company_name}
        url_data = await make_inference('url_fetch', input_data)
        current_url = url_data['url']
        print(f"Company: {company_name}, Visited URL: {current_url}")
