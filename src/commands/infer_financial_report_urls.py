import csv
import logging
from make_inference import make_inference
from bs4 import BeautifulSoup
from commands.get_url import get_url

logger = logging.getLogger(__name__)

async def infer_financial_report_urls(input_file, limit=None):
    """
    Infers the financial reporting page (e.g., investor relations) for a list of companies from a CSV file.

    :param input_file: Path to the input CSV file containing company names.
    :param limit: Optional limit on the number of companies to process.
    """
    # Note: We might want to get rid of the get-url command and just have
    # everything flow through this command
    urls = await get_url(input_file, limit)

    all_fin_doc_urls = []
    for company_home_url in urls:
        financial_document_urls = await _infer_financial_report_url([company_home_url])
        all_fin_doc_urls.append(financial_document_urls)

    # TODO: zip these up by company in input_file, using limit.


async def _infer_financial_report_url(url_stack):
    if len(url_stack) >= 5:
        logger.error(f"Recursion limit reached. Trace: {url_stack}")
        return

    current_url = url_stack[-1]

    # Note: we'll want to disable cachine for this call in production. Hold
    # off on this for now.
    response = await make_inference('http_fetch', {'url': current_url})
    html_content = response['content']
    print(html_content)

    # TODO: Check if we've landed on the right page!!

    # Page not found yet, check which links are available to crawl.
    soup = BeautifulSoup(html_content, 'html.parser')
    links = [(a.get('href'), a.text) for a in soup.find_all('a', href=True)]
    logger.info(f"Found links: {links}")

    # Use Determine10KLink to find the most likely 10-K link
    response = await make_inference('determine_10k_link', {'links': links})
    best_link = response['best_match']
    logger.info(f"Best 10-K link: {best_link}")

    # If a valid link is found, add it to the stack and continue recursion
    if best_link:
        next_url = best_link if best_link.startswith('http') else f"{current_url}/{best_link}"
        await _infer_financial_report_url(url_stack + [next_url])
